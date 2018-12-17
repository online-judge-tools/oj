# Python Version: 3.x
import onlinejudge
import onlinejudge.problem
import onlinejudge.implementation.utils as utils
import onlinejudge.implementation.logging as log
import os
import colorama
import sys
import json
from typing import *
if TYPE_CHECKING:
    import argparse

def convert_sample_to_dict(sample: onlinejudge.problem.TestCase) -> dict:
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
    kwargs = {}
    if args.system:
        supported_service_names = [ 'aoj', 'yukicoder' ]
        if problem.get_service().get_name() not in supported_service_names:
            log.error('--system for %s is not supported', problem.get_service().get_name())
            sys.exit(1)
        kwargs['is_system'] = True
    if args.format is None:
        if kwargs.get('is_system'):
            if problem.get_service().get_name() == 'yukicoder':
                args.format = '%b.%e'
            else:
                args.format = '%i.%e'
        else:
            args.format = 'sample-%i.%e'

    # get samples from the server
    with utils.with_cookiejar(utils.new_default_session(), path=args.cookie) as sess:
        samples = problem.download(session=sess, **kwargs)  # type: ignore

    # write samples to files
    for i, sample in enumerate(samples):
        log.emit('')
        log.info('sample %d', i)
        for kind in [ 'input', 'output' ]:
            ext = kind[: -3]
            data = getattr(sample, kind).data
            name = getattr(sample, kind).name
            table = {}
            table['i'] = str(i+1)
            table['e'] = ext
            table['n'] = name
            table['b'] = os.path.basename(name)
            table['d'] = os.path.dirname(name)
            path = os.path.join(args.directory, utils.parcentformat(args.format, table))
            log.status('%sput: %s', ext, name)
            log.emit(colorama.Style.BRIGHT + data.rstrip() + colorama.Style.RESET_ALL)
            if args.dry_run:
                continue
            if os.path.exists(path):
                log.warning('file already exists: %s', path)
                if not args.overwrite:
                    log.warning('skipped')
                    continue
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as fh:
                fh.write(data)
            log.success('saved to: %s', path)

    # print json
    if args.json:
        print(json.dumps(list(map(convert_sample_to_dict, samples))))
