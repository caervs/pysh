import importlib.machinery
import os
import subprocess
import sys
import types

from pysh.interface import shell


class OutWrapper(object):
    def __init__(self):
        self.stdout = sys.stdout
        self.delete_next = False

    def write(self, s):
        if self.delete_next:
            self.delete_next = False
            s = s[1:]
        if s == shell.DELETE_STRING:
            self.delete_next = True
        else:
            self.stdout.write(s)

    def __getattr__(self, attr_name):
        return getattr(self.stdout, attr_name)


class PyshImportHook(object):
    def find_spec(self, fullname, path, target=None):
        if fullname.startswith("pysh.scopes."):
            if fullname.startswith(
                    "pysh.scopes.standard") or fullname.startswith(
                        "pysh.scopes.current"):
                return None
            return importlib.machinery.ModuleSpec(fullname, self)

    def load_module(self, name):
        if name.startswith("pysh.scopes.local"):
            pyshdir = self.find_project_pysh_dir()
        else:
            raise NotImplementedError
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

    def make_and_cache_module(self, name, source, src_path=None):
        if src_path is None:
            src_path = name
        module = types.ModuleType(name, source)
        # TODO set full path
        module.__file__ = src_path
        byte_code = compile(source, name, 'exec')
        exec(byte_code, module.__dict__)
        sys.modules[name] = module
        return module

    def find_project_pysh_dir(self):
        # TODO implement
        return ".pysh"


def import_module(module_name, get=None):
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
    sys.stdout = OutWrapper()
    sys.meta_path.insert(0, PyshImportHook())
    chain = shell.FallbackChain(
        globals()['__builtins__'],
        shell.Shell(search_path='pysh.scopes.local.commands'))
    globals()['__builtins__'] = chain
    globals()['prt'] = import_module
    if command:
        exit(getattr(chain, command[0])(*command[1:])())


def main():
    import sys
    if len(sys.argv) < 2:
        patch_and_run()
    elif sys.argv[1] == '-i':
        path_to_pysh = os.path.abspath(__file__)
        subprocess.Popen(["python3", "-i", path_to_pysh]).wait()
    else:
        patch_and_run(*sys.argv[1:])


if __name__ == "__main__":
    main()
