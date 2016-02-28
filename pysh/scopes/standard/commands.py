import functools

from pysh.interface.command import Command, FunctionCommand
from pysh.interface.shell import Shell

SH = Shell()


def init():
    """
    Initialize this source-tree for project specific pysh commands
    """
    pass


def edit():
    """
    Edit a pysh command or module
    """
    pass


def config():
    """
    Modify or read pysh settings
    """
    pass


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
def ls():
    """
    List existing pysh commands
    """
    for module in SH.search_objs:
        getmodattr = functools.partial(getattr, module)
        all_attrs = dict(zip(dir(module), map(getmodattr, dir(module))))
        cmd_attrs = {
            attrname: attr
            for attrname, attr in all_attrs.items()
            if getattr(attr, 'is_pysh_command', False) == True
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
