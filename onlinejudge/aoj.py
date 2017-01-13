#!/usr/bin/env python3
import onlinejudge.service
import onlinejudge.problem
import onlinejudge.dispatch
import onlinejudge.implementation.utils as utils
import onlinejudge.implementation.logging as log
import re
import io
import os.path
import bs4
import requests
import urllib.parse
import zipfile
import collections


@utils.singleton
class AOJService(onlinejudge.service.Service):

    def get_url(self):
        return 'http://judge.u-aizu.ac.jp/onlinejudge/'

    def get_name(self):
        return 'aoj'

    @classmethod
    def from_url(cls, s):
        if re.match(r'^http://judge\.u-aizu\.ac\.jp/onlinejudge(/(index\.jsp)?)?$', s):
            return cls()


class AOJProblem(onlinejudge.problem.Problem):
    def __init__(self, problem_id):
        self.problem_id = problem_id

    def download(self, session=None):
        session = session or requests.Session()
        url = self.get_url()
        # get
        log.status('GET: %s', url)
        resp = session.get(url)
        log.status(utils.describe_status_code(resp.status_code))
        resp.raise_for_status()
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        samples = utils.SampleZipper()
        for pre in soup.find_all('pre'):
            log.debug('pre: %s', str(pre))
            hn = utils.previous_sibling_tag(pre)
            log.debug('hN: %s', str(hn))
            log.debug(hn)
            if hn and hn.name in [ 'h2', 'h3' ] and hn.string and 'ample' in hn.string.lower(): # 'ample' is the suffix of 'sample', 'example'
                s = utils.textfile(pre.string.lstrip())
                name = hn.string
                samples.add(s, name)
        return samples.get()

    def get_url(self):
        return 'http://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id={}'.format(self.problem_id)

    @classmethod
    def from_url(cls, s):
        m = re.match(r'^http://judge\.u-aizu\.ac\.jp/onlinejudge/description\.jsp\?id=([0-9A-Za-z_]+)$', s)
        if m:
            return cls(m.group(1))

    def get_service(self):
        return AOJService()


onlinejudge.dispatch.services += [ AOJService ]
onlinejudge.dispatch.problems += [ AOJProblem ]
