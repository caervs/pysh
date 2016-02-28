import io
import unittest

from pysh.examples import posix


class PosixTestCase(unittest.TestCase):
    pass


class GrepWorks(PosixTestCase):
    def test_matched_output(self):
        stdin = io.StringIO("Hello\nWorld!")
        stdout = io.StringIO()
        posix.grep("Wo")(stdin=stdin, stdout=stdout)
        assert stdout.getvalue() == "World!\n"
