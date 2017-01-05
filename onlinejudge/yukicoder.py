#!/usr/bin/env python3
import onlinejudge
import onlinejudge.problem
import onlinejudge.implementation.utils as utils
from onlinejudge.logging import logger, prefix
import re
import bs4
import requests
import urllib.parse

class Yukicoder(onlinejudge.problem.OnlineJudge):
    service_name = 'yukicoder'

    def __init__(self, problem_no=None, problem_id=None):
        assert problem_no or problem_id
        assert not problem_no or isinstance(problem_no, int)
        assert not problem_id or isinstance(problem_id, int)
        self.problem_no = problem_no
        self.problem_id = problem_id

    def download(self, session=None):
        content = utils.download(self.get_url(), session)
        soup = bs4.BeautifulSoup(content, 'lxml')
        samples = utils.SampleZipper()
        for pre in soup.find_all('pre'):
            it = self.parse_sample_tag(pre)
            if it is not None:
                s, name = it
                samples.add(s, name)
        return samples.get()

    def parse_sample_tag(self, tag):
        assert isinstance(tag, bs4.Tag)
        assert tag.name == 'pre'
        prv = tag.previous_sibling
        while prv and prv.string and prv.string.strip() == '':
            prv = prv.previous_sibling
        pprv = tag.parent.previous_sibling
        while pprv and pprv.string and pprv.string.strip() == '':
            pprv = pprv.previous_sibling
        if prv.name == 'h6' and tag.parent.name == 'div' and tag.parent['class'] == ['paragraph'] and pprv.name == 'h5':
            return tag.string.lstrip(), pprv.string + ' ' + prv.string

    def get_url(self):
        if self.problem_no:
            return 'https://yukicoder.me/problems/no/{}'.format(self.problem_no)
        elif self.problem_id:
            return 'https://yukicoder.me/problems/{}'.format(self.problem_id)
        else:
            assert False

    @classmethod
    def from_url(cls, s):
        m = re.match('^https?://yukicoder\.me/problems/(no/)?([0-9]+)/?$', s)
        if m:
            n = int(m.group(2).lstrip('0') or '0')
            if m.group(1):
                return cls(problem_no=int(n))
            else:
                return cls(problem_id=int(n))

    def login(self, session, get_credentials, method=None):
        if method == 'github':
            return self.login_with_github(session, get_credentials)
        elif method == 'twitter':
            return self.login_with_twitter(session, get_credentials)
        else:
            assert False
    def login_with_github(self, session, get_credentials):
        url = 'https://yukicoder.me/auth/github'
        logger.info(prefix['status'] + 'GET: %s', url)
        resp = session.get(url)
        logger.info(prefix['info'] + utils.describe_status_code(resp.status_code))
        resp.raise_for_status()
        if urllib.parse.urlparse(resp.url).hostname == 'yukicoder.me':
            logger.info(prefix['info'] + 'You have already signed in.')
            return
        username, password = get_credentials()
        payload = {}
        soup = bs4.BeautifulSoup(resp.content, 'lxml')
        form = soup.find('form')
        logger.debug(prefix['debug'] + 'form: %s', str(form))
        for tag in soup.find_all('input'):
            logger.debug(prefix['debug'] + 'input: %s', str(tag))
            if tag['name']:
                if tag['name'] == 'login':
                    value = username
                elif tag['name'] == 'password':
                    value = password
                elif tag['value']:
                    value = tag['value']
                else:
                    continue
                payload[tag['name']] = value
        url = urllib.parse.urljoin(resp.url, form['action'])
        logger.info(prefix['status'] + 'POST: %s', url)
        resp = session.post(url, data=payload)
        logger.info(prefix['info'] + utils.describe_status_code(resp.status_code))
        resp.raise_for_status()
        if urllib.parse.urlparse(resp.url).hostname == 'yukicoder.me':
            logger.info(prefix['success'] + 'You signed in.')
        else:
            logger.error(prefix['error'] + 'You failed to sign in. Wrong user ID or password.')
            raise requests.HTTPError

    def login_with_twitter(self, session, get_credentials):
        url = 'https://yukicoder.me/auth/twitter'
        raise NotImplementedError

onlinejudge.problem.list += [ Yukicoder ]
