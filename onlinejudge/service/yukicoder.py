# Python Version: 3.x
# -*- coding: utf-8 -*-
"""
the module for yukicoder (https://yukicoder.me/)

:note: There is the official API https://petstore.swagger.io/?url=https://yukicoder.me/api/swagger.yaml
"""

import collections
import io
import json
import os.path
import posixpath
import re
import urllib.parse
from typing import *

import bs4
import requests

import onlinejudge._implementation.logging as log
import onlinejudge._implementation.testcase_zipper
import onlinejudge._implementation.utils as utils
import onlinejudge.dispatch
from onlinejudge.type import *


class YukicoderService(onlinejudge.type.Service):
    def login(self, get_credentials: onlinejudge.type.CredentialsProvider, session: Optional[requests.Session] = None, method: Optional[str] = None) -> None:
        if method == 'github':
            return self.login_with_github(get_credentials, session=session)
        elif method == 'twitter':
            return self.login_with_twitter(get_credentials, session=session)
        else:
            assert False

    def login_with_github(self, get_credentials: onlinejudge.type.CredentialsProvider, session: Optional[requests.Session] = None) -> None:
        """
        :raise LoginError:
        """

        session = session or utils.get_default_session()
        url = 'https://yukicoder.me/auth/github'
        # get
        resp = utils.request('GET', url, session=session)
        if urllib.parse.urlparse(resp.url).hostname == 'yukicoder.me':
            log.info('You have already signed in.')
            return
        # redirect to github.com
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        form = soup.find('form')
        if not form:
            log.error('form not found')
            raise LoginError('something wrong')
        log.debug('form: %s', str(form))
        # post
        username, password = get_credentials()
        form = utils.FormSender(form, url=resp.url)
        form.set('login', username)
        form.set('password', password)
        resp = form.request(session)
        resp.raise_for_status()
        if urllib.parse.urlparse(resp.url).hostname == 'yukicoder.me':
            log.success('You signed in.')
        else:
            log.failure('You failed to sign in. Wrong user ID or password.')
            raise LoginError

    def login_with_twitter(self, get_credentials: onlinejudge.type.CredentialsProvider, session: Optional[requests.Session] = None) -> None:
        """
        :raise NotImplementedError: always raised
        """

        session = session or utils.get_default_session()
        url = 'https://yukicoder.me/auth/twitter'
        raise NotImplementedError

    def is_logged_in(self, session: Optional[requests.Session] = None, method: Optional[str] = None) -> bool:
        session = session or utils.get_default_session()
        url = 'https://yukicoder.me/auth/github'
        resp = utils.request('GET', url, session=session, allow_redirects=False)
        assert resp.status_code == 302
        return 'oauth' not in resp.headers['Location']

    def get_url(self) -> str:
        return 'https://yukicoder.me/'

    def get_name(self) -> str:
        return 'yukicoder'

    @classmethod
    def from_url(cls, url: str) -> Optional['YukicoderService']:
        # example: http://yukicoder.me/
        result = urllib.parse.urlparse(url)
        if result.scheme in ('', 'http', 'https') \
                and result.netloc == 'yukicoder.me':
            return cls()
        return None

    def _issue_official_api(self, api: str, id: Optional[int] = None, name: Optional[str] = None, session: Optional[requests.Session] = None) -> Any:
        assert (id is not None) != (name is not None)
        if id is not None:
            assert isinstance(id, int)
            sometihng = {'user': '', 'solved': 'id/'}[api]
            url = 'https://yukicoder.me/api/v1/{}/{}{}'.format(api, sometihng, id)
        else:
            assert name is not None
            url = 'https://yukicoder.me/api/v1/{}/name/{}'.format(api, urllib.parse.quote(name))
        session = session or utils.get_default_session()
        try:
            resp = utils.request('GET', url, session=session)
        except requests.exceptions.HTTPError:
            # {"Message":"指定したユーザーは存在しません"} がbodyに入っているはずだがNoneに潰す
            return None
        return json.loads(resp.content.decode(resp.encoding))

    # example: {"Id":10,"Name":"yuki2006","Solved":280,"Level":34,"Rank":59,"Score":52550,"Points":7105,"Notice":"匿名ユーザーの情報は取れません。ユーザー名が重複している場合は最初に作られたIDが優先されます（その場合は運営にご報告いただければマージします）。このAPIはベータ版です。予告なく変更される場合があります。404を返したら廃止です。"}
    def get_user(self, *args, **kwargs) -> Dict[str, Any]:
        """
        .. deprecated:: 6.0.0
            This method may be deleted in future.
        """
        return self._issue_official_api('user', *args, **kwargs)

    # https://twitter.com/yukicoder/status/935943170210258944
    # example: [{"No":46,"ProblemId":43,"Title":"はじめのn歩","AuthorId":25,"TesterId":0,"Level":1,"ProblemType":0,"Tags":"実装"}]
    def get_solved(self, *args, **kwargs) -> List[Dict[str, Any]]:
        """
        .. deprecated:: 6.0.0
            This method may be deleted in future.
        """
        return self._issue_official_api('solved', *args, **kwargs)

    # example: https://yukicoder.me/users/237/favorite
    def get_user_favorite(self, id: int, session: Optional[requests.Session] = None) -> List[Any]:
        """
        .. deprecated:: 6.0.0
            This method may be deleted in future.
        """
        url = 'https://yukicoder.me/users/%d/favorite' % id
        columns, rows = self._get_and_parse_the_table(url, session=session)
        assert columns == ['#', '提出時間', '提出者', '問題', '言語', '結果', '実行時間', 'コード長']
        for row in rows:
            for column in columns:
                if row[column].find('a'):
                    row[column + '/url'] = row[column].find('a').attrs.get('href')
                if column == '#':
                    row[column] = int(row[column].text)
                else:
                    row[column] = row[column].text.strip()
        return rows

    # example: https://yukicoder.me/users/504/favoriteProblem
    def get_user_favorite_problem(self, id, session: Optional[requests.Session] = None) -> List[Any]:
        """
        .. deprecated:: 6.0.0
            This method may be deleted in future.
        """
        url = 'https://yukicoder.me/users/%d/favoriteProblem' % id
        columns, rows = self._get_and_parse_the_table(url, session=session)
        assert columns == ['ナンバー', '問題名', 'レベル', 'タグ', '時間制限', 'メモリ制限', '作問者']
        for row in rows:
            for column in columns:
                if row[column].find('a'):
                    row[column + '/url'] = row[column].find('a').attrs.get('href')
                if column == 'ナンバー':
                    row[column] = int(row[column].text)
                elif column == 'レベル':
                    row[column] = self._parse_star(row[column])
                elif column == 'タグ':
                    # NOTE: 現在(2017/11/01)の仕様だと 練習モード「ゆるふわ」 でないとACしててもタグが非表示
                    # NOTE: ログインしてないとタグが非表示の仕様
                    # NOTE: ログインしてるはずだけどrequestsからGETしてもタグが降ってこない場合は適切な Session objectを指定してるか確認
                    row[column] = row[column].text.strip().split()
                else:
                    row[column] = row[column].text.strip()
        return rows

    # example: https://yukicoder.me/users/1786/favoriteWiki
    def get_user_favorite_wiki(self, id: int, session: Optional[requests.Session] = None) -> List[Any]:
        """
        .. deprecated:: 6.0.0
            This method may be deleted in future.
        """
        url = 'https://yukicoder.me/users/%d/favoriteWiki' % id
        columns, rows = self._get_and_parse_the_table(url, session=session)
        assert columns == ['Wikiページ']
        for row in rows:
            for column in columns:
                row[column + '/url'] = row[column].find('a').attrs.get('href')
                row[column] = row[column].text.strip()
        return rows

    # example: https://yukicoder.me/submissions?page=4220
    # example: https://yukicoder.me/submissions?page=2192&status=AC
    # NOTE: 1ページしか読まない 全部欲しい場合は呼び出し側で頑張る
    def get_submissions(self, page: int, status: Optional[str] = None, session: Optional[requests.Session] = None) -> List[Any]:
        """
        .. deprecated:: 6.0.0
            This method may be deleted in future.
        """
        assert isinstance(page, int) and page >= 1
        url = 'https://yukicoder.me/submissions?page=%d' % page
        if status is not None:
            assert status in 'AC WA RE TLE MLE OLE J_TLE CE WJ Judge NoOut IE'.split()
            url += '&status=' + status
        columns, rows = self._get_and_parse_the_table(url, session=session)
        assert columns == ['#', '提出日時', '', '提出者', '問題', '言語', '結果', '実行時間', 'コード長']  # 空白は「このユーザーの提出の表示」の虫眼鏡のため
        for row in rows:
            for column in columns:
                if column and row[column].find('a'):
                    row[column + '/url'] = row[column].find('a').attrs.get('href')
                if column == '#':
                    row[column] = int(row[column].text)
                elif column == '':
                    del row[column]
                else:
                    row[column] = row[column].text.strip()
        return rows

    # example: https://yukicoder.me/problems?page=2
    # NOTE: loginしてると
    def get_problems(self, page: int, comp_problem: bool = True, other: bool = False, sort: Optional[str] = None, session: Optional[requests.Session] = None) -> List[Any]:
        """
        .. deprecated:: 6.0.0
            This method may be deleted in future.
        """
        assert isinstance(page, int) and page >= 1
        url = 'https://yukicoder.me/problems'
        if other:
            url += '/other'
        url += '?page=%d' % page
        if comp_problem:  # 未完成問題は(ログインしてても)デフォルトで除外
            url += '&comp_problem=on'
        if sort is not None:
            assert sort in (
                'no_asc',
                'level_asc',
                'level_desc',
                'solved_asc',
                'solved_desc',
                'fav_asc',
                'fav_desc',
            )
            url += '&sort=' + sort
        columns, rows = self._get_and_parse_the_table(url, session=session)
        assert columns == ['ナンバー', '問題名', 'レベル', 'タグ', '作問者', '解いた人数', 'Fav']
        for row in rows:
            for column in columns:
                if column and row[column].find('a'):
                    row[column + '/url'] = row[column].find('a').attrs.get('href')
                if column in ('ナンバー', '解いた人数', 'Fav'):
                    row[column] = int(row[column].text)
                elif column == 'レベル':
                    row[column] = self._parse_star(row[column])
                elif column == 'タグ':
                    # NOTE: ログインしてないとタグが非表示の仕様
                    # NOTE: ログインしてるはずだけどrequestsからGETしてもタグが降ってこない場合は適切な Session objectを指定してるか確認
                    row[column] = row[column].text.strip().split()
                else:
                    row[column] = row[column].text.strip()
        return rows

    def _get_and_parse_the_table(self, url: str, session: Optional[requests.Session] = None) -> Tuple[List[Any], List[Dict[str, bs4.Tag]]]:
        # get
        session = session or utils.get_default_session()
        resp = utils.request('GET', url, session=session)
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        assert len(soup.find_all('table')) == 1
        table = soup.find('table')
        columns = [th.text.strip() for th in table.find('thead').find('tr') if th.name == 'th']
        data = []  # type: List[Dict[str, List[str]]]
        for row in table.find('tbody').find_all('tr'):
            values = [td for td in row if td.name == 'td']
            assert len(columns) == len(values)
            data += [dict(zip(columns, values))]
        return columns, data

    def _parse_star(self, tag: bs4.Tag) -> str:
        star = str(len(tag.find_all(class_='fa-star')))
        if tag.find_all(class_='fa-star-half-full'):
            star += '.5'
        return star


class YukicoderProblem(onlinejudge.type.Problem):
    def __init__(self, problem_no=None, problem_id=None):
        assert problem_no or problem_id
        assert not problem_no or isinstance(problem_no, int)
        assert not problem_id or isinstance(problem_id, int)
        self.problem_no = problem_no
        self.problem_id = problem_id

    def download_sample_cases(self, session: Optional[requests.Session] = None) -> List[TestCase]:
        session = session or utils.get_default_session()
        # get
        resp = utils.request('GET', self.get_url(), session=session)
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        samples = onlinejudge._implementation.testcase_zipper.SampleZipper()
        for pre in soup.select('.sample pre'):
            log.debug('pre: %s', str(pre))
            it = self._parse_sample_tag(pre)
            if it is not None:
                data, name = it
                samples.add(data.encode(), name)
        return samples.get()

    def download_system_cases(self, session: Optional[requests.Session] = None) -> List[TestCase]:
        """
        :raises NotLoggedInError:
        """

        session = session or utils.get_default_session()
        if not self.get_service().is_logged_in(session=session):
            raise NotLoggedInError
        url = 'https://yukicoder.me/problems/no/{}/testcase.zip'.format(self.problem_no)
        resp = utils.request('GET', url, session=session)
        fmt = 'test_%e/%s'
        return onlinejudge._implementation.testcase_zipper.extract_from_zip(resp.content, fmt)

    def _parse_sample_tag(self, tag: bs4.Tag) -> Optional[Tuple[str, str]]:
        assert isinstance(tag, bs4.Tag)
        assert tag.name == 'pre'
        prv = utils.previous_sibling_tag(tag)
        pprv = tag.parent and utils.previous_sibling_tag(tag.parent)
        if prv.name == 'h6' and tag.parent.name == 'div' and tag.parent['class'] == ['paragraph'] and pprv.name == 'h5':
            log.debug('h6: %s', str(prv))
            log.debug('name.encode(): %s', prv.string.encode())
            s = tag.string or ''  # tag.string for the tag "<pre></pre>" returns None
            return utils.textfile(s.lstrip()), pprv.string + ' ' + prv.string
        return None

    def submit_code(self, code: bytes, language_id: LanguageId, filename: Optional[str] = None, session: Optional[requests.Session] = None) -> onlinejudge.type.Submission:
        """
        :raises NotLoggedInError:
        """

        session = session or utils.get_default_session()
        # get
        url = self.get_url() + '/submit'
        resp = utils.request('GET', url, session=session)
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        form = soup.find('form', id='submit_form')
        if not form:
            log.error('form not found')
            raise NotLoggedInError
        # post
        form = utils.FormSender(form, url=resp.url)
        form.set('lang', language_id)
        form.set_file('file', filename or 'code', code)
        form.unset('custom_test')
        resp = form.request(session=session)
        resp.raise_for_status()
        # result
        if 'submissions' in resp.url:
            # example: https://yukicoder.me/submissions/314087
            log.success('success: result: %s', resp.url)
            return utils.DummySubmission(resp.url, problem=self)
        else:
            log.failure('failure')
            soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
            for div in soup.findAll('div', attrs={'role': 'alert'}):
                log.warning('yukicoder says: "%s"', div.string)
            raise SubmissionError

    def get_available_languages(self, session: Optional[requests.Session] = None) -> List[Language]:
        session = session or utils.get_default_session()
        # get
        # We use the problem page since it is available without logging in
        resp = utils.request('GET', self.get_url(), session=session)
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        select = soup.find('select', id='lang')
        languages = []  # type: List[Language]
        for option in select.find_all('option'):
            languages += [Language(option.attrs['value'], ' '.join(option.string.split()))]
        return languages

    def get_url(self) -> str:
        if self.problem_no:
            return 'https://yukicoder.me/problems/no/{}'.format(self.problem_no)
        elif self.problem_id:
            return 'https://yukicoder.me/problems/{}'.format(self.problem_id)
        else:
            raise ValueError

    @classmethod
    def from_url(cls, url: str) -> Optional['YukicoderProblem']:
        # example: https://yukicoder.me/problems/no/499
        # example: http://yukicoder.me/problems/1476
        result = urllib.parse.urlparse(url)
        dirname, basename = posixpath.split(utils.normpath(result.path))
        if result.scheme in ('', 'http', 'https') \
                and result.netloc == 'yukicoder.me':
            n = None  # type: Optional[int]
            try:
                n = int(basename)
            except ValueError:
                pass
            if n is not None:
                if dirname == '/problems/no':
                    return cls(problem_no=int(n))
                if dirname == '/problems':
                    return cls(problem_id=int(n))
            return cls()
        return None

    def get_service(self) -> YukicoderService:
        return YukicoderService()

    def get_input_format(self, session: Optional[requests.Session] = None) -> Optional[str]:
        session = session or utils.get_default_session()
        # get
        resp = utils.request('GET', self.get_url(), session=session)
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        for h4 in soup.find_all('h4'):
            if h4.string == '入力':
                return h4.parent.find('pre').decode_contents(formatter=None)
        return None


onlinejudge.dispatch.services += [YukicoderService]
onlinejudge.dispatch.problems += [YukicoderProblem]
