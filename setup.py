import re
import ast
import platform
from setuptools import setup, find_packages
from smycli import __version__

description = 'Base on  the MYCLI CLI for MySQL Database,add additional secure manner via ssh tunnel'

install_requirements = [
    'paramiko >= 1.7.7.1',
    'mycli >= 1.8.1',
]
version = __version__
setup(
    name='smycli',
    author='xgtiger',
    author_email='xgtiger@163.com',
    version=version,
    url='https://github.com/XGTIGER/smycli',
    packages=find_packages(),
    package_data={'smycli': ['../AUTHORS']},
    description=description,
    long_description=open('README.md').read(),
    keywords="cli mysql mycli",
    license="MIT",
    install_requires=install_requirements,
    entry_points='''
            [console_scripts]
            smycli=smycli.main:scli
        ''',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: SQL',
        'Topic :: Database',
        'Topic :: Database :: Front-Ends',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
