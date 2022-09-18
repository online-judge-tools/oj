import argparse
import concurrent.futures
import contextlib
import enum
import hashlib
import itertools
import os
import pathlib
import subprocess
import sys
import tempfile
import threading
from logging import getLogger
from typing import *

import onlinejudge_command.format_utils as fmtutils
import onlinejudge_command.pretty_printers as pretty_printers
import onlinejudge_command.utils as utils

logger = getLogger(__name__)


def add_subparser(subparsers: argparse.Action) -> None:
    subparsers_add_parser: Callable[..., argparse.ArgumentParser] = subparsers.add_parser  # type: ignore
    subparser = subparsers_add_parser('generate-reactive', aliases=['g/r'], help='generate input files for reactive problems from given generator', formatter_class=argparse.RawTextHelpFormatter, epilog='''\
format string for --format:
  %s                    name
  %e                    extension: "in" or "out"
  (both %d and %e are required.)

tips:
  For the random testing, you can read a tutorial: https://github.com/online-judge-tools/oj/blob/master/docs/getting-started.md#random-testing

  There is a command to automatically generate a input generator, `oj-template` command. See https://github.com/online-judge-tools/template-generator .

  This subcommand has also the feature to find a hack case.
    e.g. for a target program `a.out`, and a reactive judge program `judge.py` which generates a random input-case by itself, run $ oj g/r ./a.out 'python3 judge.py'
    For this case, `judge.py` should print debugging information.

    e.g. for a target program `a.out`, a random input-case generator `generate.py`, and a reactive judge program `judge.py`, run $ oj g/r -g 'python3 generate.py' ./a.out 'python3 judge.py'

  You can do similar things with shell
    e.g. $ for i in `seq 100` ; do [[ -e a.pipe ]] && rm -f a.pipe ; mkfifo a.pipe && ./a.out < a.pipe | python3 judge.py > a.pipe; done
    e.g. $ for i in `seq 100` ; do python3 generate.py > test/random-$i.in ; [[ -e a.pipe ]] && rm -f a.pipe ; mkfifo a.pipe && ./a.out < a.pipe | python3 judge.py test/random-$i.in > a.pipe; done
''')
    subparser.add_argument('-f', '--format', default='%s.%e', help='a format string to recognize the relationship of test cases. (default: "%%s.%%e")')
    subparser.add_argument('-d', '--directory', type=pathlib.Path, default=pathlib.Path('test'), help='a directory name for test cases (default: test/)')
    subparser.add_argument('-t', '--tle', type=float, help='set the time limit (in second) (default: inf)')
    subparser.add_argument('-j', '--jobs', type=int, help='run tests in parallel')
    subparser.add_argument('--width', type=int, default=3, help='specify the width of indices of cases. (default: 3)')
    subparser.add_argument('--name', help='specify the base name of cases. (default: "random")')
    subparser.add_argument('-g', '--generator', type=str, help='your program to generate test cases')
    subparser.add_argument('hack', help='specify your wrong solution to be judged with the reactive program')
    subparser.add_argument('judge', type=str, help='judge program using standard I/O')
    subparser.add_argument('count', nargs='?', type=int, help='the number of cases to generate (default: 100)')


@contextlib.contextmanager
def BufferedExecutor(lock: Optional[threading.Lock]):
    buf: List[Tuple[Callable, List[Any], Dict[str, Any]]] = []

    def submit(f, *args, **kwargs):
        nonlocal buf
        if lock is None:
            f(*args, **kwargs)
        else:
            buf += [(f, args, kwargs)]

    result = yield submit

    if lock is not None:
        with lock:
            for f, args, kwargs in buf:
                f(*args, **kwargs)
    return result


def write_result(input_data: bytes, *, input_path: pathlib.Path, lock: Optional[threading.Lock] = None) -> None:
    # acquire lock to print logs properly, if in parallel
    nullcontext = contextlib.ExitStack()  # TODO: use contextlib.nullcontext after Python 3.7
    with lock or nullcontext:
        if not input_path.parent.is_dir():
            os.makedirs(str(input_path.parent), exist_ok=True)
        with input_path.open('wb') as fh:
            fh.write(input_data)
        logger.info(utils.SUCCESS + 'saved to: %s', input_path)


def check_status(info: Dict[str, Any], proc: subprocess.Popen, *, submit: Callable[..., None], input_data: Optional[bytes]) -> bool:
    submit(logger.info, 'time: %f sec', info['elapsed'])
    if proc.returncode is None:
        submit(logger.info, utils.FAILURE + utils.red('TLE'))
        if input_data is not None:
            submit(logger.info, utils.NO_HEADER + 'input:')
            submit(logger.info, utils.NO_HEADER + '%s', pretty_printers.make_pretty_large_file_content(input_data, limit=40, head=20, tail=10))
        submit(logger.info, 'skipped.')
        return False
    elif proc.returncode != 0:
        submit(logger.info, utils.FAILURE + utils.red('RE') + ': return code %d', proc.returncode)
        if input_data is not None:
            submit(logger.info, utils.NO_HEADER + 'input:')
            submit(logger.info, utils.NO_HEADER + '%s', pretty_printers.make_pretty_large_file_content(input_data, limit=40, head=20, tail=10))
        submit(logger.info, 'skipped.')
        return False
    assert info['answer'] is not None
    return True


def check_randomness_of_generator(input_data: bytes, *, name: str, lock: Optional[threading.Lock], generated_input_hashes: Dict[bytes, str]) -> Optional[str]:
    """check_randomness_of_generator() checks the generated inputs. This adds some overheads but is needed for foolproof. Many users forget to initialize their library and use fixed seeds.

    :returns: a previous name of the input when it was already once generated. None if it's a new input.
    """

    # To prevent consuming unlimited memories, do nothing if the user's generator is properly implemented.
    limit = 1000
    if len(generated_input_hashes) >= limit:
        return None

    input_digest = hashlib.sha1(input_data).digest()
    nullcontext = contextlib.ExitStack()  # TODO: use contextlib.nullcontext after Python 3.7
    with lock or nullcontext:
        if len(generated_input_hashes) < limit:
            if input_digest in generated_input_hashes:
                return generated_input_hashes[input_digest]
            else:
                generated_input_hashes[input_digest] = name
                if len(generated_input_hashes) == limit:
                    logger.info('Conflict checking of generated inputs is disabled now because it seems the given input generator has enough randomness.')  # This prints a log line but it's safe because here is in a lock.
    return None


class JudgeStatus(enum.Enum):
    AC = 'AC'
    WA = 'WA'
    RE = 'RE'


@contextlib.contextmanager
def fifo() -> Generator[Tuple[Any, Any], None, None]:
    fdr, fdw = os.pipe()
    fhr = os.fdopen(fdr, 'r')
    fhw = os.fdopen(fdw, 'w')
    yield fhr, fhw
    fhw.close()
    fhr.close()
    # os.close(fdw), os.close(fdr) are unnecessary


def run_reactive(hack: str, judge: str, generated_file: Optional[pathlib.Path]) -> JudgeStatus:
    with fifo() as (fhr1, fhw1):
        with fifo() as (fhr2, fhw2):
            with subprocess.Popen(hack, shell=True, stdin=fhr2, stdout=fhw1, stderr=sys.stderr) as proc1:
                if generated_file is not None:
                    judge_command = ' '.join([judge, str(generated_file.resolve())])
                else:
                    judge_command = judge

                with subprocess.Popen(judge_command, shell=True, stdin=fhr1, stdout=fhw2, stderr=sys.stderr) as proc2:
                    proc1.communicate()
                    proc2.communicate()

                    if proc1.returncode != 0:
                        return JudgeStatus.RE
                    elif proc2.returncode == 0:
                        return JudgeStatus.AC
                    else:
                        return JudgeStatus.WA


def try_hack_once(generator: Optional[str], hack: str, judge: str, *, tle: Optional[float], attempt: int, lock: Optional[threading.Lock] = None, generated_input_hashes: Dict[bytes, str]) -> Tuple[bool, Optional[bytes]]:
    with BufferedExecutor(lock) as submit:

        # print the header
        submit(logger.info, '')
        submit(logger.info, '%d-th attempt', attempt)

        # generate input if generator is given
        if generator is None:
            input_data = None
        else:
            submit(logger.info, 'generate input...')
            info, proc = utils.exec_command(generator, stdin=None, timeout=tle)
            input_data: Optional[bytes] = info['answer']
            if not check_status(info, proc, submit=submit, input_data=input_data):
                return None
            assert input_data is not None
    
        # check the randomness of generator
        name = '{}-th attempt'.format(attempt)
        if input_data is not None:
            conflicted_name = check_randomness_of_generator(input_data, name=name, lock=lock, generated_input_hashes=generated_input_hashes)
            if conflicted_name is not None:
                submit(logger.warning, 'The same input is already generated at %s. Please use a random input generator.', conflicted_name)
                submit(logger.info, utils.NO_HEADER + 'input:')
                submit(logger.info, utils.NO_HEADER + '%s', pretty_printers.make_pretty_large_file_content(input_data, limit=40, head=20, tail=10))

        # hack
        submit(logger.info, 'hack...')
        if generator is not None:
            with tempfile.NamedTemporaryFile(delete=True) as fh:
                with open(fh.name, 'wb') as fh1:
                    fh1.write(input_data)
                status = run_reactive(hack, judge, pathlib.Path(fh.name))
        else:
            status = run_reactive(hack, judge, None)

        if status != JudgeStatus.AC and input_data is not None:
            logger.info(utils.FAILURE + '' + utils.red(status.value))
            logger.info(utils.NO_HEADER + 'input:\n%s', pretty_printers.make_pretty_large_file_content(input_data, limit=40, head=20, tail=10))

        # return the result
        if status == JudgeStatus.AC:
            return (False, None)
        elif generator is None:
            return (True, None)
        else:
            return (True, input_data)


def run(args: argparse.Namespace) -> None:
    if not args.generator:
        logger.info('--generator is not given. It will assume the reactive judge generates a random input-case each time.')

    if args.name is None:
        args.name = 'hack'

    if args.count is None:
        args.count = 1

    def iterate_path():
        for i in itertools.count():
            name = '{}-{}'.format(args.name, str(i).zfill(args.width))
            input_path = fmtutils.path_from_format(args.directory, args.format, name=name, ext='in')
            if not input_path.exists():
                yield (name, input_path)

    # generate cases
    generated_input_hashes: Dict[bytes, str] = {}
    if args.jobs is None:
        for name, input_path in itertools.islice(iterate_path(), args.count):
            # hack serially
            for attempt in itertools.count(1):
                (hacked, input_data) = try_hack_once(args.generator, hack=args.hack, judge=args.judge, tle=args.tle, attempt=attempt, generated_input_hashes=generated_input_hashes)
                if hacked:
                    if input_data is not None:
                        write_result(input_data, input_path=input_path)
                    break
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as executor:
            lock = threading.Lock()
            futures: List[concurrent.futures.Future] = []

            # hack concurrently
            attempt = 0
            for _ in range(args.jobs):
                attempt += 1
                futures += [executor.submit(try_hack_once, args.generator, hack=args.hack, judge=args.judge, tle=args.tle, attempt=attempt, lock=lock, generated_input_hashes=generated_input_hashes)]
            for _, input_path, in itertools.islice(iterate_path(), args.count):
                hacked = False
                while not hacked:
                    concurrent.futures.wait(futures, return_when=concurrent.futures.FIRST_COMPLETED)
                    for i in range(len(futures)):
                        if not futures[i].done():
                            continue
                        [hacked, input_data] = futures[i].result()
                        attempt += 1
                        futures[i] = executor.submit(try_hack_once, args.generator, hack=args.hack, judge=args.judge, tle=args.tle, attempt=attempt, lock=lock, generated_input_hashes=generated_input_hashes)
                        if hacked:
                            break
                if input_data is not None:
                    write_result(input_data, input_path=input_path, lock=lock)
