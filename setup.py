# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 Northwestern University.
#
# invenio-subjects-lcsh is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""LCSH subject terms for InvenioRDM"""

from setuptools import find_packages, setup

readme = open('README.md').read()
history = open('CHANGES.md').read()

tests_require = [
    'pytest-invenio>=1.4.7,<2.0.0',
]

dev_requires = [
    'click>=7.0,<9.0',
    'pyyaml>=5.4.1,<7.0',
    'requests>=2.25.1,<3.0'
]

extras_require = {
    'tests': tests_require,
    'dev': dev_requires
}

extras_require['all'] = []
for reqs in extras_require.values():
    extras_require['all'].extend(reqs)

packages = find_packages()

setup(
    name='invenio-subjects-lcsh',
    description=__doc__,
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/markdown',
    keywords='invenio inveniordm subjects LCSH',
    license='MIT',
    author='Northwestern University',
    author_email='DL_FSM_GDS@e.northwestern.edu',
    url='https://github.com/galterlibrary/invenio-subjects-lcsh',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'console_scripts': [
            "invenio-subjects-lcsh = invenio_subjects_lcsh.cli:main"
        ],
        'invenio_rdm_records.fixtures': [
            'invenio_subjects_lcsh = invenio_subjects_lcsh.vocabularies',
        ],
    },
    extras_require=extras_require,
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
