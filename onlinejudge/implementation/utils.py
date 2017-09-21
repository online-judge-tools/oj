# Python Version: 3.x
# -*- coding: utf-8 -*-
import onlinejudge.implementation.logging as log
import onlinejudge.implementation.version as version
import re
import os
import os.path
import requests
import bs4
import contextlib
import urllib.parse
import http.cookiejar
import http.client
import subprocess
import posixpath
import sys
import ast
import time
import selenium.webdriver

default_data_dir = os.path.join(os.environ.get('XDG_DATA_HOME') or os.path.expanduser('~/.local/share'), 'onlinejudge')
html_parser = 'html.parser'  # TODO: this is NOT a utility.

def parcentformat(s, table):
    assert '%' not in table or table['%'] == '%'
    table['%'] = '%'
    result = ''
    for m in re.finditer('[^%]|%(.)', s):
        if m.group(1):
            if m.group(1) in table:
                result += table[m.group(1)]
        else:
            result += m.group(0)
    return result

def describe_status_code(status_code):
    return '{} {}'.format(status_code, http.client.responses[status_code])

def previous_sibling_tag(tag):
    tag = tag.previous_sibling
    while tag and not isinstance(tag, bs4.Tag):
        tag = tag.previous_sibling
    return tag

def new_default_session():  # without setting cookiejar
    session = requests.Session()
    session.headers['User-Agent'] += ' (+{})'.format(version.__url__)
    return session

default_cookie_path = os.path.join(default_data_dir, 'cookie.jar')

@contextlib.contextmanager
def with_cookiejar(session, path):
    path = path or default_cookie_path
    session.cookies = http.cookiejar.LWPCookieJar(path)
    if os.path.exists(path):
        log.info('load cookie from: %s', path)
        session.cookies.load()
    yield session
    log.info('save cookie to: %s', path)
    if os.path.dirname(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    session.cookies.save()
    os.chmod(path, 0o600)  # NOTE: to make secure a little bit

@contextlib.contextmanager
def run_webdriver(webdriver, target_url, cookie_path, headless=True):
    # launch
    if webdriver is None:
         log.error('webdriver is not specified')
         sys.exit(1)
    elif 'phantomjs' in os.path.basename(webdriver):
        kwargs = {}
        if '/' in webdriver:
            kwargs['executable_path'] = webdriver
        driver = selenium.webdriver.PhantomJS(**kwargs)
    elif 'chrom' in os.path.basename(webdriver):
        kwargs = {}
        if '/' in webdriver:
            kwargs['executable_path'] = webdriver
        kwargs['chrome_options'] = selenium.webdriver.ChromeOptions()
        if headless:
            kwargs['chrome_options'].add_argument('--headless')
            kwargs['chrome_options'].add_argument('--disable-gpu')
        driver = selenium.webdriver.Chrome(**kwargs)
    else:
        parser.error('unknown webdriver: %s', webdriver)

    # workaround
    # NOTE: selenium can read/write only cookies of the current domain
    domain = '.'.join(urllib.parse.urlparse(target_url).netloc.split('.')[- 2 :])

    # default cookie path
    default_selenium_cookie_path = os.path.join(default_data_dir, 'cookie-' + driver.name + '-' + domain + '.jar')
    cookie_path = cookie_path or default_selenium_cookie_path

    # load cookie
    if os.path.exists(cookie_path):
        log.info('load cookie for %s from: %s', driver.name, cookie_path)
        driver.get(target_url)
        time.sleep(1)
        with open(cookie_path) as fh:
            cookies = ast.literal_eval(fh.read())
        for cookie in cookies:
            log.debug('cookie: %s', repr(cookie))
            try:
                driver.add_cookie(cookie)
            except selenium.common.exceptions.WebDriverException as e:
                log.debug('exception:\n%s', str(e))

    yield driver

    # save cookie
    log.info('save cookie for %s to: %s', driver.name, cookie_path)
    driver.get(target_url)
    time.sleep(1)
    if os.path.dirname(cookie_path):
        os.makedirs(os.path.dirname(cookie_path), exist_ok=True)
    with open(cookie_path, 'w') as fh:
        fh.write(repr(driver.get_cookies()) + '\n')
    os.chmod(cookie_path, 0o600)  # NOTE: to make secure a little bit

    driver.close()


class SampleZipper(object):
    def __init__(self):
        self.data = []
        self.dangling = None

    def add(self, s, name=''):
        if self.dangling is None:
            if re.search('output', name, re.IGNORECASE) or re.search('出力', name):
                log.warning('strange name for input string: %s', name)
            self.dangling = { 'data': s, 'name': name }
        else:
            if re.search('input', name, re.IGNORECASE) or re.search('入力', name):
                log.warning('strange name for output string: %s', name)
            self.data += [ {
                'input': self.dangling,
                'output': { 'data': s, 'name': name },
                } ]
            self.dangling = None

    def get(self):
        if self.dangling is not None:
            log.error('dangling sample string: %s', self.dangling[1])
        return self.data

class FormSender(object):
    def __init__(self, form, url):
        assert isinstance(form, bs4.Tag)
        assert form.name == 'form'
        self.form = form
        self.url = url
        self.payload = {}
        self.files = {}
        for input in self.form.find_all('input'):
            log.debug('input: %s', str(input))
            if input.attrs.get('type') in [ 'checkbox', 'radio' ]:
                continue
            if 'name' in input.attrs and 'value' in input.attrs:
                self.payload[input['name']] = input['value']

    def set(self, key, value):
        self.payload[key] = value

    def get(self):
        return self.payload

    def set_file(self, key, value):
        self.files[key] = value

    def request(self, session, action=None, **kwargs):
        action = action or self.form['action']
        url = urllib.parse.urljoin(self.url, action)
        method = self.form['method'].upper()
        log.status('%s: %s', method, url)
        log.debug('payload: %s', str(self.payload))
        resp = session.request(method, url, data=self.payload, files=self.files, **kwargs)
        log.status(describe_status_code(resp.status_code))
        return resp

def dos2unix(s):
    return s.replace('\r\n', '\n')
def textfile(s): # should have trailing newline
    if s.endswith('\n'):
        return s
    elif '\r\n' in s:
        return s + '\r\n'
    else:
        return s + '\n'

# http://stackoverflow.com/questions/31875/is-there-a-simple-elegant-way-to-define-singletons-in-python/12850496#12850496
def singleton(cls):
    instance = cls()
    # Always return the same object
    cls.__new__ = staticmethod(lambda cls: instance)
    # Disable __init__
    try:
        del cls.__init__
    except AttributeError:
        pass
    return cls

def exec_command(command, timeout=None, **kwargs):
    try:
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=sys.stderr, **kwargs)
    except FileNotFoundError:
        log.error('No such file or directory: %s', command)
        sys.exit(1)
    except PermissionError:
        log.error('Permission denied: %s', command)
        sys.exit(1)
    try:
        answer, _ = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        answer = b''
    return answer, proc

# We should use this instead of posixpath.normpath
# posixpath.normpath doesn't collapse a leading duplicated slashes. see: https://stackoverflow.com/questions/7816818/why-doesnt-os-normpath-collapse-a-leading-double-slash
def normpath(path):
    path = posixpath.normpath(path)
    if path.startswith('//'):
        path = '/' + path.lstrip('/')
    return path


def request(method, url, session=None, raise_for_status=True, **kwargs):
    assert method in [ 'GET', 'POST' ]
    kwargs.setdefault('allow_redirects', True)
    log.status('%s: %s', method, url)
    resp = session.request(method, url, **kwargs)
    log.status(describe_status_code(resp.status_code))
    if raise_for_status:
        resp.raise_for_status()
    return resp
