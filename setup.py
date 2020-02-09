#!/usr/bin/env python3
import imp

from setuptools import find_packages, setup


def load_module(module_path):
    path = None
    for name in module_path.split('.'):
        file, path, description = imp.find_module(name, path)
        path = [path]
    return imp.load_module(name, file, path[0], description)


version = load_module('onlinejudge.__about__')

setup(
    name=version.__package_name__,
    version=version.__version__,
    author=version.__author__,
    author_email=version.__email__,
    url=version.__url__,
    license=version.__license__,
    description=version.__description__,
    python_requires='>=3.5',
    install_requires=[
        'appdirs >= 1',
        'beautifulsoup4 >= 4',
        'colorama >= 0.3',
        'diff-match-patch >= 20181111',
        'lxml >= 4',
        'requests >= 2',
        'toml >= 0.10',
    ],
    packages=find_packages(exclude=('tests', 'docs')),
    entry_points={
        'console_scripts': [
            'oj = onlinejudge._implementation.main:main',
        ],
    },
)
