# pysh
Pysh: the python shell


Pysh is a tool for interacting with your machine that has the expressive power of a python shell and the versatility of an OS shell. Additionally it provides an extensible single point of entry for doing all of the common tasks associated with your projects like building, testing, and deploying your code and collecting documentation.


## Installing


## Using interactive mode

Running pysh in interactive mode lets you call your everyday shell procedures as if they were python functions

TODO insert examples of running with no arguments, running with arguments, piping, funneling, etc.


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

