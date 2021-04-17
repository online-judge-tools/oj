import argparse
import json
import os
import pathlib
from logging import getLogger
from typing import *

import requests.exceptions

import onlinejudge.dispatch as dispatch
import onlinejudge_command.download_history
import onlinejudge_command.format_utils as format_utils
import onlinejudge_command.pretty_printers as pretty_printers
import onlinejudge_command.utils as utils
from onlinejudge.service.yukicoder import YukicoderProblem
from onlinejudge.type import SampleParseError, TestCase

logger = getLogger(__name__)


def add_subparser(subparsers: argparse.Action) -> None:
    subparsers_add_parser: Callable[..., argparse.ArgumentParser] = subparsers.add_parser  # type: ignore
    subparser = subparsers_add_parser('download', aliases=['d', 'dl'], help='download sample cases', formatter_class=argparse.RawTextHelpFormatter, epilog='''\
supported services:
  Anarchy Golf
  Aizu Online Judge (including the Arena)
  AtCoder
  Codeforces
  yukicoder
  CS Academy
  HackerRank
  PKU JudgeOnline
  Kattis
  Toph (Problem Archive)
  CodeChef
  Facebook Hacker Cup
  Google Code Jam
  Library Checker (https://judge.yosupo.jp/)

supported services with --system:
  Aizu Online Judge
  yukicoder
  Library Checker (https://judge.yosupo.jp/)

format string for --format:
  %i                    index: 1, 2, 3, ...
  %e                    extension: "in" or "out"
  %n                    name: e.g. "Sample Input 1", "system_test3.txt", ...
  %b                    os.path.basename(name)
  %d                    os.path.dirname(name)
  %%                    '%' itself

tips:
  This subcommand doesn't have the feature to download all test cases for all problems in a contest at once. If you want to do this, please use `oj-prepare` command at https://github.com/online-judge-tools/template-generator instead.

  You can do similar things with shell and oj-api command. see https://github.com/online-judge-tools/api-client
    e.g. $ oj-api get-problem https://atcoder.jp/contests/agc001/tasks/agc001_a | jq -cr '.result.tests | to_entries[] | [{path: "test/sample-\\(.key).in", data: .value.input}, {path: "test/sample-\\(.key).out", data: .value.output}][] | {path, data: @sh "\\(.data)"} | "mkdir -p test; echo -n \\(.data) > \\(.path)"' | sh
''')
    subparser.add_argument('url')
    subparser.add_argument('-f', '--format', help='a format string to specify paths of cases (default: "sample-%%i.%%e" if not --system)')  # default must be None for --system
    subparser.add_argument('-d', '--directory', type=pathlib.Path, help='a directory name for test cases (default: test/)')  # default must be None for guessing in submit command
    subparser.add_argument('-n', '--dry-run', action='store_true', help='don\'t write to files')
    subparser.add_argument('-a', '--system', action='store_true', help='download system testcases')
    subparser.add_argument('-s', '--silent', action='store_true')
    subparser.add_argument('--yukicoder-token', type=str)
    subparser.add_argument('--log-file', type=pathlib.Path, help=argparse.SUPPRESS)


def convert_sample_to_dict(sample: TestCase) -> Dict[str, str]:
    data: Dict[str, str] = {}
    data["name"] = sample.name
    data["input"] = sample.input_data.decode()
    if sample.output_data is not None:
        data["output"] = sample.output_data.decode()
    return data


def run(args: argparse.Namespace) -> bool:
    # prepare values
    problem = dispatch.problem_from_url(args.url)
    if problem is None:
        if dispatch.contest_from_url(args.url) is not None:
            logger.warning('You specified a URL for a contest instead of a problem. If you want to download for all problems of a contest at once, please try to use `oj-prepare` command of https://github.com/online-judge-tools/template-generator')
        logger.error('The URL "%s" is not supported', args.url)
        return False
    is_default_format = args.format is None and args.directory is None  # must be here since args.directory and args.format are overwritten
    if args.directory is None:
        args.directory = pathlib.Path('test')
    if args.format is None:
        args.format = '%b.%e'

    # get samples from the server
    with utils.new_session_with_our_user_agent(path=args.cookie) as sess:
        if args.yukicoder_token and isinstance(problem, YukicoderProblem):
            sess.headers['Authorization'] = 'Bearer {}'.format(args.yukicoder_token)
        try:
            if args.system:
                samples = problem.download_system_cases(session=sess)
            else:
                samples = problem.download_sample_cases(session=sess)
        except requests.exceptions.RequestException as e:
            logger.error('%s', e)
            logger.error(utils.HINT + 'You may need to login to use `$ oj download ...` during contest. Please run: $ oj login %s', problem.get_service().get_url())
            return False
        except SampleParseError as e:
            logger.error('%s', e)
            return False

    if not samples:
        logger.error("Sample not found")
        return False

    # append the history for submit subcommand
    if not args.dry_run and is_default_format:
        history = onlinejudge_command.download_history.DownloadHistory()
        if not list(args.directory.glob('*')):
            # reset the history to help users who use only one directory for many problems
            history.remove(directory=pathlib.Path.cwd())
        history.add(problem, directory=pathlib.Path.cwd())

    # prepare files to write
    def iterate_files_to_write(sample: TestCase, *, i: int) -> Iterator[Tuple[str, pathlib.Path, bytes]]:
        for ext in ['in', 'out']:
            data = getattr(sample, ext + 'put_data')
            if data is None:
                continue
            name = sample.name
            table = {}
            table['i'] = str(i + 1)
            table['e'] = ext
            table['n'] = name
            table['b'] = os.path.basename(name)
            table['d'] = os.path.dirname(name)
            path: pathlib.Path = args.directory / format_utils.percentformat(args.format, table)
            yield ext, path, data

    for i, sample in enumerate(samples):
        for _, path, _ in iterate_files_to_write(sample, i=i):
            if path.exists():
                logger.error('Failed to download since file already exists: %s', str(path))
                logger.info(utils.HINT + 'We recommend adding your own test cases to test/ directory, and using one directory per one problem. Please see also https://github.com/online-judge-tools/oj/blob/master/docs/getting-started.md#random-testing. If you wanted to keep using one directory per one contest, you can run like `$ rm -rf test/ && oj d https://...`.')
                return False

    # write samples to files
    for i, sample in enumerate(samples):
        logger.info('')
        logger.info('sample %d', i)
        for ext, path, data in iterate_files_to_write(sample, i=i):
            content = ''
            if not args.silent:
                content = '\n' + pretty_printers.make_pretty_large_file_content(data, limit=40, head=20, tail=10, bold=True)
            logger.info('%sput: %s%s', ext, sample.name, content)
            if not args.dry_run:
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open('wb') as fh:
                    fh.write(data)
                logger.info(utils.SUCCESS + 'saved to: %s', path)

    if args.log_file:
        with args.log_file.open(mode='w') as fhs:
            json.dump(list(map(convert_sample_to_dict, samples)), fhs)

    return True
