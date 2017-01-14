#!/usr/bin/env python3
from setuptools import setup, find_packages

with open('readme.md') as fh:
    readme = fh.read()

setup(
    name='online-judge-tools',
    version='0.1.6',
    description='Tools for online-judge services',
    install_requires=[
        'requests',
        'beautifulsoup4',
        'colorama',
        'sympy',
    ],
    long_description=readme,
    author='Kimiyuki Onaka',
    author_email='kimiyuki95@gmail.com',
    url='https://github.com/kmyk/online-judge-tools',
    license='MIT License',
    packages=find_packages(exclude=( 'tests', 'docs' )),
    scripts=[ 'oj' ],
    classifiers=[
        'Development Status :: 3 - Alpha',
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
