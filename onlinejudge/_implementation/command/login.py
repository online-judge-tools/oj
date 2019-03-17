# Python Version: 3.x
import getpass
import sys
from typing import *

import onlinejudge
import onlinejudge._implementation.logging as log
import onlinejudge._implementation.utils as utils

if TYPE_CHECKING:
    import argparse


def login(args: 'argparse.Namespace') -> None:
    # get service
    service = onlinejudge.dispatch.service_from_url(args.url)
    if service is None:
        sys.exit(1)

    # configure
    kwargs = {}
    if isinstance(service, onlinejudge.service.yukicoder.YukicoderService):
        if not args.method:
            args.method = 'github'
        if args.method not in ['github', 'twitter']:
            log.failure('login for yukicoder: invalid option: --method %s', args.method)
            sys.exit(1)
        kwargs['method'] = args.method
    else:
        if args.method:
            log.failure('login for %s: invalid option: --method %s', service.get_name(), args.method)
            sys.exit(1)

    with utils.with_cookiejar(utils.new_session_with_our_user_agent(), path=args.cookie) as sess:

        if args.check:
            if service.is_logged_in(session=sess):
                log.info('You have already signed in.')
            else:
                log.info('You are not signed in.')
                sys.exit(1)

        else:
            # login
            def get_credentials() -> Tuple[str, str]:
                if args.username is None:
                    args.username = input('Username: ')
                if args.password is None:
                    args.password = getpass.getpass()
                return args.username, args.password

            log.warning('If you don\'t want to give your password to this program, you can give only your session tokens.')
            log.info('see: https://github.com/kmyk/online-judge-tools/blob/master/LOGIN_WITH_COOKIES.md')

            try:
                service.login(get_credentials, session=sess, **kwargs)  # type: ignore
            except onlinejudge.type.LoginError:
                pass
