# Contributing to Bashhub
Thanks for contributing to Bashhub! This file outlines several best practices when trying to develop and contribute to the repo.

## Pull Requests
Simple changes can be submitted directly as PRs against Master. Major pull requests and new features should be submitted against the current development branch. Checkout a copy of the next version which is postfixed with `-dev`.
The latest development version can be found on https://github.com/rcaloras/bashhub-client/branches.

## Dev Environment Setup
You should be able to develop and execute Bashhub's client locally as well as run its unit tests. This typically involves cloning the repo and setting up a virtualenv to develop with. 
Bashhub is currently setup as Python 2 project built with setuptools.

```bash
# setup and clone our repo locally
mkdir ~/git/ && cd ~/git
git clone git@github.com:rcaloras/bashhub-client.git
cd ~/git/bashhub-client
```
Setup a new Python 2 virtualenv to install the project locally to and develop from. This example is with [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/index.html#introduction).
The project should be converted to Python 3 as part of [Issue #56](https://github.com/rcaloras/bashhub-client/issues/56). 
```bash
# setup a virtualenv specifying python 2
mkvirtualenv -p python2.7 bashhub_dev
# Install our project locally to develop, execute, and test against.
pip install -e ".[test]"
```

This should setup the project locally. Output should look something like:
```bash
[rcaloras:~/git/bashhub-client] [bashhub_dev] master ± pip install -e ".[test]"
Obtaining file:///Users/rcaloras/git/bashhub-client
Collecting requests==1.2.3 (from bashhub===-version-)
  Using cached requests-1.2.3.tar.gz
Collecting jsonpickle==0.7.0 (from bashhub===-version-)
  Using cached jsonpickle-0.7.0.tar.gz
...
Successfully built requests jsonpickle npyscreen pyCLI pymongo inflection humanize
Installing collected packages: requests, jsonpickle, click, npyscreen, six, python-dateutil, pyCLI, pymongo, inflection, humanize, bashhub
  Running setup.py develop for bashhub
Successfully installed bashhub click-3.3 humanize-0.5.1 inflection-0.2.1 jsonpickle-0.7.0 npyscreen-4.9.1 pyCLI-2.0.3 pymongo-2.6 python-dateutil-2.4.0 requests-1.2.3 six-1.11.0
```
From within this virtualenv `bh` and `bashhub` exectuables should now be wired up for development. You should also be able to run pytest (you may have to start a new terminal session).

```bash
# bashhub and bh exectuables point to our current dev env
[rcaloras:~/git/bashhub-client] [bashhub_dev] master ± which bashhub
/Users/rcaloras/Envs/bashhub_dev/bin/bashhub
[rcaloras:~/git/bashhub-client] [bashhub_dev] master ± which bh
/Users/rcaloras/Envs/bashhub_dev/bin/bh

# pytest should run locally against our repo
[rcaloras:~/git/bashhub-client] [bashhub_dev] master ± pytest
============= test session starts =================
platform darwin -- Python 2.7.10, pytest-3.3.1, py-1.5.2, pluggy-0.6.0
rootdir: /Users/rcaloras/git/bashhub-client, inifile:
collected 10 items

tests/test_bashhub.py ..                                                                                                                                                                             [ 20%]
tests/test_bashhub_globals.py ..                                                                                                                                                                     [ 40%]
tests/test_command.py ...                                                                                                                                                                            [ 70%]
tests/test_command_form.py ..                                                                                                                                                                        [ 90%]
tests/test_shell_utils.py .

```








