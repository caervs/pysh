"""
Pysh implementations of standard posix commands
"""
from pysh.interface.command import FunctionCommand


@FunctionCommand.from_generator
def grep(expression: (str, "The expression to match against"),
         v: (bool, "Whether to match against complement")=False,
         *files: (str, "files to check")):
    """
    grep as a pysh command
    """
    if files:
        # TODO implement
        # yield from filegrep(expression, v, files)
        raise StopIteration
    line = yield None
    while True:
        if line is None:
            break
        # TODO regexp support
        if (expression in line) ^ v:
            line = yield line, True
        else:
            line = yield None


@FunctionCommand.from_generator
def echo(*args: (str, "Strings to write to stdout")):
    """
    echo as a pysh command
    """
    yield " ".join(args)
