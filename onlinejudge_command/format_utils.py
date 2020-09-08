import collections
import glob
import os
import pathlib
import re
import sys
from logging import getLogger
from typing import Dict, Generator, List, Match, Optional, Set

logger = getLogger(__name__)


def percentsplit(s: str) -> Generator[str, None, None]:
    for m in re.finditer('[^%]|%(.)', s):
        yield m.group(0)


def percentformat(s: str, table: Dict[str, str]) -> str:
    assert '%' not in table or table['%'] == '%'
    table['%'] = '%'
    result = ''
    for c in percentsplit(s):
        if c.startswith('%'):
            result += table[c[1]]
        else:
            result += c
    return result


def percentparse(s: str, format: str, table: Dict[str, str]) -> Optional[Dict[str, str]]:
    table = {key: '(?P<{}>{})'.format(key, value) for key, value in table.items()}
    used: Set[str] = set()
    pattern = ''
    for token in percentsplit(re.escape(format).replace('\\%', '%')):
        if token.startswith('%'):
            c = token[1]
            if c not in used:
                pattern += table[c]
                used.add(c)
            else:
                pattern += r'(?P={})'.format(c)
        else:
            pattern += token
    m = re.match(pattern, s)
    if not m:
        return None
    return m.groupdict()


def glob_with_format(directory: pathlib.Path, format: str) -> List[pathlib.Path]:
    if os.name == 'nt':
        format = format.replace('/', '\\')
    table = {}
    table['s'] = '*'
    table['e'] = '*'
    pattern = (glob.escape(str(directory) + os.path.sep) + percentformat(glob.escape(format).replace(glob.escape('%'), '%'), table))
    paths = list(map(pathlib.Path, glob.glob(pattern)))
    for path in paths:
        logger.debug('testcase globbed: %s', path)
    return paths


def match_with_format(directory: pathlib.Path, format: str, path: pathlib.Path) -> Optional[Match[str]]:
    if os.name == 'nt':
        format = format.replace('/', '\\')
    table = {}
    table['s'] = '(?P<name>.+)'
    table['e'] = '(?P<ext>in|out)'
    pattern = re.compile(re.escape(str(directory.resolve()) + os.path.sep) + percentformat(re.escape(format).replace(re.escape('%'), '%'), table))
    return pattern.match(str(path.resolve()))


def path_from_format(directory: pathlib.Path, format: str, name: str, ext: str) -> pathlib.Path:
    table = {}
    table['s'] = name
    table['e'] = ext
    return directory / percentformat(format, table)


def is_backup_or_hidden_file(path: pathlib.Path) -> bool:
    basename = path.name
    return basename.endswith('~') or (basename.startswith('#') and basename.endswith('#')) or basename.startswith('.')


def drop_backup_or_hidden_files(paths: List[pathlib.Path]) -> List[pathlib.Path]:
    result: List[pathlib.Path] = []
    for path in paths:
        if is_backup_or_hidden_file(path):
            logger.warning('ignore a backup file: %s', path)
        else:
            result += [path]
    return result


def construct_relationship_of_files(paths: List[pathlib.Path], directory: pathlib.Path, format: str) -> Dict[str, Dict[str, pathlib.Path]]:
    tests: Dict[str, Dict[str, pathlib.Path]] = collections.defaultdict(dict)
    for path in paths:
        m = match_with_format(directory, format, path.resolve())
        if not m:
            logger.error('unrecognizable file found: %s', path)
            sys.exit(1)
        name = m.groupdict()['name']
        ext = m.groupdict()['ext']
        assert ext not in tests[name]
        tests[name][ext] = path
    for name in tests:
        if 'in' not in tests[name]:
            assert 'out' in tests[name]
            logger.error('dangling output case: %s', tests[name]['out'])
            sys.exit(1)
    if not tests:
        logger.error('no cases found')
        sys.exit(1)
    logger.info('%d cases found', len(tests))
    return tests
