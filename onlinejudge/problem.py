# Python Version: 3.x
from typing import *
if TYPE_CHECKING:
    import requests
    from onlinejudge.service import Service
    from onlinejudge.submission import Submission

LabeledString = NamedTuple('LabeledString', [ ('name', str), ('data', str) ])
TestCase = NamedTuple('TestCase', [ ('input', LabeledString), ('output', LabeledString) ])
# Language = NamedTuple('Language', [ ('id', str), ('name', str), ('description': str) ])
Language = Dict[str, Any]
Standings = Tuple[List[str], List[Dict[str, Any]]]  # ( [ 'column1', 'column2', ... ], [ { 'column1': data1, ... } ... ] )

class SubmissionError(RuntimeError):
    pass

class Problem(object):
    def download(self, session: Optional['requests.Session'] = None) -> List[TestCase]:
        raise NotImplementedError
    def submit(self, code: str, language: str, session: Optional['requests.Session'] = None) -> 'Submission':  # or SubmissionError
        raise NotImplementedError
    def get_language_dict(self, session: Optional['requests.Session'] = None) -> Dict[str, Language]:
        raise NotImplementedError
    def get_url(self) -> str:
        raise NotImplementedError
    def get_service(self) -> 'Service':
        raise NotImplementedError
    def get_input_format(self, session: Optional['requests.Session'] = None) -> Optional[str]:
        raise NotImplementedError
    def get_standings(self, session: Optional['requests.Session'] = None) -> Standings:
        raise NotImplementedError
    @classmethod
    def from_url(self, s: str) -> Optional['Problem']:
        pass
