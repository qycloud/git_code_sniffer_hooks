#-*- coding:utf-8 -*-
from commands import getoutput
from termcolor import colored
from common import get_commit_errors as get_php_commit_errors
from common import get_receive_errors as get_php_receive_errors
from config import base_path, config

def get_commit_errors():
  return get_php_commit_errors("php", _get_commit_file_error)

def _get_commit_file_error(path):
  file_sniffs = _get_sniffs(path, "emacs")
  file_errors = _get_errors(path)
  file_mds = _get_phpmd(path)

  file_errors = file_sniffs + file_errors + file_mds

  if not file_errors:
    return None

  errors = []
  for error in file_errors:
    errorInfo = error.split(' ')
    firstWord = errorInfo[0]
    secondWord = errorInfo[1]

    if "The class" in error or "The method" in error:
        print(colored(error, 'green'))
        continue;

    if firstWord == "No" or firstWord == "Errors":
        continue

    if secondWord == 'error':
      errors.append(colored(error, "red"))
    else:
      errors.append(colored(error, "yellow"))

  return "\n".join(errors)

def get_receive_errors(rev_old, rev_new):
  return get_php_receive_errors(
    rev_old, rev_new, "php", _get_receive_file_error
  )

def _get_receive_file_error(path):
  file_sniffs = _get_sniffs(path, "summary")
  if not file_sniffs:
    return None

  file_error = file_sniffs[-2].split(" ")
  error_count = int(file_error[3])
  warning_count = int(file_error[6])
  error = colored("%s error(s)" % error_count, "red")
  warning = colored("%s warning(s)" % warning_count, "yellow")

  if error_count > 0 and warning_count > 0:
    return "    %s  %s" % (error, warning)

  if error_count > 0 or warning_count > 0:
    return "    %s" % (error if error_count > 0 else warning)

  return None

def _get_sniffs(path, report):
  errors = getoutput(
    "%s/bin/phpcs --report=%s %s" % (base_path, report, path)
  ).split("\n")

  return [error for error in errors if error]

def _get_errors(path):
  errors = getoutput(
    "php -l  %s" % (path)
  ).split("\n")

  return [error for error in errors if error]

def _get_phpmd(path):
    errors = getoutput(
      "%s/php-bin/phpmd %s text codesize,unusedcode " % (base_path, path)
    ).split("\n")
    return [error for error in errors if error]
