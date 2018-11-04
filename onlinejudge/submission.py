# Python Version: 3.x
from typing import NamedTuple, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    import requests
    from onlinejudge.problem import Problem
    from onlinejudge.service import Service

class Submission(object):
    def download(self, session: Optional['requests.Session'] = None) -> str:
        raise NotImplementedError
    def get_url(self) -> str:
        raise NotImplementedError
    def get_problem(self) -> 'Problem':
        raise NotImplementedError
    def get_service(self) -> 'Service':
        return self.get_problem().get_service()
    @classmethod
    def from_url(cls, s: str) -> Optional['Submission']:
        pass

class CompatibilitySubmission(Submission):
    def __init__(self, url: str, problem: 'Problem'):
        self.url = url
        self.problem = problem
    def get_url(self) -> str:
        return self.url
    def get_problem(self) -> 'Problem':
        return self.problem

class DummySubmission(Submission):
    def __init__(self, url: str):
        self.url = url
    def get_url(self) -> str:
        return self.url
    def get_problem(self) -> 'Problem':
        raise Exception
