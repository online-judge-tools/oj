# Python Version: 3.x
import json
import math
import sys
import time
from typing import *

import onlinejudge
import onlinejudge._implementation.format_utils as cutils
import onlinejudge._implementation.logging as log
import onlinejudge._implementation.utils as utils

if TYPE_CHECKING:
    import argparse


def compare_as_floats(xs_: str, ys_: str, error: float) -> bool:
    def f(x):
        try:
            y = float(x)
            if not math.isfinite(y):
                log.warning('not an real number found: %f', y)
            return y
        except ValueError:
            return x

    xs = list(map(f, xs_.split()))
    ys = list(map(f, ys_.split()))
    if len(xs) != len(ys):
        return False
    for x, y in zip(xs, ys):
        if isinstance(x, float) and isinstance(y, float):
            if not math.isclose(x, y, rel_tol=error, abs_tol=error):
                return False
        else:
            if x != y:
                return False
    return True


def test(args: 'argparse.Namespace') -> None:
    # prepare
    if not args.test:
        args.test = cutils.glob_with_format(args.directory, args.format)  # by default
    if args.ignore_backup:
        args.test = cutils.drop_backup_or_hidden_files(args.test)
    tests = cutils.construct_relationship_of_files(args.test, args.directory, args.format)
    if args.error:  # float mode
        match = lambda a, b: compare_as_floats(a, b, args.error)
    else:

        def match(a, b):
            if a == b:
                return True
            if args.rstrip and a.rstrip(rstrip_targets) == b.rstrip(rstrip_targets):
                log.warning('WA if no rstrip')
                return True
            return False

    rstrip_targets = ' \t\r\n\f\v\0'  # ruby's one, follow AnarchyGolf
    slowest = -1  # type: Union[int, float]
    slowest_name = ''
    ac_count = 0

    history = []  # type: List[Dict[str, Any]]
    for name, it in sorted(tests.items()):
        is_printed_input = not args.print_input

        def print_input():
            nonlocal is_printed_input
            if not is_printed_input:
                is_printed_input = True
                with open(it['in'], 'rb') as inf:
                    log.emit('input:\n%s', utils.snip_large_file_content(inf.read(), limit=40, head=20, tail=10, bold=True))

        log.emit('')
        log.info('%s', name)

        # run the binary
        with it['in'].open() as inf:
            begin = time.perf_counter()
            answer_byte, proc = utils.exec_command(args.command, shell=True, stdin=inf, timeout=args.tle)
            end = time.perf_counter()
            elapsed = end - begin
            answer = answer_byte.decode()  # TODO: the `answer` should be bytes, not str
            if slowest < elapsed:
                slowest = elapsed
                slowest_name = name
            log.status('time: %f sec', elapsed)
            proc.terminate()

        # check TLE, RE or not
        result = 'AC'
        if proc.returncode is None:
            log.failure(log.red('TLE'))
            result = 'TLE'
            print_input()
        elif proc.returncode != 0:
            log.failure(log.red('RE') + ': return code %d', proc.returncode)
            result = 'RE'
            print_input()

        # check WA or not
        if 'out' in it:
            with it['out'].open() as outf:
                correct = outf.read()
            # compare
            if args.mode == 'all':
                if not match(answer, correct):
                    log.failure(log.red('WA'))
                    print_input()
                    if not args.silent:
                        log.emit('output:\n%s', utils.snip_large_file_content(answer.encode(), limit=40, head=20, tail=10, bold=True))
                        log.emit('expected:\n%s', utils.snip_large_file_content(correct.encode(), limit=40, head=20, tail=10, bold=True))
                    result = 'WA'
            elif args.mode == 'line':
                answer_words = answer.splitlines()
                correct_words = correct.splitlines()
                for i, (x, y) in enumerate(zip(answer_words + [None] * len(correct_words), correct_words + [None] * len(answer_words))):  # type: ignore
                    if x is None and y is None:
                        break
                    elif x is None:
                        print_input()
                        log.failure(log.red('WA') + ': line %d: line is nothing: expected "%s"', i + 1, log.bold(y))
                        result = 'WA'
                    elif y is None:
                        print_input()
                        log.failure(log.red('WA') + ': line %d: unexpected line: output "%s"', i + 1, log.bold(x))
                        result = 'WA'
                    elif not match(x, y):
                        print_input()
                        log.failure(log.red('WA') + ': line %d: output "%s": expected "%s"', i + 1, log.bold(x), log.bold(y))
                        result = 'WA'
            else:
                assert False
        else:
            if not args.silent:
                log.emit(utils.snip_large_file_content(answer.encode(), limit=40, head=20, tail=10, bold=True))
        if result == 'AC':
            log.success(log.green('AC'))
            ac_count += 1

        # push the result
        testcase = {
            'name': name,
            'input': str(it['in'].resolve()),
        }
        if 'out' in it:
            testcase['output'] = str(it['out'].resolve())
        history += [{
            'result': result,
            'testcase': testcase,
            'output': answer,
            'exitcode': proc.returncode,
            'elapsed': elapsed,
        }]

    # summarize
    log.emit('')
    log.status('slowest: %f sec  (for %s)', slowest, slowest_name)
    if ac_count == len(tests):
        log.success('test ' + log.green('success') + ': %d cases', len(tests))
    else:
        log.failure('test ' + log.red('failed') + ': %d AC / %d cases', ac_count, len(tests))

    if args.json:
        print(json.dumps(history))

    if ac_count != len(tests):
        sys.exit(1)
