# Python Version: 3.x
import onlinejudge
import onlinejudge.implementation.utils as utils
import onlinejudge.implementation.logging as log
import sys
import os
import os.path
import pathlib
import re
import glob
import collections
from typing import Dict, List, Match, Optional

def glob_with_format(directory: pathlib.Path, format: str) -> List[pathlib.Path]:
    table = {}
    table['s'] = '*'
    table['e'] = '*'
    pattern = str(directory / utils.parcentformat(format, table))
    paths = list(map(pathlib.Path, glob.glob(pattern)))
    for path in paths:
        log.debug('testcase globbed: %s', path)
    return paths

def match_with_format(directory: pathlib.Path, format: str, path: pathlib.Path) -> Optional[Match[str]]:
    table = {}
    table['s'] = '(?P<name>.+)'
    table['e'] = '(?P<ext>in|out)'
    pattern = re.compile('^' + utils.parcentformat(format, table) + '$')
    path = path.absolute().relative_to(directory.absolute()).resolve()
    return pattern.match(str(path))

def path_from_format(directory: pathlib.Path, format: str, name: str, ext: str) -> pathlib.Path:
    table = {}
    table['s'] = name
    table['e'] = ext
    return directory / utils.parcentformat(format, table)

def is_backup_or_hidden_file(path: pathlib.Path) -> bool:
    basename = path.stem
    return basename.endswith('~') or (basename.startswith('#') and basename.endswith('#')) or basename.startswith('.')

def drop_backup_or_hidden_files(paths: List[pathlib.Path]) -> List[pathlib.Path]:
    result = []  # type: List[pathlib.Path]
    for path in paths:
        if is_backup_or_hidden_file(path):
            log.warning('ignore a backup file: %s', path)
        else:
            result += [ path ]
    return result

def construct_relationship_of_files(paths: List[pathlib.Path], directory: pathlib.Path, format: str) -> Dict[str, Dict[str, pathlib.Path]]:
    tests = collections.defaultdict(dict)  # type: Dict[str, Dict[str, pathlib.Path]]
    for path in paths:
        m = match_with_format(directory, format, path.resolve())
        if not m:
            log.error('unrecognizable file found: %s', path)
            sys.exit(1)
        name = m.groupdict()['name']
        ext  = m.groupdict()['ext']
        assert ext not in tests[name]
        tests[name][ext] = path
    for name in tests:
        if 'in' not in tests[name]:
            assert 'out' in tests[name]
            log.error('dangling output case: %s', tests[name]['out'])
            sys.exit(1)
    if not tests:
        log.error('no cases found')
        sys.exit(1)
    log.info('%d cases found', len(tests))
    return tests
