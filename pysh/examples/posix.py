"""
Pysh implementations of standard posix commands
"""
from pysh.interface.command import FunctionCommand


@FunctionCommand.from_generator
def grep(expression: (str, "The expression to match against"),
         v: (bool, "Whether to match against complement")=False,
         *files: (str, "files to check")):
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
            line = yield line
        else:
            line = yield None


@FunctionCommand.from_generator
def echo(*args: (str, "Strings to write to stdout")):
    yield " ".join(args), False
