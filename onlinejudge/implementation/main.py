# Python Version: 3.x
# -*- coding: utf-8 -*-
import onlinejudge
import onlinejudge.implementation.utils as utils
import onlinejudge.implementation.logging as log
from onlinejudge.implementation.command.download import download
from onlinejudge.implementation.command.login import login
from onlinejudge.implementation.command.submit import submit
from onlinejudge.implementation.command.generate_scanner import generate_scanner
from onlinejudge.implementation.command.test import test, generate_output
from onlinejudge.implementation.command.split_input import split_input, split_input_auto_footer
from onlinejudge.implementation.command.test_reactive import test_reactive
import argparse
import sys
import os
import os.path

default_data_dir = os.path.join(os.environ.get('XDG_DATA_HOME') or os.path.expanduser('~/.local/share'), 'onlinejudge')

def main(args=None):

    # argparse
    parser = argparse.ArgumentParser(description='Tools for online judge services')
    parser.add_argument('-v', '--verbose', action='store_true')
    default_cookie_path = os.path.join(default_data_dir, 'cookie.jar')
    parser.add_argument('-c', '--cookie', default=default_cookie_path,
            help='path for cookie. (default: {})'.format(default_cookie_path))
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
  HackerRank
  Yukicoder
  CS Academy

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
    subparser.add_argument('-f', '--format', help='a format string to specify paths of cases')
    subparser.add_argument('--overwrite', action='store_true')
    subparser.add_argument('-n', '--dry-run', action='store_true', help='don\'t write to files')
    subparser.add_argument('-a', '--system', action='store_true', help='download system testcases')

    # login
    subparser = subparsers.add_parser('login',
            aliases=[ 'l' ],
            help='login to a service',
            formatter_class=argparse.RawTextHelpFormatter,
            epilog='''\
supported services:
  AtCoder
  Codeforces
  HackerRank
  Yukicoder

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
''')
    subparser.add_argument('url')
    subparser.add_argument('file')
    subparser.add_argument('-l', '--language')
    subparser.add_argument('--open', nargs='?', const=True, help='open the result page after submission')
    subparser.add_argument('-w', '--wait', metavar='SECCOND', type=float, default=3, help='sleep before submitting')
    subparser.add_argument('-y', '--yes', action='store_true', help='don\'t confirm')

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
    subparser.add_argument('--shell', action='store_true', help='use the --command as a shellscript instead of a path')
    subparser.add_argument('-f', '--format', default='test/%s.%e', help='a format string to recognize the relationship of test cases. (default: "test/%%s.%%e")')
    subparser.add_argument('-m', '--mode', choices=[ 'all', 'line' ], default='all', help='mode to check an output with the correct answer. (default: all)')
    subparser.add_argument('-1', '--line', dest='mode', action='store_const', const='line', help='equivalent to --mode line')
    subparser.add_argument('--rstrip', action='store_true', help='rstrip output before comapre')
    subparser.add_argument('-s', '--silent', action='store_true', help='don\'t report output and correct answer even if not AC  (for --mode all)')
    subparser.add_argument('-e', '--error', type=float, help='check as floating point number: correct if its absolute or relative error doesn\'t exceed it')
    subparser.add_argument('-t', '--tle', type=float)
    subparser.add_argument('test', nargs='*', help='paths of test cases. (if empty: globbed from --format)')

    # generate scanner
    subparser = subparsers.add_parser('generate-scanner',
            aliases=[ 'g/s' ],
            help='generate input scanner  (experimental)',
            formatter_class=argparse.RawTextHelpFormatter,
            epilog='''\
supported services:
  AtCoder
  Yukicoder
  HackerRank

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
  You can do similar things with shell: e.g. `for f in test/*.in ; do ./aout < $f > ${f/.in/.out} ; done`
''')
    subparser.add_argument('-c', '--command', default='./a.out', help='your solution to be tested. (default: "./a.out")')
    subparser.add_argument('--shell', action='store_true', help='use the --command as a shellscript instead of a path')
    subparser.add_argument('-f', '--format', default='test/%s.%e', help='a format string to recognize the relationship of test cases. (default: "test/%%s.%%e")')
    subparser.add_argument('test', nargs='*', help='paths of input cases. (if empty: globbed from --format)')

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
  exampe:
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
    subparser.add_argument('--shell', action='store_true', help='use the --command as a shellscript instead of a path')
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
    subparser.add_argument('--shell', action='store_true', help='use the judge  and --command as a shellscript instead of a path')
    subparser.add_argument('judge', help='judge program using standard I/O')

    args = parser.parse_args(args=args)

    # logging
    log_level = log.logging.INFO
    if args.verbose:
        log_level = log.logging.DEBUG
    log.setLevel(log_level)
    handler = log.logging.StreamHandler(sys.stderr)
    handler.setLevel(log_level)
    log.addHandler(handler)

    log.debug('args: %s', str(args))

    if args.subcommand in [ 'download', 'd', 'dl' ]:
        download(args)
    elif args.subcommand in [ 'login', 'l' ]:
        login(args)
    elif args.subcommand in [ 'submit', 's' ]:
        submit(args)
    elif args.subcommand in [ 'test', 't' ]:
        test(args)
    elif args.subcommand in [ 'test-reactiv', 't/r' ]:
        test_reactive(args)
    elif args.subcommand in [ 'generate-scanner', 'g/s' ]:
        generate_scanner(args)
    elif args.subcommand in [ 'generate-output', 'g/o' ]:
        generate_output(args)
    elif args.subcommand in [ 'split-input', 's/i' ]:
        split_input(args)
    else:
        parser.print_help(file=sys.stderr)
        sys.exit(1)


