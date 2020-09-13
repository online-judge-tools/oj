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


def convert_sample_to_dict(sample: TestCase) -> Dict[str, str]:
    data: Dict[str, str] = {}
    data["name"] = sample.name
    data["input"] = sample.input_data.decode()
    if sample.output_data is not None:
        data["output"] = sample.output_data.decode()
    return data


def download(args: argparse.Namespace) -> None:
    # prepare values
    problem = dispatch.problem_from_url(args.url)
    if problem is None:
        if dispatch.contest_from_url(args.url) is not None:
            logger.warning('You specified a URL for a contest instead of a problem. If you want to download for all problems of a contest at once, please try to use `oj-prepare` command of https://github.com/online-judge-tools/template-generator')
        raise requests.exceptions.InvalidURL('The URL "%s" is not supported' % args.url)
    is_default_format = args.format is None and args.directory is None  # must be here since args.directory and args.format are overwritten
    if args.directory is None:
        args.directory = pathlib.Path('test')
    if args.format is None:
        args.format = '%b.%e'

    # get samples from the server
    with utils.new_session_with_our_user_agent(path=args.cookie) as sess:
        if args.yukicoder_token and isinstance(problem, YukicoderProblem):
            sess.headers['Authorization'] = 'Bearer {}'.format(args.yukicoder_token)
        if args.system:
            samples = problem.download_system_cases(session=sess)
        else:
            samples = problem.download_sample_cases(session=sess)

    if not samples:
        raise SampleParseError("Sample not found")

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
                raise FileExistsError('Failed to download since file already exists: ' + str(path))

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
