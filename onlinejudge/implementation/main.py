# Python Version: 3.x
# -*- coding: utf-8 -*-
import onlinejudge
import onlinejudge.__about__ as version
import onlinejudge.implementation.utils as utils
import onlinejudge.implementation.logging as log
from onlinejudge.implementation.command.download import download
from onlinejudge.implementation.command.login import login
from onlinejudge.implementation.command.submit import submit
from onlinejudge.implementation.command.generate_scanner import generate_scanner
from onlinejudge.implementation.command.test import test
from onlinejudge.implementation.command.generate_output import generate_output
from onlinejudge.implementation.command.split_input import split_input, split_input_auto_footer
from onlinejudge.implementation.command.test_reactive import test_reactive
from onlinejudge.implementation.command.code_statistics import code_statistics
from onlinejudge.implementation.command.get_standings import get_standings
import argparse
import sys
import os
import os.path
import pathlib
from typing import List, Optional


def version_check() -> None:
    if utils.is_update_available_on_pypi():
        log.warning('update available: %s -> %s', version.__version__, utils.get_latest_version_from_pypi())
        log.info('run: $ pip3 install -U %s', version.__package_name__)


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Tools for online judge services')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-c', '--cookie',
            type=pathlib.Path,
            default=utils.default_cookie_path,
            help='path to cookie. (default: {})'.format(utils.default_cookie_path))
    subparsers = parser.add_subparsers(dest='subcommand', help='for details, see "{} COMMAND --help"'.format(sys.argv[0]))

    # download
    subparser = subparsers.add_parser('download',
            aliases=[ 'd', 'dl' ],
            help='download sample cases',
            formatter_class=argparse.RawTextHelpFormatter,
            epilog='''\
supported services:
  Anarchy Golf
  Aizu Online Judge
  AtCoder
  Codeforces
  Yukicoder
  CS Academy

  (HackerRank has been removed)

supported services with --system:
  Aizu Online Judge
  Yukicoder

format string for --format:
  %i                    index: 1, 2, 3, ...
  %e                    extension: "in" or "out"
  %n                    name: e.g. "Sample Input 1", "system_test3.txt", ...
  %b                    os.path.basename(name)
  %d                    os.path.dirname(name)
  %%                    '%' itself
''')
    subparser.add_argument('url')
    subparser.add_argument('-f', '--format', help='a format string to specify paths of cases (defaut: "sample-%%i.%%e" if not --system)')  # default must be None for --system
    subparser.add_argument('-d', '--directory', type=pathlib.Path, default=pathlib.Path('test'), help='a directory name for test cases (default: test/)')
    subparser.add_argument('--overwrite', action='store_true')
    subparser.add_argument('-n', '--dry-run', action='store_true', help='don\'t write to files')
    subparser.add_argument('-a', '--system', action='store_true', help='download system testcases')
    subparser.add_argument('--json', action='store_true')

    # login
    subparser = subparsers.add_parser('login',
            aliases=[ 'l' ],
            help='login to a service',
            formatter_class=argparse.RawTextHelpFormatter,
            epilog='''\
supported services:
  AtCoder
  Codeforces
  Yukicoder
  TopCoder

  (HackerRank has been removed)

strings for --method:
  github                for yukicoder, login via github (default)
  twitter               for yukicoder, login via twitter (not implementated yet)
''')
    subparser.add_argument('url')
    subparser.add_argument('-u', '--username')
    subparser.add_argument('-p', '--password')
    subparser.add_argument('--method')

    # submit
    subparser = subparsers.add_parser('submit',
            aliases=[ 's' ],
            help='submit your solution',
            formatter_class=argparse.RawTextHelpFormatter,
            epilog='''\
supported services:
  AtCoder
  Yukicoder
  TopCoder (Marathon Match)
''')
    subparser.add_argument('url')
    subparser.add_argument('file', type=pathlib.Path)
    subparser.add_argument('-l', '--language', help='narrow down language choices if ambiguous')
    subparser.add_argument('--no-guess', action='store_false', dest='guess')
    subparser.add_argument('-g', '--guess', action='store_true', help='guess the language for your file (default)')
    subparser.add_argument('--no-guess-latest', action='store_false', dest='guess_cxx_latest')
    subparser.add_argument('--guess-cxx-latest', action='store_true', help='use the lasest version for C++ (default)')
    subparser.add_argument('--guess-cxx-compiler', choices=( 'gcc', 'clang', 'all' ), default='gcc', help='use the specified C++ compiler if both of GCC and Clang are available (default: gcc)')
    subparser.add_argument('--guess-python-version', choices=( '2', '3', 'auto', 'all' ), default='auto', help='shebang or modelines are used by default. write something like "#!/usr/bin/env python3". (default: auto)')
    subparser.add_argument('--guess-python-interpreter', choices=( 'cpython', 'pypy', 'all' ), default='cpython', help='use the specified Python interpreter if both of CPython and PyPy are available (default: cpython)')
    subparser.add_argument('--format-dos2unix', action='store_true', help='replace CRLF with LF for given file')
    subparser.add_argument('--format-rstrip', action='store_true', help='remove trailing newlines from given file')
    subparser.add_argument('-G', '--golf', action='store_true', help='now equivalent to --format-dos2unix --format-rstrip')
    subparser.add_argument('--no-open', action='store_false', dest='open')
    subparser.add_argument('--open', action='store_true', default=True, help='open the result page after submission (default)')
    subparser.add_argument('--open-browser')
    subparser.add_argument('-w', '--wait', metavar='SECOND', type=float, default=3, help='sleep before submitting')
    subparser.add_argument('-y', '--yes', action='store_true', help='don\'t confirm')
    subparser.add_argument('--full-submission', action='store_true', help='for TopCoder Marathon Match. use this to do "Submit", the default behavier is "Test Examples".')

    # test
    subparser = subparsers.add_parser('test',
            aliases=[ 't' ],
            help='test your code',
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
    subparser.add_argument('-f', '--format', default='%s.%e', help='a format string to recognize the relationship of test cases. (default: "%%s.%%e")')
    subparser.add_argument('-d', '--directory', type=pathlib.Path, default=pathlib.Path('test'), help='a directory name for test cases (default: test/)')
    subparser.add_argument('-m', '--mode', choices=[ 'all', 'line' ], default='all', help='mode to check an output with the correct answer. (default: all)')
    subparser.add_argument('-1', '--line', dest='mode', action='store_const', const='line', help='equivalent to --mode line')
    subparser.add_argument('--no-rstrip', action='store_false', dest='rstrip')
    subparser.add_argument('--rstrip', action='store_true', help='rstrip output before compare (default)')
    subparser.add_argument('-s', '--silent', action='store_true', help='don\'t report output and correct answer even if not AC  (for --mode all)')
    subparser.add_argument('-e', '--error', type=float, help='check as floating point number: correct if its absolute or relative error doesn\'t exceed it')
    subparser.add_argument('-t', '--tle', type=float)
    subparser.add_argument('-i', '--print-input', action='store_true', help='print input cases if not AC')
    subparser.add_argument('--no-ignore-backup', action='store_false', dest='ignore_backup')
    subparser.add_argument('--ignore-backup', action='store_true', help='ignore backup files and hidden files (i.e. files like "*~", "\\#*\\#" and ".*") (default)')
    subparser.add_argument('test', nargs='*', type=pathlib.Path, help='paths of test cases. (if empty: globbed from --format)')

    # generate scanner
    subparser = subparsers.add_parser('generate-scanner',
            aliases=[ 'g/s' ],
            help='generate input scanner  (experimental)',
            formatter_class=argparse.RawTextHelpFormatter,
            epilog='''\
supported services:
  AtCoder

  (Yukicoder has been removed)
  (HackerRank has been removed)

example:
  http://agc001.contest.atcoder.jp/tasks/agc001_a
  input format:
    N
    L_1 L_2 \dots L_{2N}
  generated code:
    int N; cin >> N;
    vector<int> L(2*N); REPEAT (i,2*N) cin >> L[i];

tips:
  in Vim, the command "r! oj g/s -s http://agc001.contest.atcoder.jp/tasks/agc001_a" inserts above generated code.
  in Emacs, the command "C-u M-! oj g/s -s http://agc001.contest.atcoder.jp/tasks/agc001_a" does.
  I recommend that map it to some command, like "nnoremap <space>gs :r! oj generate-scanner --silent --repeat-macro=repeat ",
               and use some plugin for templates, e.g. https://github.com/thinca/vim-template.
''')
    subparser.add_argument('--repeat-macro', help='use repeat macro with given name')
    subparser.add_argument('--scanf', action='store_true', help='use scanf instead of cin')
    subparser.add_argument('-s', '--silent', action='store_true')
    subparser.add_argument('url')

    # generate output
    subparser = subparsers.add_parser('generate-output',
            aliases=[ 'g/o' ],
            help='generate output files form input and reference implementation',
            formatter_class=argparse.RawTextHelpFormatter,
            epilog='''\
format string for --format:
  %s                    name
  %e                    extension: "in" or "out"
  (both %s and %e are required.)

tips:
  You can do similar things with shell: e.g. `for f in test/*.in ; do ./a.out < $f > ${f/.in/.out} ; done`
''')
    subparser.add_argument('-c', '--command', default='./a.out', help='your solution to be tested. (default: "./a.out")')
    subparser.add_argument('-f', '--format', default='%s.%e', help='a format string to recognize the relationship of test cases. (default: "%%s.%%e")')
    subparser.add_argument('-d', '--directory', type=pathlib.Path, default=pathlib.Path('test'), help='a directory name for test cases (default: test/)')
    subparser.add_argument('test', nargs='*', type=pathlib.Path, help='paths of input cases. (if empty: globbed from --format)')
    subparser.add_argument('--no-ignore-backup', action='store_false', dest='ignore_backup')
    subparser.add_argument('--ignore-backup', action='store_true', help='ignore backup files and hidden files (i.e. files like "*~", "\\#*\\#" and ".*") (default)')

    # split input
    subparser = subparsers.add_parser('split-input',
            aliases=[ 's/i' ],
            help='split a input file which contains many cases, using your implementation',
            formatter_class=argparse.RawTextHelpFormatter,
            epilog='''\
format string for --output:
  %i                    index

command for --command:
  Specify a command which outputs something after reading each case.
  It can be easily made from your solution for the problem.
  example:
    #include <iostream>
    using namespace std;
    int main() {
        while (true) {
            int v, e; cin >> v >> e;
            if (v == 0 and e == 0) break;
            for (int i = 0; i < e; ++ i) {
                int v, w; char c; cin >> v >> w >> c;
            }
            cout << "foo" << endl;
        }
        return 0;
    }

example:
  if original input is below, it consists of two cases:
    4 2
    0 1 A
    1 2 B
    6 6
    0 1 A
    0 2 A
    0 3 B
    0 4 A
    1 2 B
    4 5 C
    0 0
  then the result with appropriate options:
    4 2
    0 1 A
    1 2 B
    0 0
  ans
    6 6
    0 1 A
    0 2 A
    0 3 B
    0 4 A
    1 2 B
    4 5 C
    0 0
''')
    subparser.add_argument('-c', '--command', default='./a.out', help='your solution to be tested. (default: "./a.out")')
    subparser.add_argument('-i', '--input',  metavar='PATH', required=True, help='input file  (required)')
    subparser.add_argument('-o', '--output', metavar='FORMAT', required=True, help='output path  (required)')
    subparser.add_argument('-t', '--time', metavar='SECOND', default=0.1, type=float, help='the interval between two cases')
    subparser.add_argument('--ignore', metavar='N', default=0, type=int, help='ignore initial N lines of input')
    subparser.add_argument('--header', help='put a header string to the output')
    subparser.add_argument('--footer', help='put a footer string to the output')
    subparser.add_argument('--auto-footer', action='store_const', const=split_input_auto_footer, dest='footer', help='use the original last line as a footer')

    # test reactive
    subparser = subparsers.add_parser('test-reactive',
            aliases=[ 't/r' ],
            help='test for reactive problem',
            formatter_class=argparse.RawTextHelpFormatter,
            epilog='''\
''')
    subparser.add_argument('-c', '--command', default='./a.out', help='your solution to be tested. (default: "./a.out")')
    subparser.add_argument('judge', help='judge program using standard I/O')

    # code statistics
    subparser = subparsers.add_parser('code-statistics',
            aliases=[ 'c/s' ],
            help='print the code statistics used in Anarchy Golf',
            formatter_class=argparse.RawTextHelpFormatter,
            epilog='''\
''')
    subparser.add_argument('file')

    # get standings
    subparser = subparsers.add_parser('get-standings',
            help='get and print the standings',
            formatter_class=argparse.RawTextHelpFormatter,
            epilog='''\
supported services:
  TopCoder (Marathon Match)
''')
    subparser.add_argument('url')
    subparser.add_argument('-f', '--format', choices=[ 'csv', 'tsv', 'json' ], default='tsv', help='default: tsv')

    return parser


def run_program(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    if args.verbose:
        log.setLevel(log.logging.DEBUG)
    log.debug('args: %s', str(args))

    if args.subcommand in [ 'download', 'd', 'dl' ]:
        download(args)
    elif args.subcommand in [ 'login', 'l' ]:
        login(args)
    elif args.subcommand in [ 'submit', 's' ]:
        submit(args)
    elif args.subcommand in [ 'test', 't' ]:
        test(args)
    elif args.subcommand in [ 'test-reactive', 't/r' ]:
        test_reactive(args)
    elif args.subcommand in [ 'generate-scanner', 'g/s' ]:
        generate_scanner(args)
    elif args.subcommand in [ 'generate-output', 'g/o' ]:
        generate_output(args)
    elif args.subcommand in [ 'split-input', 's/i' ]:
        split_input(args)
    elif args.subcommand in [ 'code-statistics', 'c/s' ]:
        code_statistics(args)
    elif args.subcommand == 'get-standings':
        get_standings(args)
    else:
        parser.print_help(file=sys.stderr)
        sys.exit(1)


def main(args: Optional[List[str]] = None) -> None:
    log.addHandler(log.logging.StreamHandler(sys.stderr))
    log.setLevel(log.logging.INFO)
    version_check()
    parser = get_parser()
    namespace = parser.parse_args(args=args)
    run_program(namespace, parser=parser)
