# Python Version: 3.x
import collections
import concurrent.futures
import contextlib
import itertools
import json
import math
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import traceback
from typing import *

import diff_match_patch

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


def compare_and_report(proc: subprocess.Popen, answer: str, memory: Optional[float], test_input_path: pathlib.Path, test_output_path: Optional[pathlib.Path], *, mle: Optional[float], mode: str, error: Optional[float], does_print_input: bool, silent: bool, rstrip: bool, judge: Optional[str]) -> str:
    rstrip_targets = ' \t\r\n\f\v\0'  # ruby's one, follow AnarchyGolf

    # prepare the comparing function
    if error is not None:  # float mode
        match = lambda a, b: compare_as_floats(a, b, error)
    elif judge is not None:  # special judge mode

        def match(a, b):
            # On Windows, a temp file is not created if we use "with" statement,
            user_output = tempfile.NamedTemporaryFile(delete=False)
            judge_result = False
            try:
                if rstrip:
                    user_output.write(a.rstrip(rstrip_targets).encode())
                else:
                    user_output.write(a.encode())
                user_output.close()

                arg0 = judge
                arg1 = str(test_input_path.resolve())
                arg2 = user_output.name
                arg3 = str((str(test_output_path.resolve()) if test_output_path is not None else ''))

                actual_command = '{} {} {} {}'.format(arg0, arg1, arg2, arg3)  # TODO: quote arguments for paths including spaces; see https://github.com/kmyk/online-judge-tools/pull/584
                log.status('$ %s', actual_command)
                info, proc = utils.exec_command(actual_command)
                if not silent:
                    log.emit('judge\'s output:\n%s', utils.make_pretty_large_file_content(info['answer'] or b'', limit=40, head=20, tail=10, bold=True))
                judge_result = (proc.returncode == 0)
            finally:
                os.unlink(user_output.name)
            return judge_result
    else:

        def match(a, b):
            if a == b:
                return True
            if rstrip and a.rstrip(rstrip_targets) == b.rstrip(rstrip_targets):
                log.warning('WA if no rstrip')
                return True
            if a == b.replace('\n', '\r\n'):
                log.warning(r'WA if not replacing "\r\n" with "\n"')
                return True
            if rstrip and a.rstrip(rstrip_targets) == b.replace('\n', '\r\n').rstrip(rstrip_targets):
                log.warning('WA if no rstrip')
                log.warning(r'WA if not replacing "\r\n" with "\n"')
                return True
            if a.replace('\n', '\r\n') == b:
                log.warning(r'WA if not replacing "\n" with "\r\n"')
                return True
            if rstrip and a.replace('\n', '\r\n').rstrip(rstrip_targets) == b.rstrip(rstrip_targets):
                # TODO: use a smart way if you need more equality patterns
                log.warning('WA if no rstrip')
                log.warning(r'WA if not replacing "\n" with "\r\n"')
                return True
            return False

    # prepare the function to print the input
    is_input_printed = False

    def print_input():
        nonlocal is_input_printed
        if does_print_input and not is_input_printed:
            is_input_printed = True
            with test_input_path.open('rb') as inf:
                log.emit('input:\n%s', utils.make_pretty_large_file_content(inf.read(), limit=40, head=20, tail=10, bold=True))

    # check TLE, RE or not
    status = 'AC'
    if proc.returncode is None:
        log.failure(log.red('TLE'))
        status = 'TLE'
        print_input()
    elif memory is not None and mle is not None and memory > mle:
        log.failure(log.red('MLE'))
        status = 'MLE'
        print_input()
    elif proc.returncode != 0:
        log.failure(log.red('RE') + ': return code %d', proc.returncode)
        status = 'RE'
        print_input()

    # check WA or not
    if (test_output_path is not None) or (judge is not None):
        if test_output_path is not None:
            with test_output_path.open('rb') as outf:
                expected = outf.read().decode()
        else:  # only if --judge-command option
            expected = ''
            log.warning('expected output is not found')
        # compare
        if not match(answer, expected):
            log.failure(log.red('WA'))
            print_input()
            if not silent:
                if mode == 'simple':
                    log.emit('output:\n%s', utils.make_pretty_large_file_content(answer.encode(), limit=40, head=20, tail=10, bold=True))
                    log.emit('expected:\n%s', utils.make_pretty_large_file_content(expected.encode(), limit=40, head=20, tail=10, bold=True))
                elif mode == 'side-by-side':
                    if max(answer.count('\n'), expected.count('\n')) <= 40:
                        display_side_by_side_color(answer, expected)
                    else:
                        display_snipped_side_by_side_color(answer, expected)
                else:
                    assert False
            status = 'WA'
    else:
        if not silent:
            log.emit(('output:\n%s' if is_input_printed else '%s'), utils.make_pretty_large_file_content(answer.encode(), limit=40, head=20, tail=10, bold=True))
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
        answer = (info['answer'] or b'').decode(errors='replace')  # type: str
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

        status = compare_and_report(proc, answer, memory, test_input_path, test_output_path, mle=args.mle, mode=args.display_mode, error=args.error, does_print_input=args.print_input, silent=args.silent, rstrip=args.rstrip, judge=args.judge)

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
        raise  # NameError is not a runtime error caused by the environment, but a coding mistake
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
    if args.mle is not None and args.gnu_time is None:
        raise RuntimeError('--mle is used but GNU time does not exist')

    # run tests
    history = []  # type: List[Dict[str, Any]]
    if args.jobs is None:
        for name, paths in sorted(tests.items()):
            history += [test_single_case(name, paths['in'], paths.get('out'), args=args)]
    else:
        if os.name == 'nt':
            log.warning("-j/--jobs opiton is unstable on Windows environmet")
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


def space_padding(s: str, max_length: int) -> str:
    return s + " " * max_length


def display_side_by_side_color(answer: str, expected: str):
    max_chars = shutil.get_terminal_size()[0] // 2 - 2

    log.emit("output:" + " " * (max_chars - 7) + "|" + "expected:")
    log.emit("-" * max_chars + "|" + "-" * max_chars)
    for _, diff_found, ans_line, exp_line, ans_chars, exp_chars in side_by_side_diff(answer, expected):
        if diff_found:
            log.emit(log.red(space_padding(ans_line, max_chars - ans_chars)) + "|" + log.green(exp_line))
        else:
            log.emit(space_padding(ans_line, max_chars - ans_chars) + "|" + exp_line)


def display_snipped_side_by_side_color(answer: str, expected: str):
    """
    Display first differ line and its previous 3 lines and its next 3 lines.
    """
    max_chars = shutil.get_terminal_size()[0] // 2 - 2
    deq = collections.deque(maxlen=7)  # type: Deque[Tuple[Optional[int], bool, str, str, int, int]]

    count_from_first_difference = 0
    i = 0
    for flag, diff_found, ans_line, exp_line, ans_chars, exp_chars in side_by_side_diff(answer, expected):
        if flag: i += 1
        if count_from_first_difference > 0:
            count_from_first_difference += 1
        line_num = i if flag else None
        deq.append((line_num, diff_found, ans_line, exp_line, ans_chars, exp_chars))
        if diff_found:
            if count_from_first_difference == 0:
                count_from_first_difference = 1
        if count_from_first_difference == 4:
            break

    max_line_num_digits = max([len(str(entry[0])) for entry in deq if entry[0] is not None])

    log.emit(" " * max_line_num_digits + "|output:" + " " * (max_chars - 7 - max_line_num_digits - 1) + "|" + "expected:")
    log.emit("-" * max_chars + "|" + "-" * max_chars)

    last_line_number = 0
    for (line_number, diff_found, ans_line, exp_line, ans_chars, exp_chars) in deq:
        num_spaces_after_output = max_chars - ans_chars - max_line_num_digits - 1
        line_number_str = str(line_number) if line_number is not None else ""
        line_num_display = space_padding(line_number_str, max_line_num_digits - len(line_number_str)) + "|"
        if not diff_found:
            log.emit(line_num_display + space_padding(ans_line, num_spaces_after_output) + "|" + exp_line)
        else:
            log.emit(line_num_display + log.red(space_padding(ans_line, num_spaces_after_output)) + "|" + log.green(exp_line))
        if line_number is not None:
            last_line_number = line_number
    num_snipped_lines = answer.count('\n') + 1 - last_line_number
    if num_snipped_lines > 0:
        log.emit('... ({} lines) ...'.format(num_snipped_lines))


def yield_open_entry(open_entry: Tuple[List[str], List[str], List[int], List[int]]) -> Generator[Tuple[bool, bool, str, str, int, int], None, None]:
    """ Yield all open changes. """
    ls, rs, lnums, rnums = open_entry
    # Get unchanged parts onto the right line
    if ls[0] == rs[0]:
        yield (True, False, ls[0], rs[0], lnums[0], rnums[0])
        for l, r, lnum, rnum in itertools.zip_longest(ls[1:], rs[1:], lnums[1:], rnums[1:]):
            yield (l is not None, True, l or '', r or '', lnum or 0, rnum or 0)
    elif ls[-1] == rs[-1]:
        for l, r, lnum, rnum in itertools.zip_longest(ls[:-1], rs[:-1], lnums[:-1], rnums[:-1]):
            yield (l is not None, l != r, l or '', r or '', lnum or 0, rnum or 0)
        yield (True, False, ls[-1], rs[-1], lnums[-1], rnums[-1])
    else:
        for l, r, lnum, rnum in itertools.zip_longest(ls, rs, lnums, rnums):
            yield (l is not None, True, l or '', r or '', lnum or 0, rnum or 0)


def side_by_side_diff(old_text: str, new_text: str) -> Generator[Tuple[bool, bool, str, str, int, int], None, None]:
    """
    Calculates a side-by-side line-based difference view.
    """
    line_split = re.compile(r'(?:\r?\n)')
    dmp = diff_match_patch.diff_match_patch()

    diff = dmp.diff_main(old_text, new_text)
    dmp.diff_cleanupSemantic(diff)

    open_entry = ([''], [''], [0], [0])
    for change_type, entry in diff:
        assert change_type in [-1, 0, 1]

        entry = (entry.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
        lines = line_split.split(entry)

        # Merge with previous entry if still open
        ls, rs, lnums, rnums = open_entry

        line = lines[0]
        if line:
            if change_type == 0:
                ls[-1] += line
                rs[-1] += line
                lnums[-1] += len(line)
                rnums[-1] += len(line)
            elif change_type == 1:
                rs[-1] = rs[-1] or ''
                rs[-1] += log.green_diff(line) if line else ''
                rnums[-1] += len(line)
            elif change_type == -1:
                ls[-1] = ls[-1] or ''
                ls[-1] += log.red_diff(line) if line else ''
                lnums[-1] += len(line)

        lines = lines[1:]

        if lines:
            if change_type == 0:
                # Push out open entry
                for entry in yield_open_entry(open_entry):
                    yield entry

                # Directly push out lines until last
                for line in lines[:-1]:
                    yield (True, False, line, line, len(line), len(line))

                # Keep last line open
                open_entry = ([lines[-1]], [lines[-1]], [len(lines[-1])], [len(lines[-1])])
            elif change_type == 1:
                ls, rs, lnums, rnums = open_entry
                for line in lines:
                    rs.append(log.green_diff(line) if line else '')
                    rnums.append(len(line))
            elif change_type == -1:
                ls, rs, lnums, rnums = open_entry
                for line in lines:
                    ls.append(log.red_diff(line) if line else '')
                    lnums.append(len(line))

    # Push out open entry
    for entry in yield_open_entry(open_entry):
        yield entry
