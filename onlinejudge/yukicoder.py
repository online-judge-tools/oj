#!/usr/bin/env python3
import onlinejudge
import onlinejudge.problem
import onlinejudge.implementation.utils as utils
import re
import bs4

class Yukicoder(onlinejudge.problem.OnlineJudge):
    onlinejudge_name = 'yukicoder'

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

onlinejudge.problem.list += [ Yukicoder ]
