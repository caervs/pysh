import enum
import functools
import importlib
import os
import subprocess
import sys

from pysh.interface.command import ProcessCommand

STANDARD_SEARCH_PATH = ":".join(["pysh.scopes.local.commands",
                                 "pysh.scopes.user.commands",
                                 "pysh.scopes.global.commands",
                                 "pysh.scopes.standard.commands", ])

SEARCH_PATH = os.environ.get("PYSHPATH", STANDARD_SEARCH_PATH)
DELETE_STRING = "--DELETE NEXT 348ty1[29yavi--"


class CommandCall(object):
    def __init__(self, command):
        self.command = command
        self.status = None

    def __or__(self, other):
        left_commands = [self.command] if hasattr(self, 'command') else \
                        self.commands
        right_commands = [other.command] if hasattr(other, 'command') else \
                         other.commands
        return PipingCall(left_commands + right_commands)

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

    @staticmethod
    def to_str(str_or_byte):
        if isinstance(str_or_byte, str):
            return str_or_byte
        return str_or_byte.decode("utf-8")


# TODO should be able to generalize to arbitrary IO redirection
class PipingCall(CommandCall):
    def __init__(self, commands):
        self.commands = commands

    def __call__(self, wait=True, **channels):
        first, *middle, last = self.commands
        first_channels = {'stdout': subprocess.PIPE}
        last_channels = channels
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
            for command in self.commands:
                command.wait()

    def __iter__(self):
        self(stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        yield self.to_str(self.commands[-1].stdout.read())
        yield self.to_str(self.commands[-1].stderr.read())


class ExecutionMode(enum.Enum):
    on_init = 0
    on_read = 1


class PartialCall(object):
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


class Shell(object):
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
        self.working_dir = new_dir

    def export(self, **kwargs):
        self.exports.update(kwargs)

    @staticmethod
    def get_search_objs(search_path):
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
    def __init__(self, *obj_chain):
        self.__dict__['obj_chain'] = obj_chain

    def __getattr__(self, attr_name):
        for obj in self.obj_chain:
            if hasattr(obj, attr_name):
                return getattr(obj, attr_name)
        raise AttributeError(key)

    def __setattr__(self, attr_name, attr):
        return setattr(self.obj_chain[0], attr_name, attr)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)
