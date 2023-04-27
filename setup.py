#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='java-test-genie',
    version='0.1.0',
    description='AI-Driven Unit Test Generation for Java',
    author='Bora Elci',
    author_email='bora.elci@columbia.edu',
    url='https://github.com/boraelci/java-test-genie',
    py_modules=[
        'genie.main',
    ],
    packages=find_packages(),
    entry_points={'console_scripts': ['genie = genie.main:main']},
)
