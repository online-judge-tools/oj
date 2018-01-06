# Python Version: 3.x
# -*- coding: utf-8 -*-
import onlinejudge.service
import onlinejudge.problem
import onlinejudge.submission
import onlinejudge.dispatch
import onlinejudge.implementation.utils as utils
import onlinejudge.implementation.logging as log
import re
import io
import os.path
import posixpath
import bs4
import json
import requests
import urllib.parse
import zipfile
import collections


@utils.singleton
class YukicoderService(onlinejudge.service.Service):

    def login(self, get_credentials, session=None, method=None):
        if method == 'github':
            return self.login_with_github(get_credentials, session=session)
        elif method == 'twitter':
            return self.login_with_twitter(get_credentials, session=session)
        else:
            assert False

    def login_with_github(self, get_credentials, session=None):
        session = session or utils.new_default_session()
        url = 'https://yukicoder.me/auth/github'
        # get
        resp = utils.request('GET', url, session=session)
        if urllib.parse.urlparse(resp.url).hostname == 'yukicoder.me':
            log.info('You have already signed in.')
            return True
        # redirect to github.com
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        form = soup.find('form')
        if not form:
            log.error('form not found')
            log.info('Did you logged in?')
            return False
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
            return True
        else:
            log.failure('You failed to sign in. Wrong user ID or password.')
            return False

    def login_with_twitter(self, get_credentials, session=None):
        session = session or utils.new_default_session()
        url = 'https://yukicoder.me/auth/twitter'
        raise NotImplementedError

    def get_url(self):
        return 'https://yukicoder.me/'

    def get_name(self):
        return 'yukicoder'

    @classmethod
    def from_url(cls, s):
        # example: http://yukicoder.me/
        result = urllib.parse.urlparse(s)
        if result.scheme in ('', 'http', 'https') \
                and result.netloc == 'yukicoder.me':
            return cls()

    def _issue_official_api(self, api, id=None, name=None, session=None):
        assert (id is not None) != (name is not None)
        if id is not None:
            assert isinstance(id, int)
            sometihng = { 'user': '', 'solved': 'id/' }[api]
            url = 'https://yukicoder.me/api/v1/{}/{}{}'.format(api, sometihng, id)
        else:
            url = 'https://yukicoder.me/api/v1/{}/name/{}'.format(api, urllib.parse.quote(name))
        session = session or utils.new_default_session()
        try:
            resp = utils.request('GET', url, session=session)
        except requests.exceptions.HTTPError:
            # {"Message":"指定したユーザーは存在しません"} がbodyに入っているはずだがNoneに潰す
            return None
        return json.loads(resp.content.decode(resp.encoding))

    # example: {"Id":10,"Name":"yuki2006","Solved":280,"Level":34,"Rank":59,"Score":52550,"Points":7105,"Notice":"匿名ユーザーの情報は取れません。ユーザー名が重複している場合は最初に作られたIDが優先されます（その場合は運営にご報告いただければマージします）。このAPIはベータ版です。予告なく変更される場合があります。404を返したら廃止です。"}
    def get_user(self, *args, **kwargs):
        return self._issue_official_api('user', *args, **kwargs)

    # https://twitter.com/yukicoder/status/935943170210258944
    # example: [{"No":46,"ProblemId":43,"Title":"はじめのn歩","AuthorId":25,"TesterId":0,"Level":1,"ProblemType":0,"Tags":"実装"}]
    def get_solved(self, *args, **kwargs):
        return self._issue_official_api('solved', *args, **kwargs)

    # example: https://yukicoder.me/users/237/favorite
    def get_user_favorite(self, id, session=None):
        url = 'https://yukicoder.me/users/%d/favorite' % id
        columns, rows = self._get_and_parse_the_table(url, session=session)
        assert columns == [ '#', '提出時間', '提出者', '問題', '言語', '結果', '実行時間', 'コード長' ]
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
    def get_user_favorite_problem(self, id, session=None):
        url = 'https://yukicoder.me/users/%d/favoriteProblem' % id
        columns, rows = self._get_and_parse_the_table(url, session=session)
        assert columns == [ 'ナンバー', '問題名', 'レベル', 'タグ', '時間制限', 'メモリ制限', '作問者' ]
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
    def get_user_favorite_wiki(self, id, session=None):
        url = 'https://yukicoder.me/users/%d/favoriteWiki' % id
        columns, rows = self._get_and_parse_the_table(url, session=session)
        assert columns == [ 'Wikiページ' ]
        for row in rows:
            for column in columns:
                row[column + '/url'] = row[column].find('a').attrs.get('href')
                row[column] = row[column].text.strip()
        return rows

    # example: https://yukicoder.me/submissions?page=4220
    # example: https://yukicoder.me/submissions?page=2192&status=AC
    # NOTE: 1ページしか読まない 全部欲しい場合は呼び出し側で頑張る
    def get_submissions(self, page, status=None, session=None):
        assert isinstance(page, int) and page >= 1
        url = 'https://yukicoder.me/submissions?page=%d' % page
        if status is not None:
            assert status in 'AC WA RE TLE MLE OLE J_TLE CE WJ Judge NoOut IE'.split()
            url += '&status=' + status
        columns, rows = self._get_and_parse_the_table(url, session=session)
        assert columns == [ '#', '提出日時', '', '提出者', '問題', '言語', '結果', '実行時間', 'コード長' ]  # 空白は「このユーザーの提出の表示」の虫眼鏡のため
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
    def get_problems(self, page, comp_problem=True, other=False, sort=None, session=None):
        assert isinstance(page, int) and page >= 1
        url = 'https://yukicoder.me/problems'
        if other:
            url += '/other'
        url += '?page=%d' % page
        if comp_problem:  # 未完成問題は(ログインしてても)デフォルトで除外
            url += '&comp_problem=on'
        if sort is not None:
            assert sort in ( 'no_asc', 'level_asc', 'level_desc', 'solved_asc', 'solved_desc', 'fav_asc', 'fav_desc', )
            url += '&sort=' + sort
        columns, rows = self._get_and_parse_the_table(url, session=session)
        assert columns == [ 'ナンバー', '問題名', 'レベル', 'タグ', '作問者', '解いた人数', 'Fav' ]
        for row in rows:
            for column in columns:
                if column and row[column].find('a'):
                    row[column + '/url'] = row[column].find('a').attrs.get('href')
                if column in ( 'ナンバー', '解いた人数', 'Fav' ):
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

    def _get_and_parse_the_table(self, url, session=None):
        # get
        session = session or utils.new_default_session()
        resp = utils.request('GET', url, session=session)
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        assert len(soup.find_all('table')) == 1
        table = soup.find('table')
        columns = [ th.text.strip() for th in table.find('thead').find('tr') if th.name == 'th' ]
        data = []
        for row in table.find('tbody').find_all('tr'):
            values = [ td for td in row if td.name == 'td' ]
            assert len(columns) == len(values)
            data += [ dict(zip(columns, values)) ]
        return columns, data

    def _parse_star(self, tag):
        star = str(len(tag.find_all(class_='fa-star')))
        if tag.find_all(class_='fa-star-half-full'):
            star += '.5'
        return star  # str

class YukicoderProblem(onlinejudge.problem.Problem):
    def __init__(self, problem_no=None, problem_id=None):
        assert problem_no or problem_id
        assert not problem_no or isinstance(problem_no, int)
        assert not problem_id or isinstance(problem_id, int)
        self.problem_no = problem_no
        self.problem_id = problem_id

    def download(self, session=None, is_system=False):
        if is_system:
            return self.download_system(session=session)
        else:
            return self.download_samples(session=session)
    def download_samples(self, session=None):
        session = session or utils.new_default_session()
        # get
        resp = utils.request('GET', self.get_url(), session=session)
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        samples = utils.SampleZipper()
        for pre in soup.find_all('pre'):
            log.debug('pre: %s', str(pre))
            it = self._parse_sample_tag(pre)
            if it is not None:
                data, name = it
                samples.add(data, name)
        return samples.get()
    def download_system(self, session=None):
        session = session or utils.new_default_session()
        # get
        url = 'https://yukicoder.me/problems/no/{}/testcase.zip'.format(self.problem_no)
        resp = utils.request('GET', url, session=session)
        # parse
        samples = collections.defaultdict(dict)
        with zipfile.ZipFile(io.BytesIO(resp.content)) as fh:
            for filename in sorted(fh.namelist()):  # "test_in" < "test_out"
                dirname = os.path.dirname(filename)
                basename = os.path.basename(filename)
                kind = { 'test_in': 'input', 'test_out': 'output' }[dirname]
                data = fh.read(filename).decode()
                name = basename
                if os.path.splitext(name)[1] == '.in':  # ".in" extension is confusing
                    name = os.path.splitext(name)[0]
                print(filename, name)
                samples[basename][kind] = { 'data': data, 'name': name }
        for sample in samples.values():
            if 'input' not in sample or 'output' not in sample:
                log.error('dangling sample found: %s', str(sample))
        return list(map(lambda it: it[1], sorted(samples.items())))

    def _parse_sample_tag(self, tag):
        assert isinstance(tag, bs4.Tag)
        assert tag.name == 'pre'
        prv = utils.previous_sibling_tag(tag)
        pprv = tag.parent and utils.previous_sibling_tag(tag.parent)
        if prv.name == 'h6' and tag.parent.name == 'div' and tag.parent['class'] == ['paragraph'] and pprv.name == 'h5':
            log.debug('h6: %s', str(prv))
            log.debug('name.encode(): %s', prv.string.encode())
            s = tag.string or ''  # tag.string for the tag "<pre></pre>" returns None
            return utils.textfile(s.lstrip()), pprv.string + ' ' + prv.string

    def get_url(self):
        if self.problem_no:
            return 'https://yukicoder.me/problems/no/{}'.format(self.problem_no)
        elif self.problem_id:
            return 'https://yukicoder.me/problems/{}'.format(self.problem_id)
        else:
            assert False

    @classmethod
    def from_url(cls, s):
        # example: https://yukicoder.me/problems/no/499
        # example: http://yukicoder.me/problems/1476
        result = urllib.parse.urlparse(s)
        dirname, basename = posixpath.split(utils.normpath(result.path))
        if result.scheme in ('', 'http', 'https') \
                and result.netloc == 'yukicoder.me':
            try:
                n = int(basename)
            except ValueError:
                n = None
            if n is not None:
                if dirname == '/problems/no':
                    return cls(problem_no=int(n))
                if dirname == '/problems':
                    return cls(problem_id=int(n))
            return cls()

    def get_service(self):
        return YukicoderService()

    def get_input_format(self, session=None):
        session = session or utils.new_default_session()
        # get
        resp = utils.request('GET', self.get_url(), session=session)
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        for h4 in soup.find_all('h4'):
            if h4.string == '入力':
                return h4.parent.find('pre').string


onlinejudge.dispatch.services += [ YukicoderService ]
onlinejudge.dispatch.problems += [ YukicoderProblem ]
