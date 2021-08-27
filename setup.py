#!/usr/bin/env python3
from setuptools import find_packages, setup

import onlinejudge_command.__about__ as version

setup(
    name=version.__package_name__,
    version=version.__version__,
    author=version.__author__,
    author_email=version.__email__,
    url=version.__url__,
    license=version.__license__,
    description=version.__description__,
    python_requires='>=3.6',
    install_requires=[
        'online-judge-api-client >= 10.9.0, < 11',
        'colorama >= 0.3, < 1',
        'requests >= 2, < 3',
    ],
    packages=find_packages(exclude=('tests', 'docs')),
    entry_points={
        'console_scripts': [
            'oj = onlinejudge_command.main:main',
        ],
    },
)
