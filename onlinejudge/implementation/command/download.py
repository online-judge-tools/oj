# Python Version: 3.x
import datetime
import json
import os
import pathlib
import random
import sys
from typing import *

import colorama

import onlinejudge
import onlinejudge.implementation.download_history
import onlinejudge.implementation.logging as log
import onlinejudge.implementation.utils as utils
import onlinejudge.type

if TYPE_CHECKING:
    import argparse


def convert_sample_to_dict(sample: onlinejudge.type.TestCase) -> dict:
    data = {}
    data["input"] = sample.input.data
    data["output"] = sample.output.data
    if sample.input.name == sample.output.name:
        data["name"] = sample.input.name
    return data


def download(args: 'argparse.Namespace') -> None:
    # prepare values
    problem = onlinejudge.dispatch.problem_from_url(args.url)
    if problem is None:
        sys.exit(1)
    is_default_format = args.format is None and args.directory is None  # must be here since args.directory and args.format are overwritten
    if args.directory is None:
        args.directory = pathlib.Path('test')
    if args.format is None:
        if args.system:
            if problem.get_service().get_name() == 'yukicoder':
                args.format = '%b.%e'
            else:
                args.format = '%i.%e'
        else:
            args.format = 'sample-%i.%e'

    # get samples from the server
    with utils.with_cookiejar(utils.new_default_session(), path=args.cookie) as sess:
        if args.system:
            samples = problem.download_system_cases(session=sess)  # type: ignore
        else:
            samples = problem.download_sample_cases(session=sess)  # type: ignore

    # append the history for submit command
    if not args.dry_run and is_default_format:
        history = onlinejudge.implementation.download_history.DownloadHistory()
        history.add(problem)

    # write samples to files
    for i, sample in enumerate(samples):
        log.emit('')
        log.info('sample %d', i)
        for kind in ['input', 'output']:
            ext = kind[:-3]
            data = getattr(sample, kind).data
            name = getattr(sample, kind).name
            table = {}
            table['i'] = str(i + 1)
            table['e'] = ext
            table['n'] = name
            table['b'] = os.path.basename(name)
            table['d'] = os.path.dirname(name)
            path = args.directory / utils.percentformat(args.format, table)  # type: pathlib.Path
            log.status('%sput: %s', ext, name)
            if not args.silent:
                log.emit(utils.snip_large_file_content(data.rstrip(), limit=40, head=20, tail=10, bold=True))
            if args.dry_run:
                continue
            if path.exists():
                log.warning('file already exists: %s', path)
                if not args.overwrite:
                    log.warning('skipped')
                    continue
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('w') as fh:
                fh.write(data)
            log.success('saved to: %s', path)

    # print json
    if args.json:
        print(json.dumps(list(map(convert_sample_to_dict, samples))))
