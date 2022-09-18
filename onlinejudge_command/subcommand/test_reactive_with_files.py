import argparse
import concurrent.futures
import contextlib
import enum
import os
import pathlib
import subprocess
import sys
import threading
from logging import getLogger
from typing import *

import onlinejudge_command.format_utils as fmtutils
from onlinejudge_command import pretty_printers, utils

logger = getLogger(__name__)


def add_subparser(subparsers: argparse.Action) -> None:
    subparsers_add_parser: Callable[..., argparse.ArgumentParser] = subparsers.add_parser  # type: ignore
    subparser = subparsers_add_parser('test-reactive-with-files', aliases=['test-reactive-with-files', 't/rf'], help='test for interactive problem with input files', formatter_class=argparse.RawTextHelpFormatter, epilog='''\
tips:
  You can do similar things with shell:
    e.g. $ for f in test/*; do [[ -e a.pipe ]] && rm -f a.pipe ; mkfifo a.pipe && ./a.out < a.pipe | python3 judge.py $f > a.pipe; done
''')
    subparser.add_argument('-c', '--command', default=utils.get_default_command(), help='your solution to be tested. (default: "{}")'.format(utils.get_default_command()))
    subparser.add_argument('-f', '--format', default='%s.%e', help='a format string to recognize the relationship of test cases. (default: "%%s.%%e")')
    subparser.add_argument('-d', '--directory', type=pathlib.Path, default=pathlib.Path('test'), help='a directory name for test cases (default: test/)')
    subparser.add_argument('-j', '--jobs', metavar='N', type=int, help='specifies the number of jobs to run simultaneously  (default: no parallelization)')
    subparser.add_argument('--no-ignore-backup', action='store_false', dest='ignore_backup')
    subparser.add_argument('--ignore-backup', action='store_true', help='ignore backup files and hidden files (i.e. files like "*~", "\\#*\\#" and ".*") (default)')
    subparser.add_argument('judge', help='judge program using standard I/O')
    subparser.add_argument('test', nargs='*', type=pathlib.Path, help='paths of test cases. (if empty: globbed from --format)')


@contextlib.contextmanager
def fifo() -> Generator[Tuple[Any, Any], None, None]:
    fdr, fdw = os.pipe()
    fhr = os.fdopen(fdr, 'r')
    fhw = os.fdopen(fdw, 'w')
    yield fhr, fhw
    fhw.close()
    fhr.close()
    # os.close(fdw), os.close(fdr) are unnecessary


class JudgeStatus(enum.Enum):
    AC = 'AC'
    WA = 'WA'
    RE = 'RE'


def run(args: argparse.Namespace) -> bool:
    # list tests
    if not args.test:
        args.test = fmtutils.glob_with_format(args.directory, args.format)  # by default
    if args.ignore_backup:
        args.test = fmtutils.drop_backup_or_hidden_files(args.test)
    tests = fmtutils.construct_relationship_of_files(args.test, args.directory, args.format)

    # run tests
    history: List[Dict[str, Any]] = []
    if args.jobs is None:
        for name, paths in sorted(tests.items()):
            history += [test_single_case(name, paths['in'], args=args)]
    else:
        if os.name == 'nt':
            logger.warning("-j/--jobs opiton is unstable on Windows environment")
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as executor:
            lock = threading.Lock()
            futures: List[concurrent.futures.Future] = []
            for name, paths in sorted(tests.items()):
                futures += [executor.submit(test_single_case, name, paths['in'], lock=lock, args=args)]
            for future in futures:
                history += [future.result()]

    # summarize
    ac_count = 0
    for result in history:
        if result['status'] == 'AC':
            ac_count += 1

    # print the summary
    logger.info('')
    if ac_count == len(tests):
        logger.info(utils.SUCCESS + 'test ' + utils.green('success') + ': %d cases', len(tests))
    else:
        logger.info(utils.FAILURE + 'test ' + utils.red('failed') + ': %d AC / %d cases', ac_count, len(tests))

    # return the result
    return ac_count == len(tests)


def test_single_case(test_name: str, test_input_path: pathlib.Path, *, lock: Optional[threading.Lock] = None, args: argparse.Namespace) -> Dict[str, Any]:
    # print the header earlier if not in parallel
    if lock is None:
        logger.info('')
        logger.info('%s', test_name)

    with fifo() as (fhr1, fhw1):
        with fifo() as (fhr2, fhw2):
            with subprocess.Popen(args.command, shell=True, stdin=fhr2, stdout=fhw1, stderr=sys.stderr) as proc1:
                judge_command = ' '.join([
                    args.judge,
                    str(test_input_path.resolve()),
                ])
                with subprocess.Popen(judge_command, shell=True, stdin=fhr1, stdout=fhw2, stderr=sys.stderr) as proc2:
                    proc1.communicate()
                    proc2.communicate()

                    # lock is require to avoid mixing logs if in parallel
                    nullcontext = contextlib.ExitStack()  # TODO: use contextlib.nullcontext() after updating Python to 3.7
                    with lock or nullcontext:
                        if lock is not None:
                            logger.info('')
                            logger.info('%s', test_name)

                    status = JudgeStatus.AC
                    if proc1.returncode != 0:
                        logger.info(utils.FAILURE + 'RE: solution returns %d', proc1.returncode)
                        status = JudgeStatus.RE
                    if proc2.returncode == 0:
                        logger.info(utils.SUCCESS + 'AC')
                    else:
                        logger.info(utils.FAILURE + 'WA: judge returns %d', proc2.returncode)
                        status = JudgeStatus.WA

                    if status != JudgeStatus.AC:
                        with test_input_path.open('rb') as inf:
                            logger.info(utils.NO_HEADER + 'input:\n%s', pretty_printers.make_pretty_large_file_content(inf.read(), limit=40, head=20, tail=10))

                    testcase = {
                        'name': test_name,
                        'input': str(test_input_path.resolve()),
                    }
                    return {
                        'status': status.value,
                        'testcase': testcase,
                    }
