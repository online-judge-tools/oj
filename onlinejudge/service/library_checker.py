# Python Version: 3.x
"""
the module for yosupo's Library Checker (https://judge.yosupo.jp)
"""

import os
import re
import subprocess
import sys
import urllib.parse
from typing import *

import requests
import toml

import onlinejudge._implementation.logging as log
import onlinejudge._implementation.testcase_zipper
import onlinejudge._implementation.utils as utils
import onlinejudge.type
from onlinejudge.type import TestCase


class LibraryCheckerService(onlinejudge.type.Service):
    def get_url(self) -> str:
        return 'https://judge.yosupo.jp/'

    def get_name(self) -> str:
        return 'Library Checker'

    @classmethod
    def from_url(cls, url: str) -> Optional['LibraryCheckerService']:
        # example: https://judge.yosupo.jp/
        result = urllib.parse.urlparse(url)
        if result.scheme in ('', 'http', 'https') \
                and result.netloc == 'judge.yosupo.jp':
            return cls()
        return None


class LibraryCheckerProblem(onlinejudge.type.Problem):
    def __init__(self, *, problem_id: str):
        self.problem_id = problem_id

    def download_sample_cases(self, *, session: Optional[requests.Session] = None) -> List[TestCase]:
        self._generate_test_cases_in_cloned_repository()
        path = self._get_problem_directory_path()
        files = []  # type: List[Tuple[str, bytes]]
        files += [(file.name, file.read_bytes()) for file in path.glob('in/*.in') if file.name.startswith('example_')]
        files += [(file.name, file.read_bytes()) for file in path.glob('out/*.out') if file.name.startswith('example_')]
        return onlinejudge._implementation.testcase_zipper.extract_from_files(iter(files))

    def download_system_cases(self, *, session: Optional[requests.Session] = None) -> List[TestCase]:
        self._generate_test_cases_in_cloned_repository()
        path = self._get_problem_directory_path()
        files = []  # type: List[Tuple[str, bytes]]
        files += [(file.name, file.read_bytes()) for file in path.glob('in/*.in')]
        files += [(file.name, file.read_bytes()) for file in path.glob('out/*.out')]
        return onlinejudge._implementation.testcase_zipper.extract_from_files(iter(files))

    def _get_cloned_repository_path(self):
        return utils.cache_dir / 'library-checker-problems'

    def _generate_test_cases_in_cloned_repository(self):
        path = self._get_cloned_repository_path()

        try:
            subprocess.check_call(['git', '--version'], stdout=sys.stdout, stderr=sys.stderr)
        except FileNotFoundError:
            log.error('git command not found')
            raise

        # init the problem repository
        if not path.exists():
            url = 'https://github.com/yosupo06/library-checker-problems'
            log.status('$ git clone %s %s', url, path)
            subprocess.check_call(['git', 'clone', url, str(path)], stdout=sys.stdout, stderr=sys.stderr)

        log.status('$ cd %s', path)
        with utils.chdir(path):
            # sync the problem repository
            log.status('$ git pull')
            subprocess.check_call(['git', 'pull'], stdout=sys.stdout, stderr=sys.stderr)

            # generate test cases
            if sys.version_info < (3, 6):
                log.warning("generate.py may not work on Python 3.5 or older")
            if os.name == 'nt':
                log.warning("generate.py may not work on Windows")
            log.status('$ ./generate.py problems.toml -p %s', self.problem_id)
            try:
                subprocess.check_call([sys.executable, 'generate.py', 'problems.toml', '-p', self.problem_id], stdout=sys.stdout, stderr=sys.stderr)
            except subprocess.CalledProcessError:
                log.error("the generate.py failed: check https://github.com/yosupo06/library-checker-problems/issues")
                raise

    def _get_problem_directory_path(self):
        path = self._get_cloned_repository_path()
        problems = toml.load(path / 'problems.toml')
        return path / problems['problems'][self.problem_id]['dir']

    def get_url(self) -> str:
        return 'https://judge.yosupo.jp/problem/{}'.format(self.problem_id)

    def get_service(self) -> LibraryCheckerService:
        return LibraryCheckerService()

    @classmethod
    def from_url(cls, url: str) -> Optional['LibraryCheckerProblem']:
        # example: https://judge.yosupo.jp/problem/unionfind
        result = urllib.parse.urlparse(url)
        if result.scheme in ('', 'http', 'https') \
                and result.netloc == 'judge.yosupo.jp':
            m = re.match(r'/problem/(\w+)/?', result.path)
            if m:
                return cls(problem_id=m.group(1))
        return None


onlinejudge.dispatch.services += [LibraryCheckerService]
onlinejudge.dispatch.problems += [LibraryCheckerProblem]
