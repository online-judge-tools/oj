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
import selenium
import time


@utils.singleton
class TopCoderService(onlinejudge.service.Service):

    def login(self, get_credentials, session=None):
        driver = session  # rename
        assert isinstance(driver, selenium.webdriver.remote.webdriver.WebDriver)

        # go to the login page
        url = 'https://accounts.topcoder.com/member'
        driver.get(url)
        log.status('wait for redirect...')
        time.sleep(3)
        if driver.current_url != url:
            log.info('You have already logged in.')
            return True

        # type credentials and click login
        username, password = get_credentials()
        driver.find_element_by_xpath('//form[@name="vm.loginForm"]//input[@name="username"]').send_keys(username)
        driver.find_element_by_xpath('//form[@name="vm.loginForm"]//input[@id="current-password-input"]').send_keys(password)
        driver.find_element_by_xpath('//form[@name="vm.loginForm"]//button[@type="submit" and text()="Log In"]').click()

        # wait a minute
        log.info('Logging in...')
        time.sleep(6)
        if driver.current_url != url:
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
    def __init__(self, rd, compid=None, pm=None):
        self.rd = rd
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
                for name in [ 'rd', 'compid', 'pm' ]:
                    if name in querystring:
                        kwargs[name] = int(querystring[name])
                return cls(**kwargs)

    def get_language_dict(self, session=None):
        driver = session  # rename
        assert isinstance(driver, selenium.webdriver.remote.webdriver.WebDriver)

        # at 2017/09/21
        return {
                'Java':   { 'description': 'Java 8' },
                'C++':    { 'description': 'C++11' },
                'C#':     { 'description': '' },
                'VB':     { 'description': '' },
                'Python': { 'description': 'Pyhton 2' },
            }

    def submit(self, code, language, kind='example', session=None):
        assert kind in [ 'example', 'full' ]
        driver = session  # rename
        assert isinstance(driver, selenium.webdriver.remote.webdriver.WebDriver)

        # get params and enter the module=Submit page
        url_match_detail = 'https://community.topcoder.com/tc?module=MatchDetails&rd=%d' % self.rd
        log.info('GET: %s', url_match_detail)
        driver.get(url_match_detail)
        link = driver.find_element_by_xpath('//a[text() = "Register/Submit"]')
        log.info('GET: %s', link.get_attribute('href'))
        link.click()
        try:
            link = driver.find_element_by_xpath('//a[text() = "Submit" and contains(@href, "rd=%d")]' % self.rd)
        except selenium.common.exceptions.NoSuchElementException:
            log.error('link to submit not found:  Are you registered?  Is the contest running?')
            return None
        log.info('GET: %s', link.get_attribute('href'))
        link.click()

        # select the language
        log.status('click: %s', language)
        language_id = [ None, 'Java', None, 'C++', 'C#', 'VB', 'Python' ].index(language)
        driver.find_element_by_xpath('//form[@name = "codingForm"]//input[@type = "radio" and @name = "lid" and @value = "%d"]' % language_id).click()

        # type the code
        log.warning('TODO: make faster')
        driver.find_element_by_xpath('//form[@name = "codingForm"]//div[@class = "CodeMirror-code"]//pre').click()
        time.sleep(0.1)
        driver.switch_to.active_element.send_keys(selenium.webdriver.common.keys.Keys.CONTROL, 'a')
        driver.switch_to.active_element.send_keys(selenium.webdriver.common.keys.Keys.BACKSPACE)
        for line in code.splitlines():
            log.status('type: %s', line.decode())
            driver.switch_to.active_element.send_keys(line.decode())
            driver.switch_to.active_element.send_keys(selenium.webdriver.common.keys.Keys.RETURN)
            driver.switch_to.active_element.send_keys(selenium.webdriver.common.keys.Keys.HOME)
            driver.switch_to.active_element.send_keys(selenium.webdriver.common.keys.Keys.CONTROL, selenium.webdriver.common.keys.Keys.DELETE)

        # submit
        log.status('click: Test')
        alt_text = { 'example': 'Test', 'full': 'Submit' }[kind]
        driver.find_element_by_xpath('//form[@name = "codingForm"]//img[@alt = "%s"]' % alt_text).click()

        # check
        for _ in range(8):
            if 'module=SubmitSuccess' in driver.current_url:
                break
            time.sleep(1)
        else:
            message = driver.find_element_by_xpath('//textarea[@name = "messages"]').text
            log.failure('%s', message)
            return None

        log.success('success: result: %s', driver.current_url)
        return onlinejudge.submission.CompatibilitySubmission(driver.current_url)

onlinejudge.dispatch.services += [ TopCoderService ]
onlinejudge.dispatch.problems += [ TopCoderLongContestProblem ]
