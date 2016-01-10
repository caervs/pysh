from subprocess import Popen


# Ideas for flushing shell in non-interactive mode
# - shell is a context manager
# - call call to slush it
# - shell decorates function

class Shell(object):
    def __init__(self):
        self.wd = "/"
        self.stdin = None
        self.stdout = None
        self.stderr = None

    def __getattr__(self, attr_name):
        return AtomicCommandFactory(self, attr_name)


class AtomicCommandFactory(object):
    # TODO use replicate
    def __init__(self, shell, program_name):
        self.shell = shell
        self.program_name = program_name

    def __call__(self, *args, **kwargs):
        return AtomicCommand(self.shell, self.program_name, *args, **kwargs)

    def __repr__(self):
        return repr(self())


class Command(object):
    pass


class CommandOutput(str):
    def __init__(self, value):
        self.value = value
        self.__dict__ = {}

    def __getattr__(self, attr_name):
        return self.__dict__[attr_name]


class AtomicCommand(Command):
    def __init__(self, shell, program_name, *args, **kwargs):
        self.shell = shell
        self.args = (program_name, ) + args + tuple("--{}={}".format(
            key, value) for key, value in kwargs.items())
        self.status = None

    def __call__(self):
        if self.status is not None:
            return self.status

        proc = Popen(self.args,
                     cwd=self.shell.wd,
                     stdin=self.shell.stdin,
                     stdout=self.shell.stdout,
                     stderr=self.shell.stderr)
        self.status = proc.wait()
        return self.status

    def __repr__(self):
        if self.status is None:
            self()
        return "<PYSHCommandResult>"


class CompositeCommand(Command):
    def __init__(self, subcommands, routing_policy):
        pass

    def __call__(self, *args, **kwargs):
        pass


class HierarchicalObject(object):
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
