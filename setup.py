"""
	Copyright (C) 2022 Victor Chavez
    This file is part of Relative Include
	
    IOLink Device Generator is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    IOLink Device Generator is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with Relative Include.  If not, see <https://www.gnu.org/licenses/>.
"""
# Standard library imports
import pathlib
# Third party imports
from setuptools import setup
import re
VERSIONFILE="relative_include/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

# The directory containing this file
HERE = pathlib.Path(__file__).resolve().parent

# The text of the README file is used as a description
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="relative_include",
    version="1.0.0",
    description="Makes include paths for a C/C++ lib relative",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/vChavezB/include-relative",
    author="Victor Chavez",
    author_email="vchavezb@protonmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
		"Operating System :: OS Independent",
    ],
    packages=["relative_include"],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "relative-include=RelativeInclude.__main__:main",
        ]
    },
)
