from setuptools import setup, find_packages
import os.path

__version__ = '0.1.0'

setup(
    name='rorolite',
    version=__version__,
    author='rorodata',
    author_email='rorodata.team@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click==6.7',
        'Fabric3>=1.13.1.post1',
    ],
    entry_points='''
        [console_scripts]
        rorolite=rorolite.main:main
    ''',
)
