import re
import ast
from setuptools import setup


_version_re = re.compile(r'__version__=(.*)')

with open('helium/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))


setup(
    name='Helium',
    version=version,
    url='http://github.com/helium/api_example/',
    license='BSD',
    author='Marc Nijdam',
    author_email='marc@helium.com',
    description='A CLI and service wrapper for the Helium API',
    long_description=__doc__,
    packages=['helium'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'requests>=2.9',
        'dpath>=1.4',
        'futures>=3.0',
        'tablib>=0.11',
        'click>=6.6',
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
