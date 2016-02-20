import sys

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


def main():
    sys.stdout = OutWrapper()
    builtins = globals()['__builtins__']
    globals()['__builtins__'] = shell.FallbackChain(
        builtins, shell.Shell(search_path=''))
    globals()['__builtins__'].__import__ = builtins.__import__


if __name__ == "__main__":
    main()
