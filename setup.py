"""
rorolite
========

rorolite is a command-line tool to deploy ML applications written in Python to your own server with a single command. It is an open-source tool licensed under Apache license.

The interface of ``rorolite`` is based on the interface of `rorodata platform <http://rorodata.com>`_. While ``rorolite`` is limited to running programs on already created server, the [rorodata platform][rorodata] allows allocating compute resources on demand and provides more tools to streamline data science.

Currently ``rorolite`` is limited to deploying one project per server.

See `<https://github.com/rorodata/rorolite>`_ for more details.

"""
from setuptools import setup, find_packages

__version__ = '0.2.1'

setup(
    name='rorolite',
    version=__version__,
    author='rorodata',
    author_email='rorodata.team@gmail.com',
    description='Command-line tool to deploy ML applications to your own server with a single command',
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'click==6.7',
        'Fabric3>=1.13.1.post1',
        'firefly-python>=0.1.9'
    ],
    entry_points='''
        [console_scripts]
        rorolite=rorolite.main:main
    ''',
)
