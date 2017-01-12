#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name='online-judge-tools',
    version='0.1.2',
    description='Tools for online-judge services',
    install_requires=[
        'requests',
        'beautifulsoup4',
        'colorama',
    ],
    author='Kimiyuki Onaka',
    author_email='kimiyuki95@gmail.com',
    url='https://github.com/kmyk/online-judge-tools',
    license='MIT License',
    packages=find_packages(exclude=( 'tests', 'docs' )),
    scripts=[ 'oj' ],
)
