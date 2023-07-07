#!/usr/bin/env python3
###################################################################################################
# MIT License
#
# Copyright (c) 2023 The Water Institute
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Author: Zach Cobell
# Contact: zcobell@thewaterinstitute.org
# Organization: The Water Institute
#
###################################################################################################

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
        "prettytable",
    ],
)
