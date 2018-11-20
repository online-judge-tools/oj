# Python Version: 3.x
import onlinejudge
import onlinejudge.implementation.utils as utils
import onlinejudge.implementation.logging as log
import sys
import time
import shutil
import subprocess
import os
import re
from typing import *
if TYPE_CHECKING:
    import argparse

default_url_opener = [ 'sensible-browser', 'xdg-open', 'open' ]

def submit(args: 'argparse.Namespace') -> None:
    # parse url
    problem = onlinejudge.dispatch.problem_from_url(args.url)
    if problem is None:
        sys.exit(1)

    # read code
    with open(args.file) as fh:
        code = fh.buffer.read()
    format_config = {
        'dos2unix': args.format_dos2unix or args.golf,
        'rstrip': args.format_dos2unix or args.golf,
    }
    code = format_code(code, **format_config)

    # report code
    try:
        s = code.decode()
    except UnicodeDecodeError as e:
        log.failure('%s: %s', e.__class__.__name__, str(e))
        s = repr(code)[ 1 : ]
    log.info('code (%d byte):', len(code))
    log.emit(log.bold(s))


    with utils.with_cookiejar(utils.new_default_session(), path=args.cookie) as sess:
        # guess or select language ids
        langs = problem.get_language_dict(session=sess)
        matched_lang_ids: Optional[List[str]] = None
        if args.language in langs:
            matched_lang_ids = [ args.language ]
        else:
            if args.guess:
                kwargs = {
                    'language_dict': langs,
                    'cxx_latest': args.guess_cxx_latest,
                    'cxx_compiler': args.guess_cxx_compiler,
                    'python_version': args.guess_python_version,
                    'python_interpreter': args.guess_python_interpreter,
                }
                matched_lang_ids = guess_lang_ids_of_file(args.file, code, **kwargs)
                if not matched_lang_ids:
                    log.info('failed to guess languages from the file name')
                    matched_lang_ids = list(langs.keys())
                if args.language is not None:
                    log.info('you can use `--no-guess` option if you want to do an unusual submission')
                    matched_lang_ids = select_ids_of_matched_languages(args.language.split(), matched_lang_ids, language_dict=langs)
            else:
                if args.language is None:
                    matched_lang_ids = None
                else:
                    matched_lang_ids = select_ids_of_matched_languages(args.language.split(), list(langs.keys()), language_dict=langs)

        # report selected language ids
        if matched_lang_ids is not None and len(matched_lang_ids) == 1:
            args.language = matched_lang_ids[0]
            log.info('choosed language: %s (%s)', args.language, langs[args.language]['description'])
        else:
            if matched_lang_ids is None:
                log.error('language is unknown')
                log.info('supported languages are:')
            elif len(matched_lang_ids) == 0:
                log.error('no languages are matched')
                log.info('supported languages are:')
            else:
                log.error('Matched languages were not narrowed down to one.')
                log.info('You have to choose:')
            for lang_id in sorted(matched_lang_ids or langs.keys()):
                log.emit('%s (%s)', lang_id, langs[lang_id]['description'])
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
        kwargs = {}
        if problem.get_service().get_name() == 'topcoder':
            if args.full_submission:
                kwargs['kind'] = 'full'
            else:
                kwargs['kind'] = 'example'
        try:
            submission = problem.submit(code, language=args.language, session=sess, **kwargs)  # type: ignore
        except onlinejudge.problem.SubmissionError:
            log.failure('submission failed')
            return

        # show result
        if args.open:
            if args.open_browser:
                browser = args.open_browser
            else:
                for browser in default_url_opener:
                    if shutil.which(browser):
                        break
                else:
                    browser = None
                    log.failure('couldn\'t find browsers to open the url. please specify a browser')
            if browser:
                log.status('open the submission page with: %s', browser)
                subprocess.check_call([ browser, submission.get_url() ], stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)

def select_ids_of_matched_languages(words: List[str], lang_ids: List[str], language_dict, split: bool = False, remove: bool = False) -> List[str]:
    result = []
    for lang_id in lang_ids:
        desc = language_dict[lang_id]['description'].lower()
        if split:
            desc = desc.split()
        pred = all([ word.lower() in desc for word in words ])
        if remove:
            pred = not pred
        if pred:
            result.append(lang_id)
    return result

def guess_lang_ids_of_file(filename: str, code: bytes, language_dict, cxx_latest: bool = False, cxx_compiler: str = 'all', python_version: str = 'all', python_interpreter: str = 'all') -> List[str]:
    assert cxx_compiler.lower() in ( 'gcc', 'clang', 'all' )
    assert python_version.lower() in ( '2', '3', 'auto', 'all' )
    assert python_interpreter.lower() in ( 'cpython', 'pypy', 'all' )

    select = lambda word, lang_ids, **kwargs: select_ids_of_matched_languages([ word ], lang_ids, language_dict=language_dict, **kwargs)
    _, ext = os.path.splitext(filename)
    lang_ids = language_dict.keys()

    log.debug('file extension: %s', ext)
    ext = ext.lstrip('.')

    if ext in ( 'cpp', 'cxx', 'cc', 'C' ):
        log.debug('language guessing: C++')
        # memo: https://stackoverflow.com/questions/1545080/c-code-file-extension-cc-vs-cpp
        lang_ids = select('c++', lang_ids)
        if not lang_ids:
            return []

        # compiler
        if select('gcc', lang_ids) and select('clang', lang_ids):
            log.info('both GCC and Clang are available for C++ compiler')
            if cxx_compiler.lower() == 'gcc':
                log.info('use: GCC')
                lang_ids = select('gcc', lang_ids)
            elif cxx_compiler.lower() == 'clang':
                log.info('use: Clang')
                lang_ids = select('clang', lang_ids)
            else:
                assert cxx_compiler.lower() == 'all'

        # version
        if cxx_latest:
            saved_ids = lang_ids
            lang_ids = []
            for compiler in ( None, 'gcc', 'clang' ):  # use the latest for each compiler
                version_of = {}
                ids = select(compiler, saved_ids) if compiler else saved_ids
                if not ids:
                    continue
                for lang_id in ids:
                    m = re.search(r'c\+\+\w\w', language_dict[lang_id]['description'].lower())
                    if m:
                        version_of[lang_id] = m[0]
                ids.sort(key=lambda lang_id: version_of.get(lang_id, ''))
                lang_ids += [ ids[-1] ]  # since C++11 < C++1y < ... as strings
            lang_ids = list(set(lang_ids))

        assert lang_ids
        return lang_ids

    elif ext == 'py':
        log.debug('language guessing: Python')
        if select('pypy', language_dict.keys()):
            log.info('PyPy is available for Python interpreter')

        # interpreter
        lang_ids = []
        if python_interpreter.lower() in ( 'cpython', 'all' ):
            lang_ids += select('python', language_dict.keys())
        elif python_interpreter.lower() in ( 'pypy', 'all' ) or not lang_ids:
            lang_ids += select('pypy', language_dict.keys())

        # version
        if select('python2', lang_ids) and select('python3', lang_ids):
            log.info('both Python2 and Python3 are available for version of Python')
            if python_version in ( '2', '3' ):
                versions = [ int(python_version) ]
            elif python_version == 'all':
                versions = [ 2, 3 ]
            else:
                assert python_version == 'auto'
                lines = code.splitlines()
                if code.startswith(b'#!'):
                    s = lines[0]  # use shebang
                else:
                    s = b'\n'.join(lines[: 5] + lines[-5 :])  # use modelines
                versions = []
                for version in ( 2, 3 ):
                    if re.search(r'python ?%d'.encode() % version, s.lower()):
                        versions += [ version ]
                if not versions:
                    versions = [ 2, 3 ]
            log.info('use: %s', ', '.join(map(str, versions)))

            saved_ids = lang_ids
            lang_ids = []
            for version in versions:
                lang_ids += select('python%d'  % version, saved_ids)
                lang_ids += select('python %d' % version, saved_ids)

        lang_ids = list(set(lang_ids))
        return lang_ids

    else:
        log.debug('language guessing: othres')
        table: List[Dict[str, Any]] = [
             { 'names': [ 'awk'                   ], 'exts': [ 'awk'       ] },
             { 'names': [ 'bash'                  ], 'exts': [ 'sh'        ] },
             { 'names': [ 'brainfuck'             ], 'exts': [ 'bf'        ] },
             { 'names': [ 'c#'                    ], 'exts': [ 'cs'        ] },
             { 'names': [ 'c'                     ], 'exts': [ 'c'         ], 'split': True },
             { 'names': [ 'd'                     ], 'exts': [ 'd'         ], 'split': True },
             { 'names': [ 'f#'                    ], 'exts': [ 'fs'        ] },
             { 'names': [ 'fortran'               ], 'exts': [ 'for', 'f', 'f90', 'f95', 'f03' ] },
             { 'names': [ 'go'                    ], 'exts': [ 'go'        ], 'split': True },
             { 'names': [ 'haskell'               ], 'exts': [ 'hs'        ] },
             { 'names': [ 'java'                  ], 'exts': [ 'java'      ] },
             { 'names': [ 'javascript'            ], 'exts': [ 'js'        ] },
             { 'names': [ 'lua'                   ], 'exts': [ 'lua'       ] },
             { 'names': [ 'objective-c'           ], 'exts': [ 'm'         ] },
             { 'names': [ 'ocaml'                 ], 'exts': [ 'ml'        ] },
             { 'names': [ 'octave'                ], 'exts': [ 'm'         ] },
             { 'names': [ 'pascal'                ], 'exts': [ 'pas'       ] },
             { 'names': [ 'perl6'                 ], 'exts': [ 'p6', 'pl6', 'pm6' ] },
             { 'names': [ 'perl'                  ], 'exts': [ 'pl', 'pm'  ], 'split': True },
             { 'names': [ 'php'                   ], 'exts': [ 'php'       ] },
             { 'names': [ 'ruby'                  ], 'exts': [ 'rb'        ] },
             { 'names': [ 'rust'                  ], 'exts': [ 'rs'        ] },
             { 'names': [ 'scala'                 ], 'exts': [ 'scala'     ] },
             { 'names': [ 'scheme'                ], 'exts': [ 'scm'       ] },
             { 'names': [ 'sed'                   ], 'exts': [ 'sed'       ] },
             { 'names': [ 'standard ml'           ], 'exts': [ 'sml'       ] },
             { 'names': [ 'swift'                 ], 'exts': [ 'swift'     ] },
             { 'names': [ 'text'                  ], 'exts': [ 'txt'       ] },
             { 'names': [ 'typescript'            ], 'exts': [ 'ts'        ] },
             { 'names': [ 'vim script'            ], 'exts': [ 'vim'       ] },
        ]

        lang_ids = []
        for data in table:
            if ext in data['exts']:
                for name in data['names']:
                        lang_ids += select(name, language_dict.keys(), split=data.get('split', False))
        return list(set(lang_ids))


def format_code(code: bytes, dos2unix: bool = False, rstrip: bool = False) -> bytes:
    if dos2unix:
        log.status('dos2unix...')
        code = code.replace(b'\r\n', b'\n')
    if rstrip:
        log.status('rstrip...')
        code = code.rstrip()
    return code
