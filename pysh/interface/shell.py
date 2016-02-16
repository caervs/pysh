import enum
import functools
import importlib
import os
import subprocess

from pysh.interface.command import ProcessCommand

STANDARD_SEARCH_PATH = ":".join(["pysh.scopes.local.commands",
                                 "pysh.scopes.user.commands",
                                 "pysh.scopes.global.commands",
                                 "pysh.scopes.standard.commands", ])

SEARCH_PATH = os.environ.get("PYSHPATH", STANDARD_SEARCH_PATH)


class CommandResult(object):
    def __init__(self, command):
        self.command = command
        self.status = None

    def __or__(self, other):
        return PipingResult(self.command, other.command)

    def __call__(self, wait=True, **channels):
        if self.status is not None:
            return
        self.status = 'called'
        return self.command(wait=wait, **channels)

    def __iter__(self):
        self(stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        yield self.to_str(self.command.stdout.read())
        yield self.to_str(self.command.stderr.read())

    @staticmethod
    def to_str(str_or_byte):
        if isinstance(str_or_byte, str):
            return str_or_byte
        return str_or_byte.decode("utf-8")


# TODO should be able to generalize to arbitrary IO redirection
class PipingResult(CommandResult):
    def __init__(self, carcmd, cdrcmd):
        self.carcmd = carcmd
        self.cdrcmd = cdrcmd

    def __call__(self, wait=True, **channels):
        car_channels = {'stdout': subprocess.PIPE}
        cdr_channels = channels
        if 'stdin' in channels:
            car_channels['stdin'] = channels['stdin']
            del channels['stdin']
        self.carcmd(wait=False, **car_channels)
        self.cdrcmd(wait=False, stdin=self.carcmd.stdout, **cdr_channels)
        if wait:
            return self.carcmd.wait(), self.cdrcmd.wait()

    def __iter__(self):
        self(stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        yield self.to_str(self.cdrcmd.stdout.read())
        yield self.to_str(self.cdrcmd.stderr.read())


class ExecutionMode(enum.Enum):
    on_init = 0
    on_read = 1


class Shell(object):
    def __init__(self,
                 working_dir,
                 search_path=SEARCH_PATH,
                 execution_mode=ExecutionMode.on_read):
        if execution_mode != ExecutionMode.on_read:
            raise NotImplementedError(
                "Non on-read execution mode not implemented")
        self.search_objs = self.get_search_objs(search_path)

    def cd(self, new_dir):
        self.working_dir = new_dir

    def export(self, **kwargs):
        self.exports.update(kwargs)

    @staticmethod
    def get_search_objs(search_path):
        return [importlib.import_module(module)
                for module in search_path.split(":")]

    def get_partial_result(self, command_factory):
        @functools.wraps(command_factory)
        def partial_result(*args, **kwargs):
            return CommandResult(command_factory(*args, **kwargs))

        return partial_result

    def __getattr__(self, cmd_name):
        for search_obj in self.search_objs:
            if hasattr(search_obj, cmd_name):
                command_factory = getattr(search_obj, cmd_name)
                return self.get_partial_result(command_factory)
        return self.get_partial_result(ProcessCommand.from_proc_name(cmd_name))
