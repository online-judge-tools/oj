# Python Version: 3.x
import concurrent.futures
import contextlib
import os
import pathlib
import threading
import time
from typing import *

import onlinejudge
import onlinejudge._implementation.format_utils as fmtutils
import onlinejudge._implementation.logging as log
import onlinejudge._implementation.utils as utils

if TYPE_CHECKING:
    import argparse


def generate_output_single_case(test_name: str, test_input_path: pathlib.Path, *, lock: Optional[threading.Lock] = None, args: 'argparse.Namespace') -> None:

    # print the header
    if lock is None:
        log.emit('')
        log.info('%s', test_name)

    # run the command
    with test_input_path.open() as inf:
        info, proc = utils.exec_command(args.command, stdin=inf, timeout=args.tle)
        answer = info['answer']  # type: Optional[bytes]
        elapsed = info['elapsed']  # type: float

    # acquire lock to print logs properly, if in parallel
    nullcontext = contextlib.ExitStack()
    with lock or nullcontext:
        if lock is not None:
            log.emit('')
            log.info('%s', test_name)

        # check the result
        log.status('time: %f sec', elapsed)
        if proc.returncode is None:
            log.failure(log.red('TLE'))
            log.info('skipped.')
            return
        elif proc.returncode != 0:
            log.failure(log.red('RE') + ': return code %d', proc.returncode)
            log.info('skipped.')
            return
        assert answer is not None
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


def generate_output_single_case_exists_ok(test_name: str, test_input_path: pathlib.Path, test_output_path: Optional[pathlib.Path], *, lock: Optional[threading.Lock] = None, args: 'argparse.Namespace') -> None:
    if test_output_path is not None:
        nullcontext = contextlib.ExitStack()
        with lock or nullcontext:
            log.emit('')
            log.info('%s', test_name)
            log.info('output file already exists.')
            log.info('skipped.')
    else:
        generate_output_single_case(test_name, test_input_path, lock=lock, args=args)


def generate_output(args: 'argparse.Namespace') -> None:
    # list tests
    if not args.test:
        args.test = fmtutils.glob_with_format(args.directory, args.format)  # by default
    if args.ignore_backup:
        args.test = fmtutils.drop_backup_or_hidden_files(args.test)
    tests = fmtutils.construct_relationship_of_files(args.test, args.directory, args.format)

    # generate cases
    if args.jobs is None:
        for name, paths in sorted(tests.items()):
            generate_output_single_case_exists_ok(name, paths['in'], paths.get('out'), args=args)
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as executor:
            lock = threading.Lock()
            futures = []  # type: List[concurrent.futures.Future]
            for name, paths in sorted(tests.items()):
                futures += [executor.submit(generate_output_single_case_exists_ok, name, paths['in'], paths.get('out'), lock=lock, args=args)]
            for future in futures:
                future.result()
