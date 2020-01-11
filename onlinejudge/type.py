# Python Version: 3.x
"""
the module containing base types

:note: Some methods are not implemented in subclasses.
    Please check the definitions of subclasses under :py:mod:`onlinejudge.service`.
"""

import datetime
from abc import ABC, abstractmethod
from typing import Callable, Iterator, List, NamedTuple, NewType, Optional, Sequence, Tuple

import requests

CredentialsProvider = Callable[[], Tuple[str, str]]


class LoginError(RuntimeError):
    def __init__(self, message: str = 'failed to login'):
        super().__init__(message)


class Service(ABC):
    def login(self, *, get_credentials: CredentialsProvider, session: Optional[requests.Session] = None) -> None:
        """
        :param get_credentials: returns a tuple of (username, password)
        :raises LoginError:
        """
        raise NotImplementedError

    def get_url_of_login_page(self) -> str:
        """
        .. versionadded:: 7.0.0
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
        """
        .. versionadded:: 7.0.0
        """
        raise NotImplementedError


TestCase = NamedTuple('TestCase', [
    ('name', str),
    ('input_name', str),
    ('input_data', bytes),
    ('output_name', str),
    ('output_data', bytes),
])
"""
.. versionchanged:: 7.0.0
"""

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
    def __init__(self, message: str = 'login required'):
        super().__init__(message)


class SampleParseError(RuntimeError):
    """
    .. versionadded:: 7.0.0
    """
    def __init__(self, message: str = 'failed to parse samples'):
        super().__init__(message)


class SubmissionError(RuntimeError):
    def __init__(self, message: str = 'failed to submit'):
        super().__init__(message)


class DownloadedData(ABC):
    """
    :note: :py:class:`DownloadedData` and its subclasses represent contents which are obtained by network access. The values may depends your session.
           :py:class:`DownloadedData` とそのサブクラスは、ネットワークアクセスの結果得られるようなデータを表現します。その値はログイン状況などにより接続のたびに変化することがあります。

    .. versionadded:: 7.0.0
    """
    @property
    @abstractmethod
    def url(self) -> str:
        raise NotImplementedError

    @property
    def json(self) -> Optional[bytes]:
        return None

    @property
    def html(self) -> Optional[bytes]:
        return None

    @property
    def timestamp(self) -> Optional[datetime.datetime]:
        return None

    @property
    def session(self) -> Optional[requests.Session]:
        return None

    @property
    def response(self) -> Optional[requests.Response]:
        return None


class ContestData(DownloadedData):
    """
    .. versionadded:: 7.0.0
    """
    def url(self) -> str:
        return self.contest.get_url()

    @property
    @abstractmethod
    def contest(self) -> 'Contest':
        raise NotImplementedError

    @property
    def service(self) -> Service:
        return self.contest.get_service()

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError


class Contest(ABC):
    """
    :note: :py:class:`Contest` represents just a URL of a contest, without the data of the contest.

    .. versionadded:: 7.0.0
    """
    def list_problems(self, *, session: Optional[requests.Session] = None) -> Sequence['Problem']:
        raise NotImplementedError

    def download_data(self, *, session: Optional[requests.Session] = None) -> ContestData:
        raise NotImplementedError

    def iterate_submissions(self, *, session: Optional[requests.Session] = None) -> Iterator['Submission']:
        """
        .. versionadded:: 7.0.0
        """
        raise NotImplementedError

    @abstractmethod
    def get_url(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_service(self) -> Service:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_url(self, s: str) -> Optional['Contest']:
        pass


class ProblemData(DownloadedData):
    """
    .. versionadded:: 7.0.0
    """
    def url(self) -> str:
        return self.problem.get_url()

    @property
    @abstractmethod
    def problem(self) -> 'Problem':
        raise NotImplementedError

    @property
    def contest(self) -> Contest:
        return self.problem.get_contest()

    @property
    def service(self) -> Service:
        return self.problem.get_service()

    @property
    @abstractmethod
    def name(self) -> str:
        """
        for example of :py:class:`Problem`:

        -   `器物損壊！高橋君`
        -   `AtCoDeerくんと変なじゃんけん / AtCoDeer and Rock-Paper`
        -   `Xor Sum`
        """
        raise NotImplementedError

    @property
    def sample_cases(self) -> Optional[List[TestCase]]:
        raise NotImplementedError


class Problem(ABC):
    """
    :note: :py:class:`Problem` represents just a URL of a problem, without the data of the problem.
           :py:class:`Problem` はちょうど問題の URL のみを表現します。キャッシュや内部状態は持ちません。
    """
    @abstractmethod
    def download_sample_cases(self, *, session: Optional[requests.Session] = None) -> List[TestCase]:
        """
        :raises SampleParseError:

        .. versionchanged:: 7.0.0
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

    def get_contest(self) -> Contest:
        raise NotImplementedError

    @abstractmethod
    def get_service(self) -> Service:
        raise NotImplementedError

    def download_data(self, *, session: Optional[requests.Session] = None) -> ProblemData:
        """
        .. versionadded:: 7.0.0
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


class SubmissionData(DownloadedData):
    """
    .. versionadded:: 7.0.0
    """
    def url(self) -> str:
        return self.submission.get_url()

    @property
    @abstractmethod
    def submission(self) -> 'Submission':
        raise NotImplementedError

    @property
    def service(self) -> Service:
        return self.submission.get_service()

    @property
    def source_code(self) -> bytes:
        raise NotImplementedError

    @property
    @abstractmethod
    def status(self) -> str:
        raise NotImplementedError


class Submission(ABC):
    def download_data(self, *, session: Optional[requests.Session] = None) -> SubmissionData:
        """
        .. versionadded:: 7.0.0
        """
        raise NotImplementedError

    @abstractmethod
    def get_url(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def download_problem(self, *, session: Optional[requests.Session] = None) -> Problem:
        raise NotImplementedError

    def download_contest(self) -> Contest:
        return self.download_problem().get_contest()

    @abstractmethod
    def get_service(self) -> Service:
        raise NotImplementedError

    def __repr__(self) -> str:
        return '{}.from_url({})'.format(self.__class__.__name__, repr(self.get_url()))

    def __eq__(self, other) -> bool:
        return self.__class__ == other.__class__ and self.get_url() == other.get_url()

    @classmethod
    @abstractmethod
    def from_url(cls, s: str) -> Optional['Submission']:
        raise NotImplementedError
