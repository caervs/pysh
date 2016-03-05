"""
Command: an abstraction that wraps subprocs and functions in a similar interface
"""

import functools
import os
import subprocess
import sys
import threading
import tempfile


class Command(object):
    """
    Abstract base class for pysh commands

    Any command should support the interface:
     - Initialize with arguments
     - Call to execute the command
    """
    pass


class FunctionCommand(object):
    """
    A command defined using a python function
    """

    def __init__(self, function, *args):
        self.function = function
        self.arguments = self.canonicalize(args)
        self.exit_code = None
        self.stdin = None

    @staticmethod
    def get_temp_path():
        """
        return a path to a temporary file
        """
        with tempfile.NamedTemporaryFile() as temp:
            return temp.name

    def __call__(self, wait=True, **channels):
        for std_channel in ['stdin', 'stdout', 'stderr']:
            if std_channel not in channels:
                channels[std_channel] = getattr(sys, std_channel)

        self.make_buffers(channels)
        threading.Thread(target=self.execute, args=(channels, )).start()
        for channel_name in sorted(channels):
            channel = channels[channel_name]
            if isinstance(channel, str):
                if channel_name == "stdin":
                    self.stdin = open(channel, 'w')
                else:
                    setattr(self, channel_name, open(channel))
            else:
                setattr(self, channel_name, channel)
        if wait:
            return self.wait()

    def wait(self):
        """
        wait for command to finish running
        """
        while self.exit_code is None:
            continue
        # TODO better return value for non-wait case?
        return self.exit_code

    def make_buffers(self, channels):
        """
        make any FIFOs used for PIPEing in and out of function
        """
        for channel_key, channel_value in channels.items():
            if channel_value != subprocess.PIPE:
                continue
            path = self.get_temp_path()
            os.mkfifo(path)
            channels[channel_key] = path
        # TODO figure out how to unlink FIFOs when done

    def execute(self, channels):
        """
        Run the function and act like a subprocess
        """
        channels = dict(channels)
        for channel_name in sorted(channels.keys()):
            channel = channels[channel_name]
            if isinstance(channel, str):
                if channel_name == "stdin":
                    channels['stdin'] = open(channel)
                else:
                    channels[channel_name] = open(channel, 'w')

        gen = self.function(*self.arguments)
        message = next(gen)
        stdin = channels['stdin']
        while True:
            outline, wantsline, end = self.parse_message(message)
            if outline is not None:
                out_channel, line = outline
                channels.get(out_channel).write(line)
                channels.get(out_channel).write(end)
            try:
                if wantsline:
                    inline = self.decode(stdin.readline())
                    sanitized_inline = inline.replace("\n",
                                                      "") if inline else None
                    message = gen.send(sanitized_inline)
                else:
                    message = next(gen)
            except StopIteration:
                break
        # TODO should set code to 1 if exception happens
        self.exit_code = 0

    @staticmethod
    def decode(str_or_byte):
        """
        decode utf-8 bytes to str objects
        """
        if isinstance(str_or_byte, str):
            return str_or_byte
        return str_or_byte.decode("utf-8")

    @staticmethod
    def parse_message(raw_message):
        """
        parse a message yielded from the command function
        """
        if not isinstance(raw_message, tuple):
            raw_message = (raw_message, )
        message = list(raw_message)
        if message[-1] is None:
            message[-1] = True
        if isinstance(message[-1], str):
            message.append(False)
        if len(message) == 1:
            return None, message[0], "\n"

        if len(message) == 2:
            message.insert(0, "stdout")

        # TODO support for silencing newline
        return message[:2], message[2], "\n"

    @classmethod
    def from_generator(cls, generator):
        """
        Create a FunctionCommand from a generator function
        """

        @functools.wraps(generator)
        @pyshcommand
        def wrapper(*args):
            """
            wrap the generator function to create a FunctionCommand
            from args passed into the generator function
            """
            return cls(generator, *args)

        return wrapper

    @staticmethod
    def canonicalize(args):
        """
        Convert flags and dash-args to booleans and kwargs
        """
        # TODO Convert flags and dash-args to booleans and kwargs
        return args


class ProcessCommand(object):
    """
    A pysh command wrapping a subprocess
    """

    def __init__(self, proc_name, *args):
        self.arguments = [proc_name] + self.canonicalize(args)
        self.subproc = None

    def __call__(self, wait=True, **channels):
        stdchannels = ['stdin', 'stdout', 'stderr']
        unknown_channels = {key for key in channels if key not in stdchannels}
        if unknown_channels:
            raise ValueError("Unknown channels", unknown_channels)
        self.subproc = subprocess.Popen(self.arguments, **channels)
        for channel in stdchannels:
            setattr(self, channel, getattr(self.subproc, channel))
        if wait:
            return self.wait()

    def wait(self):
        """
        wait for the subprocess to finish
        """
        return self.subproc.wait()

    @classmethod
    def from_proc_name(cls, proc_name):
        """
        create a ProcessCommand given a process name
        """
        return functools.partial(cls, proc_name)

    @staticmethod
    def canonicalize(args):
        """
        Convert flags and dash-args to booleans and kwargs
        """
        # TODO Convert flags and dash-args to booleans and kwargs
        return list(args)


def pyshcommand(cmd):
    """
    generator letting pysh know wrapped function is a pysh command
    """

    @functools.wraps(cmd)
    def wrapper(*args, **kwargs):
        """
        run the wrapped function
        """
        return cmd(*args, **kwargs)

    wrapper.is_pysh_command = True
    return wrapper
