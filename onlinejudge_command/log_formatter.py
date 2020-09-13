import http.client
import logging
from typing import *

import colorama

colorama.init()

log_colors_level = {
    logging.DEBUG: '[' + colorama.Fore.RED + 'DEBUG' + colorama.Style.RESET_ALL + '] ',
    logging.INFO: '[' + colorama.Fore.BLUE + 'INFO' + colorama.Style.RESET_ALL + '] ',
    logging.WARNING: '[' + colorama.Fore.YELLOW + 'WARNING' + colorama.Style.RESET_ALL + '] ',
    logging.ERROR: '[' + colorama.Fore.RED + 'ERROR' + colorama.Style.RESET_ALL + '] ',
    logging.CRITICAL: '[' + colorama.Fore.RED + colorama.Style.BRIGHT + 'CRITICAL' + colorama.Style.RESET_ALL + '] ',
}

log_colors_semantics = {
    'NO_HEADER': '',
    'HINT': '[' + colorama.Fore.YELLOW + 'HINT' + colorama.Style.RESET_ALL + '] ',
    'NETWORK': '[' + colorama.Fore.MAGENTA + 'NETWORK' + colorama.Style.RESET_ALL + '] ',
    'SUCCESS': '[' + colorama.Fore.GREEN + 'SUCCESS' + colorama.Style.RESET_ALL + '] ',
    'FAILURE': '[' + colorama.Fore.RED + 'FAILURE' + colorama.Style.RESET_ALL + '] ',
}

status_code_messages: Set[str] = {str(int(key)) + ' ' + str(value) for key, value in http.client.responses.items()}


class LogFormatter(logging.Formatter):
    def __init__(self, datefmt: Optional[str] = None):
        fmt = '[%(levelname)s] %(message)s'
        super().__init__(fmt=fmt, datefmt=datefmt)

    def format(self, record: logging.LogRecord) -> str:
        if record.levelno not in log_colors_level:
            return super().format(record)

        # detect the heading from the record
        heading = None
        message = record.getMessage()
        if not message and record.exc_info is None:
            heading = ''
        if heading is None:
            for key, value in log_colors_semantics.items():
                if message.upper().startswith(key + ':'):
                    heading = value
                    message = message[len(key + ':'):].lstrip()
                    break
        if heading is None:
            heading = log_colors_level[record.levelno]

        # exception
        if record.exc_info is not None:
            message += '\n' + self.formatException(record.exc_info)

        # make a string
        if not heading:
            return message
        return heading + message
