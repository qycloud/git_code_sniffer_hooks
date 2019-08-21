# -*- coding:utf-8 -*-
import hashlib

from os import path, system
from commands import getoutput
from sh import awk, grep, cat, mkdir, rm
from termcolor import colored
from config import config, except_paths, base_path


def get_branch(ref_name):
    # trim "ref/heads/" and "\n"
    branch = ref_name[len("ref/heads/") + 1:].rstrip("\n")
    return branch


# 在服务端执行会返回master分支的最后一个commit id
def get_latest_commit_id():
    commit_id = getoutput("git log -1 --pretty=format:\"%h\"")
    return commit_id


# return commit id
def get_merge_base(source_branch, target_branch):
    base = getoutput("git merge-base %s %s" % (source_branch, target_branch))
    return base


def get_commit_errors(file_type, function):
    checkable = True
    if file_type == "js":
        checkable = config.getboolean("commit", "CHECK_JAVASCRIPT")
    elif file_type == "php":
        checkable = config.getboolean("commit", "CHECK_PHP")
    
    if not checkable:
        return None
    
    files = _get_commit_files(file_type)
    if not files:
        return None
    
    # Get files are both in cached zone and modified zone
    system("git diff --name-status > /tmp/git_hook")
    modified_files = _get_files(file_type, 2)
    if modified_files:
        # Ask user whether add a file in modified zone to commit
        modified_files = [modified_file for modified_file in modified_files if modified_file in files]
        stdin = open('/dev/tty')
        for modified_file in modified_files:
            print(
                'File %s has been modified but not in the cached zone, add it into ? [Y|n]' %
                colored(modified_file, 'red')
            )
            if not stdin.readline().strip().lower().startswith('n'):
                system('git add %s' % modified_file)
        
        stdin.close()
    
    errors = []
    for file_path in files:
        if path.exists(file_path):
            file_error = function(file_path)
            if file_error:
                errors.append(file_error)
    
    if errors:
        errors = colored(
            "There are some errors in below %s files:\n\n" % file_type, "magenta"
        ) + "\n".join(errors).strip("\n")
    
    return errors


def get_receive_errors(rev_old, rev_new, file_type, function, with_filename=True):
    checkable = True
    if file_type == "js":
        checkable = config.getboolean("receive", "CHECK_JAVASCRIPT")
    elif file_type == "php":
        checkable = config.getboolean("receive", "CHECK_PHP")
    
    if not checkable:
        return None
    # 改动文件的相对路径
    files = _get_receive_files(rev_old, rev_new, file_type)
    if not files:
        return None
    
    tmp_dir = config.get("receive", "TMP_DIR")
    errors = []
    for file_path in files:
        # 临时文件名
        source_file_path = tmp_dir + file_path
        mkdir("-p", "/".join(source_file_path.split("/")[:-1]))
        # 将文件内容写入临时文件
        show = getoutput("git show %s:%s > %s" % (rev_new, file_path, source_file_path))
        if show != '':
            continue
        if path.exists(source_file_path):
            # cache
            checksum = _file_checksum(source_file_path)
            checked, msg = _get_cached_check_result(checksum, function)
            if checked:
                if len(msg) > 0:
                    error_msg = file_path + msg if with_filename else msg
                    errors.append(error_msg)
                continue
            file_error = function(source_file_path)
            if file_error:
                if with_filename:
                    error_msg = file_path + file_error
                else:
                    error_msg = file_error
                errors.append(error_msg)
            _set_check_cache(checksum, function, file_error)
    # 临时文件交给系统处理
    # rm("-rf", tmp_dir)
    return "\n".join(errors)


def _get_commit_files(file_type):
    system("git diff --cached --name-status > /tmp/git_hook")
    return _get_files(file_type, 2)


def _get_receive_files(rev_old, rev_new, file_type):
    system("git diff-tree -r %s..%s > /tmp/git_hook" % (rev_old, rev_new))
    return _get_files(file_type, 6)


def _get_files(file_type, file_index):
    files = awk(
        grep(
            cat("/tmp/git_hook"), "-P", "(A|M).*.%s$" % file_type,
            _ok_code=[0, 1]
        ),
        "{print $%s}" % file_index, _iter=True
    )
    
    if not files:
        return None
    
    exten = ".%s" % file_type
    files = [file_path[:file_path.rindex(exten) + len(exten)] for file_path in files]
    if not except_paths:
        return files
    
    except_files = []
    for file_path in files:
        for except_path in except_paths:
            if file_path not in except_files and file_path.startswith(except_path):
                except_files.append(file_path)
    
    return [file_path for file_path in files if file_path not in except_files]


def _get_cached_check_result(checksum, func):
    try:
        f = open(_cache_filename(checksum, func), 'r')
        msg = f.read()
        f.close()
        return True, msg
    except IOError:
        return False, ''


def _file_checksum(filepath):
    return hashlib.md5(open(filepath, 'rb').read()).hexdigest()


def _set_check_cache(checksum, func, msg):
    try:
        f = open(_cache_filename(checksum, func), 'w')
    except IOError:
        f = open(_cache_filename(checksum, func), 'w')
    f.write(msg)
    f.close()


def _cache_filename(checksum, func):
    return base_path + '/cache/' + func.__name__ + '-' + checksum + '.cache'
