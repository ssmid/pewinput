#!/usr/bin/python3

import setuptools


with open('README.md') as readme:
    long_description = readme.read()

setuptools.setup(
    name="pewinput-ssmid",
    version='0.0.1',
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
    python_requires='>=3.6'
)
