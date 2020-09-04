import distutils.version
import http.client
import json
import time
from logging import getLogger
from typing import *

import requests

import onlinejudge.__about__ as api_version
import onlinejudge_command.__about__ as version
from onlinejudge.utils import user_cache_dir

logger = getLogger(__name__)


def describe_status_code(status_code: int) -> str:
    return '{} {}'.format(status_code, http.client.responses[status_code])


def request(method: str, url: str, session: requests.Session, raise_for_status: bool = True, **kwargs) -> requests.Response:
    assert method in ['GET', 'POST']
    kwargs.setdefault('allow_redirects', True)
    logger.info('%s: %s', method, url)
    if 'data' in kwargs:
        logger.debug('data: %s', repr(kwargs['data']))
    resp = session.request(method, url, **kwargs)
    if resp.url != url:
        logger.info('redirected: %s', resp.url)
    logger.info(describe_status_code(resp.status_code))
    if raise_for_status:
        resp.raise_for_status()
    return resp


def get_latest_version_from_pypi(package_name: str) -> str:
    pypi_url = 'https://pypi.org/pypi/{}/json'.format(package_name)
    version_cache_path = user_cache_dir / "pypi.json"
    update_interval = 60 * 60 * 8  # 8 hours

    # load cache
    cache: Dict[str, Any] = {}
    if version_cache_path.exists():
        try:
            logger.debug('load the cache for update checking: %s', str(version_cache_path))
            with version_cache_path.open() as fh:
                cache = json.load(fh)
            if time.time() < cache[package_name]['time'] + update_interval:
                return cache[package_name]['version']
        except Exception as e:
            logger.warning('failed to load the cache in update checking: %s', e)

    # get
    try:
        resp = request('GET', pypi_url, session=requests.Session())
        data = json.loads(resp.content.decode())
        value = data['info']['version']
    except requests.RequestException as e:
        logger.error(str(e))
        value = '0.0.0'  # ignore since this failure is not important
    cache[package_name] = {
        'time': int(time.time()),  # use timestamp because Python's standard datetime library is too weak to parse strings
        'version': value,
    }

    # store cache
    logger.debug('store the cache for update checking: %s', str(version_cache_path))
    version_cache_path.parent.mkdir(parents=True, exist_ok=True)
    with version_cache_path.open('w') as fh:
        json.dump(cache, fh)

    return value


def is_update_available_on_pypi(package_name: str, current_version: str) -> bool:
    a = distutils.version.StrictVersion(current_version)
    b = distutils.version.StrictVersion(get_latest_version_from_pypi(package_name))
    return a < b


def run_for_package(*, package_name: str, current_version: str) -> bool:
    is_updated = not is_update_available_on_pypi(package_name, current_version)
    if not is_updated:
        logger.warning('update available for %s: %s -> %s', package_name, current_version, get_latest_version_from_pypi(package_name))
        logger.info('run: $ pip3 install -U %s', package_name)
    return is_updated


def run() -> bool:
    """
    :returns: :any:`True` if they are updated.
    """

    try:
        is_updated = run_for_package(package_name=version.__package_name__, current_version=version.__version__)
        is_api_updated = run_for_package(package_name=api_version.__package_name__, current_version=api_version.__version__)
        return is_updated and is_api_updated

    except Exception as e:
        logger.error('failed to check update: %s', e)
        return True
