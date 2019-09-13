# Python Version: 3.x
import datetime
import getpass
import http.cookies
import sys
import time
from typing import *

import requests

import onlinejudge
import onlinejudge._implementation.logging as log
import onlinejudge._implementation.utils as utils

if TYPE_CHECKING:
    import argparse


def login_with_password(service: onlinejudge.type.Service, *, username: Optional[str], password: Optional[str], session: requests.Session) -> None:
    def get_credentials() -> Tuple[str, str]:
        nonlocal username, password
        if username is None:
            username = input('Username: ')
        if password is None:
            password = getpass.getpass()
        return username, password

    service.login(get_credentials=get_credentials, session=session)


# a wrapper class, because selenium.common.exceptions.* is not always imported
class WebDriverException(Exception):
    pass


def login_with_browser(service: onlinejudge.type.Service, *, session: requests.Session) -> None:
    try:
        import selenium.webdriver
    except ImportError:
        raise

    try:
        profile = selenium.webdriver.FirefoxProfile()
        profile.set_preference("general.useragent.override", session.headers['User-Agent'])
        driver = selenium.webdriver.Firefox(firefox_profile=profile)
    except selenium.common.exceptions.WebDriverException as e:
        raise WebDriverException(e)

    # get cookies via Selenium
    url = service.get_url_of_login_page()
    log.info('open with WebDriver: %s', url)
    driver.get(url)
    cookies = []  # type: List[Dict[str, str]]
    try:
        while driver.current_url:
            cookies = driver.get_cookies()
            time.sleep(0.1)
    except selenium.common.exceptions.WebDriverException:
        pass  # the window is closed

    # set cookies to the requests.Session
    log.info('copy cookies from WebDriver')
    for c in cookies:
        log.status('set cookie: %s', c['name'])
        morsel = http.cookies.Morsel()  # type: http.cookies.Morsel
        morsel.set(c['name'], c['value'], c['value'])
        morsel.update({key: value for key, value in c.items() if morsel.isReservedKey(key)})
        if not morsel['expires']:
            expires = datetime.datetime.now(datetime.timezone.utc).astimezone() + datetime.timedelta(days=180)
            morsel.update({'expires': expires.strftime('%a, %d-%b-%Y %H:%M:%S GMT')})  # RFC2109 format
        cookie = requests.cookies.morsel_to_cookie(morsel)
        session.cookies.set_cookie(cookie)  # type: ignore


def is_logged_in_with_message(service: onlinejudge.type.Service, *, session: requests.Session) -> bool:
    if service.is_logged_in(session=session):
        log.info('You have already signed in.')
        return True
    else:
        log.warning('You are not signed in.')
        return False


def login(args: 'argparse.Namespace') -> None:
    service = onlinejudge.dispatch.service_from_url(args.url)
    if service is None:
        sys.exit(1)

    with utils.with_cookiejar(utils.new_session_with_our_user_agent(), path=args.cookie) as session:

        if is_logged_in_with_message(service, session=session):
            return
        else:
            if args.check:
                sys.exit(1)

        if args.use_browser in ('always', 'auto'):
            try:
                login_with_browser(service, session=session)
            except ImportError:
                log.error('Selenium is not installed: try $ pip3 install selenium')
                pass
            except WebDriverException as e:
                log.error('%s', e)
                pass
            else:
                if is_logged_in_with_message(service, session=session):
                    return
                else:
                    sys.exit(1)

        if args.use_browser in ('never', 'auto'):
            if args.use_browser == 'auto':
                log.warning('use CUI login since Selenium fails')
            try:
                login_with_password(service, username=args.username, password=args.password, session=session)
            except NotImplementedError as e:
                log.error('%s', e)
                pass
            except onlinejudge.type.LoginError:
                sys.exit(1)
            else:
                if is_logged_in_with_message(service, session=session):
                    return
                else:
                    sys.exit(1)

        sys.exit(1)
