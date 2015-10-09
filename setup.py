#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = [line.strip() for line in open("requirements.txt").readlines()]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='yamt',
    version='0.1.1',
    description='"A Make-like tool with a syntax similar to Drake."',
    long_description=readme + '\n\n' + history,
    author='Hugo Martiniano',
    author_email='hugomartiniano@gmail.com',
    url='https://github.com/hmartiniano/yamt',
    packages=[
        'yamt',
    ],
    package_dir={'yamt':
                 'yamt'},
    entry_points={
        'console_scripts': [
            'yamt = yamt.main:main',
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='yamt',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
