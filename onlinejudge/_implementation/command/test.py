# Python Version: 3.x
import concurrent.futures
import contextlib
import json
import math
import pathlib
import subprocess
import sys
import tempfile
import threading
import time
import traceback
from typing import *

import onlinejudge
import onlinejudge._implementation.format_utils as fmtutils
import onlinejudge._implementation.logging as log
import onlinejudge._implementation.utils as utils

if TYPE_CHECKING:
    import argparse

MEMORY_WARNING = 500  # megabyte
MEMORY_PRINT = 100  # megabyte


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


def compare_and_report(proc: subprocess.Popen, answer: str, test_input_path: pathlib.Path, test_output_path: Optional[pathlib.Path], *, mode: str, error: Optional[float], does_print_input: bool, silent: bool, rstrip: bool) -> str:
    # prepare the comparing function
    if error:  # float mode
        match = lambda a, b: compare_as_floats(a, b, error)
    else:
        rstrip_targets = ' \t\r\n\f\v\0'  # ruby's one, follow AnarchyGolf

        def match(a, b):
            if a == b:
                return True
            if rstrip and a.rstrip(rstrip_targets) == b.rstrip(rstrip_targets):
                log.warning('WA if no rstrip')
                return True
            return False

    # prepare the function to print the input
    is_input_printed = False

    def print_input():
        nonlocal is_input_printed
        if does_print_input and not is_input_printed:
            is_input_printed = True
            with test_input_path.open('rb') as inf:
                log.emit('input:\n%s', utils.snip_large_file_content(inf.read(), limit=40, head=20, tail=10, bold=True))

    # check TLE, RE or not
    status = 'AC'
    if proc.returncode is None:
        log.failure(log.red('TLE'))
        status = 'TLE'
        print_input()
    elif proc.returncode != 0:
        log.failure(log.red('RE') + ': return code %d', proc.returncode)
        status = 'RE'
        print_input()

    # check WA or not
    if test_output_path is not None:
        with test_output_path.open() as outf:
            expected = outf.read()
        # compare
        if mode == 'all':
            if not match(answer, expected):
                log.failure(log.red('WA'))
                print_input()
                if not silent:
                    log.emit('output:\n%s', utils.snip_large_file_content(answer.encode(), limit=40, head=20, tail=10, bold=True))
                    log.emit('expected:\n%s', utils.snip_large_file_content(expected.encode(), limit=40, head=20, tail=10, bold=True))
                status = 'WA'
        elif mode == 'line':
            answer_words = answer.splitlines()
            correct_words = expected.splitlines()
            for i, (x, y) in enumerate(zip(answer_words + [None] * len(correct_words), correct_words + [None] * len(answer_words))):  # type: ignore
                if x is None and y is None:
                    break
                elif x is None:
                    print_input()
                    log.failure(log.red('WA') + ': line %d: line is nothing: expected "%s"', i + 1, log.bold(y))
                    status = 'WA'
                elif y is None:
                    print_input()
                    log.failure(log.red('WA') + ': line %d: unexpected line: output "%s"', i + 1, log.bold(x))
                    status = 'WA'
                elif not match(x, y):
                    print_input()
                    log.failure(log.red('WA') + ': line %d: output "%s": expected "%s"', i + 1, log.bold(x), log.bold(y))
                    status = 'WA'
        else:
            assert False
    else:
        if not silent:
            log.emit(('output:\n%s' if is_input_printed else '%s'), utils.snip_large_file_content(answer.encode(), limit=40, head=20, tail=10, bold=True))
    if status == 'AC':
        log.success(log.green('AC'))

    return status


def test_single_case(test_name: str, test_input_path: pathlib.Path, test_output_path: Optional[pathlib.Path], *, lock: Optional[threading.Lock] = None, args: 'argparse.Namespace') -> Dict[str, Any]:
    # print the header earlier if not in parallel
    if lock is None:
        log.emit('')
        log.info('%s', test_name)

    # run the binary
    with test_input_path.open() as inf:
        info, proc = utils.exec_command(args.command, stdin=inf, timeout=args.tle, gnu_time=args.gnu_time)
        # TODO: the `answer` should be bytes, not str
        answer = (info['answer'] or b'').decode()  # type: str
        elapsed = info['elapsed']  # type: float
        memory = info['memory']  # type: Optional[float]

    # lock is require to avoid mixing logs if in parallel
    nullcontext = contextlib.ExitStack()  # TODO: use contextlib.nullcontext() after updating Python to 3.7
    with lock or nullcontext:
        if lock is not None:
            log.emit('')
            log.info('%s', test_name)
        log.status('time: %f sec', elapsed)
        if memory:
            if memory < MEMORY_PRINT:
                if args.print_memory:
                    log.status('memory: %f MB', memory)
            elif memory < MEMORY_WARNING:
                log.status('memory: %f MB', memory)
            else:
                log.warning('memory: %f MB', memory)

        status = compare_and_report(proc, answer, test_input_path, test_output_path, mode=args.mode, error=args.error, does_print_input=args.print_input, silent=args.silent, rstrip=args.rstrip)

    # return the result
    testcase = {
        'name': test_name,
        'input': str(test_input_path.resolve()),
    }
    if test_output_path:
        testcase['output'] = str(test_output_path.resolve())
    return {
        'status': status,
        'testcase': testcase,
        'output': answer,
        'exitcode': proc.returncode,
        'elapsed': elapsed,
        'memory': memory,
    }


def check_gnu_time(gnu_time: str) -> bool:
    try:
        with tempfile.NamedTemporaryFile(delete=True) as fh:
            proc = subprocess.run([gnu_time, '-f', '%M KB', '-o', fh.name, '--', 'true'])
            assert proc.returncode == 0
            with open(fh.name) as fh1:
                data = fh1.read()
            int(utils.remove_suffix(data.rstrip().splitlines()[-1], ' KB'))
            return True
    except NameError:
        raise  # NameError is not a runtime error caused by the environmet, but a coding mistake
    except AttributeError:
        raise  # AttributeError is also a mistake
    except Exception as e:
        log.debug(traceback.format_exc())
    return False


def test(args: 'argparse.Namespace') -> None:
    # list tests
    if not args.test:
        args.test = fmtutils.glob_with_format(args.directory, args.format)  # by default
    if args.ignore_backup:
        args.test = fmtutils.drop_backup_or_hidden_files(args.test)
    tests = fmtutils.construct_relationship_of_files(args.test, args.directory, args.format)

    # check wheather GNU time is available
    if not check_gnu_time(args.gnu_time):
        log.warning('GNU time is not available: %s', args.gnu_time)
        args.gnu_time = None

    # run tests
    history = []  # type: List[Dict[str, Any]]
    if args.jobs is None:
        for name, paths in sorted(tests.items()):
            history += [test_single_case(name, paths['in'], paths.get('out'), args=args)]
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as executor:
            lock = threading.Lock()
            futures = []  # type: List[concurrent.futures.Future]
            for name, paths in sorted(tests.items()):
                futures += [executor.submit(test_single_case, name, paths['in'], paths.get('out'), lock=lock, args=args)]
            for future in futures:
                history += [future.result()]

    # summarize
    slowest = -1.0  # type: float
    slowest_name = ''
    heaviest = -1.0  # type: float
    heaviest_name = ''
    ac_count = 0
    for result in history:
        if result['status'] == 'AC':
            ac_count += 1
        if slowest < result['elapsed']:
            slowest = result['elapsed']
            slowest_name = result['testcase']['name']
        if result['memory'] is not None and heaviest < result['memory']:
            heaviest = result['memory']
            heaviest_name = result['testcase']['name']

    # print the summary
    log.emit('')
    log.status('slowest: %f sec  (for %s)', slowest, slowest_name)
    if heaviest >= 0:
        if heaviest < MEMORY_WARNING:
            log.status('max memory: %f MB  (for %s)', heaviest, heaviest_name)
        else:
            log.warning('max memory: %f MB  (for %s)', heaviest, heaviest_name)
    if ac_count == len(tests):
        log.success('test ' + log.green('success') + ': %d cases', len(tests))
    else:
        log.failure('test ' + log.red('failed') + ': %d AC / %d cases', ac_count, len(tests))

    if args.json:
        print(json.dumps(history))

    if ac_count != len(tests):
        sys.exit(1)
