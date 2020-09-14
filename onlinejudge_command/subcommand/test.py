import argparse
import concurrent.futures
import contextlib
import enum
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import threading
import traceback
from logging import getLogger
from typing import *

import onlinejudge_command.format_utils as fmtutils
import onlinejudge_command.output_comparators as output_comparators
import onlinejudge_command.pretty_printers as pretty_printers
import onlinejudge_command.utils as utils

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
    ALL = 'all'
    DIFF = 'diff'


def build_match_function(*, compare_mode: CompareMode, error: Optional[float], judge_command: Optional[str], silent: bool, test_input_path: pathlib.Path, test_output_path: Optional[pathlib.Path]) -> Callable[[bytes, bytes], bool]:
    """build_match_function builds the function to compare actual outputs and expected outputs.

    This function doesn't any I/O.
    """

    if judge_command is not None:
        special_judge = output_comparators.SpecialJudge(judge_command=judge_command, is_silent=silent)

        def run_judge_command(actual: bytes, expected: bytes) -> bool:
            # the second argument is ignored
            return special_judge.run(
                actual_output=actual,
                input_path=test_input_path,
                expected_output_path=test_output_path,
            )

        return run_judge_command

    is_exact = False
    if compare_mode == CompareMode.EXACT_MATCH and error is None:
        is_exact = True
        file_comparator: output_comparators.OutputComparator = output_comparators.ExactComparator()
    elif compare_mode == CompareMode.CRLF_INSENSITIVE_EXACT_MATCH and error is None:
        is_exact = True
        file_comparator = output_comparators.CRLFInsensitiveComparator(output_comparators.ExactComparator())
    else:
        if error is not None:
            word_comparator: output_comparators.OutputComparator = output_comparators.FloatingPointNumberComparator(rel_tol=error, abs_tol=error)
        else:
            word_comparator = output_comparators.ExactComparator()
        if compare_mode in (CompareMode.EXACT_MATCH, CompareMode.CRLF_INSENSITIVE_EXACT_MATCH, CompareMode.IGNORE_SPACES):
            file_comparator = output_comparators.SplitLinesComparator(output_comparators.SplitComparator(word_comparator))
        elif compare_mode == CompareMode.IGNORE_SPACES_AND_NEWLINES:
            file_comparator = output_comparators.SplitComparator(word_comparator)
        else:
            assert False
        file_comparator = output_comparators.CRLFInsensitiveComparator(file_comparator)

    def compare_outputs(actual: bytes, expected: bytes) -> bool:
        result = file_comparator(actual, expected)
        if not result and is_exact:
            non_stcict_comparator = output_comparators.CRLFInsensitiveComparator(output_comparators.SplitComparator(output_comparators.ExactComparator()))
            if non_stcict_comparator(actual, expected):
                logger.warning('This was AC if spaces and newlines were ignored. Please use --ignore-spaces (-S) option or --ignore-spaces-and-newline (-N) option.')
        return result

    return compare_outputs


def run_checking_output(*, answer: bytes, test_output_path: Optional[pathlib.Path], is_special_judge: bool, match_function: Callable[[bytes, bytes], bool]) -> Optional[bool]:
    """run_checking_output executes matching of the actual output and the expected output.

    This function has file I/O including the execution of the judge command.
    """

    if test_output_path is None and not is_special_judge:
        return None
    if test_output_path is not None:
        with test_output_path.open('rb') as outf:
            expected = outf.read()
    else:
        # only if --judge option
        expected = b''
        logger.warning('expected output is not found')
    return match_function(answer, expected)


class JudgeStatus(enum.Enum):
    AC = 'AC'
    WA = 'WA'
    RE = 'RE'
    TLE = 'TLE'
    MLE = 'MLE'


def display_result(proc: subprocess.Popen, answer: str, memory: Optional[float], test_input_path: pathlib.Path, test_output_path: Optional[pathlib.Path], *, mle: Optional[float], display_mode: DisplayMode, does_print_input: bool, silent: bool, match_result: Optional[bool]) -> JudgeStatus:
    """display_result prints the result of the test and its statistics.

    This function prints many logs and does some I/O.
    """

    # prepare the function to print the input
    is_input_printed = False

    def print_input() -> None:
        nonlocal is_input_printed
        if does_print_input and not is_input_printed:
            is_input_printed = True
            with test_input_path.open('rb') as inf:
                logger.info(utils.NO_HEADER + 'input:\n%s', pretty_printers.make_pretty_large_file_content(inf.read(), limit=40, head=20, tail=10, bold=True))

    # check TLE, RE or not
    status = JudgeStatus.AC
    if proc.returncode is None:
        logger.info(utils.FAILURE + '' + utils.red('TLE'))
        status = JudgeStatus.TLE
        if not silent:
            print_input()
    elif memory is not None and mle is not None and memory > mle:
        logger.info(utils.FAILURE + '' + utils.red('MLE'))
        status = JudgeStatus.MLE
        if not silent:
            print_input()
    elif proc.returncode != 0:
        logger.info(utils.FAILURE + '' + utils.red('RE') + ': return code %d', proc.returncode)
        status = JudgeStatus.RE
        if not silent:
            print_input()

    # check WA or not
    if match_result is not None and not match_result:
        if status == JudgeStatus.AC:
            logger.info(utils.FAILURE + '' + utils.red('WA'))
        status = JudgeStatus.WA
        if not silent:
            print_input()
            if test_output_path is not None:
                with test_output_path.open('rb') as outf:
                    expected = outf.read().decode()
            else:
                expected = ''
            if display_mode == DisplayMode.SUMMARY:
                logger.info(utils.NO_HEADER + 'output:\n%s', pretty_printers.make_pretty_large_file_content(answer.encode(), limit=40, head=20, tail=10, bold=True))
                logger.info(utils.NO_HEADER + 'expected:\n%s', pretty_printers.make_pretty_large_file_content(expected.encode(), limit=40, head=20, tail=10, bold=True))
            elif display_mode == DisplayMode.DIFF:
                if max(answer.count('\n'), expected.count('\n')) <= 40:
                    pretty_printers.display_side_by_side_color(answer, expected)
                else:
                    pretty_printers.display_snipped_side_by_side_color(answer, expected)
            else:
                assert False
    if match_result is None:
        if not silent:
            print_input()
            logger.info(utils.NO_HEADER + 'output:\n%s', pretty_printers.make_pretty_large_file_content(answer.encode(), limit=40, head=20, tail=10, bold=True))
    if status == JudgeStatus.AC:
        logger.info(utils.SUCCESS + '' + utils.green('AC'))

    return status


def test_single_case(test_name: str, test_input_path: pathlib.Path, test_output_path: Optional[pathlib.Path], *, lock: Optional[threading.Lock] = None, args: argparse.Namespace) -> Dict[str, Any]:
    # print the header earlier if not in parallel
    if lock is None:
        logger.info('')
        logger.info('%s', test_name)

    # run the binary
    with test_input_path.open('rb') as inf:
        info, proc = utils.exec_command(args.command, stdin=inf, timeout=args.tle, gnu_time=args.gnu_time)
        # TODO: the `answer` should be bytes, not str
        answer: str = (info['answer'] or b'').decode(errors='replace')
        elapsed: float = info['elapsed']
        memory: Optional[float] = info['memory']

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

        match_function = build_match_function(compare_mode=CompareMode(args.compare_mode), error=args.error, judge_command=args.judge, silent=args.silent, test_input_path=test_input_path, test_output_path=test_output_path)
        match_result = run_checking_output(answer=answer.encode(), test_output_path=test_output_path, is_special_judge=args.judge is not None, match_function=match_function)
        status = display_result(proc, answer, memory, test_input_path, test_output_path, mle=args.mle, display_mode=DisplayMode(args.display_mode), does_print_input=args.print_input, silent=args.silent, match_result=match_result)

    # return the result
    testcase = {
        'name': test_name,
        'input': str(test_input_path.resolve()),
    }
    if test_output_path:
        testcase['output'] = str(test_output_path.resolve())
    return {
        'status': status.value,
        'testcase': testcase,
        'output': answer,
        'exitcode': proc.returncode,
        'elapsed': elapsed,
        'memory': memory,
    }


def check_gnu_time(gnu_time: str) -> bool:
    try:
        with tempfile.NamedTemporaryFile(delete=True) as fh:
            subprocess.check_call([gnu_time, '-f', '%M KB', '-o', fh.name, '--', 'true'])
            with open(fh.name) as fh1:
                data = fh1.read()
            int(utils.remove_suffix(data.rstrip().splitlines()[-1], ' KB'))
            return True
    except NameError:
        raise  # NameError is not a runtime error caused by the environment, but a coding mistake
    except AttributeError:
        raise  # AttributeError is also a mistake
    except Exception:
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
    history: List[Dict[str, Any]] = []
    if args.jobs is None:
        for name, paths in sorted(tests.items()):
            history += [test_single_case(name, paths['in'], paths.get('out'), args=args)]
    else:
        if os.name == 'nt':
            logger.warning("-j/--jobs opiton is unstable on Windows environmet")
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as executor:
            lock = threading.Lock()
            futures: List[concurrent.futures.Future] = []
            for name, paths in sorted(tests.items()):
                futures += [executor.submit(test_single_case, name, paths['in'], paths.get('out'), lock=lock, args=args)]
            for future in futures:
                history += [future.result()]

    # summarize
    slowest: float = -1.0
    slowest_name = ''
    heaviest: float = -1.0
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

    if args.log_file:
        with args.log_file.open(mode='w') as fh:
            json.dump(history, fh)

    if ac_count != len(tests):
        sys.exit(1)
