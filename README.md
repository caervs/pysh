# pysh: a bridge between the python shell and your OS shell

Pysh is a tool for interacting with your machine that has the expressive power of a python shell and the versatility of an OS shell. Additionally it provides an extensible single point of entry for doing all of the common tasks associated with your projects like building, testing, and deploying your code and collecting documentation.


## Getting Started

### Installation

If you have pip3 installation is easy. Just run

```bash
pip3 install -e git+https://github.com/caervs/pysh.git#egg=pysh
```

## Interactive mode

Running pysh in interactive mode lets you call your everyday shell procedures as if they were python functions. To try out interactive mode just run `pysh` with no arguments.

```python3
>>> echo("Hello World!")
Hello World!
>>> 
```

that's all there is. The pysh interpreter is just a standard python3 interpreter with a little monkey patching so anything you can do in python you can do in pysh. Piping is done with python syntax but has a look similar to if you were running bash.

```python3
>>> echo("Hello\nWorld") | grep("H")
Hello
>>> 
```

pretty cool, right? You might be thinking, "this is a fun academic exercise but what's the point?" Imagine having the expressability of python with the vocabulary of bash. You can elegantly combine subprocesses in ways that were too cumbersome before. For example, imagine you want to pipe the following file through a chain of greps:

```python3
>>> out, _err = tee("example.txt")
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

in bash you might have to create some super complex expression that's the combination of all of the expressions you want to test. If you can't do that you'll setting for manually creating a string of greps, one for each expression. With the power of python however pysh makes this easy, just run

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

## Adding pysh to your project

is as easy as running "pysh init"

add new procedures with "pysh edit <module>"

call procedures with "pysh {module.function, function, re-router} arg0 arg1... argn --kvarg0=val0..."


## The pysh standard command set

Should include:
- building
- building with Docker
- creating virtual envs
- testing (with nose maybe)
- doc collection
- quality testing (yapf and lint)
- versioning


TODO extensibility --

your global pysh config should consist of additional packages that will be referenced in any project you initialize.

Top level commands:

- init: create the .pysh directory
- config: modify local or global pysh configuration (change settings, add packages, etc)
- edit: edit a local pysh module

## Why would you do this?

All the power of your OS and the expressability of python -- 

example -- doing a grep chain

expressions = [...]

out, err = reduce(operator.or_, map(shell.grep, expressions),
                  shell.cat('file.txt'))

