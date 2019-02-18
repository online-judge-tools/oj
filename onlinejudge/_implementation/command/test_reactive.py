# Python Version: 3.x
import contextlib
import os
import subprocess
import sys
from typing import *

import onlinejudge
import onlinejudge._implementation.logging as log
import onlinejudge._implementation.utils as utils

if TYPE_CHECKING:
    import argparse


@contextlib.contextmanager
def fifo() -> Generator[Tuple[Any, Any], None, None]:
    fdr, fdw = os.pipe()
    fhr = os.fdopen(fdr, 'r')
    fhw = os.fdopen(fdw, 'w')
    yield fhr, fhw
    fhw.close()
    fhr.close()
    # os.close(fdw), os.close(fdr) are unnecessary


def test_reactive(args: 'argparse.Namespace') -> None:
    with fifo() as (fhr1, fhw1):
        with fifo() as (fhr2, fhw2):
            with subprocess.Popen(args.command, shell=True, stdin=fhr2, stdout=fhw1, stderr=sys.stderr) as proc1:
                with subprocess.Popen(args.judge, shell=True, stdin=fhr1, stdout=fhw2, stderr=sys.stderr) as proc2:
                    proc1.communicate()
                    proc2.communicate()
                    if proc1.returncode != 0:
                        log.failure('RE: solution returns %d', proc1.returncode)
                    if proc2.returncode == 0:
                        log.success('AC')
                    else:
                        log.failure('WA: judge returns %d', proc2.returncode)
