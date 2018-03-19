#!/usr/bin/env python3
from setuptools import setup, find_packages

import imp
def load_module(module_path):
    path = None
    for name in module_path.split('.'):
        file, path, description = imp.find_module(name, path)
        path = [ path ]
    return imp.load_module(name, file, path[0], description)
version = load_module('onlinejudge.implementation.version')

with open('readme.md', encoding='utf-8') as fh:
    readme = fh.read()

setup(
    name='online-judge-tools',
    version=version.__version__,
    description='Tools for online-judge services',
    install_requires=[
        'requests',
        'lxml',
        'beautifulsoup4',
        'colorama',
        'sympy',
    ],
    long_description=readme,
    author=version.__author__,
    author_email=version.__email__,
    url=version.__url__,
    license=version.__license__,
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
