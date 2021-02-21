import argparse
import concurrent.futures
import contextlib
import hashlib
import itertools
import os
import pathlib
import subprocess
import threading
from logging import getLogger
from typing import *

import onlinejudge_command.format_utils as fmtutils
import onlinejudge_command.pretty_printers as pretty_printers
import onlinejudge_command.utils as utils

logger = getLogger(__name__)


def add_subparser(subparsers: argparse.Action) -> None:
    subparsers_add_parser: Callable[..., argparse.ArgumentParser] = subparsers.add_parser  # type: ignore
    subparser = subparsers_add_parser('generate-input', aliases=['g/i'], help='generate input files from given generator', formatter_class=argparse.RawTextHelpFormatter, epilog='''\
format string for --format:
  %s                    name
  %e                    extension: "in" or "out"
  (both %d and %e are required.)

tips:
  For the random testing, you can read a tutorial: https://github.com/online-judge-tools/oj/blob/master/docs/getting-started.md#random-testing

  There is a command to automatically generate a input generator, `oj-template` command. See https://github.com/online-judge-tools/template-generator .

  This subcommand has also the feature to find a hack case.
    e.g. for a target program `a.out`, a correct (but possibly slow) program `naive`, and a random input-case generator `generate.py`, run $ oj g/i --hack-actual ./a.out --hack-expected ./naive 'python3 generate.py'

  You can do similar things with shell
    e.g. $ for i in `seq 100` ; do python3 generate.py > test/random-$i.in ; done
''')
    subparser.add_argument('-f', '--format', default='%s.%e', help='a format string to recognize the relationship of test cases. (default: "%%s.%%e")')
    subparser.add_argument('-d', '--directory', type=pathlib.Path, default=pathlib.Path('test'), help='a directory name for test cases (default: test/)')
    subparser.add_argument('-t', '--tle', type=float, help='set the time limit (in second) (default: inf)')
    subparser.add_argument('-j', '--jobs', type=int, help='run tests in parallel')
    subparser.add_argument('--width', type=int, default=3, help='specify the width of indices of cases. (default: 3)')
    subparser.add_argument('--name', help='specify the base name of cases. (default: "random")')
    subparser.add_argument('-c', '--command', help='specify your solution to generate output')
    subparser.add_argument('--hack-expected', dest='command', help='alias of --command')
    subparser.add_argument('--hack', '--hack-actual', dest='hack', help='specify your wrong solution to be compared with the reference solution given by --hack-expected')
    subparser.add_argument('generator', type=str, help='your program to generate test cases')
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


def write_result(input_data: bytes, output_data: Optional[bytes], *, input_path: pathlib.Path, output_path: pathlib.Path, print_data: bool, lock: Optional[threading.Lock] = None) -> None:
    # acquire lock to print logs properly, if in parallel
    nullcontext = contextlib.ExitStack()  # TODO: use contextlib.nullcontext after Python 3.7
    with lock or nullcontext:

        if not input_path.parent.is_dir():
            os.makedirs(str(input_path.parent), exist_ok=True)

        if print_data:
            logger.info(utils.NO_HEADER + 'input:')
            logger.info(utils.NO_HEADER + '%s', pretty_printers.make_pretty_large_file_content(input_data, limit=40, head=20, tail=10, bold=True))
        with input_path.open('wb') as fh:
            fh.write(input_data)
        logger.info(utils.SUCCESS + 'saved to: %s', input_path)

        if output_data is not None:
            if print_data:
                logger.info(utils.NO_HEADER + 'output:')
                logger.info(pretty_printers.make_pretty_large_file_content(output_data, limit=40, head=20, tail=10, bold=True))
            with output_path.open('wb') as fh:
                fh.write(output_data)
            logger.info(utils.SUCCESS + 'saved to: %s', output_path)


def check_status(info: Dict[str, Any], proc: subprocess.Popen, *, submit: Callable[..., None]) -> bool:
    submit(logger.info, 'time: %f sec', info['elapsed'])
    if proc.returncode is None:
        submit(logger.info, utils.FAILURE + utils.red('TLE'))
        submit(logger.info, 'skipped.')
        return False
    elif proc.returncode != 0:
        submit(logger.info, utils.FAILURE + utils.red('RE') + ': return code %d', proc.returncode)
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


def generate_input_single_case(generator: str, *, input_path: pathlib.Path, output_path: pathlib.Path, command: Optional[str], tle: Optional[float], name: str, lock: Optional[threading.Lock] = None, generated_input_hashes: Dict[bytes, str]) -> None:
    with BufferedExecutor(lock) as submit:

        # print the header
        submit(logger.info, '')
        submit(logger.info, '%s', name)

        # generate input
        submit(logger.info, 'generate input...')
        info, proc = utils.exec_command(generator, timeout=tle)
        input_data: bytes = info['answer']
        if not check_status(info, proc, submit=submit):
            return

        # check the randomness of generator
        conflicted_name = check_randomness_of_generator(input_data, name=name, lock=lock, generated_input_hashes=generated_input_hashes)
        if conflicted_name is not None:
            submit(logger.warning, 'The same input is already generated at %s. Please use a random input generator.', conflicted_name)

        # generate output
        if command is None:
            output_data: Optional[bytes] = None
        else:
            submit(logger.info, 'generate output...')
            info, proc = utils.exec_command(command, input=input_data, timeout=tle)
            output_data = info['answer']
            if not check_status(info, proc, submit=submit):
                return

        # write result
        submit(write_result, input_data=input_data, output_data=output_data, input_path=input_path, output_path=output_path, print_data=True)


def simple_match(a: str, b: str) -> bool:
    if a == b:
        return True
    if a.rstrip() == b.rstrip():
        logger.warning('WA if no rstrip')
        return True
    return False


def try_hack_once(generator: str, command: str, hack: str, *, tle: Optional[float], attempt: int, lock: Optional[threading.Lock] = None, generated_input_hashes: Dict[bytes, str]) -> Optional[Tuple[bytes, bytes]]:
    with BufferedExecutor(lock) as submit:

        # print the header
        submit(logger.info, '')
        submit(logger.info, '%d-th attempt', attempt)

        # generate input
        submit(logger.info, 'generate input...')
        info, proc = utils.exec_command(generator, stdin=None, timeout=tle)
        input_data: Optional[bytes] = info['answer']
        if not check_status(info, proc, submit=submit):
            return None
        assert input_data is not None

        # check the randomness of generator
        name = '{}-th attempt'.format(attempt)
        conflicted_name = check_randomness_of_generator(input_data, name=name, lock=lock, generated_input_hashes=generated_input_hashes)
        if conflicted_name is not None:
            submit(logger.warning, 'The same input is already generated at %s. Please use a random input generator.', conflicted_name)
            submit(logger.info, utils.NO_HEADER + 'input:')
            submit(logger.info, utils.NO_HEADER + '%s', pretty_printers.make_pretty_large_file_content(input_data, limit=40, head=20, tail=10, bold=True))

        # generate output
        submit(logger.info, 'generate output...')
        info, proc = utils.exec_command(command, input=input_data, timeout=tle)
        output_data: Optional[bytes] = info['answer']
        if not check_status(info, proc, submit=submit):
            return None
        assert output_data is not None

        # hack
        submit(logger.info, 'hack...')
        info, proc = utils.exec_command(hack, input=input_data, timeout=tle)
        answer: str = (info['answer'] or b'').decode()

        # compare
        status = 'AC'
        if proc.returncode is None:
            submit(logger.info, 'FAILURE: ' + utils.red('TLE'))
            status = 'TLE'
        elif proc.returncode != 0:
            logger.info(utils.FAILURE + '' + utils.red('RE') + ': return code %d', proc.returncode)
            status = 'RE'
        expected = output_data.decode()
        if not simple_match(answer, expected):
            logger.info(utils.FAILURE + '' + utils.red('WA'))
            logger.info(utils.NO_HEADER + 'input:\n%s', pretty_printers.make_pretty_large_file_content(input_data, limit=40, head=20, tail=10, bold=True))
            logger.info(utils.NO_HEADER + 'output:\n%s', pretty_printers.make_pretty_large_file_content(answer.encode(), limit=40, head=20, tail=10, bold=True))
            logger.info(utils.NO_HEADER + 'expected:\n%s', pretty_printers.make_pretty_large_file_content(output_data, limit=40, head=20, tail=10, bold=True))
            status = 'WA'

        if status == 'AC':
            return None
        else:
            return (input_data, output_data)


def run(args: argparse.Namespace) -> None:
    if args.hack and not args.command:
        raise RuntimeError('--hack must be used with --command')

    if args.name is None:
        if args.hack:
            args.name = 'hack'
        else:
            args.name = 'random'

    if args.count is None:
        if args.hack:
            args.count = 1
        else:
            args.count = 100

    def iterate_path():
        for i in itertools.count():
            name = '{}-{}'.format(args.name, str(i).zfill(args.width))
            input_path = fmtutils.path_from_format(args.directory, args.format, name=name, ext='in')
            output_path = fmtutils.path_from_format(args.directory, args.format, name=name, ext='out')
            if not input_path.exists() and not output_path.exists():
                yield (name, input_path, output_path)

    # generate cases
    generated_input_hashes: Dict[bytes, str] = {}
    if args.jobs is None:
        for name, input_path, output_path in itertools.islice(iterate_path(), args.count):
            if not args.hack:
                # generate serially
                generate_input_single_case(args.generator, input_path=input_path, output_path=output_path, command=args.command, tle=args.tle, name=name, generated_input_hashes=generated_input_hashes)

            else:
                # hack serially
                for attempt in itertools.count(1):
                    data = try_hack_once(args.generator, command=args.command, hack=args.hack, tle=args.tle, attempt=attempt, generated_input_hashes=generated_input_hashes)
                    if data is not None:
                        write_result(*data, input_path=input_path, output_path=output_path, print_data=False)
                        break
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as executor:
            lock = threading.Lock()
            futures: List[concurrent.futures.Future] = []

            if not args.hack:
                # generate concurrently
                for name, input_path, output_path in itertools.islice(iterate_path(), args.count):
                    futures += [executor.submit(generate_input_single_case, args.generator, input_path=input_path, output_path=output_path, command=args.command, tle=args.tle, name=name, lock=lock, generated_input_hashes=generated_input_hashes)]
                for future in futures:
                    future.result()

            else:
                # hack concurrently
                attempt = 0
                for _ in range(args.jobs):
                    attempt += 1
                    futures += [executor.submit(try_hack_once, args.generator, command=args.command, hack=args.hack, tle=args.tle, attempt=attempt, lock=lock, generated_input_hashes=generated_input_hashes)]
                for _, input_path, output_path in itertools.islice(iterate_path(), args.count):
                    data = None
                    while data is None:
                        concurrent.futures.wait(futures, return_when=concurrent.futures.FIRST_COMPLETED)
                        for i in range(len(futures)):
                            if not futures[i].done():
                                continue
                            data = futures[i].result()
                            attempt += 1
                            futures[i] = executor.submit(try_hack_once, args.generator, command=args.command, hack=args.hack, tle=args.tle, attempt=attempt, lock=lock, generated_input_hashes=generated_input_hashes)
                            if data is not None:
                                break
                    write_result(*data, input_path=input_path, output_path=output_path, print_data=False, lock=lock)
