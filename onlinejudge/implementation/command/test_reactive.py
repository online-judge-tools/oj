# Python Version: 3.x
import onlinejudge
import onlinejudge.implementation.utils as utils
import onlinejudge.implementation.logging as log
import sys
import os
import os.path
import subprocess
import contextlib

@contextlib.contextmanager
def fifo():
    fdr, fdw = os.pipe()
    fhr = os.fdopen(fdr, 'r')
    fhw = os.fdopen(fdw, 'w')
    yield fhr, fhw
    fhw.close()
    fhr.close()
    # os.close(fdw), os.close(fdr) are unnecessary

def test_reactive(args):
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
