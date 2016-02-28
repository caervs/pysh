"""
pysh: a bridge between the python shell and your OS shell

See README for usage of the pysh CLI
"""

import subprocess
import sys

from pysh.interface import hook


def main():
    """
    run pysh command or interactive mode
    """
    if len(sys.argv) < 2:
        subprocess.Popen(["python3", "-i", hook.__file__]).wait()
    else:
        hook.patch_and_run(*sys.argv[1:])


if __name__ == "__main__":
    main()
