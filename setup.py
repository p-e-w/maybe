# Based on setup.py from https://github.com/pypa/sampleproject

from setuptools import setup, find_packages

setup(
    name="maybe",

    version="0.2.1",

    description="See what a program does before deciding whether you really want it to happen.",
    long_description="For a detailed description, see https://github.com/p-e-w/maybe.",

    url="https://github.com/p-e-w/maybe",

    author="Philipp Emanuel Weidmann",
    author_email="pew@worldwidemann.com",

    license="GPLv3",

    classifiers=[
        "Development Status :: 3 - Alpha",

        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: System Administrators",

        "Topic :: Utilities",

        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",

        "Operating System :: POSIX :: Linux",
        "Operating System :: POSIX :: BSD :: FreeBSD",
        "Operating System :: POSIX :: BSD :: OpenBSD",

        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],

    keywords="sandbox files access",

    packages=find_packages(),

    install_requires=[
        "blessings",
        "python-ptrace",
    ],

    entry_points={
        "console_scripts": [
            "maybe = maybe.maybe:main",
        ],
    },
)
