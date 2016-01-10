import subprocess
import sys

NOT_PRINTED = "<PYSHCommandResult>\n"


def main():
    pysh_proc = subprocess.Popen(
        ["python3", "-i", "pysh/__init__.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)

    running_line = ""

    while True:
        next_char = pysh_proc.stdout.read(1).decode("utf-8")
        if not next_char:
            exit(pysh_proc.wait())

        if NOT_PRINTED.startswith(running_line + next_char):
            running_line = running_line + next_char
        else:
            sys.stdout.write(running_line)
            sys.stdout.write(next_char)
            sys.stdout.flush()
            running_line = ""

        if running_line == NOT_PRINTED:
            running_line = ""


if __name__ == "__main__":
    while True:
        try:
            main()
        except KeyboardInterrupt as exc:
            print("\n{}".format(type(exc).__name__))
