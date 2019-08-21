# Python Version: 3.x
from abc import ABC, abstractmethod
from typing import Any, Callable, Iterator, List, NamedTuple, NewType, Optional, Tuple

import requests

CredentialsProvider = Callable[[], Tuple[str, str]]


class LoginError(RuntimeError):
    pass


class Service(ABC):
    def login(self, *, get_credentials: CredentialsProvider, session: Optional[requests.Session] = None) -> None:
        """
        :param get_credentials: returns a tuple of (username, password)
        :raises LoginError:
        """
        raise NotImplementedError

    def is_logged_in(self, *, session: Optional[requests.Session] = None) -> bool:
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

    def iterate_contests(self, *, session: Optional[requests.Session] = None) -> Iterator['Contest']:
        raise NotImplementedError


TestCase = NamedTuple('TestCase', [
    ('name', str),
    ('input_name', str),
    ('input_data', bytes),
    ('output_name', str),
    ('output_data', bytes),
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


class SampleParsingError(RuntimeError):
    pass


class SubmissionError(RuntimeError):
    pass


class Contest(ABC):
    """
    :note: :py:class:`Contest` represents just a URL of a contest, without the data of the contest.
    """
    def download_name(self, *, session: Optional[requests.Session] = None) -> str:
        content = self.download_content(session=session)  # type: Any
        return content.name

    def list_problems(self, *, session: Optional[requests.Session] = None) -> List['Problem']:
        content = self.download_content(session=session)  # type: Any
        return content.problems

    def download_content(self, *, session: Optional[requests.Session] = None) -> tuple:
        """
        :note: The returned values vary depending on the implementation.
        """
        raise NotImplementedError

    def iterate_submissions(self, *, session: Optional[requests.Session] = None) -> Iterator['Submission']:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_url(self, s: str) -> Optional['Contest']:
        pass


class Problem(ABC):
    """
    :note: :py:class:`Problem` represents just a URL of a problem, without the data of the problem.
           :py:class:`Problem` はちょうど問題の URL のみを表現します。キャッシュや内部状態は持ちません。
    """
    @abstractmethod
    def download_sample_cases(self, *, session: Optional[requests.Session] = None) -> List[TestCase]:
        """
        :raises SampleParsingError:
        """
        raise NotImplementedError

    def download_system_cases(self, *, session: Optional[requests.Session] = None) -> List[TestCase]:
        """
        :raises NotLoggedInError:
        """
        raise NotImplementedError

    def submit_code(self, code: bytes, language_id: LanguageId, *, filename: Optional[str] = None, session: Optional[requests.Session] = None) -> 'Submission':
        """
        :param code:
        :arg language_id: :py:class:`LanguageId`
        :raises NotLoggedInError:
        :raises SubmissionError:
        """
        raise NotImplementedError

    def get_available_languages(self, *, session: Optional[requests.Session] = None) -> List[Language]:
        raise NotImplementedError

    @abstractmethod
    def get_url(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_service(self) -> Service:
        raise NotImplementedError

    def download_name(self, *, session: Optional[requests.Session] = None) -> str:
        """
        example:

        -   `器物損壊！高橋君`
        -   `AtCoDeerくんと変なじゃんけん / AtCoDeer and Rock-Paper`
        -   `Xor Sum`
        """
        content = self.download_content(session=session)  # type: Any
        return content.name

    def download_content(self, *, session: Optional[requests.Session] = None) -> tuple:
        """
        :note: The returned values vary depending on the implementation.
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
    def download_code(self, *, session: Optional[requests.Session] = None) -> bytes:
        content = self.download_content(session=session)  # type: Any
        return content.source_code

    def download_content(self, *, session: Optional[requests.Session] = None) -> tuple:
        """
        :note: The returned values vary depending on the implementation.
        """
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
