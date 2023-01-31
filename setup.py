#!/usr/bin/env python3

import os
import re
from setuptools import setup


__pgdr = "PG Drange <Pal.Drange@uib.no>"
__source = "https://github.com/pgdr/cristin"
__webpage = __source
__description = "cristin API"



def _src(x):
    root = os.path.dirname(__file__)
    return os.path.abspath(os.path.join(root, x))


def _read_file(fname, op):
    with open(_src(fname), "r") as fin:
        return op(fin.readlines())


def readme():
    try:
        return _read_file("README.md", lambda lines: "".join(lines))
    except Exception:
        return __description


VERSIONFILE = "cristin/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

setup(
    version=verstr,
    name="cristin",
    packages=["cristin"],
    description=__description,
    long_description=readme(),
    long_description_content_type="text/markdown",
    author="PG Drange",
    author_email="Pal.Drange@uib.no",
    maintainer=__pgdr,
    url=__webpage,
    project_urls={
        "Bug Tracker": "{}/issues".format(__source),
        "Documentation": "{}/blob/master/README.md".format(__source),
        "Source Code": __source,
    },
    license="MIT",
    keywords="cristin",
    install_requires=["requests"],
    entry_points={
        "console_scripts": [
            "cristin = cristin:main",
        ],
    },
)
