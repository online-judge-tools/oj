import argparse
import pathlib
import sys
import traceback
from logging import DEBUG, INFO, StreamHandler, basicConfig, getLogger
from typing import *

import onlinejudge.__about__ as api_version
import onlinejudge_command.__0_workaround_for_conflict  # pylint: disable=unused-import
import onlinejudge_command.__about__ as version
import onlinejudge_command.log_formatter as log_formatter
import onlinejudge_command.subcommand.download as subcommand_download
import onlinejudge_command.subcommand.generate_input as subcommand_generate_input
import onlinejudge_command.subcommand.generate_output as subcommand_generate_output
import onlinejudge_command.subcommand.login as subcommand_login
import onlinejudge_command.subcommand.submit as subcommand_submit
import onlinejudge_command.subcommand.test as subcommand_test
import onlinejudge_command.subcommand.test_reactive as subcommand_test_reactive
import onlinejudge_command.update_checking as update_checking
import onlinejudge_command.utils as utils

logger = getLogger(__name__)


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Tools for online judge services',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
tips:
  The official tutorial exists on the web: https://github.com/online-judge-tools/oj/blob/master/docs/getting-started.md
''',
    )
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-c', '--cookie', type=pathlib.Path, default=utils.default_cookie_path, help='path to cookie. (default: {})'.format(utils.default_cookie_path))
    parser.add_argument('--version', action='store_true', help='print the online-judge-tools version number')

    subparsers = parser.add_subparsers(dest='subcommand', help='for details, see "{} COMMAND --help"'.format(sys.argv[0]))
    subcommand_download.add_subparser(subparsers)
    subcommand_login.add_subparser(subparsers)
    subcommand_submit.add_subparser(subparsers)
    subcommand_test.add_subparser(subparsers)
    subcommand_generate_output.add_subparser(subparsers)
    subcommand_generate_input.add_subparser(subparsers)
    subcommand_test_reactive.add_subparser(subparsers)

    return parser


def run_program(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    if args.version:
        print('online-judge-tools {} (+ online-judge-api-client {})'.format(version.__version__, api_version.__version__))
        return 0
    logger.debug('args: %s', str(args))

    # print the version to use for user-supporting
    logger.info('online-judge-tools %s (+ online-judge-api-client %s)', version.__version__, api_version.__version__)

    # TODO: make functions for subcommand take a named tuple instead of the raw result of argparse. Using named tuples make code well-typed.
    if args.subcommand in ['download', 'd', 'dl']:
        if not subcommand_download.run(args):
            return 1
    elif args.subcommand in ['login', 'l']:
        if not subcommand_login.run(args):
            return 1
    elif args.subcommand in ['submit', 's']:
        if not subcommand_submit.run(args):
            return 1
    elif args.subcommand in ['test', 't']:
        if not subcommand_test.run(args):
            return 1
    elif args.subcommand in ['test-reactive', 't/r']:
        if not subcommand_test_reactive.run(args):
            return 1
    elif args.subcommand in ['generate-output', 'g/o']:
        subcommand_generate_output.run(args)
    elif args.subcommand in ['generate-input', 'g/i']:
        subcommand_generate_input.run(args)
    else:
        parser.print_help(file=sys.stderr)
        return 1
    return 0


def main(args: Optional[List[str]] = None) -> 'NoReturn':
    parser = get_parser()
    parsed = parser.parse_args(args=args)

    # configure the logger
    level = INFO
    if parsed.verbose:
        level = DEBUG
    handler = StreamHandler(sys.stdout)
    handler.setFormatter(log_formatter.LogFormatter())
    basicConfig(level=level, handlers=[handler])

    # check update
    is_updated = update_checking.run()

    try:
        sys.exit(run_program(parsed, parser=parser))
    except NotImplementedError as e:
        logger.debug('\n' + traceback.format_exc())
        logger.error('NotImplementedError')
        logger.info('The operation you specified is not supported yet. Pull requests are welcome.')
        logger.info('see: https://github.com/online-judge-tools/oj')
        if not is_updated:
            logger.info(utils.HINT + 'try updating the version of online-judge-tools: $ pip3 install -U online-judge-tools online-judge-api-client')
        sys.exit(1)
    except Exception as e:
        logger.debug('\n' + traceback.format_exc())
        logger.exception(str(e))
        if not is_updated:
            logger.info(utils.HINT + 'try updating the version of online-judge-tools: $ pip3 install -U online-judge-tools online-judge-api-client')
        sys.exit(1)


if __name__ == '__main__':
    main()
