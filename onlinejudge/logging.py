#!/usr/bin/env python3
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

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
logger.addHandler(handler)
