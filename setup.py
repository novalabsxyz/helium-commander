import re
import ast
from setuptools import setup
from helium.version import __version__

with open('README.rst') as file:
    long_description = file.read()

setup(
    name='helium-commander',
    version=__version__,
    url='http://github.com/helium/helium-commander/',
    license='BSD',
    author='Marc Nijdam',
    author_email='marc@helium.com',
    description='A CLI and service wrapper for the Helium API',
    long_description=long_description,
    packages=['helium', 'helium.commands'],
    platforms='all',
    install_requires=[
        'future>=0.15',
        'requests>=2.9',
        'dpath>=1.4',
        'futures>=3.0',
        'terminaltables>=2.1.0',
        'click>=6.6',
        'unicodecsv>=0.14.1',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        "Topic :: Utilities",
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    entry_points='''
        [console_scripts]
        helium=helium.cli:main
    '''
)
