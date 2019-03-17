# Python Version: 3.x
import pathlib
import re
import shutil
import subprocess
import sys
import time
from typing import *

import onlinejudge
import onlinejudge._implementation.download_history
import onlinejudge._implementation.logging as log
import onlinejudge._implementation.utils as utils
from onlinejudge.type import *

if TYPE_CHECKING:
    import argparse

default_url_opener = ['sensible-browser', 'xdg-open', 'open']


def submit(args: 'argparse.Namespace') -> None:
    # guess url
    history = onlinejudge._implementation.download_history.DownloadHistory()
    if args.file.parent.resolve() == pathlib.Path.cwd():
        guessed_urls = history.get()
    else:
        log.warning('cannot guess URL since the given file is not in the current directory')
        guessed_urls = []
    if args.url is None:
        if len(guessed_urls) == 1:
            args.url = guessed_urls[0]
            log.info('guessed problem: %s', args.url)
        else:
            log.error('failed to guess the URL to submit')
            log.info('please manually specify URL as: $ oj submit URL FILE')
            sys.exit(1)

    # parse url
    problem = onlinejudge.dispatch.problem_from_url(args.url)
    if problem is None:
        sys.exit(1)

    # read code
    with args.file.open('rb') as fh:
        code = fh.read()  # type: bytes
    format_config = {
        'dos2unix': args.format_dos2unix or args.golf,
        'rstrip': args.format_dos2unix or args.golf,
    }
    code = format_code(code, **format_config)

    # report code
    log.info('code (%d byte):', len(code))
    log.emit(utils.snip_large_file_content(code, limit=30, head=10, tail=10, bold=True))

    with utils.with_cookiejar(utils.new_session_with_our_user_agent(), path=args.cookie) as sess:
        # guess or select language ids
        langs = {language.id: {'description': language.name} for language in problem.get_available_languages(session=sess)}  # type: Dict[LanguageId, Dict[str, str]]
        matched_lang_ids = None  # type: Optional[List[str]]
        if args.language in langs:
            matched_lang_ids = [args.language]
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
            log.info('chosen language: %s (%s)', args.language, langs[LanguageId(args.language)]['description'])
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
                log.emit('%s (%s)', lang_id, langs[LanguageId(lang_id)]['description'])
            sys.exit(1)

        # confirm
        guessed_unmatch = ([problem.get_url()] != guessed_urls)
        if guessed_unmatch:
            samples_text = ('samples of "{}'.format('", "'.join(guessed_urls)) if guessed_urls else 'no samples')
            log.warning('the problem "%s" is specified to submit, but %s were downloaded in this directory. this may be mis-operation', problem.get_url(), samples_text)
        if args.wait:
            log.status('sleep(%.2f)', args.wait)
            time.sleep(args.wait)
        if not args.yes:
            if guessed_unmatch:
                problem_id = problem.get_url().rstrip('/').split('/')[-1].split('?')[-1]  # this is too ad-hoc
                key = problem_id[:3] + (problem_id[-1] if len(problem_id) >= 4 else '')
                sys.stdout.write('Are you sure? Please type "{}" '.format(key))
                sys.stdout.flush()
                c = sys.stdin.readline().rstrip()
                if c != key:
                    log.info('terminated.')
                    return
            else:
                sys.stdout.write('Are you sure? [y/N] ')
                sys.stdout.flush()
                c = sys.stdin.read(1)
                if c.lower() != 'y':
                    log.info('terminated.')
                    return

        # submit
        kwargs = {}
        if isinstance(problem, onlinejudge.service.topcoder.TopcoderLongContestProblem):
            if args.full_submission:
                kwargs['kind'] = 'full'
            else:
                kwargs['kind'] = 'example'
        try:
            submission = problem.submit_code(code, language_id=LanguageId(args.language), session=sess, **kwargs)  # type: ignore
        except NotLoggedInError:
            log.failure('login required')
            sys.exit(1)
        except SubmissionError:
            log.failure('submission failed')
            sys.exit(1)

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
                subprocess.check_call([browser, submission.get_url()], stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)


def select_ids_of_matched_languages(words: List[str], lang_ids: List[str], language_dict, split: bool = False, remove: bool = False) -> List[str]:
    result = []
    for lang_id in lang_ids:
        desc = language_dict[lang_id]['description'].lower()
        if split:
            desc = desc.split()
        pred = all([word.lower() in desc for word in words])
        if remove:
            pred = not pred
        if pred:
            result.append(lang_id)
    return result


def guess_lang_ids_of_file(filename: pathlib.Path, code: bytes, language_dict, cxx_latest: bool = False, cxx_compiler: str = 'all', python_version: str = 'all', python_interpreter: str = 'all') -> List[str]:
    assert cxx_compiler.lower() in ('gcc', 'clang', 'all')
    assert python_version.lower() in ('2', '3', 'auto', 'all')
    assert python_interpreter.lower() in ('cpython', 'pypy', 'all')

    select_words = (lambda words, lang_ids, **kwargs: select_ids_of_matched_languages(words, lang_ids, language_dict=language_dict, **kwargs))
    select = (lambda word, lang_ids, **kwargs: select_words([word], lang_ids, **kwargs))
    ext = filename.suffix
    lang_ids = language_dict.keys()

    log.debug('file extension: %s', ext)
    ext = ext.lstrip('.')

    if ext in ('cpp', 'cxx', 'cc', 'C'):
        log.debug('language guessing: C++')
        # memo: https://stackoverflow.com/questions/1545080/c-code-file-extension-cc-vs-cpp
        lang_ids = list(set(select('c++', lang_ids) + select('g++', lang_ids)))
        if not lang_ids:
            return []
        log.debug('all lang ids for C++: %s', lang_ids)

        # compiler
        select_gcc = lambda ids: list(set(select('gcc', ids) + select('clang', select('g++', ids), remove=True)))
        if select_gcc(lang_ids) and select('clang', lang_ids):
            log.status('both GCC and Clang are available for C++ compiler')
            if cxx_compiler.lower() == 'gcc':
                log.status('use: GCC')
                lang_ids = select_gcc(lang_ids)
            elif cxx_compiler.lower() == 'clang':
                log.status('use: Clang')
                lang_ids = select('clang', lang_ids)
            else:
                assert cxx_compiler.lower() == 'all'
        log.debug('lang ids after compiler filter: %s', lang_ids)

        # version
        if cxx_latest:
            saved_ids = lang_ids
            lang_ids = []
            for compiler in (None, 'gcc', 'clang'):  # use the latest for each compiler
                version_of = {}
                if compiler == 'gcc':
                    ids = select_gcc(saved_ids)
                elif compiler == 'clang':
                    ids = select('clang', saved_ids)
                else:
                    ids = saved_ids
                if not ids:
                    continue
                for lang_id in ids:
                    m = re.search(r'[cg]\+\+\w\w', language_dict[lang_id]['description'].lower())
                    if m:
                        version_of[lang_id] = m.group(0)
                ids.sort(key=lambda lang_id: version_of.get(lang_id, ''))
                lang_ids += [ids[-1]]  # since C++11 < C++1y < ... as strings
            lang_ids = list(set(lang_ids))
        log.debug('lang ids after version filter: %s', lang_ids)

        assert lang_ids
        return lang_ids

    elif ext == 'py':
        log.debug('language guessing: Python')
        if select('pypy', language_dict.keys()):
            log.status('PyPy is available for Python interpreter')

        # interpreter
        lang_ids = []
        if python_interpreter.lower() in ('cpython', 'all'):
            lang_ids += select('python', language_dict.keys())
        elif python_interpreter.lower() in ('pypy', 'all') or not lang_ids:
            lang_ids += select('pypy', language_dict.keys())

        # version
        if select_words(['python', '2'], lang_ids) and select_words(['python', '3'], lang_ids):
            log.status('both Python2 and Python3 are available for version of Python')
            if python_version in ('2', '3'):
                versions = [int(python_version)]
            elif python_version == 'all':
                versions = [2, 3]
            else:
                assert python_version == 'auto'
                lines = code.splitlines()
                if code.startswith(b'#!'):
                    s = lines[0]  # use shebang
                else:
                    s = b'\n'.join(lines[:10] + lines[-5:])  # use modelines
                versions = []
                for version in (2, 3):
                    if re.search(r'python *(version:? *)?%d'.encode() % version, s.lower()):
                        versions += [version]
                if not versions:
                    log.status('no version info in code')
                    versions = [2, 3]
            log.status('use: %s', ', '.join(map(str, versions)))

            saved_ids = lang_ids
            lang_ids = []
            for version in versions:
                lang_ids += select('python%d' % version, saved_ids)
                lang_ids += select('python %d' % version, saved_ids)

        lang_ids = list(set(lang_ids))
        return lang_ids

    else:
        log.debug('language guessing: othres')
        table = [
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
        ]  # type: List[Dict[str, Any]]  # yapf: disable

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
