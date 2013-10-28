#!/usr/bin/env python
#


import os

from setuptools import setup, find_packages, Extension


__HERE__ = os.path.abspath(os.path.dirname(__file__))

# we do not really use these versions...
__VERSION__ = os.environ.get('CANDELABRA_VERSION', open('VERSION', 'r').read().strip())
__RELEASE__ = os.environ.get('CANDELABRA_RELEASE', open('RELEASE', 'r').read().strip())

entry_points = """
[console_scripts]
candelabra  = candelabra.main:main
"""

if __name__ == "__main__":
    setup(
        name='candelabra',
        version=__VERSION__,
        description='Candelabra',

        author='Alvaro Saurin',
        author_email='alvaro.saurin@gmail.com',

        maintainer='Alvaro Saurin',
        maintainer_email='alvaro.saurin@gmail.com',

        url='http://inercia.tumblr.com',
        license='Copyright Alvaro Saurin 2013 - All rights reserved',

        packages=find_packages(),
        package_dir={
            '': '.'
        },

        install_requires=[
            'setuptools',
            'setproctitle',
            'configparser',
            'vbox',
            'pyaml',
        ],

        tests_require=[
            'nose',
        ],

        # install with "pip install -e .[develop]"
        extras_require={
            'develop': [
                'sphinx'
            ],
        },

        entry_points=entry_points,

        zip_safe=False,
    )



