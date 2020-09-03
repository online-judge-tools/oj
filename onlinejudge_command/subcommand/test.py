# Python Version: 3.x
import collections
import concurrent.futures
import contextlib
import enum
import itertools
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import traceback
from logging import getLogger
from typing import *

import diff_match_patch
import onlinejudge_command.format_utils as fmtutils
import onlinejudge_command.output_comparators as output_comparators
import onlinejudge_command.utils as utils

if TYPE_CHECKING:
    import argparse

logger = getLogger(__name__)

MEMORY_WARNING = 500  # megabyte
MEMORY_PRINT = 100  # megabyte


class CompareMode(enum.Enum):
    EXACT_MATCH = 'exact-match'
    CRLF_INSENSITIVE_EXACT_MATCH = 'crlf-insensitive-exact-match'
    IGNORE_SPACES = 'ignore-spaces'
    IGNORE_SPACES_AND_NEWLINES = 'ignore-spaces-and-newlines'


class DisplayMode(enum.Enum):
    SUMMARY = 'summary'
    DIFF = 'diff'


def compare_and_report(proc: subprocess.Popen, answer: str, memory: Optional[float], test_input_path: pathlib.Path, test_output_path: Optional[pathlib.Path], *, mle: Optional[float], display_mode: DisplayMode, error: Optional[float], does_print_input: bool, silent: bool, compare_mode: CompareMode, judge_command: Optional[str]) -> str:
    # prepare the comparing function
    if judge_command is not None:
        special_judge = output_comparators.SpecialJudge(judge_command=judge_command, is_silent=silent)

        def match(actual: bytes, expected: bytes) -> bool:
            # the second argument is ignored
            return special_judge.run(
                actual_output=actual,
                input_path=test_input_path,
                expected_output_path=test_output_path,
            )
    else:
        is_exact = False
        if compare_mode == CompareMode.EXACT_MATCH and error is None:
            is_exact = True
            file_comparator = output_comparators.ExactComparator()  # type: output_comparators.OutputComparator
        elif compare_mode == CompareMode.CRLF_INSENSITIVE_EXACT_MATCH and error is None:
            is_exact = True
            file_comparator = output_comparators.CRLFInsensitiveComparator(output_comparators.ExactComparator())
        else:
            if error is not None:
                word_comparator = output_comparators.FloatingPointNumberComparator(rel_tol=error, abs_tol=error)  # type: output_comparators.OutputComparator
            else:
                word_comparator = output_comparators.ExactComparator()
            if compare_mode in (CompareMode.EXACT_MATCH, CompareMode.CRLF_INSENSITIVE_EXACT_MATCH, CompareMode.IGNORE_SPACES):
                file_comparator = output_comparators.SplitLinesComparator(output_comparators.SplitComparator(word_comparator))
            elif compare_mode == CompareMode.IGNORE_SPACES_AND_NEWLINES:
                file_comparator = output_comparators.SplitComparator(word_comparator)
            else:
                assert False
            file_comparator = output_comparators.CRLFInsensitiveComparator(file_comparator)

        def match(actual: bytes, expected: bytes) -> bool:
            result = file_comparator(actual, expected)
            if not result and is_exact:
                non_stcict_comparator = output_comparators.CRLFInsensitiveComparator(output_comparators.SplitComparator(output_comparators.ExactComparator()))
                if non_stcict_comparator(actual, expected):
                    logger.warning('This was AC if spaces and newlines were ignored. Please use --ignore-spaces (-S) option or --ignore-spaces-and-newline (-N) option.')
            return result

    # prepare the function to print the input
    is_input_printed = False

    def print_input() -> None:
        nonlocal is_input_printed
        if does_print_input and not is_input_printed:
            is_input_printed = True
            with test_input_path.open('rb') as inf:
                logger.info(utils.NO_HEADER + 'input:\n%s', utils.make_pretty_large_file_content(inf.read(), limit=40, head=20, tail=10, bold=True))

    # check TLE, RE or not
    status = 'AC'
    if proc.returncode is None:
        logger.info(utils.FAILURE + '' + utils.red('TLE'))
        status = 'TLE'
        print_input()
    elif memory is not None and mle is not None and memory > mle:
        logger.info(utils.FAILURE + '' + utils.red('MLE'))
        status = 'MLE'
        print_input()
    elif proc.returncode != 0:
        logger.info(utils.FAILURE + '' + utils.red('RE') + ': return code %d', proc.returncode)
        status = 'RE'
        print_input()

    # check WA or not
    if (test_output_path is not None) or (judge_command is not None):
        if test_output_path is not None:
            with test_output_path.open('rb') as outf:
                expected = outf.read().decode()
        else:  # only if --judge option
            expected = ''
            logger.warning('expected output is not found')
        # compare
        if not match(answer.encode(), expected.encode()):
            logger.info(utils.FAILURE + '' + utils.red('WA'))
            print_input()
            if not silent:
                if display_mode == DisplayMode.SUMMARY:
                    logger.info(utils.NO_HEADER + 'output:\n%s', utils.make_pretty_large_file_content(answer.encode(), limit=40, head=20, tail=10, bold=True))
                    logger.info(utils.NO_HEADER + 'expected:\n%s', utils.make_pretty_large_file_content(expected.encode(), limit=40, head=20, tail=10, bold=True))
                elif display_mode == DisplayMode.DIFF:
                    if max(answer.count('\n'), expected.count('\n')) <= 40:
                        display_side_by_side_color(answer, expected)
                    else:
                        display_snipped_side_by_side_color(answer, expected)
                else:
                    assert False
            status = 'WA'
    else:
        if not silent:
            header = ('output:\n' if is_input_printed else '')
            logger.info(utils.NO_HEADER + '%s%s', header, utils.make_pretty_large_file_content(answer.encode(), limit=40, head=20, tail=10, bold=True))
    if status == 'AC':
        logger.info(utils.SUCCESS + '' + utils.green('AC'))

    return status


def test_single_case(test_name: str, test_input_path: pathlib.Path, test_output_path: Optional[pathlib.Path], *, lock: Optional[threading.Lock] = None, args: 'argparse.Namespace') -> Dict[str, Any]:
    # print the header earlier if not in parallel
    if lock is None:
        logger.info('')
        logger.info('%s', test_name)

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
            logger.info('')
            logger.info('%s', test_name)
        logger.info('time: %f sec', elapsed)
        if memory:
            if memory < MEMORY_PRINT:
                if args.print_memory:
                    logger.info('memory: %f MB', memory)
            elif memory < MEMORY_WARNING:
                logger.info('memory: %f MB', memory)
            else:
                logger.warning('memory: %f MB', memory)

        status = compare_and_report(proc, answer, memory, test_input_path, test_output_path, mle=args.mle, display_mode=DisplayMode(args.display_mode), error=args.error, does_print_input=args.print_input, silent=args.silent, compare_mode=CompareMode(args.compare_mode), judge_command=args.judge)

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
        logger.debug(traceback.format_exc())
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
        logger.warning('GNU time is not available: %s', args.gnu_time)
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
            logger.warning("-j/--jobs opiton is unstable on Windows environmet")
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
    logger.info('')
    logger.info('slowest: %f sec  (for %s)', slowest, slowest_name)
    if heaviest >= 0:
        if heaviest < MEMORY_WARNING:
            logger.info('max memory: %f MB  (for %s)', heaviest, heaviest_name)
        else:
            logger.warning('max memory: %f MB  (for %s)', heaviest, heaviest_name)
    if ac_count == len(tests):
        logger.info(utils.SUCCESS + 'test ' + utils.green('success') + ': %d cases', len(tests))
    else:
        logger.info(utils.FAILURE + 'test ' + utils.red('failed') + ': %d AC / %d cases', ac_count, len(tests))

    if args.json:
        print(json.dumps(history))

    if ac_count != len(tests):
        sys.exit(1)


def space_padding(s: str, max_length: int) -> str:
    return s + " " * max_length


def display_side_by_side_color(answer: str, expected: str):
    max_chars = shutil.get_terminal_size()[0] // 2 - 2

    logger.info(utils.NO_HEADER + 'output:' + " " * (max_chars - 7) + "|" + "expected:")
    logger.info(utils.NO_HEADER + '%s', "-" * max_chars + "|" + "-" * max_chars)
    for _, diff_found, ans_line, exp_line, ans_chars, exp_chars in side_by_side_diff(answer, expected):
        if diff_found:
            logger.info(utils.NO_HEADER + '%s', utils.red(space_padding(ans_line, max_chars - ans_chars)) + "|" + utils.green(exp_line))
        else:
            logger.info(utils.NO_HEADER + '%s', space_padding(ans_line, max_chars - ans_chars) + "|" + exp_line)


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

    logger.info(utils.NO_HEADER + '%s', " " * max_line_num_digits + "|output:" + " " * (max_chars - 7 - max_line_num_digits - 1) + "|" + "expected:")
    logger.info(utils.NO_HEADER + '%s', "-" * max_chars + "|" + "-" * max_chars)

    last_line_number = 0
    for (line_number, diff_found, ans_line, exp_line, ans_chars, exp_chars) in deq:
        num_spaces_after_output = max_chars - ans_chars - max_line_num_digits - 1
        line_number_str = str(line_number) if line_number is not None else ""
        line_num_display = space_padding(line_number_str, max_line_num_digits - len(line_number_str)) + "|"
        if not diff_found:
            logger.info(utils.NO_HEADER + '%s', line_num_display + space_padding(ans_line, num_spaces_after_output) + "|" + exp_line)
        else:
            logger.info(utils.NO_HEADER + '%s', line_num_display + utils.red(space_padding(ans_line, num_spaces_after_output)) + "|" + utils.green(exp_line))
        if line_number is not None:
            last_line_number = line_number
    num_snipped_lines = answer.count('\n') + 1 - last_line_number
    if num_snipped_lines > 0:
        logger.info(utils.NO_HEADER + '... (%s lines) ...', num_snipped_lines)


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
                rs[-1] += utils.green_diff(line) if line else ''
                rnums[-1] += len(line)
            elif change_type == -1:
                ls[-1] = ls[-1] or ''
                ls[-1] += utils.red_diff(line) if line else ''
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
                    rs.append(utils.green_diff(line) if line else '')
                    rnums.append(len(line))
            elif change_type == -1:
                ls, rs, lnums, rnums = open_entry
                for line in lines:
                    ls.append(utils.red_diff(line) if line else '')
                    lnums.append(len(line))

    # Push out open entry
    for entry in yield_open_entry(open_entry):
        yield entry
