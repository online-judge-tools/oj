#!/usr/bin/env python3
import onlinejudge.implementation.logging as log

problems = []
def problem_from_url(s):
    for cls in problems:
        it = cls.from_url(s)
        if it is not None:
            log.status('problem recognized: %s: %s', str(it), s)
            return it
    log.failure('unknown problem: %s', s)

services = []
def service_from_url(s):
    for cls in services:
        it = cls.from_url(s)
        if it is not None:
            log.status('service recognized: %s: %s', str(it), s)
            return it
    it = problem_from_url(s)
    if it is not None:
        return it.get_service()
    log.failure('unknown service: %s', s)
