from setuptools import setup

author = 'Helium'
author_email = 'hello@helium.com'
install_requires = [
    'helium-python>=0.2.0',
    'future>=0.15',
    'dpath>=1.4',
    'futures>=3.0',
    'terminaltables>=2.1.0',
    'click>=6.6',
    'unicodecsv>=0.14.1',
]
setup_requires = [
    'vcversioner',
]

with open('README.md', 'r') as infile:
    long_description = infile.read()

setup(
    name='helium-commander',
    url='http://github.com/helium/helium-commander/',
    author=author,
    author_email=author_email,
    long_description=long_description,
    license='BSD',
    description='A CLI and service wrapper for the Helium API',
    packages=['helium_commander', 'helium_commander.commands'],
    platforms='all',
    install_requires=install_requires,
    setup_requires=setup_requires,
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
    vcversioner={
        "version_module_paths": ["helium_commander/_version.py"]
    },
    entry_points='''
        [console_scripts]
        helium=helium_commander.cli:main
    '''
)
