# Python Version: 3.x
import onlinejudge.implementation.logging as log

submissions = []
def submission_from_url(s):
    for cls in submissions:
        it = cls.from_url(s)
        if it is not None:
            log.status('submission recognized: %s: %s', str(it), s)
            return it
    log.failure('unknown submission: %s', s)

problems = []
def problem_from_url(s):
    for cls in problems:
        it = cls.from_url(s)
        if it is not None:
            log.status('problem recognized: %s: %s', str(it), s)
            return it
    it = submission_from_url(s)
    if it is not None:
        return it.get_problem()
    log.failure('unknown problem: %s', s)

services = []
def service_from_url(s):
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
