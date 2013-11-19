#!/usr/bin/env python
#


import os

from setuptools import setup, find_packages


__HERE__ = os.path.abspath(os.path.dirname(__file__))

# we do not really use these versions...
__VERSION__ = os.environ.get('CANDELABRA_VERSION', open('VERSION', 'r').read().strip())
__RELEASE__ = os.environ.get('CANDELABRA_RELEASE', open('RELEASE', 'r').read().strip())

entry_points = """
[console_scripts]
candelabra  = candelabra.main:main

[candelabra.command]
destroy = candelabra.command.destroy.plugin:register
down = candelabra.command.down.plugin:register
import = candelabra.command.import.plugin:register
net = candelabra.command.net.plugin:register
provision = candelabra.command.provision.plugin:register
show = candelabra.command.show.plugin:register
up = candelabra.command.up.plugin:register

[candelabra.provider]
virtualbox = candelabra.provider.virtualbox.plugin:register

[candelabra.provisioner]
puppet = candelabra.provisioner.puppet.plugin:register

[candelabra.guest]
linux = candelabra.guest.linux.plugin:register

[candelabra.communicator]
ssh = candelabra.communicator.ssh.plugin:register
virtualbox = candelabra.communicator.virtualbox.plugin:register
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

        # trying to add files...
        include_package_data=True,
        package_data={
            '': ['static/*.conf']
        },

        install_requires=[
            'setuptools',
            'configparser',
            'requests',
            'pyvbox',
            'pyaml',
            'colorlog',
            'ssh',
            'paramiko',
            'fabric',
        ],

        test_suite='nose.collector',
        tests_require=[
            'nose',
        ],

        # install with "pip install -e .[develop]"
        extras_require={
            'develop': [
                'sphinx',
                'sphinxtogithub',
                'sphinx_bootstrap_theme',
            ],
            'tests' : [
                'nose',
            ]
        },

        entry_points=entry_points,

        zip_safe=False,
    )



