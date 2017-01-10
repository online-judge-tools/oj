#!/usr/bin/env python3
import onlinejudge.atcoder
import onlinejudge.yukicoder
import onlinejudge.anarchygolf
import onlinejudge.codeforces
import onlinejudge.dispatch
import onlinejudge.implementation.utils as utils
import onlinejudge.implementation.logging as log
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

def download(args):
    problem = onlinejudge.dispatch.problem_from_url(args.url)
    if problem is None:
        sys.exit(1)
    kwargs = {}
    if problem.get_service().get_name() == 'yukicoder':
        for x in args.extra_option:
            if x == 'all':
                kwargs['is_all'] = True
    if args.format is None:
        if problem.get_service().get_name() == 'yukicoder' and kwargs.get('is_all'):
            args.format = 'test/%b.%e'
        else:
            args.format = 'test/sample-%i.%e'
    with utils.session(cookiejar=args.cookie) as sess:
        samples = problem.download(session=sess, **kwargs)
    for i, sample in enumerate(samples):
        log.emit('')
        log.info('sample %d', i)
        for ext, (s, name) in zip(['in', 'out'], sample):
            table = {}
            table['i'] = str(i+1)
            table['e'] = ext
            table['n'] = name
            table['b'] = os.path.basename(name)
            table['d'] = os.path.dirname(name)
            path = parcentformat(args.format, table)
            log.status('%sput: %s', ext, name)
            log.emit(colorama.Style.BRIGHT + s.rstrip() + colorama.Style.RESET_ALL)
            if os.path.exists(path):
                log.warning('file already exists: %s', path)
                if not args.overwrite:
                    log.warning('skipped')
                    continue
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as fh:
                fh.write(s)
            log.success('saved to: %s', path)

def login(args):
    service = onlinejudge.dispatch.service_from_url(args.url)
    if service is None:
        sys.exit(1)
    kwargs = {}
    if service.get_name() == 'yukicoder':
        method = ''
        for x in args.extra_option:
            if x.startswith('method='):
                method += x[ len('method=') : ]
        if method not in [ 'github', 'twitter' ]:
            log.failure('login for yukicoder: one of following options required: -x method=github, -x method=twitter')
            sys.exit(1)
        kwargs['method'] = method
    def get_credentials():
        if args.username is None:
            args.username = input('Username: ')
        if args.password is None:
            args.password = getpass.getpass()
        return args.username, args.password
    with utils.session(cookiejar=args.cookie) as sess:
        service.login(get_credentials, session=sess, **kwargs)

def submit(args):
    problem = onlinejudge.dispatch.problem_from_url(args.url)
    if problem is None:
        sys.exit(1)
    if args.language not in problem.get_languages():
        log.error('language is unknown')
        log.info('supported languages are:')
        for lang in problem.get_languages():
            log.emit('%s (%s)', lang, problem.get_language_description(lang))
        sys.exit(1)
    with open(args.file) as fh:
        code = fh.buffer.read()
    try:
        s = code.decode()
    except UnicodeDecodeError as e:
        log.failure('%s: %s', e.__class__.__name__, str(e))
        s = repr(code)[ 1 : ]
    log.info('code:\n%s', s)
    with utils.session(cookiejar=args.cookie) as sess:
        problem.submit(code, language=args.language, session=sess)

def main():
    # argparse
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
    subparser.add_argument('file')
    subparser.add_argument('-l', '--language')
    # test
    subparser = subparsers.add_parser('test')

    args = parser.parse_args()

    # logging
    log_level = log.logging.INFO
    if args.verbose:
        log_level = log.logging.DEBUG
    log.setLevel(log_level)
    handler = log.logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    log.addHandler(handler)

    if args.command == 'download':
        download(args)
    elif args.command == 'login':
        login(args)
    elif args.command == 'submit':
        submit(args)
    elif args.command == 'test':
        raise NotImplementedError
    else:
        assert False

if __name__ == '__main__':
    main()
