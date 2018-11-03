# Python Version: 3.x
import onlinejudge
import onlinejudge.implementation.utils as utils
import onlinejudge.implementation.logging as log
import onlinejudge.implementation.command.utils as cutils
import time
from typing import *
if TYPE_CHECKING:
    import argparse

def generate_output(args: 'argparse.Namespace') -> None:
    if not args.test:
        args.test = cutils.glob_with_format(args.directory, args.format) # by default
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
        with open(it['in']) as inf:
            begin = time.perf_counter()
            answer, proc = utils.exec_command(args.command, shell=True, stdin=inf)
            end = time.perf_counter()
            log.status('time: %f sec', end - begin)
        if proc.returncode != 0:
            log.failure(log.red('RE') + ': return code %d', proc.returncode)
            log.info('skipped.')
            continue
        log.emit(log.bold(answer.decode().rstrip()))
        name = cutils.match_with_format(args.directory, args.format, it['in']).groupdict()['name']  # type: ignore
        path = cutils.path_from_format(args.directory, args.format, name=name, ext='out')
        with open(path, 'w') as fh:
            fh.buffer.write(answer)
        log.success('saved to: %s', path)
