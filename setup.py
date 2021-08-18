import os
import sys
from setuptools import setup, find_packages

# https://github.com/microsoft/vscode-recipes/tree/master/debugging%20python

# CI setup based on a mix of:
#   - https://docs.travis-ci.com/user/languages/python/
#   - https://github.com/samgiles/slumber
#   - https://github.com/kiorky/croniter


def read(file):
    return open(file).read()


def requires(file):
    return [
        a.strip()
        for a in read(f"requirements/{file}.txt").splitlines()
        if a.strip() and not a.startswith(("#", "-"))
    ]


exec(read("./crony/manifest.py"))
manifest = locals()

# Sync from .travis.yml to tox.ini:
if sys.argv[-1] == "syncci":
    os.system("panci --to=tox .travis.yml > tox.ini")
    sys.exit()

setup(
    name=manifest["pkgname"],
    version=manifest["version"],
    author="Lee Crosby",
    author_email="lee.crosby@outlook.com",
    maintainer="Lee Crosby",
    maintainer_email="lee.crosby@outlook.com",
    url="http://github.com/cygnut/crony",
    description=manifest["description"],
    long_description=read("README.md"),
    keywords="development, workflow, server, maintenance",
    license="MIT License",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=requires("install"),
    tests_require=requires("test"),
    entry_points={"console_scripts": ["crony = crony.cli:main"]},
    # Required for MANIFEST.in to also install e.g. README.md for use in the long_description.
    include_package_data=True,
    test_suite="tests",
)
