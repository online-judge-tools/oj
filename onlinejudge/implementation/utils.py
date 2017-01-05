#!/usr/bin/env python3
import re
import os
import os.path
import requests
import contextlib
import http.cookiejar
import http.client # for the description string of status codes
from onlinejudge.logging import logger, prefix

def download(url, session, get_options={}):
    logger.info(prefix['status'] + 'GET: %s', url)
    if session is None:
        session = requests.Session()
    resp = session.get(url, **get_options)
    if resp.status_code != 200:
        logger.error(prefix['error'] + '%d %s', resp.status_code, http.client.responses[resp.status_code])
        raise requests.HTTPError
    logger.info(prefix['success'] + '%d %s', resp.status_code, http.client.responses[resp.status_code])
    return resp.content

@contextlib.contextmanager
def session(cookiejar):
    s = requests.Session()
    s.cookies = http.cookiejar.LWPCookieJar(cookiejar)
    if os.path.exists(cookiejar):
        logger.info(prefix['info'] + 'load cookie from: %s', cookiejar)
        s.cookies.load()
    yield s
    logger.info(prefix['info'] + 'save cookie to: %s', cookiejar)
    if os.path.dirname(cookiejar):
        os.makedirs(os.path.dirname(cookiejar), exist_ok=True)
    s.cookies.save()
    os.chmod(cookiejar, 0o600)  # NOTE: to make secure a little bit

class SampleZipper(object):
    def __init__(self):
        self.data = []
        self.dangling = None

    def add(self, s, name=''):
        if self.dangling is None:
            if re.search('output', name, re.IGNORECASE) or re.search('出力', name):
                logger.warning(prefix['warning'] + 'strange name for input string: %s: %s', name, repr(s))
            self.dangling = (s, name)
        else:
            if re.search('input', name, re.IGNORECASE) or re.search('入力', name):
                logger.warning(prefix['warning'] + 'strange name for output string: %s: %s', name, repr(s))
            self.data += [( self.dangling, (s, name) )]
            self.dangling = None

    def get(self):
        if self.dangling is not None:
            logger.warning(prefix['warning'] + 'dangling sample string: %s: %s', self.dangling[1], repr(self.dangling[0]))
        return self.data
