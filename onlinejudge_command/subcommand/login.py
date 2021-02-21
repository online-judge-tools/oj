import argparse
import datetime
import getpass
import http.cookies
import textwrap
import time
from logging import getLogger
from typing import *

import requests

import onlinejudge.dispatch as dispatch
import onlinejudge_command.utils as utils
from onlinejudge.type import LoginError, Service

logger = getLogger(__name__)


def add_subparser(subparsers: argparse.Action) -> None:
    subparsers_add_parser: Callable[..., argparse.ArgumentParser] = subparsers.add_parser  # type: ignore
    subparser = subparsers_add_parser('login', aliases=['l'], help='login to a service', formatter_class=argparse.RawTextHelpFormatter, epilog='''\
supported services:
  AtCoder
  Codeforces
  yukicoder
  HackerRank
  Toph

tips:
  You can do similar things with shell and oj-api command. see https://github.com/online-judge-tools/api-client
    e.g. $ USERNAME=foo PASSWORD=bar oj-api login-service https://atcoder.jp/
''')
    subparser.add_argument('url')
    subparser.add_argument('-u', '--username')
    subparser.add_argument('-p', '--password')
    subparser.add_argument('--check', action='store_true', help='check whether you are logged in or not')
    subparser.add_argument('--use-browser', choices=('always', 'auto', 'never'), default='auto', help='specify whether it uses a GUI web browser to login or not  (default: auto)')


def login_with_password(service: Service, *, username: Optional[str], password: Optional[str], session: requests.Session) -> None:
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


def get_webdriver() -> Any:
    """get_webdriver() detects an available webdriver and returns it.

    :raises ImportError: of Selenium
    """

    import selenium.webdriver  # pylint: disable=import-error,import-outside-toplevel

    logger.info('Trying to open Chrome via WebDriver...')
    try:
        return selenium.webdriver.Chrome()
    except selenium.common.exceptions.WebDriverException as e:
        logger.error(e)

    logger.info('Trying to open Firefox via WebDriver...')
    try:
        return selenium.webdriver.Firefox()
    except Exception as e:
        logger.error(e)

    logger.info('Trying to open Edge via WebDriver...')
    try:
        return selenium.webdriver.Edge()
    except Exception as e:
        logger.error(e)

    logger.info('Trying to open Internet Explorer via WebDriver...')
    try:
        return selenium.webdriver.Ie()
    except Exception as e:
        logger.error(e)

    logger.info('Trying to open Safari via WebDriver...')
    try:
        return selenium.webdriver.Safari()
    except Exception as e:
        logger.error(e)

    logger.info('Trying to open Opera via WebDriver...')
    try:
        return selenium.webdriver.Opera()
    except Exception as e:
        logger.error(e)

    logger.error('No WebDriver is available.')
    logger.info(utils.HINT + textwrap.dedent("""
        Please install a WebDriver.
        See https://www.selenium.dev/documentation/en/webdriver/driver_requirements/

        Detailed instructions:
            If you use Ubuntu:
                1. Run $ sudo apt install chromium-chromedriver firefox-geckodriver
            If you use Ubuntu under Windows Subsystem for Linux:
                1. Make a symbolic link from cookie.jar in WSL to cookie.jar out of WSL. For example, run $ ln -s /mnt/c/Users/%USERNAME%/AppData/Local/online-judge-tools/online-judge-tools/cookie.jar /home/ubuntu/.local/share/online-judge-tools/cookie.jar
                2. Use `oj login` outside of WSL
            If you use Windows:
                1. Install Chocolatey. See https://chocolatey.org/
                2. Run > choco install selenium-all-drivers
    """))
    raise WebDriverException('No WebDriver is installed.')


def login_with_browser(service: Service, *, session: requests.Session) -> None:
    """
    :raises ImportError: of Selenium
    :raises WebDriverException:
    """

    import selenium.webdriver  # pylint: disable=import-error,import-outside-toplevel

    with get_webdriver() as driver:
        # get cookies via Selenium
        url = service.get_url_of_login_page()
        logger.info('Opening the URL via WebDriver: %s', url)
        logger.info('Please do the followings:\n    1. login in the GUI browser\n    2. close the GUI browser')
        driver.get(url)
        cookies: List[Dict[str, str]] = []
        try:
            while driver.current_url:
                cookies = driver.get_cookies()
                time.sleep(0.1)
        except selenium.common.exceptions.WebDriverException as e:
            logger.debug(e)  # the window is closed

    # set cookies to the requests.Session
    logger.info('Copying cookies via WebDriver...')
    for c in cookies:
        logger.debug('set cookie: %s', c['name'])
        morsel: http.cookies.Morsel = http.cookies.Morsel()
        morsel.set(c['name'], c['value'], c['value'])
        morsel.update({key: value for key, value in c.items() if morsel.isReservedKey(key)})
        if not morsel['expires']:
            expires = datetime.datetime.now(datetime.timezone.utc).astimezone() + datetime.timedelta(days=180)
            morsel.update({'expires': expires.strftime('%a, %d-%b-%Y %H:%M:%S GMT')})  # RFC2109 format
        cookie = requests.cookies.morsel_to_cookie(morsel)
        session.cookies.set_cookie(cookie)  # type: ignore


def is_logged_in_with_message(service: Service, *, session: requests.Session) -> bool:
    if service.is_logged_in(session=session):
        logger.info(utils.SUCCESS + 'You have already signed in.')
        return True
    else:
        logger.info(utils.FAILURE + 'You are not signed in.')
        return False


def run(args: argparse.Namespace) -> bool:
    """
    :returns: whether it is logged in or not.
    """

    service = dispatch.service_from_url(args.url)
    if service is None:
        return False

    with utils.new_session_with_our_user_agent(path=args.cookie) as session:

        if is_logged_in_with_message(service, session=session):
            return True
        else:
            if args.check:
                return False

        if args.use_browser in ('always', 'auto'):
            try:
                login_with_browser(service, session=session)
            except ImportError:
                logger.error('Selenium is not installed. Please run $ pip3 install selenium')
            except WebDriverException as e:
                logger.debug(e)
            else:
                return is_logged_in_with_message(service, session=session)

        if args.use_browser in ('never', 'auto'):
            if args.use_browser == 'auto':
                logger.warning('Switch to use CUI-based login instead of Selenium')
            try:
                login_with_password(service, username=args.username, password=args.password, session=session)
            except NotImplementedError as e:
                logger.exception(e)
            except LoginError as e:
                logger.debug(e)
            except Exception as e:
                logger.exception(e)
            else:
                return is_logged_in_with_message(service, session=session)

        return False
