# Python Version: 3.x
"""
the module for CodeChef (https://www.codechef.com/)
"""

import re
import urllib.parse
from typing import *

import bs4
import requests

import onlinejudge._implementation.logging as log
import onlinejudge._implementation.testcase_zipper
import onlinejudge._implementation.utils as utils
import onlinejudge.dispatch
import onlinejudge.type
from onlinejudge.type import SampleParseError


class CodeChefService(onlinejudge.type.Service):
    def get_url(self) -> str:
        return 'https://www.codechef.com/'

    def get_name(self) -> str:
        return 'CodeChef'

    @classmethod
    def from_url(cls, url: str) -> Optional['CodeChefService']:
        # example: https://www.codechef.com/
        result = urllib.parse.urlparse(url)
        if result.scheme in ('', 'http', 'https') \
                and result.netloc == 'www.codechef.com':
            return cls()
        return None


class CodeChefProblem(onlinejudge.type.Problem):
    def __init__(self, *, contest_id: str, problem_id: str):
        self.contest_id = contest_id
        self.problem_id = problem_id

    def download_sample_cases(self, *, session: Optional[requests.Session] = None) -> List[onlinejudge.type.TestCase]:
        session = session or utils.get_default_session()

        # get
        url = self.get_url()
        resp = utils.request('GET', url, session=session)

        # parse HTML
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        for div in soup.find_all('div', class_='content'):
            # TODO: find a proper way to detect this tag
            # find a tag which contains something like Markdown
            if len(list(filter(lambda line: line.startswith('###'), div.decode_contents().splitlines()))) >= 3:
                log.debug('%s', str(div))
                break
        else:
            raise SampleParseError('no markdown')

        # parse Markdown
        # TODO: Should we use a Markdown parser? But I want to avoid making a new dependency only for CodeChef
        # pattern 1: "### Example Input" and a code block  https://www.codechef.com/COOK113A/problems/DAND
        # pattern 2: "###Sample Input:" and a indent https://www.codechef.com/PLIN2020/problems/CNTSET
        # not implemented: "<h3>Example</h3> <pre><b>Input:</b> 1 5 1 2 3 4 5 <b>Output:</b> 2 </pre>" https://www.codechef.com/CNES2017/problems/ACESQN
        def iterate():
            header = None  # type: Optional[str]
            fenced = None  # type: Optional[str]
            indented = None  # type: Optional[str]
            for line in div.decode_contents().splitlines(keepends=True):
                if indented and not (line.startswith(' ' * 4) or line.startswith('\t')):
                    yield header, indented
                    indented = None
                if line.startswith('###'):
                    header = ' '.join(line.strip(' \r\n#:').split())
                elif not fenced and (line.startswith(' ' * 4) or line.startswith('\t')):
                    if indented is None:
                        indented = ''
                    indented += line.lstrip()
                elif not indented and line.rstrip() == '```':
                    if fenced is None:
                        fenced = ''
                    else:
                        yield header, fenced
                        fenced = None
                else:
                    if fenced is not None:
                        fenced += line
            if indented:
                yield header, indented
                indented = None

        # make a testcase object
        name = None  # type: Optional[str]
        input_name = None  # type: Optional[str]
        input_data = None  # type: Optional[bytes]
        output_name = None  # type: Optional[str]
        output_data = None  # type: Optional[bytes]
        for header, codeblock in iterate():
            if header is None:
                pass
            elif header.lower() in ('sample input', 'example input'):
                if input_data is not None:
                    raise SampleParseError('two inputs found')
                input_name = header
                input_data = codeblock.encode()
            elif header.lower() in ('sample output', 'example output'):
                if output_data is not None:
                    raise SampleParseError('two outputs found')
                output_name = header
                output_data = codeblock.encode()
            elif header.lower() in ('sample', 'example'):
                name = header
                if input_data is None:
                    input_data = codeblock.encode()
                elif output_data is None:
                    output_data = codeblock.encode()
                else:
                    raise SampleParseError('two samples found')

        if input_data is None:
            raise SampleParseError('no input found')
        if output_data is None:
            raise SampleParseError('no output found')
        testcase = onlinejudge.type.TestCase(
            name=name or 'sample',
            input_name=input_name or 'input',
            input_data=input_data,
            output_name=output_name or 'output',
            output_data=output_data,
        )
        return [testcase]

    def get_url(self, *, contests: bool = True) -> str:
        return 'https://www.codechef.com/{}/problems/{}'.format(self.contest_id, self.problem_id)

    def get_service(self) -> CodeChefService:
        return CodeChefService()

    @classmethod
    def from_url(cls, url: str) -> Optional['CodeChefProblem']:
        # example: https://www.codechef.com/JAN20A/problems/DYNAMO
        # example: https://www.codechef.com/JAN20A/submit/DYNAMO
        # example: https://www.codechef.com/JAN20A/status/DYNAMO
        result = urllib.parse.urlparse(url)
        if result.scheme in ('', 'http', 'https') \
                and result.netloc == 'www.codechef.com':
            m = re.match(r'/([0-9A-Z_a-z-]+)/(?:problems|submit|status)/([0-9A-Z_a-z-]+)/?', result.path)
            if m:
                contest_id = m.group(1)
                problem_id = m.group(2)
                return cls(problem_id=problem_id, contest_id=contest_id)
        return None


onlinejudge.dispatch.services += [CodeChefService]
onlinejudge.dispatch.problems += [CodeChefProblem]
