#!/usr/bin/python3

import sys
import os
import shutil
import setuptools
from setuptools.command.install import install


def build_pewinput():
    print(': removing pewinput')
    if os.path.exists('pewinput'):
        shutil.rmtree('pewinput')
    print(': building pewinput')
    os.mkdir('pewinput')
    shutil.copy('src/pewinput.py', 'pewinput/__init__.py')
    os.system('cc -Wall -Werror -pedantic src/pewinput.c -o pewinput/libpewinput.so -fPIC -shared')


class BuildAndInstall(install):

    def run(self):
        build_pewinput()
        super(BuildAndInstall, self).run()


with open('README.md') as readme:
    long_description = readme.read()

setuptools.setup(
    name="pewinput-ssmid",
    version='1.0.0',
    author='ssmid@github',
    description='A library to emulate input devices on linux',
    long_description=long_description,
    url='https://github.com/ssmid/pewinput',
    packages=setuptools.find_packages(),
    package_data={
        'pewinput': ['libpewinput.so']
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux'
    ],
    python_requires='>=3.6',
    cmdclass={
        'install': BuildAndInstall
    }
)
