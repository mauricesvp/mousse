# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="mousse",
    version="0.1.0",
    description="Module Search Super Easy",
    author="mauricesvp",
    url="https://github.com/mauricesvp/mousse",
    package_data={"mousse": ["py.typed"]},
    packages=find_packages(),
    zip_safe=False,
)
