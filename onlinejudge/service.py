# Python Version: 3.x
import requests
from typing import Callable, Optional, Tuple

class Service(object):
    def login(self, get_credentials: Callable[[], Tuple[str, str]], session: Optional[requests.Session] = None):
        raise NotImplementedError
    def get_url(self) -> str:
        raise NotImplementedError
    def get_name(self) -> str:
        raise NotImplementedError
    @classmethod
    def from_url(self, s: str) -> str:
        pass
