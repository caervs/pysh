"""
main interface for pysh: core tools for running pysh commands
"""

import enum
import importlib
import os
import subprocess

from pysh.interface.command import ProcessCommand

STANDARD_SEARCH_PATH = ":".join(["pysh.scopes.local.commands",
                                 "pysh.scopes.user.commands",
                                 "pysh.scopes.global.commands",
                                 "pysh.scopes.standard.commands", ])

SEARCH_PATH = os.environ.get("PYSHPATH", STANDARD_SEARCH_PATH)

# TODO think of a better way to suppress CommandCall output
DELETE_STRING = "--DELETE NEXT 348ty1[29yavi--"


class CommandCall(object):
    """
    A wrapper to allow for easy stringing of pysh commands
    """

    def __init__(self, command=None, commands=None):
        self.command = command
        self.commands = commands if commands else [command]
        self.status = None

    def __or__(self, other):
        left_commands = self.commands
        right_commands = other.commands
        return PipingCall(left_commands + right_commands)

    def __gt__(self, filename):
        return FunnelCall(self, filename)

    def __call__(self, wait=True, **channels):
        if self.status is not None:
            return
        self.status = 'called'
        return self.command(wait=wait, **channels)

    def __iter__(self):
        self(stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        yield self.to_str(self.command.stdout.read())
        yield self.to_str(self.command.stderr.read())

    def __repr__(self):
        self()
        return DELETE_STRING

    def wait(self):
        """
        wait for command to finish
        """
        return self.command.wait()

    @staticmethod
    def to_str(str_or_byte):
        """
        decode byte from utf-8 encoding
        """
        if isinstance(str_or_byte, str):
            return str_or_byte
        return str_or_byte.decode("utf-8")


# TODO should subclass CommandCall
class FunnelCall(object):
    """
    A command whose output is written to a file
    """

    def __init__(self, command_call, outfile):
        self.command_call = command_call
        self.outfile = outfile

    def __call__(self, **kwargs):
        with open(self.outfile, 'w') as f:
            kwargs['stdout'] = f
            return self.command_call(**kwargs)

    def __repr__(self):
        self()
        return DELETE_STRING


# TODO should be able to generalize to arbitrary IO redirection
class PipingCall(CommandCall):
    """
    A CommandCall which pipes output from one command into another
    """

    def __init__(self, commands):
        super().__init__(commands=commands)

    def __call__(self, wait=True, **channels):
        first, *middle, last = self.commands
        first_channels = {'stdout': subprocess.PIPE}
        if 'stdin' in channels:
            first_channels['stdin'] = channels['stdin']
            del channels['stdin']
        first(wait=False, **first_channels)
        previous_command = first
        for command in middle:
            command(wait=False,
                    stdin=previous_command.stdout,
                    stdout=subprocess.PIPE)
            previous_command = command
        last(wait=False, stdin=previous_command.stdout, **channels)
        if wait:
            self.wait()

    def wait(self):
        """
        wait for subcommands to finish
        """
        for command in self.commands:
            command.wait()

    def __iter__(self):
        self(stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        yield self.to_str(self.commands[-1].stdout.read())
        yield self.to_str(self.commands[-1].stderr.read())


class ExecutionMode(enum.Enum):
    """
    The execution mode of the shell:

    on_init: when the command is first initialized
    on_read: when the caller tries to get output from the command
    """
    on_init = 0
    on_read = 1


class PartialCall(object):
    """
    A call which has not yet been given arguments
    """

    def __init__(self, command_factory, working_dir):
        # TODO proper wrapping of command_factory
        self.command_factory = command_factory
        self.working_dir = working_dir

    def __call__(self, *args, **kwargs):
        os.chdir(self.working_dir)
        return CommandCall(self.command_factory(*args, **kwargs))

    def __repr__(self):
        return repr(self())

    def __or__(self, other):
        # TODO support reverse operations
        if isinstance(other, PartialCall):
            return self() | other()
        return self() | other

    def __gt__(self, outfile):
        return self() > outfile


class Shell(object):
    """
    A means to calling pysh commands
    """

    def __init__(self,
                 working_dir='.',
                 search_path=SEARCH_PATH,
                 execution_mode=ExecutionMode.on_read):
        if execution_mode != ExecutionMode.on_read:
            raise NotImplementedError(
                "Non on-read execution mode not implemented")
        self.search_objs = self.get_search_objs(search_path)
        self.working_dir = working_dir

    def cd(self, new_dir):
        """
        change the working directory of the shell
        """
        self.working_dir = new_dir

    def export(self, **kwargs):
        """
        export a variable to any subcommands
        """
        self.exports.update(kwargs)

    @staticmethod
    def get_search_objs(search_path):
        """
        return a list of objects in which to search for subcommands
        """
        if not search_path:
            return []
        return [importlib.import_module(module)
                for module in search_path.split(":")]

    def __getattr__(self, cmd_name):
        for search_obj in self.search_objs:
            if hasattr(search_obj, cmd_name):
                command_factory = getattr(search_obj, cmd_name)
                return PartialCall(command_factory, self.working_dir)
        return PartialCall(
            ProcessCommand.from_proc_name(cmd_name), self.working_dir)


class FallbackChain(object):
    """
    gets attrs by searching a chain of objects in sequence for that attr
    """

    def __init__(self, *obj_chain):
        self.__dict__['obj_chain'] = obj_chain

    def __getattr__(self, attr_name):
        for obj in self.obj_chain:
            if hasattr(obj, attr_name):
                return getattr(obj, attr_name)
        raise AttributeError(attr_name)

    def __setattr__(self, attr_name, attr):
        return setattr(self.obj_chain[0], attr_name, attr)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)
