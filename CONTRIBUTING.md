# Contributing to Bashhub
Thanks for contributing to Bashhub! This file outlines several best practices when trying to develop and contribute to the repo.

## Pull Requests
Simple changes can be submitted directly as PRs against Master. Major pull requests and new features should be submitted against the current development branch. Checkout a copy of the next version which is postfixed with `-dev`.
The latest development version can be found on https://github.com/rcaloras/bashhub-client/branches.

## Dev Environment Setup
You should be able to develop and execute Bashhub's client locally as well as run its unit tests. This typically involves cloning the repo and setting up a virtualenv to develop with. 
Bashhub uses modern Python packaging via `pyproject.toml` and setuptools.

```bash
# setup and clone our repo locally
mkdir ~/git/ && cd ~/git
git clone git@github.com:rcaloras/bashhub-client.git
cd ~/git/bashhub-client
```
Setup a new Python 3 [venv](https://docs.python.org/3/library/venv.html) (virtual environment). 
```bash
# Setup a venv.
python3 -m venv .venv
# Activate the venv.
source .venv/bin/activate
# Install our project locally to develop, execute, and test against.
pip install -e ".[test]"
```

This should setup the project locally. Output should look something like:
```bash
[rcaloras:~/git/bashhub-client] [bashhub_dev] master ± pip install -e ".[test]"
Obtaining file:///Users/rcaloras/git/bashhub-client
Installing build dependencies ... done
Checking if build backend supports build_editable ... done
Getting requirements to build editable ... done
Preparing editable metadata (pyproject.toml) ... done
Collecting requests>=2.32.5
Collecting jsonpickle>=4.1.1
...
Successfully built bashhub
Successfully installed bashhub click-8.1.8 humanize-4.13.0 inflection-0.5.1 jsonpickle-4.1.1 npyscreen-5.0.2 pytest-8.x python-dateutil-2.9.0.post0 requests-2.32.5
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
platform darwin -- Python 3.10.12, pytest-7.4.2, pluggy-1.3.0
rootdir: /Users/rcaloras/git/bashhub-client, inifile:
collected 10 items

tests/test_bashhub.py ..                                                                                                                                                                             [ 20%]
tests/test_bashhub_globals.py ..                                                                                                                                                                     [ 40%]
tests/test_command.py ...                                                                                                                                                                            [ 70%]
tests/test_command_form.py ..                                                                                                                                                                        [ 90%]
tests/test_shell_utils.py .

```
