#!/usr/bin/env python

from setuptools import setup

setup(
    name="metbuild",
    version="0.0.1",
    description="MetBuild Internal Library",
    author="Zach Cobell",
    author_email="zcobell@thewaterinstitute.org",
    url="https://www.thewaterinstitute.org/",
    packages=[
        "metbuild",
    ],
    install_requires=[
        "sqlalchemy",
        "psycopg2",
        "python-dateutil",
    ],
)
