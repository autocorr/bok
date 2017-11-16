#!/usr/bin/env python3

from os import path
from setuptools import setup


here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), 'r') as f:
    long_description = f.read()


setup(
    name='Bok',
    version='0.1',
    description='Bok programming language',
    long_description=long_description,
    author='Brian Svoboda',
    license='GPLv3',
    url='https://github.com/autocorr/bok',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Interpreters',
    ],
    keywords='concatentive',
    packages=['bok'],
    install_requires=[
        'termcolor',
        'lark-parser',
        'pygments',
        'prompt_toolkit',
    ],
    python_requires='>=3',
    extras_require={
        'test': ['pytest'],
    }
    data_files=[
        ('lib', ['lib/std.bok']),
    ],
    package_data={
        'lib': 'std.bok',
    },
)
