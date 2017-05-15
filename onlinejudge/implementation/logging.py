# Python Version: 3.x
import logging
logger = logging.getLogger(__name__)

def setLevel(lvl):
    logger.setLevel(lvl)
def addHandler(handler):
    logger.addHandler(handler)
def removeHandler(handler):
    logger.removeHandler(handler)

import colorama
from colorama import Fore, Back, Style
colorama.init()
# thanks to https://github.com/Gallopsled/pwntools/pwnlib/log.py
prefix = {
    'status'       : '[' + Fore.MAGENTA +                'x'        + Style.RESET_ALL + '] ',
    'success'      : '[' + Fore.GREEN   + Style.BRIGHT + '+'        + Style.RESET_ALL + '] ',
    'failure'      : '[' + Fore.RED     + Style.BRIGHT + '-'        + Style.RESET_ALL + '] ',
    'debug'        : '[' + Fore.RED     + Style.BRIGHT + 'DEBUG'    + Style.RESET_ALL + '] ',
    'info'         : '[' + Fore.BLUE    + Style.BRIGHT + '*'        + Style.RESET_ALL + '] ',
    'warning'      : '[' + Fore.YELLOW  + Style.BRIGHT + '!'        + Style.RESET_ALL + '] ',
    'error'        : '[' + Fore.RED     +                'ERROR'    + Style.RESET_ALL + '] ',
    'exception'    : '[' + Fore.RED     +                'ERROR'    + Style.RESET_ALL + '] ',
    'critical'     : '[' + Fore.RED     +                'CRITICAL' + Style.RESET_ALL + '] ',
}

def emit(s, *args):
    logger.info(str(s), *args)
def status(s, *args):
    logger.info(prefix['status'] + str(s), *args)
def success(s, *args):
    logger.info(prefix['success'] + str(s), *args)
def failure(s, *args):
    logger.info(prefix['failure'] + str(s), *args)
def debug(s, *args):
    logger.debug(prefix['debug'] + str(s), *args)
def info(s, *args):
    logger.info(prefix['info'] + str(s), *args)
def warning(s, *args):
    logger.warning(prefix['warning'] + str(s), *args)
def error(s, *args):
    logger.error(prefix['error'] + str(s), *args)
def exception(s, *args):
    logger.error(prefix['exception'] + str(s), *args)
def critical(s, *args):
    logger.critical(prefix['critical'] + str(s), *args)

bold = lambda s: colorama.Style.BRIGHT + s + colorama.Style.RESET_ALL
green = lambda s: colorama.Fore.GREEN + s + colorama.Fore.RESET
red = lambda s: colorama.Fore.RED + s + colorama.Fore.RESET
