import argparse
import contextlib
import os
import subprocess
import sys
from logging import getLogger
from typing import *

import onlinejudge_command.utils as utils

logger = getLogger(__name__)


@contextlib.contextmanager
def fifo() -> Generator[Tuple[Any, Any], None, None]:
    fdr, fdw = os.pipe()
    fhr = os.fdopen(fdr, 'r')
    fhw = os.fdopen(fdw, 'w')
    yield fhr, fhw
    fhw.close()
    fhr.close()
    # os.close(fdw), os.close(fdr) are unnecessary


# TODO: write smoke tests for this subcommand
def test_reactive(args: argparse.Namespace) -> None:
    with fifo() as (fhr1, fhw1):
        with fifo() as (fhr2, fhw2):
            with subprocess.Popen(args.command, shell=True, stdin=fhr2, stdout=fhw1, stderr=sys.stderr) as proc1:
                with subprocess.Popen(args.judge, shell=True, stdin=fhr1, stdout=fhw2, stderr=sys.stderr) as proc2:
                    proc1.communicate()
                    proc2.communicate()
                    if proc1.returncode != 0:
                        logger.info(utils.FAILURE + 'RE: solution returns %d', proc1.returncode)
                    if proc2.returncode == 0:
                        logger.info(utils.SUCCESS + 'AC')
                    else:
                        logger.info(utils.FAILURE + 'WA: judge returns %d', proc2.returncode)
