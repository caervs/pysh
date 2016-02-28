"""
Examples of pysh commands for common development workflows
"""

import os

from nose.tools import nottest

from pysh.interface.command import pyshcommand
from pysh.interface.shell import Shell

SH = Shell(search_path='')


class TestFailure(Exception):
    """
    raised when a test fails
    """
    pass


def test_lint():
    """
    Lint the current codebase
    """
    rcpath = os.environ.get("PYSH_PYLINT_RC", "pylint.rc")
    pkg_path = os.environ["PYSH_PYLINT_PKG_PATH"]
    proc = SH.python3('-m', 'pylint', '--rcfile={}'.format(rcpath), '-f',
                      'html', pkg_path)
    out, _err = proc
    # TODO support funneling of calls
    proj_path = os.path.dirname(pkg_path)
    target_path = os.path.join(proj_path, 'lint.html')
    with open(target_path, 'w') as target_file:
        target_file.write(out)

    if proc.wait():
        raise TestFailure("Linting failed")


def test_yapf():
    """
    Check current code-base for yapf formatting
    """
    pkg_path = os.environ["PYSH_PYLINT_PKG_PATH"]
    proc = SH.python3('-m', 'yapf', '-d', '--recursive', pkg_path)
    out, _err = proc
    # TODO support funneling of calls
    proj_path = os.path.dirname(pkg_path)
    target_path = os.path.join(proj_path, 'yapf.txt')
    if proc.wait():
        with open(target_path, 'w') as target_file:
            target_file.write(out)
        raise TestFailure("Format check failed")


@pyshcommand
@nottest
def test(u: (bool, "Just unit tests for the package")=False):
    """
    Run nose tests with coverage, yapf, and pylint
    """
    from pysh.scopes.local import commands
    commands_path = os.path.abspath(commands.__file__)
    pysh_dir = os.path.dirname(commands_path)
    proj_dir = os.path.dirname(pysh_dir)
    pkg_name = os.path.basename(proj_dir)
    # TODO rc should be configurable
    rcpath = os.path.join(os.path.dirname(__file__), 'pylint.rc')
    # TODO fix when shell supports exporting
    os.environ["PYSH_PYLINT_RC"] = rcpath
    os.environ["PYSH_PYLINT_PKG_PATH"] = os.path.join(proj_dir, pkg_name)
    if u:
        return SH.python3('-m', 'nose', '--with-coverage', pkg_name)
    return SH.python3('-m', 'nose', '--with-coverage', pkg_name,
                      'pysh.examples.development')


def build():
    """
    build any docker images associated with this project
    """
    # TODO
    raise NotImplementedError


def mkvenv():
    """
    Create a virtual environment and install necessary packages
    """
    # TODO
    raise NotImplementedError


def enter():
    """
    Enter the virtual environment for the project
    """
    # TODO
    raise NotImplementedError
