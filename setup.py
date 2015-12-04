__author__ = 'Ben'
# Always prefer setuptools over distutils
from setuptools import setup, find_packages

setup(include_package_data=True, install_requires=['Django', 'praw', 'pymongo', 'requests', 'wikipedia', 'redis'])