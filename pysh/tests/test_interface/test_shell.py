import functools
import io
import operator
import os
import unittest

from pysh.interface import shell
from pysh.interface import command
from pysh.examples import posix


class ShellTestCase(unittest.TestCase):
    def setUp(self):
        test_dir = os.path.dirname(__file__)
        self.shell = shell.Shell(test_dir, "pysh.examples.posix")
        for command in ["grep", "echo"]:
            new_name = "posix_" + command
            setattr(posix, new_name, getattr(posix, command))
            delattr(posix, command)

    def tearDown(self):
        for command in ["grep", "echo"]:
            new_name = "posix_" + command
            setattr(posix, command, getattr(posix, new_name))
            delattr(posix, new_name)


class BasicShellingWorks(ShellTestCase):
    def test_get_stdout_of_function(self):
        function_cmd = self.shell.posix_echo("Hello", "World!")
        self.assertIsInstance(function_cmd.command, command.FunctionCommand)
        out, _err = function_cmd
        self.assertEqual(out, "Hello World!\n")

    def test_get_stdout_of_subproc(self):
        function_cmd = self.shell.echo("Hello", "World!")
        self.assertIsInstance(function_cmd.command, command.ProcessCommand)
        out, _err = function_cmd
        self.assertEqual(out, "Hello World!\n")


class PipingWorks(ShellTestCase):
    def test_function_to_function(self):
        echo, grep = self.shell.posix_echo, self.shell.posix_grep
        out, _err = echo("Hello\nWorld!\n") | grep("Wo")
        self.assertEqual(out, "World!\n")

    def test_function_to_subproc(self):
        echo, grep = self.shell.posix_echo, self.shell.grep
        out, _err = echo("Hello\nWorld!\n") | grep("Wo")
        self.assertEqual(out, "World!\n")

    def test_subproc_to_function(self):
        echo, grep = self.shell.echo, self.shell.posix_grep
        out, _err = echo("Hello\nWorld!\n") | grep("Wo")
        self.assertEqual(out, "World!\n")

    def test_subproc_to_subproc(self):
        echo, grep = self.shell.echo, self.shell.grep
        out, _err = echo("Hello\nWorld!\n") | grep("Wo")
        self.assertEqual(out, "World!\n")

    def test_double_pipe(self):
        echo, grep = self.shell.echo, self.shell.grep
        out, _err = echo("Hello\nWorld!\n") | grep("W") | grep("o")
        self.assertEqual(out, "World!\n")

    def test_pipe_chain(self):
        expressions = ['H', 'e', 'l', 'o']
        out, _err = functools.reduce(operator.or_,
                                     map(self.shell.grep, expressions),
                                     self.shell.cat("example_file.txt"))
        self.assertEqual(out, "Hello\n")
