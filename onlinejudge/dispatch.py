# Python Version: 3.x
"""
.. py:data:: services

    :type: :py:class:`List` [ :py:class:`Type` [ :py:class:`onlinejudge.type.Service` ] ]

    contains classes to use for :py:func:`service_from_url`

.. py:data:: problems

    :type: :py:class:`List` [ :py:class:`Type` [ :py:class:`onlinejudge.type.Problem` ] ]

    contains classes to use for :py:func:`problem_from_url`

.. py:data:: submissions

    :type: :py:class:`List` [ :py:class:`Type` [ :py:class:`onlinejudge.type.Submission` ] ]

    contains classes to use for :py:func:`submission_from_url`
"""

from typing import List, Optional, Type

import onlinejudge._implementation.logging as log
from onlinejudge.type import Contest, Problem, Service, Submission

submissions = []  # type: List[Type['Submission']]


def submission_from_url(url: str) -> Optional[Submission]:
    for cls in submissions:
        submission = cls.from_url(url)
        if submission is not None:
            log.status('submission recognized: %s: %s', str(submission), url)
            return submission
    log.failure('unknown submission: %s', url)
    return None


problems = []  # type: List[Type['Problem']]


def problem_from_url(url: str) -> Optional[Problem]:
    """
    >>> onlinejudge.dispatch.problem_from_url("https://atcoder.jp/contests/abc077/tasks/arc084_b")
    <onlinejudge.service.atcoder.AtCoderProblem object at 0x7fa0538ead68>

    >>> onlinejudge.dispatch.problem_from_url("https://codeforces.com/contest/1012/problem/D")
    <onlinejudge.service.codeforces.CodeforcesProblem object at 0x7fa05a916710>
    """

    for cls in problems:
        problem = cls.from_url(url)
        if problem is not None:
            log.status('problem recognized: %s: %s', str(problem), url)
            return problem
    log.failure('unknown problem: %s', url)
    return None


contests = []  # type: List[Type['Contest']]


def contest_from_url(url: str) -> Optional[Contest]:
    for cls in contests:
        contest = cls.from_url(url)
        if contest is not None:
            log.status('contest recognized: %s: %s', str(contest), url)
            return contest
    log.failure('unknown contest: %s', url)
    return None


services = []  # type: List[Type['Service']]


def service_from_url(url: str) -> Optional[Service]:
    for cls in services:
        service = cls.from_url(url)
        if service is not None:
            log.status('service recognized: %s: %s', str(service), url)
            return service
    submission = submission_from_url(url)
    if submission is not None:
        return submission.get_service()
    problem = problem_from_url(url)
    if problem is not None:
        return problem.get_service()
    log.failure('unknown service: %s', url)
    return None
