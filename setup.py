import sys
import shlex

from setuptools import setup, find_packages

REQUIRES = ['flask', 'Pillow']

setup(
    name = 'pymgur',
    version = '0.9',
    install_requires=REQUIRES,
    description = 'pymgur - a python pastebin for images',
    entry_points = {
        'console_scripts': ['pymgur=pymgur:main'],
    },
)
