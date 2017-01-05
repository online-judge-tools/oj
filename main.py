#!/usr/bin/env python3
import argparse
import os
import os.path
import re
import colorama
import onlinejudge
import onlinejudge.atcoder
import onlinejudge.yukicoder
from onlinejudge.logging import logger, prefix

default_data_dir = os.path.join(os.environ.get('XDG_DATA_HOME') or os.path.expanduser('~/local/share'), 'onlinejudge')

def parcentformat(s, table):
    assert '%' not in table or table['%'] == '%'
    table['%'] = '%'
    result = ''
    for m in re.finditer('[^%]|%(.)', s):
        if m.group(1):
            if m.group(1) in table:
                result += table[m.group(1)]
        else:
            result += m.group(0)
    return result

def download(args):
    problem = onlinejudge.problem.from_url(args.url)
    logger.info(prefix['success'] + 'problem recognized: %s', str(problem))
    samples = problem.download()
    for i, sample in enumerate(samples):
        logger.info('')
        logger.info(prefix['info'] + 'sample %d', i)
        for ext, (s, name) in zip(['in', 'out'], sample):
            path = parcentformat(args.format, { 'i': str(i+1), 'e': ext })
            logger.info(prefix['status'] + '%sput: %s', ext, name)
            logger.info(colorama.Style.BRIGHT + s.rstrip() + colorama.Style.RESET_ALL)
            if os.path.exists(path):
                logger.warning(prefix['warning'] + 'file already exists: %s', path)
                if not args.overwrite:
                    logger.warning(prefix['failure'] + 'skipped')
                    continue
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as fh:
                fh.write(s)
            logger.info(prefix['success'] + 'saved to: %s', path)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('--cookie', default=os.path.join(default_data_dir, 'cookie.jar'))
    subparsers = parser.add_subparsers(dest='command')
    # download
    subparser = subparsers.add_parser('download')
    subparser.add_argument('url')
    subparser.add_argument('-f', '--format', default='test/sample-%i.%e')
    subparser.add_argument('--overwrite', action='store_true')
    # submit
    subparser = subparsers.add_parser('submit')
    subparser.add_argument('url')
    # test
    subparser = subparsers.add_parser('test')

    args = parser.parse_args()
    if args.command == 'download':
        download(args)
    elif args.command == 'submit':
        it = onlinejudge.from_url(args.url)
    elif args.command == 'test':
        raise NotImplementedError

if __name__ == '__main__':
    main()
