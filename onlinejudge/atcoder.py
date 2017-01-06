#!/usr/bin/env python3
import onlinejudge.problem
import onlinejudge.implementation.utils as utils
import onlinejudge.implementation.logging as log
import re
import bs4
import requests
import http.client # for the description string of status codes

class AtCoder(onlinejudge.problem.OnlineJudge):
    service_name = 'atcoder'

    def __init__(self, contest_id, problem_id):
        self.contest_id = contest_id
        self.problem_id = problem_id

    def download(self, session=None):
        content = utils.download(self.get_url(), session, get_options={ 'allow_redirects': False })  # allow_redirects: if the URL is wrong, AtCoder redirects to the top page
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
        try:
            prv = tag.previous_sibling
            while prv and prv.string.strip() == '':
                prv = prv.previous_sibling
            if prv.name == 'h3' and tag.parent.name == 'section':
                return tag.string.strip().replace('\r\n', '\n') + '\n', prv.string
        except AttributeError:
            pass
        try:
            prv = tag.parent.previous_sibling
            while prv and prv.string.strip() == '':
                prv = prv.previous_sibling
            if tag.parent.name == 'section' and prv.name == 'h3':
                return tag.string.strip().replace('\r\n', '\n') + '\n', prv.string
        except AttributeError:
            pass

    def get_url(self):
        return 'http://{}.contest.atcoder.jp/tasks/{}'.format(self.contest_id, self.problem_id)

    @classmethod
    def from_url(cls, s):
        m = re.match('^https?://([0-9A-Za-z-]+)\.contest\.atcoder\.jp/tasks/([0-9A-Za-z_]+)/?$', s)
        if m:
            return cls(m.group(1), m.group(2))

    def login(self, get_credentials, sesison=None):
        url = 'https://{}.contest.atcoder.jp/login'.format(self.contest_id)
        log.status('GET: %s', url)
        resp = session.get(url, allow_redirects=False)
        log.status(utils.describe_status_code(resp.status_code))
        if resp.status_code == 302:  # AtCoder redirects to the top page if success
            log.info('You have already signed in.')
            return
        username, password = get_credentials()
        log.status('POST: %s', url)
        resp = session.post(url, data={ 'name': username, 'password': password }, allow_redirects=False)
        if resp.status_code == 302:  # AtCoder redirects to the top page if success
            log.success(utils.describe_status_code(resp.status_code))
            log.success('You signed in.')
        else:
            log.failure(utils.describe_status_code(resp.status_code))
            log.failure('You failed to sign in. Wrong user ID or password.')
            raise requests.HTTPError

onlinejudge.problem.list += [ AtCoder ]
