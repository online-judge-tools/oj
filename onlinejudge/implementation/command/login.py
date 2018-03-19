# Python Version: 3.x
import onlinejudge
import onlinejudge.implementation.utils as utils
import onlinejudge.implementation.logging as log
import sys
import getpass

def login(args):
    # get service
    service = onlinejudge.dispatch.service_from_url(args.url)
    if service is None:
        sys.exit(1)

    # configure
    kwargs = {}
    if service.get_name() == 'yukicoder':
        if not args.method:
            args.method = 'github'
        if args.method not in [ 'github', 'twitter' ]:
            log.failure('login for yukicoder: invalid option: --method %s', args.method)
            sys.exit(1)
        kwargs['method'] = args.method
    else:
        if args.method:
            log.failure('login for %s: invalid option: --method %s', service.get_name(), args.method)
            sys.exit(1)

    # login
    def get_credentials():
        if args.username is None:
            args.username = input('Username: ')
        if args.password is None:
            args.password = getpass.getpass()
        return args.username, args.password
    with utils.with_cookiejar(utils.new_default_session(), path=args.cookie) as sess:
        service.login(get_credentials, session=sess, **kwargs)
