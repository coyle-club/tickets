#!/usr/bin/env python

from distutils.core import setup

setup(
    name="tickets",
    version="1.0",
    description="Tickets",
    author="Tom Petr",
    author_email="trpetr@gmail.com",
    packages=["tickets"],
    install_requires=["aiosqlite", "quart", "hypercorn"],
    entry_points={"console_scripts": ["tickets=tickets:main"]},
)
