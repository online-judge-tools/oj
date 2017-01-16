#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import onlinejudge
import onlinejudge.implementation.utils as utils
import onlinejudge.implementation.logging as log
from onlinejudge.implementation.cmd_generate_scanner import generate_scanner
from onlinejudge.implementation.cmd_test import test, generate_output
import argparse
import sys
import os
import os.path
import re
import glob
import getpass
import colorama
import collections
import subprocess
import time

default_data_dir = os.path.join(os.environ.get('XDG_DATA_HOME') or os.path.expanduser('~/.local/share'), 'onlinejudge')
default_url_open = 'xdg-open'

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
            path = utils.parcentformat(args.format, table)
            log.status('%sput: %s', ext, name)
            log.emit(colorama.Style.BRIGHT + s.rstrip() + colorama.Style.RESET_ALL)
            if not path: # doesn't save if --format ''
                continue
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
    # code
    with open(args.file) as fh:
        code = fh.buffer.read()
    try:
        s = code.decode() # for logging
    except UnicodeDecodeError as e:
        log.failure('%s: %s', e.__class__.__name__, str(e))
        s = repr(code)[ 1 : ]
    log.info('code:')
    log.emit(log.bold(s))
    # session
    with utils.session(cookiejar=args.cookie) as sess:
        # language
        langs = problem.get_language_dict(session=sess)
        if args.language not in langs:
            log.error('language is unknown')
            log.info('supported languages are:')
            for lang in sorted(langs.keys()):
                log.emit('%s (%s)', lang, langs[lang]['description'])
            sys.exit(1)
        # submit
        url = problem.submit(code, language=args.language, session=sess)
        if url and args.open:
            log.info('open the submission page')
            subprocess.check_call([ args.open, url ], stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)


def main(args=None):

    # argparse
    parser = argparse.ArgumentParser(description='Tools for online judge services')
    parser.add_argument('-v', '--verbose', action='store_true')
    default_cookie_path = os.path.join(default_data_dir, 'cookie.jar')
    parser.add_argument('-c', '--cookie', default=default_cookie_path,
            help='path for cookie. (default: {})'.format(default_cookie_path))
    parser.add_argument('-x', '--extra-option', action='append', default=[])
    subparsers = parser.add_subparsers(dest='subcommand', help='for details, see "{} COMMAND --help"'.format(sys.argv[0]))

    # download
    subparser = subparsers.add_parser('download', help='download sample cases',
            formatter_class=argparse.RawTextHelpFormatter,
            epilog='''\
supported services:
  Anarchy Golf
  Aizu Online Judge
  AtCoder
  Codeforces
  HackerRank
  Yukicoder

format string for --format:
  %i                    index: 1, 2, 3, ...
  %e                    extension: "in" or "out"
  %n                    name: e.g. "Sample Input 1", "system_test3.txt", ...
  %b                    os.path.basename(name)
  %d                    os.path.dirname(name)
  %%                    '%' itself

extra opitons via -x:
  -x all                for yukicoder, use "テストケース一括ダウンロード"
''')
    subparser.add_argument('url')
    subparser.add_argument('-f', '--format', help='a format string to specify paths of cases')
    subparser.add_argument('--overwrite', action='store_true')

    # login
    subparser = subparsers.add_parser('login', help='login to a service',
            formatter_class=argparse.RawTextHelpFormatter,
            epilog='''\
supported services:
  AtCoder
  Codeforces
  HackerRank
  Yukicoder

extra opitons via -x:
  -x method=github      for yukicoder, login via github
  -x method=twitter     for yukicoder, login via github (not implementated yet)
''')
    subparser.add_argument('url')
    subparser.add_argument('-u', '--username')
    subparser.add_argument('-p', '--password')

    # submit
    subparser = subparsers.add_parser('submit', help='submit your solution',
            formatter_class=argparse.RawTextHelpFormatter,
            epilog='''\
supported services:
  AtCoder
  Yukicoder
''')
    subparser.add_argument('url')
    subparser.add_argument('file')
    subparser.add_argument('-l', '--language')
    subparser.add_argument('--open', nargs='?', const=default_url_open, help='open the result page after submission')

    # test
    subparser = subparsers.add_parser('test', help='test your code',
            formatter_class=argparse.RawTextHelpFormatter,
            epilog='''\
format string for --format:
  %s                    name
  %e                    extension: "in" or "out"
  (both %s and %e are required.)

tips:
  You can do similar things with shell: e.g. `for f in test/*.in ; do echo $f ; diff <(./a.out < $f) ${f/.in/.out} ; done`
''')
    subparser.add_argument('-c', '--command', default='./a.out', help='your solution to be tested. (default: "./a.out")')
    subparser.add_argument('--shell', action='store_true', help='use the --command as a shellscript instead of a path')
    subparser.add_argument('-f', '--format', default='test/%s.%e', help='a format string to recognize the relationship of test cases. (default: "test/%%s.%%e")')
    subparser.add_argument('-m', '--mode', choices=[ 'all', 'line' ], default='all', help='mode to check an output with the correct answer. (default: all)')
    subparser.add_argument('-1', '--line', dest='mode', action='store_const', const='line', help='equivalent to --mode line')
    subparser.add_argument('--rstrip', action='store_true', help='rstrip output before comapre')
    subparser.add_argument('-s', '--silent', action='store_true', help='don\'t report output and correct answer even if not AC  (for --mode all)')
    subparser.add_argument('test', nargs='*', help='paths of test cases. (if empty: globbed from --format)')

    # generate scanner
    subparser = subparsers.add_parser('generate-scanner', help='generate input scanner  (experimental)',
            formatter_class=argparse.RawTextHelpFormatter,
            epilog='''\
supported services:
  AtCoder
  Yukicoder

example:
  http://agc001.contest.atcoder.jp/tasks/agc001_a
  input format:
    N
    L_1 L_2 \dots L_{2N}
  generated code:
    int N; cin >> N;
    vector<int> L(2*N); REPEAT (i,2*N) cin >> L[i];
''')
    subparser.add_argument('--repeat-macro', help='use repeat macro with given name')
    subparser.add_argument('--scanf', action='store_true', help='use scanf instead of cin')
    subparser.add_argument('url')

    # generate output
    subparser = subparsers.add_parser('generate-output', help='generate output files form input and reference implementation',
            formatter_class=argparse.RawTextHelpFormatter,
            epilog='''\
format string for --format:
  %s                    name
  %e                    extension: "in" or "out"
  (both %s and %e are required.)

tips:
  You can do similar things with shell: e.g. `for f in test/*.in ; do ./aout < $f > ${f/.in/.out} ; done`
''')
    subparser.add_argument('-c', '--command', default='./a.out', help='your solution to be tested. (default: "./a.out")')
    subparser.add_argument('--shell', action='store_true', help='use the --command as a shellscript instead of a path')
    subparser.add_argument('-f', '--format', default='test/%s.%e', help='a format string to recognize the relationship of test cases. (default: "test/%%s.%%e")')
    subparser.add_argument('test', nargs='*', help='paths of input cases. (if empty: globbed from --format)')

    args = parser.parse_args(args=args)

    # logging
    log_level = log.logging.INFO
    if args.verbose:
        log_level = log.logging.DEBUG
    log.setLevel(log_level)
    handler = log.logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    log.addHandler(handler)

    log.debug('args: %s', str(args))

    if args.subcommand == 'download':
        download(args)
    elif args.subcommand == 'login':
        login(args)
    elif args.subcommand == 'submit':
        submit(args)
    elif args.subcommand == 'test':
        test(args)
    elif args.subcommand == 'generate-scanner':
        generate_scanner(args)
    elif args.subcommand == 'generate-output':
        generate_output(args)
    else:
        parser.print_help(file=sys.stderr)
        sys.exit(1)
