#!/usr/bin/env python3
################################################################################
# MetGet Client
#
# This file is part of the MetGet distribution (https://github.com/waterinstitute/metget).
# Copyright (c) 2023, The Water Institute
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Author: Zach Cobell, zcobell@thewaterinstitute.org
#
################################################################################

from setuptools import setup

DEFAULT_VERSION_NUMBER = "0.0.1"


def check_for_path_executable(executable: str) -> tuple:
    from shutil import which

    path = which(executable)
    if path:
        return True, path
    else:
        return False, None


def write_version(version_number) -> str:
    with open("metgetclient/__init__.py", "w") as f:
        f.write('__version__ = "{:s}"'.format(version_number))
    return version_number


def check_version() -> str:
    import subprocess

    has_git, git_path = check_for_path_executable("git")
    if has_git:
        try:
            version = subprocess.run(
                ["git", "describe", "--always", "--tags"], capture_output=True
            )
            version_str = version.stdout.strip().decode("utf-8")
        except subprocess.CalledProcessError as e:
            return DEFAULT_VERSION_NUMBER
        return version_str
    else:
        return DEFAULT_VERSION_NUMBER


metget_client_version = check_version()
write_version(metget_client_version)

setup(
    name="metget-client",
    version="0.0.1",
    description="MetGet Client Application",
    author="Zach Cobell",
    author_email="zcobell@thewaterinstitute.org",
    url="https://www.thewaterinstitute.org/",
    packages=[
        "metgetclient",
    ],
    scripts=["metget-client"],
    install_requires=[
        "requests",
        "halo",
    ],
)
