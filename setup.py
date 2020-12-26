# --------------------------------------------
# Copyright 2020, Roberto Himmelbauer
# @Author: Roberto Himmelbauer
# @Date:   2020-12-26 07:41:42
# --------------------------------------------

from os import path
from setuptools import setup, find_packages

from barter.__version__ import VERSION

readme_file = path.join(path.dirname(path.abspath(__file__)), 'README.md')

try:
    from m2r import parse_from_file
    long_description = parse_from_file(readme_file)     # Convert the file to RST for PyPI
except ImportError:
    # m2r may not be installed in user environment
    with open(readme_file) as f:
        long_description = f.read()


package_metadata = {
    'name': 'django-barter',
    'version': VERSION,
    'description': 'Django App Toolkit for selling digital and physical goods online.',
    'long_description': long_description,
    'url': 'https://github.com/rhimmelbauer/django-barter/',
    'author': 'Grant Viklund, Roberto Himmelbauer',
    'author_email': 'robertoh89@gmail.com',
    'license': 'MIT license',
    'classifiers': [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    'keywords': ['django', 'app'],
}

setup(
    packages=find_packages(),
    package_data={'barter': ['templates/barter/*.html', 'templates/barter/*/*.html']},
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=[
        'Django>=3.1,<3.2',
        'django-autoslug',
        'django-extensions',
        'iso4217',
    ],
    extras_require={
        'dev': [
            'dj-database-url',
            'psycopg2-binary',
            'django-crispy-forms',
            'django-allauth',
            ],
        'stripe': [             # Packages needed for Stripe
            'stripe>=2.48.0,<3.0',
            ],
        'authorizenet': [
            'authorizenet',
        ],
        'test': [],
        'prod': [],
        'build': [
            'setuptools',
            'wheel',
            'twine',
            'm2r',
        ],
        'docs': [
            'recommonmark',
            'm2r',
            'django_extensions',
            'coverage',
            'Sphinx',
            'rstcheck',
            'sphinx-rtd-theme'
        ],
    },
    **package_metadata
)