"""
Commands accessible from any pysh project
"""

import os
import functools

from pysh.interface.command import FunctionCommand, pyshcommand
from pysh.interface.shell import Shell

SH = Shell()


@FunctionCommand.from_generator
def init():
    """
    Initialize this source-tree for project-specific pysh commands
    """
    yield "Making .pysh directory"
    SH.mkdir(".pysh")()
    SH.touch(".pysh/commands.py", ".pysh/config.py")()
    yield "Done"


@pyshcommand
def edit():
    """
    Edit a pysh command or module
    """
    from pysh.interface.hook import PyshImportHook
    pysh_dir = PyshImportHook.find_project_pysh_dir()
    return getattr(SH, os.environ.get(
        "EDITOR", "nano"))(os.path.join(pysh_dir, 'commands.py'))


def config():
    """
    Modify or read pysh settings
    """
    raise NotImplementedError


def _readable_description(module_name):
    """
    return a readable name for known modules
    """
    known_descriptions = {
        "pysh.scopes.standard.commands": "Standard Commands",
        "pysh.scopes.local.commands": "Local Commands",
        "pysh.scopes.global.commands": "Global Commands",
        "pysh.scopes.user.commands": "User Commands",
    }
    return known_descriptions.get(module_name, module_name)


@FunctionCommand.from_generator
def cmds():
    """
    List existing pysh commands
    """
    for module in SH.search_objs:
        getmodattr = functools.partial(getattr, module)
        all_attrs = dict(zip(dir(module), map(getmodattr, dir(module))))
        cmd_attrs = {
            attrname: attr
            for attrname, attr in all_attrs.items()
            if getattr(attr, 'is_pysh_command', False) is True
        }

        if not cmd_attrs:
            continue
        yield ''
        yield _readable_description(module.__name__)
        yield "=" * len(module.__name__)
        for command_name in sorted(cmd_attrs):
            docstr_parts = cmd_attrs[command_name].__doc__.split("\n")
            docstr = docstr_parts[0] if docstr_parts[0] or not\
                     (len(docstr_parts) > 1) else docstr_parts[1]
            yield "{}: {}".format(command_name, docstr)
