#!/usr/bin/env python3
import imp
import os

import setuptools
from pkg_resources import parse_version
from setuptools import setup

assert parse_version('30.0.8') <= parse_version(setuptools.__version__)  # for setup.cfg


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
)
