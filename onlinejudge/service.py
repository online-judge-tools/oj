# Python Version: 3.x
from typing import Callable, Optional, Tuple, TYPE_CHECKING
if TYPE_CHECKING:
    import requests

CredentialsProvider = Callable[[], Tuple[str, str]]

class Service(object):
    def login(self, get_credentials: CredentialsProvider, session: Optional['requests.Session'] = None) -> bool:
        raise NotImplementedError
    def get_url(self) -> str:
        raise NotImplementedError
    def get_name(self) -> str:
        raise NotImplementedError
    @classmethod
    def from_url(self, s: str) -> Optional['Service']:
        pass
