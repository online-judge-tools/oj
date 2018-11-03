# Python Version: 3.x
import onlinejudge.implementation.logging as log
from typing import List, Optional, Type, TYPE_CHECKING
if TYPE_CHECKING:
    from onlinejudge.submission import Submission
    from onlinejudge.problem import Problem
    from onlinejudge.service import Service

submissions: List[Type['Submission']] = []
def submission_from_url(s: str) -> Optional['Submission']:
    for cls in submissions:
        submission = cls.from_url(s)
        if submission is not None:
            log.status('submission recognized: %s: %s', str(submission), s)
            return submission
    log.failure('unknown submission: %s', s)
    return None

problems: List[Type['Problem']] = []
def problem_from_url(s: str) -> Optional['Problem']:
    for cls in problems:
        problem = cls.from_url(s)
        if problem is not None:
            log.status('problem recognized: %s: %s', str(problem), s)
            return problem
    submission = submission_from_url(s)
    if submission is not None:
        return submission.get_problem()
    log.failure('unknown problem: %s', s)
    return None

services: List[Type['Service']] = []
def service_from_url(s: str) -> Optional['Service']:
    for cls in services:
        service = cls.from_url(s)
        if service is not None:
            log.status('service recognized: %s: %s', str(service), s)
            return service
    submission = submission_from_url(s)
    if submission is not None:
        return submission.get_service()
    problem = problem_from_url(s)
    if problem is not None:
        return problem.get_service()
    log.failure('unknown service: %s', s)
    return None
