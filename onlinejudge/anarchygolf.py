#!/usr/bin/env python3
import onlinejudge.problem
import onlinejudge.implementation.utils as utils
import onlinejudge.implementation.logging as log
import re
import bs4

class AnarchyGolf(onlinejudge.problem.OnlineJudge):
    service_name = 'anarchygolf'

    def __init__(self, problem_id):
        self.problem_id = problem_id

    def download(self, session=None):
        content = utils.download(self.get_url(), session, get_options={ 'allow_redirects': False })  # allow_redirects: if the URL is wrong, AtCoder redirects to the top page
        soup = bs4.BeautifulSoup(content, 'lxml')
        samples = utils.SampleZipper()
        for h2 in soup.find_all('h2'):
            it = self.parse_sample_tag(h2)
            if it is not None:
                s, name = it
                samples.add(s, name)
        return samples.get()

    def parse_sample_tag(self, tag):
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
                s = nxt.string.lstrip()
            else:
                s = ''
            return s, name

    def get_url(self):
        return 'http://golf.shinh.org/p.rb?{}'.format(self.problem_id)

    @classmethod
    def from_url(cls, s):
        m = re.match('^http://golf\.shinh\.org/p\.rb\?([0-9A-Za-z_+]+)$', s)
        if m:
            return cls(m.group(1))

onlinejudge.problem.list += [ AnarchyGolf ]
