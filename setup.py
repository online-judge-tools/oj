#!/usr/bin/env python3
from setuptools import setup, find_packages
from onlinejudge.implementation.version import __author__, __email__, __license__, __version__

with open('readme.md') as fh:
    readme = fh.read()

setup(
    name='online-judge-tools',
    version=__version__,
    description='Tools for online-judge services',
    install_requires=[
        'requests',
        'beautifulsoup4',
        'colorama',
        'sympy',
    ],
    long_description=readme,
    author=__author__,
    author_email=__email__,
    url='https://github.com/kmyk/online-judge-tools',
    license=__license__,
    packages=find_packages(exclude=( 'tests', 'docs' )),
    scripts=[ 'oj' ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development',
        'Topic :: Text Processing :: Markup :: HTML',
        'Topic :: Utilities',
    ],
)
