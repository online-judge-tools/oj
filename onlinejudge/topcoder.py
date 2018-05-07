# Python Version: 3.x
import onlinejudge.service
import onlinejudge.problem
import onlinejudge.submission
import onlinejudge.dispatch
import onlinejudge.implementation.utils as utils
import onlinejudge.implementation.logging as log
import re
import bs4
import requests
import urllib.parse
import posixpath
import json
import time
import itertools
import collections


@utils.singleton
class TopCoderService(onlinejudge.service.Service):

    def login(self, get_credentials, session=None):
        session = session or utils.new_default_session()

        # NOTE: you can see this login page with https://community.topcoder.com/longcontest/?module=Submit
        url = 'https://community.topcoder.com/longcontest/'
        username, password = get_credentials()
        data = {
            'nextpage': 'https://www.topcoder.com/',
            'module': 'Login',
            'ha': username,
            'pass': password,
            'rem': 'on',
        }
        resp = utils.request('POST', url, session=session, data=data)

        if 'longcontest' not in resp.url:
            log.success('Success')
            return True
        else:
            log.failure('Failure')
            return False

    def get_url(self):
        return 'https://www.topcoder.com/'

    def get_name(self):
        return 'topcoder'

    @classmethod
    def from_url(cls, s):
        # example: https://www.topcoder.com/
        result = urllib.parse.urlparse(s)
        if result.scheme in ('', 'http', 'https') \
                and result.netloc in [ 'www.topcoder.com', 'community.topcoder.com' ]:
            return cls()


class TopCoderLongContestProblem(onlinejudge.problem.Problem):
    def __init__(self, rd, cd=None, compid=None, pm=None):
        self.rd = rd
        self.cd = cd
        self.compid = compid
        self.pm = pm

    def get_url(self):
        return 'https://community.topcoder.com/tc?module=MatchDetails&rd=' + str(self.rd)

    def get_service(self):
        return TopCoderService()

    @classmethod
    def from_url(cls, s):
        # example: https://community.topcoder.com/longcontest/?module=ViewProblemStatement&rd=16997&pm=14690
        # example: https://community.topcoder.com/longcontest/?module=ViewProblemStatement&rd=16997&compid=57374
        # example: https://community.topcoder.com/longcontest/?module=ViewStandings&rd=16997
        # example: https://community.topcoder.com/tc?module=MatchDetails&rd=16997
        result = urllib.parse.urlparse(s)
        if result.scheme in ('', 'http', 'https') \
                and result.netloc == 'community.topcoder.com' \
                and utils.normpath(result.path) in [ '/longcontest', '/tc' ]:
            querystring = dict(urllib.parse.parse_qsl(result.query))
            if 'rd' in querystring:
                kwargs = {}
                for name in [ 'rd', 'cd', 'compid', 'pm' ]:
                    if name in querystring:
                        kwargs[name] = int(querystring[name])
                return cls(**kwargs)

    def get_language_dict(self, session=None):
        session = session or utils.new_default_session()

        # at 2017/09/21
        return {
                'Java':   { 'value': '1', 'description': 'Java 8' },
                'C++':    { 'value': '3', 'description': 'C++11' },
                'C#':     { 'value': '4', 'description': '' },
                'VB':     { 'value': '5', 'description': '' },
                'Python': { 'value': '6', 'description': 'Pyhton 2' },
            }

    def submit(self, code, language, kind='example', session=None):
        assert kind in [ 'example', 'full' ]
        session = session or utils.new_default_session()

        # module=MatchDetails
        url = 'https://community.topcoder.com/tc?module=MatchDetails&rd=%d' % self.rd
        resp = utils.request('GET', url, session=session)
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        path = soup.find('a', text='Register/Submit').attrs['href']
        assert path.startswith('/') and 'module=ViewReg' in path

        # module=ViewActiveContests
        url = 'https://community.topcoder.com' + path
        resp = utils.request('GET', url, session=session)
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        path = [ tag.attrs['href'] for tag in soup.find_all('a', text='Submit') if ('rd=%d' % self.rd) in tag.attrs['href'] ]
        if len(path) == 0:
            log.error('link to submit not found:  Are you logged in?  Are you registered?  Is the contest running?')
            return None
        assert len(path) == 1
        path = path[0]
        assert path.startswith('/') and 'module=Submit' in path
        query = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(path).query))
        self.cd     = query['cd']
        self.compid = query['compid']

        # module=Submit
        submit_url = 'https://community.topcoder.com' + path
        resp = utils.request('GET', submit_url, session=session)
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)

        # post
        url = 'https://community.topcoder.com/longcontest/'
        language_id = self.get_language_dict(session=session)[language]['value']
        data = {
            'module': 'Submit',
            'rd': self.rd,
            'cd': self.cd,
            'compid': self.compid,
            'Action': 'submit',
            'exOn': { 'example': 'true', 'full': 'false' }[kind],
            'lid': language_id,
            'code': code,
        }
        resp = utils.request('POST', url, session=session, data=data)

        # check if module=SubmitSuccess
        if 'module=SubmitSuccess' in resp.content.decode(resp.encoding):
            url = 'http://community.topcoder.com/longcontest/?module=SubmitSuccess&rd={}&cd={}&compid={}'.format(self.rd, self.cd, self.compid)
            log.success('success: result: %s', url)
            return onlinejudge.submission.CompatibilitySubmission(url)
        else:
            # module=Submit to get error messages
            resp = utils.request('GET', submit_url, session=session)
            soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
            messages = soup.find('textarea', { 'name': 'messages' }).text
            log.failure('%s', messages)
            return None

    def get_standings(self, session=None):
        session = session or utils.new_default_session()

        header = None
        rows = []
        for start in itertools.count(1, 100):
            # get
            url = 'https://community.topcoder.com/longcontest/?sc=&sd=&nr=100&sr={}&rd={}&module=ViewStandings'.format(start, self.rd)
            resp = utils.request('GET', url, session=session)

            # parse
            soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
            table = soup.find('table', class_='statTable')
            trs = table.find_all('tr')
            if header is None:
                tr = trs[1]
                header = [ td.text.strip() for td in tr.find_all('td') ]
            for tr in trs[2 :]:
                row = collections.OrderedDict()
                for key, td in zip(header, tr.find_all('td')):
                    value = td.text.strip()
                    if not value:
                        value = None
                    elif value.isdigit():
                        value = int(value)
                    row[key] = value
                rows += [ row ]

            # check whether the next page exists
            link = soup.find('a', text='next >>')
            if link is None:
                break

        return header, rows

onlinejudge.dispatch.services += [ TopCoderService ]
onlinejudge.dispatch.problems += [ TopCoderLongContestProblem ]
