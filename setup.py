import os
from setuptools import setup, find_packages

# https://github.com/microsoft/vscode-recipes/tree/master/debugging%20python

exec(open("./crony/manifest.py").read())
manifest = locals()

setup(
    name = manifest['pkgname'],
    version = manifest['version'],
    author = "Lee Crosby",
    author_email = "lee.crosby@outlook.com",
    description = manifest['description'],
    keywords = "development workflow server maintenance",
    packages = find_packages(),
    python_requires=">=3.6",
    install_requires = [
        'croniter>=0.3',
        'python-crontab>=2.5.1',
        'dateparser>=0.7.6',
        'packaging>=20.4',
    ],
    entry_points = {
        'console_scripts': [
            'crony = crony.cli:main'
        ]
    }
)