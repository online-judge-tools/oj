#!/usr/bin/env python3
import onlinejudge
import onlinejudge.atcoder
import onlinejudge.yukicoder
import onlinejudge.anarchygolf
import onlinejudge.implementation.utils as utils
from onlinejudge.logging import logger, prefix
import argparse
import sys
import os
import os.path
import getpass
import re
import colorama

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

def get_problem(s):
    problem = onlinejudge.problem.from_url(s)
    if problem:
        logger.info(prefix['success'] + 'problem recognized: %s', str(problem))
        return problem
    else:
        logger.info(prefix['error'] + 'unknown problem: %s', s)
        sys.exit(1)

def download(args):
    problem = get_problem(args.url)
    kwargs = {}
    if problem.service_name == 'yukicoder':
        for x in args.extra_option:
            if x == 'all':
                kwargs['is_all'] = True
    if args.format is None:
        if problem.service_name == 'yukicoder' and kwargs.get('is_all'):
            args.format = 'test/%b.%e'
        else:
            args.format = 'test/sample-%i.%e'
    with utils.session(cookiejar=args.cookie) as sess:
        samples = problem.download(session=sess, **kwargs)
    for i, sample in enumerate(samples):
        logger.info('')
        logger.info(prefix['info'] + 'sample %d', i)
        for ext, (s, name) in zip(['in', 'out'], sample):
            table = {}
            table['i'] = str(i+1)
            table['e'] = ext
            table['n'] = name
            table['b'] = os.path.basename(name)
            table['d'] = os.path.dirname(name)
            path = parcentformat(args.format, table)
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

def login(args):
    problem = get_problem(args.url)
    kwargs = {}
    if problem.service_name == 'yukicoder':
        method = ''
        for x in args.extra_option:
            if x.startswith('method='):
                method += x[ len('method=') : ]
        if method not in [ 'github', 'twitter' ]:
            logger.error(prefix['failure'] + 'login for yukicoder: one of following options required: -x method=github, -x method=twitter')
            sys.exit(1)
        kwargs['method'] = method
    def get_credentials():
        if args.username is None:
            args.username = input('Username: ')
        if args.password is None:
            args.password = getpass.getpass()
        return args.username, args.password
    with utils.session(cookiejar=args.cookie) as sess:
        problem.login(sess, get_credentials, **kwargs)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-c', '--cookie', default=os.path.join(default_data_dir, 'cookie.jar'))
    parser.add_argument('-x', '--extra-option', action='append', default=[])
    subparsers = parser.add_subparsers(dest='command')

    # download
    subparser = subparsers.add_parser('download')
    subparser.add_argument('url')
    subparser.add_argument('-f', '--format')
    subparser.add_argument('--overwrite', action='store_true')
    # login
    subparser = subparsers.add_parser('login')
    subparser.add_argument('url')
    subparser.add_argument('-u', '--username')
    subparser.add_argument('-p', '--password')
    # submit
    subparser = subparsers.add_parser('submit')
    subparser.add_argument('url')
    # test
    subparser = subparsers.add_parser('test')

    args = parser.parse_args()
    if args.command == 'download':
        download(args)
    elif args.command == 'login':
        login(args)
    elif args.command == 'submit':
        raise NotImplementedError
    elif args.command == 'test':
        raise NotImplementedError
    else:
        assert False

if __name__ == '__main__':
    main()
