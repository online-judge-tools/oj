import http.client
import logging

import colorama

log_colors_level = {
    logging.DEBUG: '[' + colorama.Fore.RED + 'DEBUG' + colorama.Style.RESET_ALL + '] ',
    logging.INFO: '[' + colorama.Fore.BLUE + 'INFO' + colorama.Style.RESET_ALL + '] ',
    logging.WARNING: '[' + colorama.Fore.YELLOW + 'WARNING' + colorama.Style.RESET_ALL + '] ',
    logging.ERROR: '[' + colorama.Fore.RED + 'ERROR' + colorama.Style.RESET_ALL + '] ',
    logging.CRITICAL: '[' + colorama.Fore.RED + colorama.Style.BRIGHT + 'CRITICAL' + colorama.Style.RESET_ALL + '] ',
}

log_colors_semantics = {
    'NO_HEADER': '',
    'NETWORK': '[' + colorama.Fore.MAGENTA + 'NETWORK' + colorama.Style.RESET_ALL + '] ',
    'SUCCESS': '[' + colorama.Fore.GREEN + 'SUCCESS' + colorama.Style.RESET_ALL + '] ',
    'FAILURE': '[' + colorama.Fore.RED + 'FAILURE' + colorama.Style.RESET_ALL + '] ',
}

status_code_messages = set([str(int(key)) + ' ' + str(value) for key, value in http.client.responses.items()])


class LogFormatter(logging.Formatter):
    def __init__(self, datefmt=None):
        fmt = '[%(levelname)s] %(message)s'
        super().__init__(fmt=fmt, datefmt=datefmt)

    def format(self, record: logging.LogRecord) -> str:
        if record.levelno not in log_colors_level:
            return super().format(record)

        # detect the heading from the record
        heading = None
        message = record.getMessage()
        if not message:
            heading = ''
        if heading is None:
            for key in ('GET', 'POST', 'redirected'):
                if message.startswith(key + ': '):
                    heading = log_colors_semantics['NETWORK']
            if message in status_code_messages:
                heading = log_colors_semantics['NETWORK']
        if heading is None:
            for key, value in log_colors_semantics.items():
                if message.startswith(key + ': '):
                    heading = value
                    message = message[len(key + ': '):]
                    break
        if heading is None:
            heading = log_colors_level[record.levelno]

        # make a string
        if not heading:
            return message
        return heading + message