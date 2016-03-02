# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

version = '1.0.0'

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
