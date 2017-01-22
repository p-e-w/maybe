# Based on setup.py from https://github.com/pypa/sampleproject

from setuptools import setup

setup(
    name="maybe",

    version="0.4.0",

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

        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],

    keywords="sandbox files access",

    packages=["maybe"],

    install_requires=[
        "six==1.10.0",
        "blessings==1.6",
        "python-ptrace==0.9.1",
    ],

    setup_requires=[
        "pytest-runner>=2.7",
    ],
    tests_require=[
        "pytest>=2.9.1",
    ],

    entry_points={
        "console_scripts": [
            "maybe = maybe.maybe:main",
        ],
    },
)
