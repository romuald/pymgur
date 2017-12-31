import sys
import shlex

from setuptools import setup, find_packages

REQUIRES = ['flask', 'Pillow']

setup(
    name = 'pycasso',
    version = '0.9',
    install_requires=REQUIRES,
    description = 'Pycasso - a python pastebin for images',
    entry_points = {
        'console_scripts': ['pycasso=pycasso:main'],
    },
)