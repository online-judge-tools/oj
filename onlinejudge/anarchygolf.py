#!/usr/bin/env python3
import onlinejudge.service
import onlinejudge.problem
import onlinejudge.dispatch
import onlinejudge.implementation.utils as utils
import onlinejudge.implementation.logging as log
import re
import bs4
import requests


@utils.singleton
class AnarchyGolfService(onlinejudge.service.Service):

    def get_url(self):
        return 'http://golf.shinh.org/'

    def get_name(self):
        return 'anarchygolf'

    @classmethod
    def from_url(cls, s):
        if re.match(r'^http://golf\.shinh\.org/?$', s):
            return cls()


class AnarchyGolfProblem(onlinejudge.problem.Problem):
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
        for h2 in soup.find_all('h2'):
            it = self._parse_sample_tag(h2)
            if it is not None:
                s, name = it
                samples.add(s, name)
        return samples.get()

    def _parse_sample_tag(self, tag):
        assert isinstance(tag, bs4.Tag)
        assert tag.name == 'h2'
        name = tag.contents[0]
        if ':' in name:
            name = name[:  name.find(':') ]
        if name in [ 'Sample input', 'Sample output' ]:
            nxt = tag.next_sibling
            while nxt and nxt.string.strip() == '':
                nxt = nxt.next_sibling
            if nxt.name == 'pre':
                s = utils.textfile(utils.dos2unix(nxt.string.lstrip()))
            else:
                s = ''
            return s, name

    def get_url(self):
        return 'http://golf.shinh.org/p.rb?{}'.format(self.problem_id)

    def get_service(self):
        return AnarchyGolfService()

    @classmethod
    def from_url(cls, s):
        m = re.match(r'^http://golf\.shinh\.org/p\.rb\?([0-9A-Za-z_+]+)$', s)
        if m:
            return cls(m.group(1))


onlinejudge.dispatch.services += [ AnarchyGolfService ]
onlinejudge.dispatch.problems += [ AnarchyGolfProblem ]
