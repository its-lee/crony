import os
from setuptools import setup, find_packages

# https://github.com/microsoft/vscode-recipes/tree/master/debugging%20python

def read(file):
    return open(file).read()

exec(read("./crony/manifest.py"))
manifest = locals()

long_description = read('README.md')

install_requires = [
    a.strip()
    for a in read('requirements/base.txt').splitlines()
    if a.strip() and not a.startswith(('#', '-'))
]

setup(
    name = manifest['pkgname'],
    version = manifest['version'],
    author = "Lee Crosby",
    author_email = "lee.crosby@outlook.com",
    url='http://github.com/cygnut/crony',
    description = manifest['description'],
    long_description=long_description,
    keywords = "development, workflow, server, maintenance",
    licence = 'MIT License',
    packages = find_packages(),
    python_requires=">=3.6",
    install_requires = install_requires,
    entry_points = {
        'console_scripts': [
            'crony = crony.cli:main'
        ]
    },
    # Required for MANIFEST.in to also install e.g. README.md for use in the long_description.
    include_package_data=True
)
