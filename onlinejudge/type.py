# Python Version: 3.x
from typing import *

if TYPE_CHECKING:
    import requests

CredentialsProvider = Callable[[], Tuple[str, str]]


class Service(object):
    def login(self, get_credentials: CredentialsProvider, session: Optional['requests.Session'] = None) -> bool:
        raise NotImplementedError

    def is_logged_in(self, session: Optional['requests.Session'] = None) -> bool:
        raise NotImplementedError

    def get_url(self) -> str:
        raise NotImplementedError

    def get_name(self) -> str:
        raise NotImplementedError

    @classmethod
    def from_url(self, s: str) -> Optional['Service']:
        pass


LabeledString = NamedTuple('LabeledString', [('name', str), ('data', str)])
TestCase = NamedTuple('TestCase', [('input', LabeledString), ('output', LabeledString)])
# Language = NamedTuple('Language', [ ('id', str), ('name', str), ('description': str) ])
Language = Dict[str, Any]
Standings = Tuple[List[str], List[Dict[str, Any]]]  # ( [ 'column1', 'column2', ... ], [ { 'column1': data1, ... } ... ] )


class SubmissionError(RuntimeError):
    pass


class Problem(object):
    def download_sample_cases(self, session: Optional['requests.Session'] = None) -> List[TestCase]:
        raise NotImplementedError

    def download_system_cases(self, session: Optional['requests.Session'] = None) -> List[TestCase]:
        raise NotImplementedError

    def submit_code(self, code: bytes, language: str, session: Optional['requests.Session'] = None) -> 'Submission':
        """
        :raises SubmissionError:
        """
        raise NotImplementedError

    def get_language_dict(self, session: Optional['requests.Session'] = None) -> Dict[str, Language]:
        raise NotImplementedError

    def get_url(self) -> str:
        raise NotImplementedError

    def get_service(self) -> Service:
        raise NotImplementedError

    def get_input_format(self, session: Optional['requests.Session'] = None) -> Optional[str]:
        raise NotImplementedError

    def get_standings(self, session: Optional['requests.Session'] = None) -> Standings:
        raise NotImplementedError

    @classmethod
    def from_url(self, s: str) -> Optional['Problem']:
        pass


class Submission(object):
    def download_code(self, session: Optional['requests.Session'] = None) -> bytes:
        raise NotImplementedError

    def get_url(self) -> str:
        raise NotImplementedError

    def get_problem(self) -> Problem:
        raise NotImplementedError

    def get_service(self) -> Service:
        return self.get_problem().get_service()

    @classmethod
    def from_url(cls, s: str) -> Optional['Submission']:
        pass


class CompatibilitySubmission(Submission):
    def __init__(self, url: str, problem: Problem):
        self.url = url
        self.problem = problem

    def get_url(self) -> str:
        return self.url

    def get_problem(self) -> Problem:
        return self.problem


class DummySubmission(Submission):
    def __init__(self, url: str):
        self.url = url

    def get_url(self) -> str:
        return self.url

    def get_problem(self) -> Problem:
        raise Exception
