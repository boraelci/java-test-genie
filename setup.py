#!/usr/bin/env python

from genie import __version__
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='java-test-genie',
    version=__version__,
    description='AI-Driven Unit Test Generation for Java',
    author='Bora Elci',
    author_email='bora.elci@columbia.edu',
    url='https://github.com/boraelci/java-test-genie',
    py_modules=[
        'genie.main',
    ],
    packages=find_packages(),
    entry_points={'console_scripts': ['genie = genie.main:main']},
    long_description=long_description,
    long_description_content_type="text/markdown",
)
