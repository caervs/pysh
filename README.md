# pysh: a bridge between python and your OS shell

**Table of Contents**
* [Getting Started](#getting-started)
  * [Installation](#installation)
  * [Interactive Mode](#interactive-mode)
  * [Non-interactive Mode](#non-interactive-mode)
* [Contributing](#contributing)
  * [Running tests](#running-tests)

## Getting Started

Pysh is a tool for interacting with your machine that has the expressive power of a python shell and the versatility of an OS shell. Pysh provides an extensible single point of entry for doing all of the common tasks associated with your projects like building, testing, and deploying your code and collecting documentation.

### Installation

If you have pip3 installation is easy. Just run

```bash
pip3 install -e git+https://github.com/caervs/pysh.git#egg=pysh
```

### Interactive mode

Running pysh in interactive mode lets you call your everyday shell procedures as if they were python functions. To try out interactive mode just run `pysh` with no arguments.

```python3
bash-3.2$ pysh
>>> echo("Hello World!")
Hello World!
>>> 
```

That's all there is. The pysh interpreter is just a standard python3 interpreter with a little monkey patching so anything you can do in python you can do in pysh. Piping is done with python syntax but has a look similar to that of bash.

```python3
>>> echo("Hello\nWorld") | grep("H")
Hello
>>> 
```

pretty cool, right? You might be thinking, "this is a fun academic exercise but what's the point?"

Imagine having the expressability of python with the vocabulary of bash. You can elegantly combine subprocesses in ways that were too cumbersome before. For example, let's write the file **example.txt**

```python3
>>> cat > "example.txt"
1
2
3
4
H
e
l
l
o
H
He
Hel
Hell
Hello
>>> 
```

and then filter the file through a chain of regular expressions. In bash you might have to create some super complex expression that's the combination of all of the expressions you want to test. If you can't do that you'll settle for manually creating a string of greps, one for each expression. With the power of python however pysh makes this easy, just run

```python3
>>> prt("functools")
>>> prt("operator")
>>> 
>>> expressions = ['H', 'e', 'l', 'o']
>>> functools.reduce(operator.or_,
...                  map(grep, expressions),
...                  cat("example.txt"))
Hello
>>> 
```

Notice what we've done here. First we import `functools` and `operator` -- pysh monkey patch has a bug preventing the use of `import` (more on this later). Next we define our list of expressions which can be of arbitrary length. Finally we use some simple functional programming to chain together a cat and 4 grep processes to filter out `Hello` from the above file. Great.

Getting the output instead of printing it is easy too. Just do some assignment unpacking...


```
>>> out, err = cat("example.txt") | grep("o")
>>> print(out)
o
Hello

>>> 
```

### Non-interactive mode

Pysh lets you easily define functions and subprocess calls that are then reachable from the command line. This is especially useful if you have project-specific commands that you want to distribute with your source tree but don't want to clutter your project with individual scripts.

To get started just run this in your project directory

```bash
bash-3.2$ pysh init
Making .pysh directory
Done
bash-3.2$ 
```

This will create a **.pysh** directory with a **commands.py** module for your local commands and a **config.py** module for your local config. Now you can start adding local commands using

```bash
bash-3.2$ EDITOR=<your editor of choice (e.g. emacs)> pysh edit
```

The `pysh.examples` subpackage is full of example functions you can import (including some crude reimplementations of posix commands). To add nose testing with yapf and pylint to your project modify the **commands.py** module to include

```python
from pysh.examples.development import test
```

Save and exit. Now you can see the commands available to you with

```
bash-3.2$ pysh cmds

Local Commands
==========================
test:     Run nose tests with coverage, yapf, and pylint

Standard Commands
=============================
cmds:     List existing pysh commands
edit:     Edit a pysh command or module
init:     Initialize this source-tree for project-specific pysh commands
bash-3.2$ 
```

and run your tests

```
bash-3.2$ pysh test
...........
Name                           Stmts   Miss  Cover   Missing
------------------------------------------------------------
pysh.py                            0      0   100%   
pysh/examples.py                   0      0   100%   
pysh/examples/development.py      48     18    62%   38, 52-54, 63-75, 84, 92, 100
pysh/examples/posix.py            15      1    93%   17
pysh/interface.py                  0      0   100%   
pysh/interface/command.py        118      3    97%   54, 92, 187
pysh/interface/shell.py          109     20    82%   40, 50-51, 82-83, 134, 138-140, 153, 162, 168, 195,
 198-201, 204, 207, 210                                                                                
pysh/scopes.py                     0      0   100%   
pysh/scopes/local.py               0      0   100%   
------------------------------------------------------------
TOTAL                            290     42    86%   
----------------------------------------------------------------------
Ran 11 tests in 5.029s

OK
bash-3.2$ 
```

and of course all of this functionality is available from within pysh

```
bash-3.2$ pysh
>>> cmds

Local Commands
==========================
test:     Run nose tests with coverage, yapf, and pylint

Standard Commands
=============================
cmds:     List existing pysh commands
edit:     Edit a pysh command or module
init:     Initialize this source-tree for project-specific pysh commands
>>> 
```


## Contributing

PRs and general suggestions are welcome. This project is still a preliminary proof of concept but I hope that it will someday be a usable robust shell. Please ensure that you pass the automated test suite before submitting a request.

### Running tests

Pysh can, not surprisingly, run the pysh test suite on itself. To run the unit tests simply run

```
pysh test
```

you may also run it with the `-u` option to temporarily disable slow quality tests. The quality tests include pylint checks (the results of which are stored in `lint.html`) and a yapf formatting test (the diff of which is stored in yapf.txt if you don't pass).


