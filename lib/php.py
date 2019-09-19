#-*- coding:utf-8 -*-

from commands import getoutput
from termcolor import colored
from common import get_commit_errors as get_php_commit_errors
from common import get_receive_errors as get_php_receive_errors
from config import base_path, config

tmp_dir = config.get("receive", "TMP_DIR")
phpmd_rules = config.get("receive", "PHPMD_RULES")
phpcs_report = config.get("receive", "PHPCS_REPORT")

def get_commit_errors():
  return get_php_commit_errors("php", _get_commit_file_error)

def _get_commit_file_error(path):
  file_sniffs = _get_sniffs(path, phpcs_report)
  file_errors = _get_errors(path)
  file_mds = _get_phpmd(path, phpmd_rules)

  if not file_errors and not file_mds and not file_sniffs:
    return None
  
  msg = ""
  if len(file_sniffs) > 0:
    msg += "\nPHP Code Sniffer------\n" + colored("\n".join(file_sniffs), "red")
  if len(file_mds) > 0:
    msg += "\nPHPMD------\n" + colored("\n".join(file_mds), "red")
  
  php_errors = []
  if len(file_errors) > 0:
    for err in file_errors:
      errInfo = err.split(' ')
      if errInfo[0] == "No":
        continue
      php_errors.append(err)
  if len(php_errors) > 0:
    msg += "\nPHP Syntax check------\n" + colored("\n".join(php_errors), "red")
  
  return msg

def get_receive_errors(rev_old, rev_new):
  error = get_php_receive_errors(
    rev_old, rev_new, "php", _get_receive_file_error
  )
  return error

def get_receive_errors_using_phpmd(rev_old, rev_new):
  error = get_php_receive_errors(rev_old, rev_new, "php", _get_receive_file_error_using_phpmd, with_filename=False)
  return error

def _get_receive_file_error_using_phpmd(path):
  phpmd_errors = _get_phpmd(path, phpmd_rules)
  if not phpmd_errors:
    return None

  tmp_dir_len = len(tmp_dir)
  errors = []
  for line in phpmd_errors:
    pure_error = line[tmp_dir_len:]
    pure_error = colored(pure_error, "red")
    errors.append(pure_error)
  return "\n".join(errors)


def _get_receive_file_error(path):
  file_sniffs = _get_sniffs(path, phpcs_report)
  if not file_sniffs:
    return None

  return "\n".join(file_sniffs)

def _get_sniffs(path, report):
  if not report:
    report = "full"
  errors = getoutput(
    "%s/bin/phpcs --report=%s %s" % (base_path, report, path)
  ).split("\n")

  return [error for error in errors if error]

def _get_errors(path):
  errors = getoutput(
    "php -l  %s" % (path)
  ).split("\n")

  return [error for error in errors if error]

def _get_phpmd(path, rules):
    command = "%s/php-bin/phpmd %s text %s " % (base_path, path, rules)
    errors = getoutput(command).split("\n")
    return [error for error in errors if error]
