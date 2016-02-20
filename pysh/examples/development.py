from pysh.interface.shell import Shell

SH = Shell(search_path='')


def test():
    """
    Run nose tests with coverage, yapf, and pylint
    """
    return SH.nosetests()


def build():
    """
    build any docker images associated with this project
    """
    pass


def setup():
    """
    Create a virtual environment and install necessary packages
    """
    pass


def enter():
    """
    Enter the virtual environment for the project
    """
    pass

