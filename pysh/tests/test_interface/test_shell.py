"""
Test interaction with a Shell
"""

import functools
import operator
import os
import unittest

from pysh.interface import shell
from pysh.interface import command
from pysh.examples import posix


class ShellTestCase(unittest.TestCase):
    """
    Abstract base class for a shell test case

    patches example modules to replace command x with similarly named posix_x
    """

    def setUp(self):
        test_dir = os.path.dirname(__file__)
        self.shell = shell.Shell(test_dir, "pysh.examples.posix")
        for cmd in ["grep", "echo"]:
            new_name = "posix_" + cmd
            setattr(posix, new_name, getattr(posix, cmd))
            delattr(posix, cmd)

    def tearDown(self):
        for cmd in ["grep", "echo"]:
            new_name = "posix_" + cmd
            setattr(posix, cmd, getattr(posix, new_name))
            delattr(posix, new_name)


class BasicShellingWorks(ShellTestCase):
    """
    Test basic interaction with the shell
    """

    def test_get_stdout_of_function(self):
        """
        test getting the stdout of a FunctionCommand
        """
        function_cmd = self.shell.posix_echo("Hello", "World!")
        self.assertIsInstance(function_cmd.command, command.FunctionCommand)
        out, _err = function_cmd
        self.assertEqual(out, "Hello World!\n")

    def test_get_stdout_of_subproc(self):
        """
        test getting the stdout of a subprocess
        """
        function_cmd = self.shell.echo("Hello", "World!")
        self.assertIsInstance(function_cmd.command, command.ProcessCommand)
        out, _err = function_cmd
        self.assertEqual(out, "Hello World!\n")


class PipingWorks(ShellTestCase):
    """
    Test that piping works between commands
    """

    def test_function_to_function(self):
        """
        Test piping from a function to a function
        """
        echo, grep = self.shell.posix_echo, self.shell.posix_grep
        out, _err = echo("Hello\nWorld!\n") | grep("Wo")
        self.assertEqual(out, "World!\n")

    def test_function_to_subproc(self):
        """
        Test piping from a function to a subproc
        """
        echo, grep = self.shell.posix_echo, self.shell.grep
        out, _err = echo("Hello\nWorld!\n") | grep("Wo")
        self.assertEqual(out, "World!\n")

    def test_subproc_to_function(self):
        """
        Test piping from a subproc to a function
        """
        echo, grep = self.shell.echo, self.shell.posix_grep
        out, _err = echo("Hello\nWorld!\n") | grep("Wo")
        self.assertEqual(out, "World!\n")

    def test_subproc_to_subproc(self):
        """
        Test piping from a subproc to a subproc
        """
        echo, grep = self.shell.echo, self.shell.grep
        out, _err = echo("Hello\nWorld!\n") | grep("Wo")
        self.assertEqual(out, "World!\n")

    def test_double_pipe(self):
        """
        Test double piping subprocesses
        """
        echo, grep = self.shell.echo, self.shell.grep
        out, _err = echo("Hello\nWorld!\n") | grep("W") | grep("o")
        self.assertEqual(out, "World!\n")

    def test_pipe_chain(self):
        """
        Test chaining pipes of subprocesses
        """
        expressions = ['H', 'e', 'l', 'o']
        out, _err = functools.reduce(operator.or_,
                                     map(self.shell.grep, expressions),
                                     self.shell.cat("example_file.txt"))
        self.assertEqual(out, "Hello\n")
