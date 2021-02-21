import argparse
import contextlib
import os
import subprocess
import sys
from logging import getLogger
from typing import *

import onlinejudge_command.utils as utils

logger = getLogger(__name__)


def add_subparser(subparsers: argparse.Action) -> None:
    subparsers_add_parser: Callable[..., argparse.ArgumentParser] = subparsers.add_parser  # type: ignore
    subparser = subparsers_add_parser('test-reactive', aliases=['t/r'], help='test for reactive problem', formatter_class=argparse.RawTextHelpFormatter, epilog='''\
tips:
  You can do similar things with shell
    e.g. $ mkfifo a.pipe && ./a.out < a.pipe | python3 judge.py > a.pipe
''')
    subparser.add_argument('-c', '--command', default=utils.get_default_command(), help='your solution to be tested. (default: "{}")'.format(utils.get_default_command()))
    subparser.add_argument('judge', help='judge program using standard I/O')


@contextlib.contextmanager
def fifo() -> Generator[Tuple[Any, Any], None, None]:
    fdr, fdw = os.pipe()
    fhr = os.fdopen(fdr, 'r')
    fhw = os.fdopen(fdw, 'w')
    yield fhr, fhw
    fhw.close()
    fhr.close()
    # os.close(fdw), os.close(fdr) are unnecessary


def run(args: argparse.Namespace) -> bool:
    with fifo() as (fhr1, fhw1):
        with fifo() as (fhr2, fhw2):
            with subprocess.Popen(args.command, shell=True, stdin=fhr2, stdout=fhw1, stderr=sys.stderr) as proc1:
                with subprocess.Popen(args.judge, shell=True, stdin=fhr1, stdout=fhw2, stderr=sys.stderr) as proc2:
                    proc1.communicate()
                    proc2.communicate()

                    result = True
                    if proc1.returncode != 0:
                        logger.info(utils.FAILURE + 'RE: solution returns %d', proc1.returncode)
                        result = False
                    if proc2.returncode == 0:
                        logger.info(utils.SUCCESS + 'AC')
                    else:
                        logger.info(utils.FAILURE + 'WA: judge returns %d', proc2.returncode)
                        result = False
                    return result
