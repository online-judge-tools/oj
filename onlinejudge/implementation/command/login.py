#!/usr/bin/env python3
import onlinejudge
import onlinejudge.implementation.utils as utils
import onlinejudge.implementation.logging as log
import sys
import getpass

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
