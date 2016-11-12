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
    default_rcpath = os.path.join(os.path.dirname(__file__), 'pylint.rc')
    rcpath = os.environ.get("PYSH_PYLINT_RC", default_rcpath)
    pkg_paths = list(os.environ["PYSH_PYLINT_PKG_PATH"].split(","))
    pylint_plugins = os.environ.get("PYSH_PYLINT_PLUGINS")
    plugin_args = ['--load-plugins', pylint_plugins] if pylint_plugins else []
    args = ['-m', 'pylint', '--rcfile={}'.format(rcpath)] + plugin_args + [
        '-f', 'html'
    ] + pkg_paths
    proc = SH.python3(*args)
    out, err = proc
    # TODO support funneling of calls
    proj_path = os.environ.get("PYSH_PROJ_PATH", os.path.dirname(pkg_paths[0]))
    target_path = os.path.join(proj_path, 'lint.html')
    err_path = os.path.join(proj_path, 'lint_err.txt')
    if err:
        with open(err_path, 'w') as err_file:
            err_file.write(err)

    with open(target_path, 'w') as target_file:
        target_file.write(out)

    if proc.wait():
        raise TestFailure("Linting failed")


def test_yapf():
    """
    Check current code-base for yapf formatting
    """
    pkg_paths = list(os.environ["PYSH_YAPF_PKG_PATH"].split(","))
    proc = SH.python3('-m', 'yapf', '-d', '--recursive', *pkg_paths)
    out, _err = proc
    # TODO support funneling of calls
    proj_path = os.environ.get("PYSH_PROJ_PATH", os.path.dirname(pkg_paths[0]))
    target_path = os.path.join(proj_path, 'yapf.txt')
    if out:
        with open(target_path, 'w') as target_file:
            target_file.write(out)
        raise TestFailure("Format check failed")


@pyshcommand
@nottest
def test(u: (bool, "Just unit tests for the package")=False):
    """
    Run nose tests with coverage, yapf, and pylint
    """
    from pysh.scopes.local import commands, config
    # TODO standardize config interface
    cmd_config = getattr(config, 'COMMAND_OPTIONS', {})
    pylint_plugins = cmd_config.get('pysh.development.test.pylint_plugins')
    commands_path = os.path.abspath(commands.__file__)
    pysh_dir = os.path.dirname(commands_path)
    proj_dir = os.path.dirname(pysh_dir)
    pkg_name = os.path.basename(proj_dir)
    # TODO rc should be configurable
    if pylint_plugins:
        os.environ["PYSH_PYLINT_PLUGINS"] = ",".join(pylint_plugins)
    # TODO fix when shell supports exporting
    os.environ["PYSH_PYLINT_PKG_PATH"] = os.path.join(proj_dir, pkg_name)
    os.environ["PYSH_YAPF_PKG_PATH"] = os.path.join(proj_dir, pkg_name)
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
