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
    def __call__(self):
        pass

    def __or__(self, other):
        routing_policy = {
            0: {
                'stdin': (-1, 'stdout'),
            },
            1: {
                'stdin': (0, 'stdout'),
            },
        }
        return CompositeCommand([self, other], routing_policy)

    def __repr__(self):
        if self.status is None:
            self()
        return ""
        #return "<PYSHCommand>"


class AtomicCommand(Command):
    def __init__(self, shell, program_name, *args, **kwargs):
        self.shell = shell
        self.args = (program_name, ) + args + tuple("--{}={}".format(
            key, value) for key, value in kwargs.items())
        self.status = None

    def __call__(self, stdin=None, stdout=None, stderr=None):
        if self.status is not None:
            return self.status

        stdin = self.shell.stdin if stdin is None else stdin
        stdout = self.shell.stdout if stdout is None else stdout
        stderr = self.shell.stderr if stderr is None else stderr

        proc = Popen(self.args,
                     cwd=self.shell.wd,
                     stdin=stdin,
                     stdout=stdout,
                     stderr=stderr)
        self.status = proc.wait()
        return self.status



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
