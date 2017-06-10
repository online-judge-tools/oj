# Python Version: 3.x
# -*- coding: utf-8 -*-
import onlinejudge.service
import onlinejudge.problem
import onlinejudge.dispatch
import onlinejudge.implementation.utils as utils
import onlinejudge.implementation.logging as log
import io
import posixpath
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
        # example: http://judge.u-aizu.ac.jp/onlinejudge/
        result = urllib.parse.urlparse(s)
        if result.scheme in ('', 'http', 'https') \
                and result.netloc == 'judge.u-aizu.ac.jp':
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
            if hn is None:
                div = pre.parent
                if div is not None:
                    log.debug('div: %s', str(hn))
                    hn = utils.previous_sibling_tag(div)
            log.debug('hN: %s', str(hn))
            log.debug(hn)
            keywords = [ 'sample', 'example', '入力例', '出力例' ]
            if hn and hn.name in [ 'h2', 'h3' ] and hn.string and any(filter(lambda keyword: keyword in hn.string.lower(), keywords)):
                s = utils.textfile(pre.string.lstrip())
                name = hn.string
                samples.add(s, name)
        return samples.get()

    def get_url(self):
        return 'http://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id={}'.format(self.problem_id)

    @classmethod
    def from_url(cls, s):
        # example: http://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=1169
        # example: http://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=DSL_1_A&lang=jp
        result = urllib.parse.urlparse(s)
        querystring = urllib.parse.parse_qs(result.query)
        if result.scheme in ('', 'http', 'https') \
                and result.netloc == 'judge.u-aizu.ac.jp' \
                and posixpath.normpath(result.path) == '/onlinejudge/description.jsp' \
                and querystring.get('id') \
                and len(querystring['id']) == 1:
            n, = querystring['id']
            return cls(n)

    def get_service(self):
        return AOJService()


onlinejudge.dispatch.services += [ AOJService ]
onlinejudge.dispatch.problems += [ AOJProblem ]