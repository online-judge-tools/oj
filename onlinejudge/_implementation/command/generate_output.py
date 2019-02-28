# Python Version: 3.x
import os
import time
from typing import *

import onlinejudge
import onlinejudge._implementation.format_utils as cutils
import onlinejudge._implementation.logging as log
import onlinejudge._implementation.utils as utils

if TYPE_CHECKING:
    import argparse


def generate_output(args: 'argparse.Namespace') -> None:
    if not args.test:
        args.test = cutils.glob_with_format(args.directory, args.format)  # by default
    if args.ignore_backup:
        args.test = cutils.drop_backup_or_hidden_files(args.test)
    tests = cutils.construct_relationship_of_files(args.test, args.directory, args.format)
    for name, it in sorted(tests.items()):
        log.emit('')
        log.info('%s', name)
        if 'out' in it:
            log.info('output file already exists.')
            log.info('skipped.')
            continue
        with it['in'].open() as inf:
            begin = time.perf_counter()
            answer, proc = utils.exec_command(args.command, shell=True, stdin=inf)
            end = time.perf_counter()
            log.status('time: %f sec', end - begin)
        if proc.returncode != 0:
            log.failure(log.red('RE') + ': return code %d', proc.returncode)
            log.info('skipped.')
            continue
        log.emit(utils.snip_large_file_content(answer, limit=40, head=20, tail=10, bold=True))
        match_result = cutils.match_with_format(args.directory, args.format, it['in'])  # type: Optional[Match[Any]]
        if match_result is not None:
            matched_name = match_result.groupdict()['name']  # type: str
        else:
            assert False
        path = cutils.path_from_format(args.directory, args.format, name=matched_name, ext='out')
        if not path.parent.is_dir():
            os.makedirs(str(path.parent), exist_ok=True)
        with path.open('wb') as fh:
            fh.write(answer)
        log.success('saved to: %s', path)
