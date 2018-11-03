# Python Version: 3.x
from typing import *
if TYPE_CHECKING:
    import requests
    from onlinejudge.service import Service

class Problem(object):
    def download(self, session: Optional['requests.Session'] = None) -> List[Dict[str, Dict[str, str]]]:  # => [ { 'input': { 'data': str, 'name': str }, 'output': { ... } } ]
        raise NotImplementedError
    def submit(self, code: bytes, language: str, session: Optional['requests.Session'] = None) -> None:
        raise NotImplementedError
    def get_language_dict(self, session: Optional['requests.Session'] = None) -> Dict[str, Any]:  # => { language_id: { 'description': str } }
        raise NotImplementedError
    def get_url(self) -> str:
        raise NotImplementedError
    def get_service(self) -> 'Service':
        raise NotImplementedError
    def get_standings(self, session: Optional['requests.Session'] = None) -> Tuple[List[str], List[Dict[str, Any]]]:  # => ( [ 'column1', 'column2', ... ], [ { 'column1': data1, ... } ... ] )
        raise NotImplementedError
    @classmethod
    def from_url(self, s: str) -> Optional['Problem']:
        pass
