import os
import re
import sys
import setuptools
from setuptools.command.install import install

VERSIONFILE="signalum/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

CURRENT_DIR = os.getcwd()
REQUIREMENTS = 'requirements.txt'
requires = [line.strip('\n') for line in open(REQUIREMENTS).readlines()]
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Signalum",
    version=verstr,
    author='Domnan Diretnan, Mmadu Manasseh',
    author_email="diretnandomnan@gmail.com",
    description="Package to analyze existing connections from wifi and bluetooth",
    url="https://github.com/bisoncorps/signalum",
    packages=setuptools.find_packages(),
    install_requires=requires,
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    keywords='bluetooth detect wifi multiprotocol',
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
    ),
    scripts = [
            'signalum/scripts/signalyze'
        ],
    package_data={
        '': ['*.*'],
    },
    include_package_data=True,
    zip_safe=False,
)
