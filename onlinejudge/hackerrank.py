#!/usr/bin/env python3
import onlinejudge.service
import onlinejudge.problem
import onlinejudge.dispatch
import onlinejudge.implementation.utils as utils
import onlinejudge.implementation.logging as log
import re
import bs4
import requests
import urllib.parse
import json
import datetime
import time


@utils.singleton
class HackerRankService(onlinejudge.service.Service):

    def login(self, get_credentials, session=None):
        session = session or requests.Session()
        url = 'https://www.hackerrank.com/login'
        # get
        log.status('GET: %s', url)
        resp = session.get(url)
        log.status(utils.describe_status_code(resp.status_code))
        resp.raise_for_status()
        if resp.url != url:
            log.info('You have already signed in.')
            return True
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        form = soup.find('form', id='legacy-login')
        if not form:
            log.error('form not found')
            return False
        csrftoken = soup.find('meta', attrs={ 'name': 'csrf-token' }).attrs['content']
        # post
        username, password = get_credentials()
        form = utils.FormSender(form, url=resp.url)
        form.set('login', username)
        form.set('password', password)
        form.set('remember_me', 'true')
        form.set('fallback', 'true')
        resp = form.request(session, action='/auth/login', headers={ 'X-CSRF-Token': csrftoken })
        resp.raise_for_status()
        # result
        if resp.url != url:
            log.success('You signed in.')
            return True
        else:
            log.failure('You failed to sign in. Wrong user ID or password.')
            return False

    def get_url(self):
        return 'https://www.hackerrank.com/'

    def get_name(self):
        return 'hackerrank'

    @classmethod
    def from_url(cls, s):
        if re.match(r'^https?://www\.hackerrank\.com/?$', s):
            return cls()
        if re.match(r'^https?://www\.hackerrank\.com/domains/?$', s):
            return cls()


class HackerRankProblem(onlinejudge.problem.Problem):
    def __init__(self, contest_name, challange_name):
        self.contest_name = contest_name
        self.challange_name = challange_name

    def download(self, session=None, method='run_code'):
        if method == 'run_code':
            return self.download_with_running_code(session=session)
        elif method == 'parse_html':
            return self.download_with_parsing_html(session=session)
        else:
            assert False

    def download_with_running_code(self, session=None):
        session = session or requests.Session()
        # get
        url = self.get_url()
        log.status('GET: %s', url)
        resp = session.get(url)
        log.status(utils.describe_status_code(resp.status_code))
        resp.raise_for_status()
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        csrftoken = soup.find('meta', attrs={ 'name': 'csrf-token' }).attrs['content']
        # post
        url = 'https://www.hackerrank.com/rest/contests/{}/challenges/{}/compile_tests'.format(self.contest_name, self.challange_name)
        payload = { 'code': ':', 'language': 'bash', 'customtestcase': False }
        log.debug('payload: %s', payload)
        log.status('POST: %s', url)
        resp = session.post(url, json=payload, headers={ 'X-CSRF-Token': csrftoken })
        log.status(utils.describe_status_code(resp.status_code))
        resp.raise_for_status()
        # parse
        it = json.loads(resp.content.decode())
        log.debug('json: %s', it)
        if not it['status']:
            log.error('Run Code: fails')
            return []
        model_id = it['model']['id']
        now = datetime.datetime.now()
        unixtime = int(datetime.datetime.now().timestamp() * 10**3)
        url = 'https://www.hackerrank.com/rest/contests/{}/challenges/{}/compile_tests/{}?_={}'.format(self.contest_name, self.challange_name, it['model']['id'], unixtime)
        # sleep
        log.status('sleep(3)')
        time.sleep(3)
        # get
        log.status('GET: %s', url)
        resp = session.get(url, headers={ 'X-CSRF-Token': csrftoken })
        log.status(utils.describe_status_code(resp.status_code))
        resp.raise_for_status()
        # parse
        it = json.loads(resp.content.decode())
        log.debug('json: %s', it)
        if not it['status']:
            log.error('Run Code: fails')
            return []
        samples = []
        for i, (inf, outf) in enumerate(zip(it['model']['stdin'], it['model']['expected_output'])):
            inname  = 'Testcase {} Input'.format(i)
            outname = 'Testcase {} Expected Output'.format(i)
            samples += [[ ( utils.textfile(inf), inname ), ( utils.textfile(outf), outname ) ]]
        return samples


    def download_with_parsing_html(self, session=None):
        session = session or requests.Session()
        url = 'https://www.hackerrank.com/rest/contests/{}/challenges/{}'.format(self.contest_name, self.challange_name)
        raise NotImplementedError

    def get_url(self):
        return 'https://www.hackerrank.com/contests/{}/challenges/{}'.format(self.contest_name, self.challange_name)

    def get_service(self):
        return HackerRankService()

    @classmethod
    def from_url(cls, s):
        m = re.match(r'^https?://www\.hackerrank\.com/contests/([0-9A-Za-z-]+)/challenges/([0-9A-Za-z-]+)/?$', s)
        if m:
            return cls(m.group(1), m.group(2))


onlinejudge.dispatch.services += [ HackerRankService ]
onlinejudge.dispatch.problems += [ HackerRankProblem ]
