# -*- coding: utf-8 -*-
"""Installer for the rfa.kaltura2 package."""

from setuptools import find_packages
from setuptools import setup


long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CONTRIBUTORS.rst').read(),
    open('CHANGES.rst').read(),
])


setup(
    name='rfa.kaltura2',
    version='1.0a1',
    description="Kaltura Integration for Plone 5 and Python 3",
    long_description=long_description,
    # Get more from https://pypi.org/classifiers/
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 5.2.1",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords='Python Plone Kaltura Video',
    author='flipmcf',
    author_email='flipmcf@gmail.com',
    url='https://github.com/RadioFreeAsia/rfa.kaltura2',
    project_urls={
        'PyPI': 'https://pypi.python.org/pypi/rfa.kaltura2',
        'Source': 'https://github.com/RadioFreeAsia/rfa.kaltura2',
        'Tracker': 'https://github.com/RadioFreeAsia/rfa.kaltura2/issues',
        # 'Documentation': 'https://rfa.kaltura2.readthedocs.io/en/latest/',
    },
    license='GPL version 2',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['rfa'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    python_requires="==2.7, >=3.6",
    install_requires=[
        'setuptools',
        # -*- Extra requirements: -*-
        'z3c.jbot',
        'plone.api>=1.8.4',
        'plone.restapi',
        'plone.app.dexterity',
        'KalturaApiClient',
        'plone.formwidget.namedfile>=2.0.10',
    ],
    extras_require={
        'test': [
            'plone.app.testing',
            # Plone KGS does not use this version, because it would break
            # Remove if your package shall be part of coredev.
            # plone_coredev tests as of 2016-04-01.
            'plone.testing>=5.0.0',
            'plone.app.contenttypes',
            'plone.app.robotframework[debug]',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    [console_scripts]
    update_locale = rfa.kaltura2.locales.update:update_locale
    """,
)
