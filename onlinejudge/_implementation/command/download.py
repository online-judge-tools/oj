# Python Version: 3.x
import json
import os
import pathlib
from typing import *

import requests.exceptions

import onlinejudge
import onlinejudge._implementation.download_history
import onlinejudge._implementation.format_utils as format_utils
import onlinejudge._implementation.logging as log
import onlinejudge._implementation.utils as utils
import onlinejudge.type
from onlinejudge.service.yukicoder import YukicoderProblem

if TYPE_CHECKING:
    import argparse


def convert_sample_to_dict(sample: onlinejudge.type.TestCase) -> Dict[str, str]:
    data = {}  # type: Dict[str, str]
    data["name"] = sample.name
    data["input"] = sample.input_data.decode()
    if sample.output_data is not None:
        data["output"] = sample.output_data.decode()
    return data


def download(args: 'argparse.Namespace') -> None:
    # prepare values
    problem = onlinejudge.dispatch.problem_from_url(args.url)
    if problem is None:
        raise requests.exceptions.InvalidURL('The contest "%s" is not supported' % args.url)
    is_default_format = args.format is None and args.directory is None  # must be here since args.directory and args.format are overwritten
    if args.directory is None:
        args.directory = pathlib.Path('test')
    if args.format is None:
        args.format = '%b.%e'

    # get samples from the server
    with utils.with_cookiejar(utils.new_session_with_our_user_agent(), path=args.cookie) as sess:
        if args.yukicoder_token and isinstance(problem, YukicoderProblem):
            sess.headers['Authorization'] = 'Bearer {}'.format(args.yukicoder_token)
        if args.system:
            samples = problem.download_system_cases(session=sess)
        else:
            samples = problem.download_sample_cases(session=sess)

    if not samples:
        raise onlinejudge.type.SampleParseError("Sample not found")

    # append the history for submit command
    if not args.dry_run and is_default_format:
        history = onlinejudge._implementation.download_history.DownloadHistory()
        history.add(problem)

    # prepare files to write
    def iterate_files_to_write(sample: onlinejudge.type.TestCase, *, i: int) -> Iterator[Tuple[str, pathlib.Path, bytes]]:
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
            path = args.directory / format_utils.percentformat(args.format, table)  # type: pathlib.Path
            yield ext, path, data

    for i, sample in enumerate(samples):
        for _, path, _ in iterate_files_to_write(sample, i=i):
            if path.exists():
                raise FileExistsError('Failed to download since file already exists: ' + str(path))

    # write samples to files
    for i, sample in enumerate(samples):
        log.emit('')
        log.info('sample %d', i)
        for ext, path, data in iterate_files_to_write(sample, i=i):
            log.status('%sput: %s', ext, sample.name)
            if not args.silent:
                log.emit(utils.make_pretty_large_file_content(data, limit=40, head=20, tail=10, bold=True))
            if not args.dry_run:
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open('wb') as fh:
                    fh.write(data)
                log.success('saved to: %s', path)

    # print json
    if args.json:
        print(json.dumps(list(map(convert_sample_to_dict, samples))))
