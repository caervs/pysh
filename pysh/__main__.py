import os
import subprocess
import sys

from pysh.interface import hook


def main():
    if len(sys.argv) < 2:
        subprocess.Popen(["python3", "-i", hook.__file__]).wait()
    else:
        hook.patch_and_run(*sys.argv[1:])


if __name__ == "__main__":
    main()
