import argparse
import concurrent.futures
import contextlib
import os
import pathlib
import threading
from logging import getLogger
from typing import *

import onlinejudge_command.format_utils as fmtutils
import onlinejudge_command.pretty_printers as pretty_printers
import onlinejudge_command.utils as utils

logger = getLogger(__name__)


def add_subparser(subparsers: argparse.Action) -> None:
    subparsers_add_parser: Callable[..., argparse.ArgumentParser] = subparsers.add_parser  # type: ignore
    subparser = subparsers_add_parser('generate-output', aliases=['g/o'], help='generate output files from input and reference implementation', formatter_class=argparse.RawTextHelpFormatter, epilog='''\
format string for --format:
  %s                    name
  %e                    extension: "in" or "out"
  (both %s and %e are required.)

tips:
  You can do similar things with shell
    e.g. $ for f in test/*.in ; do ./a.out < $f > ${f%.in}.out ; done
''')
    subparser.add_argument('-c', '--command', default=utils.get_default_command(), help='your solution to be tested. (default: "{}")'.format(utils.get_default_command()))
    subparser.add_argument('-f', '--format', default='%s.%e', help='a format string to recognize the relationship of test cases. (default: "%%s.%%e")')
    subparser.add_argument('-d', '--directory', type=pathlib.Path, default=pathlib.Path('test'), help='a directory name for test cases (default: test/)')
    subparser.add_argument('-t', '--tle', type=float, help='set the time limit (in second) (default: inf)')
    subparser.add_argument('-j', '--jobs', type=int, help='run tests in parallel')
    subparser.add_argument('test', nargs='*', type=pathlib.Path, help='paths of input cases. (if empty: globbed from --format)')
    subparser.add_argument('--no-ignore-backup', action='store_false', dest='ignore_backup')
    subparser.add_argument('--ignore-backup', action='store_true', help='ignore backup files and hidden files (i.e. files like "*~", "\\#*\\#" and ".*") (default)')


def generate_output_single_case(test_name: str, test_input_path: pathlib.Path, *, lock: Optional[threading.Lock] = None, args: argparse.Namespace) -> None:

    # print the header
    if lock is None:
        logger.info('')
        logger.info('%s', test_name)

    # run the command
    with test_input_path.open('rb') as inf:
        info, proc = utils.exec_command(args.command, stdin=inf, timeout=args.tle)
        answer: Optional[bytes] = info['answer']
        elapsed: float = info['elapsed']

    # acquire lock to print logs properly, if in parallel
    nullcontext = contextlib.ExitStack()
    with lock or nullcontext:
        if lock is not None:
            logger.info('')
            logger.info('%s', test_name)

        # check the result
        logger.info('time: %f sec', elapsed)
        if proc.returncode is None:
            logger.info(utils.red('TLE'))
            logger.info('skipped.')
            return
        elif proc.returncode != 0:
            logger.info('FIALURE: ' + utils.red('RE') + ': return code %d', proc.returncode)
            logger.info('skipped.')
            return
        assert answer is not None
        logger.info(utils.NO_HEADER + '' + pretty_printers.make_pretty_large_file_content(answer, limit=40, head=20, tail=10, bold=True))

        # find the destination path
        match_result: Optional[Match[Any]] = fmtutils.match_with_format(args.directory, args.format, test_input_path)
        if match_result is not None:
            matched_name: str = match_result.groupdict()['name']
        else:
            assert False
        test_output_path = fmtutils.path_from_format(args.directory, args.format, name=matched_name, ext='out')

        # write the result to the file
        if not test_output_path.parent.is_dir():
            os.makedirs(str(test_output_path.parent), exist_ok=True)
        with test_output_path.open('wb') as fh:
            fh.write(answer)
        logger.info(utils.SUCCESS + 'saved to: %s', test_output_path)


def generate_output_single_case_exists_ok(test_name: str, test_input_path: pathlib.Path, test_output_path: Optional[pathlib.Path], *, lock: Optional[threading.Lock] = None, args: argparse.Namespace) -> None:
    if test_output_path is not None:
        nullcontext = contextlib.ExitStack()
        with lock or nullcontext:
            logger.info('')
            logger.info('%s', test_name)
            logger.info('output file already exists.')
            logger.info('skipped.')
    else:
        generate_output_single_case(test_name, test_input_path, lock=lock, args=args)


def run(args: argparse.Namespace) -> None:
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
            futures: List[concurrent.futures.Future] = []
            for name, paths in sorted(tests.items()):
                futures += [executor.submit(generate_output_single_case_exists_ok, name, paths['in'], paths.get('out'), lock=lock, args=args)]
            for future in futures:
                future.result()
