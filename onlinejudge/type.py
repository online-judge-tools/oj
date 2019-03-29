# Python Version: 3.x
from abc import ABC, abstractmethod
from typing import Callable, List, NamedTuple, NewType, Optional, Tuple

import requests

CredentialsProvider = Callable[[], Tuple[str, str]]


class LoginError(RuntimeError):
    pass


class Service(ABC):
    def login(self, get_credentials: CredentialsProvider, session: Optional[requests.Session] = None) -> None:
        """
        :param get_credentials: returns a tuple of (username, password)
        :raises LoginError:
        """
        raise NotImplementedError

    def is_logged_in(self, session: Optional[requests.Session] = None) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_url(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_name(self) -> str:
        """
        example:

        -   `AtCoder`
        -   `Codeforces`
        -   `PKU JudgeOnline`

        :note: If you want something like identifier (e.g. `atcoder`, `codeforces` or `poj`), you can use a domain obtained from :py:meth:`get_url`.
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        return '{}.from_url({})'.format(self.__class__.__name__, repr(self.get_url()))

    def __eq__(self, other) -> bool:
        return self.__class__ == other.__class__ and self.get_url() == other.get_url()

    @classmethod
    @abstractmethod
    def from_url(self, s: str) -> Optional['Service']:
        pass


TestCase = NamedTuple('TestCase', [
    ('name', str),
    ('input_name', str),
    ('input_data', bytes),
    ('output_name', Optional[str]),
    ('output_data', Optional[bytes]),
])

LanguageId = NewType('LanguageId', str)
"""
:note: This is just a :py:class:`NewType` -ed :py:class:`str` not, but you should not use this other than a label.
"""

Language = NamedTuple('Language', [
    ('id', LanguageId),
    ('name', str),
])
"""
:ivar id: :py:class:`LanguageId`
:ivar name: :py:class:`str`
"""


class NotLoggedInError(RuntimeError):
    pass


class SubmissionError(RuntimeError):
    pass


class Problem(ABC):
    """
    :note: :py:class:`Problem` represents just a URL of a problem, without the data of the problem.
    """

    @abstractmethod
    def download_sample_cases(self, session: Optional[requests.Session] = None) -> List[TestCase]:
        raise NotImplementedError

    def download_system_cases(self, session: Optional[requests.Session] = None) -> List[TestCase]:
        """
        :raises NotLoggedInError:
        """
        raise NotImplementedError

    def submit_code(self, code: bytes, language_id: LanguageId, filename: Optional[str] = None, session: Optional[requests.Session] = None) -> 'Submission':
        """
        :param code:
        :arg language_id: :py:class:`LanguageId`
        :raises NotLoggedInError:
        :raises SubmissionError:
        """
        raise NotImplementedError

    def get_available_languages(self, session: Optional[requests.Session] = None) -> List[Language]:
        raise NotImplementedError

    @abstractmethod
    def get_url(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_service(self) -> Service:
        raise NotImplementedError

    def get_name(self) -> str:
        """
        example:

        -   `器物損壊！高橋君`
        -   `AtCoDeerくんと変なじゃんけん / AtCoDeer and Rock-Paper`
        -   `Xor Sum`
        """
        raise NotImplementedError

    def get_input_format(self, session: Optional[requests.Session] = None) -> Optional[str]:
        """
        :return: the HTML in the `<pre>` tag as :py:class:`str`
        """

        raise NotImplementedError

    def __repr__(self) -> str:
        return '{}.from_url({})'.format(self.__class__.__name__, repr(self.get_url()))

    def __eq__(self, other) -> bool:
        return self.__class__ == other.__class__ and self.get_url() == other.get_url()

    @classmethod
    @abstractmethod
    def from_url(self, s: str) -> Optional['Problem']:
        pass


class Submission(ABC):
    @abstractmethod
    def download_code(self, session: Optional[requests.Session] = None) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def get_url(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_problem(self) -> Problem:
        raise NotImplementedError

    @abstractmethod
    def get_service(self) -> Service:
        return self.get_problem().get_service()

    def __repr__(self) -> str:
        return '{}.from_url({})'.format(self.__class__.__name__, repr(self.get_url()))

    def __eq__(self, other) -> bool:
        return self.__class__ == other.__class__ and self.get_url() == other.get_url()

    @classmethod
    @abstractmethod
    def from_url(cls, s: str) -> Optional['Submission']:
        pass
