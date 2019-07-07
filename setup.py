# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='ocandata',
    version='0.1.0',
    description='Open Canada data',
    long_description=readme,
    author='Dwight Gunning',
    author_email='dgunning@gmail.com',
    url='https://github.com/ocan-data/OpenCanadaData',
    license=license,
    packages=['ocandata']
)