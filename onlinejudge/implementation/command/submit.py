# Python Version: 3.x
import onlinejudge
import onlinejudge.implementation.utils as utils
import onlinejudge.implementation.logging as log
import sys
import time
import shutil
import subprocess

default_url_opener = [ 'sensible-browser', 'xdg-open', 'open' ]

def submit(args):
    # parse url
    problem = onlinejudge.dispatch.problem_from_url(args.url)
    if problem is None:
        sys.exit(1)

    # read code
    with open(args.file) as fh:
        code = fh.buffer.read()
    try:
        s = code.decode() # for logging
    except UnicodeDecodeError as e:
        log.failure('%s: %s', e.__class__.__name__, str(e))
        s = repr(code)[ 1 : ]
    log.info('code:')
    log.emit(log.bold(s))

    # prepare kwargs
    kwargs = {}
    if problem.get_service().get_name() == 'topcoder':
        if args.full_submission:
            kwargs['kind'] = 'full'
        else:
            kwargs['kind'] = 'example'

    with utils.with_cookiejar(utils.new_default_session(), path=args.cookie) as sess:
        # language
        langs = problem.get_language_dict(session=sess)
        if args.language not in langs:
            log.error('language is unknown')
            log.info('supported languages are:')
            for lang in sorted(langs.keys()):
                log.emit('%s (%s)', lang, langs[lang]['description'])
            sys.exit(1)

        # confirm
        if args.wait:
            log.status('sleep(%.2f)', args.wait)
            time.sleep(args.wait)
        if not args.yes:
            sys.stdout.write('Are you sure? [y/N] ')
            sys.stdout.flush()
            c = sys.stdin.read(1)
            if c != 'y':
                log.info('terminated.')
                return

        # submit
        submission = problem.submit(code, language=args.language, session=sess, **kwargs)

        # show result
        if submission is None:
            log.failure('submission failed')
        else:
            if args.open:
                if not isinstance(args.open, str):
                    args.open = None
                    for browser in default_url_opener:
                        args.open = shutil.which(browser)
                        if args.open:
                            break
                if not args.open:
                    log.failure('couldn\'t open the url. please specify a browser')
                else:
                    log.info('open the submission page with: %s', args.open)
                    subprocess.check_call([ args.open, submission.get_url() ], stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
