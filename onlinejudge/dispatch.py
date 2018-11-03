# Python Version: 3.x
import onlinejudge.implementation.logging as log
import onlinejudge.submissions as Submission
import onlinejudge.problems as Problem
import onlinejudge.services as Service
from typing import List, Type

submissions: List[Type[Submission]] = []
def submission_from_url(s: str) -> Submission:
    for cls in submissions:
        it = cls.from_url(s)
        if it is not None:
            log.status('submission recognized: %s: %s', str(it), s)
            return it
    log.failure('unknown submission: %s', s)

problems: List[Type[Problem]] = []
def problem_from_url(s: str) -> Problem:
    for cls in problems:
        it = cls.from_url(s)
        if it is not None:
            log.status('problem recognized: %s: %s', str(it), s)
            return it
    it = submission_from_url(s)
    if it is not None:
        return it.get_problem()
    log.failure('unknown problem: %s', s)

services: List[Type[Service]] = []
def service_from_url(s: str) -> Service:
    for cls in services:
        it = cls.from_url(s)
        if it is not None:
            log.status('service recognized: %s: %s', str(it), s)
            return it
    it = submission_from_url(s)
    if it is not None:
        return it.get_service()
    it = problem_from_url(s)
    if it is not None:
        return it.get_service()
    log.failure('unknown service: %s', s)
