"""
requisites for running pysh in interactive mode
"""

import importlib.machinery
import os
import sys
import types

import pysh

from pysh.interface import shell


class OutWrapper(object):
    """
    replaces stdout file handle and suppresses output of CommandCalls
    """

    def __init__(self):
        self.stdout = sys.stdout
        self.delete_next = False

    def write(self, string):
        """
        suppress output of CommandCalls
        """
        if self.delete_next:
            self.delete_next = False
            string = string[1:]
        if string == shell.DELETE_STRING:
            self.delete_next = True
        else:
            self.stdout.write(string)

    def __getattr__(self, attr_name):
        return getattr(self.stdout, attr_name)


class PyshImportHook(object):
    """
    hook to allow for importing of pysh.scopes.* from various .pysh directories

    pysh.scopes.local: from current project's .pysh directory
    pysh.scopes.user: from ~/.pysh/
    pysh.scopes.global: from /etc/.pysh/
    pysh.scopes.standard: from pysh/scopes/standard/
    """

    def find_spec(self, fullname, _path, _target=None):
        """
        Find a module spec for an import path
        """
        if fullname.startswith("pysh.scopes."):
            if fullname.startswith(
                    "pysh.scopes.standard") or fullname.startswith(
                        "pysh.scopes.current"):
                return None
            return importlib.machinery.ModuleSpec(fullname, self)

    def load_module(self, name):
        """
        Load a module spec for an import path
        """
        if self.is_valid_scope(name):
            pyshdir = self.find_pysh_scope(name)
        else:
            raise ValueError("Unknown pysh scope", name)
        parts = name.split(".")
        if len(parts) > 4:
            raise NotImplementedError
        # TODO consider getting from __init__.py
        root_module = self.make_and_cache_module(name, '')
        for submodule in ['commands', 'config']:
            src_path = os.path.join(pyshdir, submodule + '.py')
            if os.path.exists(src_path):
                with open(src_path) as src_file:
                    source = src_file.read()
            else:
                source = ''
                src_path = None
            submodule_name = "{}.{}".format(name, submodule)
            module = self.make_and_cache_module(submodule_name, source,
                                                src_path)
            setattr(root_module, submodule, module)

    @staticmethod
    def make_and_cache_module(name, source, src_path=None):
        """
        Make a module and store it in the system cache
        """
        if src_path is None:
            src_path = name
        module = types.ModuleType(name, source)
        # TODO set full path
        module.__file__ = src_path
        byte_code = compile(source, name, 'exec')
        exec(byte_code, module.__dict__)
        sys.modules[name] = module
        return module

    @staticmethod
    def is_valid_scope(name):
        """
        return True iff name is the name of a valid scope
        """
        return name in [
            "pysh.scopes.current",
            "pysh.scopes.local",
            "pysh.scopes.user",
            "pysh.scopes.global",
            "pysh.scopes.standard",
        ]

    def find_pysh_scope(self, name):
        """
        find the .pysh directory containing the modules for a pysh scope
        """
        directories = {
            'current': os.path.join(
                os.path.dirname(pysh.__file__), 'scopes', 'current'),
            'standard': os.path.join(
                os.path.dirname(pysh.__file__), 'scopes', 'standard'),
            'local': self.find_project_pysh_dir(),
            'user': os.path.expanduser("~/.pysh/"),
            'global': "/etc/.pysh/",
        }
        return directories[name[len("pysh.scopes."):]]

    @staticmethod
    def find_project_pysh_dir():
        """
        Find the pysh dir for the current project

        Searches the current directory for a .pysh subdir then
        traverses up the directory tree looking for .pysh until
        it gets to your home directory or the root directory
        """
        # TODO implement
        return ".pysh"


def import_module(module_name, get=None):
    """
    replacement for import statements -- used in interactive mode
    """
    if get is not None:
        src_module = importlib.import_module(module_name)
        if not isinstance(get, tuple):
            get = get,
        for item in get:
            globals()[item] = getattr(src_module, item)
        return
    parts = module_name.split(".")
    globals()[parts[0]] = __import__(module_name)


def patch_and_run(*command):
    """
    do all patching necessary to run pysh in interactive mode
    """
    sys.stdout = OutWrapper()
    sys.meta_path.insert(0, PyshImportHook())
    chain = shell.FallbackChain(globals()['__builtins__'], shell.Shell())
    globals()['__builtins__'] = chain
    globals()['prt'] = import_module
    if command:
        exit(getattr(chain, command[0])(*command[1:])())


def main():
    """
    start pysh in interactive mode
    """
    patch_and_run()


if __name__ == "__main__":
    main()
