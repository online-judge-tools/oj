# Python Version: 3.x
import onlinejudge.type
import onlinejudge.dispatch
import onlinejudge.implementation.utils as utils
import onlinejudge.implementation.logging as log
import urllib.parse
import posixpath
import bs4
import requests
from typing import *


@utils.singleton
class AnarchyGolfService(onlinejudge.type.Service):

    def get_url(self) -> str:
        return 'http://golf.shinh.org/'

    def get_name(self) -> str:
        return 'anarchygolf'

    @classmethod
    def from_url(cls, s: str) -> Optional['AnarchyGolfService']:
        # example: http://golf.shinh.org/
        result = urllib.parse.urlparse(s)
        if result.scheme in ('', 'http', 'https') \
                and result.netloc == 'golf.shinh.org':
            return cls()
        return None


class AnarchyGolfProblem(onlinejudge.type.Problem):
    def __init__(self, problem_id: str):
        self.problem_id = problem_id

    def download_sample_cases(self, session: Optional[requests.Session] = None) -> List[onlinejudge.type.TestCase]:
        session = session or utils.new_default_session()
        # get
        resp = utils.request('GET', self.get_url(), session=session)
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        samples = utils.SampleZipper()
        for h2 in soup.find_all('h2'):
            it = self._parse_sample_tag(h2)
            if it is not None:
                s, name = it
                samples.add(s, name)
        return samples.get()

    def _parse_sample_tag(self, tag: bs4.Tag) -> Optional[Tuple[str, str]]:
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
        return None

    def get_url(self) -> str:
        return 'http://golf.shinh.org/p.rb?{}'.format(self.problem_id)

    def get_service(self) -> AnarchyGolfService:
        return AnarchyGolfService()

    @classmethod
    def from_url(cls, s: str) -> Optional['AnarchyGolfProblem']:
        # example: http://golf.shinh.org/p.rb?The+B+Programming+Language
        result = urllib.parse.urlparse(s)
        if result.scheme in ('', 'http', 'https') \
                and result.netloc == 'golf.shinh.org' \
                and utils.normpath(result.path) == '/p.rb' \
                and result.query:
            return cls(result.query)
        return None


onlinejudge.dispatch.services += [ AnarchyGolfService ]
onlinejudge.dispatch.problems += [ AnarchyGolfProblem ]
