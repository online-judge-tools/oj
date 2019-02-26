# Python Version: 3.x
import json
import sys
from typing import *

import onlinejudge
import onlinejudge._implementation.logging as log
import onlinejudge._implementation.utils as utils

if TYPE_CHECKING:
    import argparse


def get_standings(args: 'argparse.Namespace') -> None:
    # parse url
    problem = onlinejudge.dispatch.problem_from_url(args.url)
    if problem is None:
        sys.exit(1)

    # get standings
    header, rows = problem.get_standings()  # type: ignore

    # print it
    if args.format in ['csv', 'tsv']:
        sep = {'csv': ',', 'tsv': '\t'}[args.format]
        print(*header, sep=sep)
        for row in rows:
            print(*[row[col] if row[col] is not None else '' for col in header], sep=sep)
    elif args.format == 'json':
        print(json.dumps(rows))
    else:
        assert False
