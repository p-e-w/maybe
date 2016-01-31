[![PyPI](https://img.shields.io/pypi/v/maybe.svg)](https://pypi.python.org/pypi/maybe) ![Python versions](https://img.shields.io/pypi/pyversions/maybe.svg)

---


```
rm -rf pic*
```

Are you sure? Are you *one hundred percent* sure?


# `maybe`...

... allows you to run a command and see what it does to your files *without actually doing it!* After reviewing the operations listed, you can then decide whether you really want these things to happen or not.

![Screenshot](screenshot.png)


## What is this sorcery?!?

`maybe` runs processes under the control of [ptrace](https://en.wikipedia.org/wiki/Ptrace) (with the help of the excellent [python-ptrace](https://bitbucket.org/haypo/python-ptrace/) library). When it intercepts a system call that is about to make changes to the file system, it logs that call, and then modifies CPU registers to both redirect the call to an invalid syscall ID (effectively turning it into a no-op) and set the return value of that no-op call to one indicating success of the original call.

As a result, the process believes that everything it is trying to do is actually happening, when in reality nothing is.

That being said, `maybe` **should :warning: NEVER :warning: be used to run untrusted code** on a system you care about! A process running under `maybe` can still do serious damage to your system because only a handful of syscalls are blocked. Currently, `maybe` is best thought of as an (alpha-quality) "what exactly will this command I typed myself do?" tool.


## Installation

`maybe` requires [Python](https://www.python.org/) 2.7+/3.2+ :snake:. If you have the [pip](https://pip.pypa.io) package manager, all you need to do is run

```
pip install maybe
```

either as a superuser or from a [virtualenv](https://virtualenv.pypa.io) environment. To develop `maybe`, clone the repository and run

```
pip install -e .
```

in its main directory to install the package in editable mode.

### Operating system support

| OS | Support status |
| --- | --- |
| Linux | :white_check_mark: Full support |
| FreeBSD / OpenBSD | :ballot_box_with_check: Limited support (subprocesses can not be intercepted) |
| OS X | :question: Might be supported in future pending OS X support in python-ptrace |


## Usage

### Command line

```
maybe COMMAND [ARGUMENT]...
```

No other command line parameters are currently accepted.

### Example

```
maybe mkdir test
```


## License

Copyright &copy; 2016 Philipp Emanuel Weidmann (<pew@worldwidemann.com>)

Released under the terms of the [GNU General Public License, version 3](https://gnu.org/licenses/gpl.html)
