# Python Version: 3.x
"""
the module for yosupo's Library Checker (https://judge.yosupo.jp)
"""

import os
import pathlib
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

    @classmethod
    def _get_cloned_repository_path(cls) -> pathlib.Path:
        return utils.user_cache_dir / 'library-checker-problems'

    is_repository_updated = False

    @classmethod
    def _update_cloned_repository(cls) -> None:
        if cls.is_repository_updated:
            return

        try:
            subprocess.check_call(['git', '--version'], stdout=sys.stdout, stderr=sys.stderr)
        except FileNotFoundError:
            log.error('git command not found')
            raise

        path = LibraryCheckerService._get_cloned_repository_path()
        if not path.exists():
            # init the problem repository
            url = 'https://github.com/yosupo06/library-checker-problems'
            log.status('$ git clone %s %s', url, path)
            subprocess.check_call(['git', 'clone', url, str(path)], stdout=sys.stdout, stderr=sys.stderr)
        else:
            # sync the problem repository
            log.status('$ git -C %s pull', str(path))
            subprocess.check_call(['git', '-C', str(path), 'pull'], stdout=sys.stdout, stderr=sys.stderr)

        cls.is_repository_updated = True


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

    def _generate_test_cases_in_cloned_repository(self) -> None:
        LibraryCheckerService._update_cloned_repository()
        path = LibraryCheckerService._get_cloned_repository_path()

        if sys.version_info < (3, 6):
            log.warning("generate.py may not work on Python 3.5 or older")
        if os.name == 'nt':
            log.warning("generate.py may not work on Windows")

        command = [sys.executable, str(path / 'generate.py'), str(path / 'problems.toml'), '-p', self.problem_id]
        log.status('$ %s', ' '.join(command))
        try:
            subprocess.check_call(command, stdout=sys.stdout, stderr=sys.stderr)
        except subprocess.CalledProcessError:
            log.error("the generate.py failed: check https://github.com/yosupo06/library-checker-problems/issues")
            raise

    def _get_problem_directory_path(self) -> pathlib.Path:
        path = LibraryCheckerService._get_cloned_repository_path()
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

    def download_checker_cpp(self) -> bytes:
        LibraryCheckerService._update_cloned_repository()
        path = self._get_problem_directory_path()
        with open(str(path / "checker.cpp"), "rb") as fh:
            return fh.read()


onlinejudge.dispatch.services += [LibraryCheckerService]
onlinejudge.dispatch.problems += [LibraryCheckerProblem]
