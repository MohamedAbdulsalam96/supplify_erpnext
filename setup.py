# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

# get version from __version__ variable in supplify_erpnext/__init__.py
_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('supplify_erpnext/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    name='supplify_erpnext',
    version=version,
    description='Drop Ship App for Supplify',
    author='Revant Nandgaonkar',
    author_email='support@castlecraft.in',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=("frappe",),
)
