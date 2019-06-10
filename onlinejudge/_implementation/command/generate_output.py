# Python Version: 3.x
import os
import pathlib
import time
from typing import *

import onlinejudge
import onlinejudge._implementation.format_utils as fmtutils
import onlinejudge._implementation.logging as log
import onlinejudge._implementation.utils as utils

if TYPE_CHECKING:
    import argparse


def generate_output_single_case(test_name: str, test_input_path: pathlib.Path, *, args: 'argparse.Namespace') -> None:
    # print the header
    log.emit('')
    log.info('%s', test_name)

    # run the command
    with test_input_path.open() as inf:
        begin = time.perf_counter()
        answer, proc = utils.exec_command(args.command, stdin=inf, timeout=args.tle)
        end = time.perf_counter()

    # check the result
    log.status('time: %f sec', end - begin)
    if proc.returncode is None:
        log.failure(log.red('TLE'))
        log.info('skipped.')
        return
    elif proc.returncode != 0:
        log.failure(log.red('RE') + ': return code %d', proc.returncode)
        log.info('skipped.')
        return
    log.emit(utils.snip_large_file_content(answer, limit=40, head=20, tail=10, bold=True))

    # find the destination path
    match_result = fmtutils.match_with_format(args.directory, args.format, test_input_path)  # type: Optional[Match[Any]]
    if match_result is not None:
        matched_name = match_result.groupdict()['name']  # type: str
    else:
        assert False
    test_output_path = fmtutils.path_from_format(args.directory, args.format, name=matched_name, ext='out')

    # write the result to the file
    if not test_output_path.parent.is_dir():
        os.makedirs(str(test_output_path.parent), exist_ok=True)
    with test_output_path.open('wb') as fh:
        fh.write(answer)
    log.success('saved to: %s', test_output_path)


def generate_output(args: 'argparse.Namespace') -> None:
    # list tests
    if not args.test:
        args.test = fmtutils.glob_with_format(args.directory, args.format)  # by default
    if args.ignore_backup:
        args.test = fmtutils.drop_backup_or_hidden_files(args.test)
    tests = fmtutils.construct_relationship_of_files(args.test, args.directory, args.format)

    # generate cases
    for name, paths in sorted(tests.items()):
        if 'out' in paths:
            log.emit('')
            log.info('%s', name)
            log.info('output file already exists.')
            log.info('skipped.')
        else:
            generate_output_single_case(name, paths['in'], args=args)
