<img src="https://bashhub.com/assets/images/bashhub-logo.png" alt="Bashhub Logo">

Bashhub saves every terminal command entered across all sessions and systems and provides powerful querying across all commands.

[![Build Status](https://github.com/rcaloras/bashhub-client/actions/workflows/main.yml/badge.svg)](https://github.com/rcaloras/bashhub-client/actions/)
[![GitHub version](https://badge.fury.io/gh/rcaloras%2Fbashhub-client.svg)](https://badge.fury.io/gh/rcaloras%2Fbashhub-client)

### Features
- Super command search by using context about how commands are executed.
  - e.g. the directory, session, system, exit status, etc.
- Unlimited detailed terminal history stored in the cloud.
  - [Stored privately and encrypted at rest](https://github.com/rcaloras/bashhub-client/wiki/Security-and-Privacy).
- Support across systems. Access your terminal history from anywhere!
- Support for Bash and Zsh with a sweet cli for everything.

![gif](http://i.imgur.com/02ABZxn.gif)

# Quick Install
```shell
curl -OL https://bashhub.com/setup && $SHELL setup
```
For non default login shells, just specify the shell e.g. (`bash setup`, `zsh setup`, `fish setup`)

Detailed installation instructions can be found at
https://github.com/rcaloras/bashhub-client/wiki/Install

# Usage
Bashhub can be accessed from the command line in a couple ways:

- `bh` for searching
- `bashhub` for everything else

It also provides a key binding of `ctrl + b` for quickly dropping into interactive search.

## Search
You can search through your commands in a lot of different ways. Check `bh --help` for more specifics. By default `bh` will output the most recently used unique commands to standard out. Adding the `-i` argument to any `bh` search will make it **interactive**. There are also several arguments to pass to filter, query, and get more specific about your searches!

## Examples

The last 100 commands you executed anywhere. (100 is default limit without `-n`)
```bash
$ bh
```

The last 20 files I've grep'd.
```bash
$ bh -n 20 "grep"
```
Find that wget command with interactive search to execute it again :P
```bash
$ bh -i "wget github"
```

### Directory-specific Searching

The last commands you executed in this directory.
```bash
$ bh -d
```
The last 10 things you vim'd in this directory
```bash
$ bh -d -n 10 "vim"
```

### System-specific Searching

The last 10 curl commands you produced on this system

```bash
$ bh -sys -n 10 "curl"
```

### How Search Results are Ordered
By default results are sorted by **most recently** used, and are **unique**. This means frequent commands like `git status` or `ls` will only appear once in the position they were most recently invoked.

This can be altered by using the `-dups` command to include duplicates

Your git commands including duplicates.

```bash
$ bh -dups "git"
```

## Interactive Search
One of the most useful features is interactive search which is accessed via `bh -i` or `ctrl + b`. This is similar to reverse search i.e. `ctrl + r`. Interactive search drops you into a small menu where you can select a command to run on the command line.

Enter interactive search for all the rsync commands executed in this directory
```bash
$ bh -i -d
(bashhub-i-search): rsync
```

### Command Details
From interactive search you can also access detailed information on each command by hitting `i` or `space` on any listed command.

![Command Details](http://i.imgur.com/is0gNnB.png)


## Bashhub Status
You can get a summary of your user's stats/status by using the `status` command.
```bash
bashhub status
```
Most of this information is also displayed on the user profile page.

```bash
=== Bashhub Status
http://bashhub.com/u/rccola
Total Commands: 94965
Total Sessions: 16400
Total Systems:  18
===
Session PID 15311 Started 9 days ago
Commands In Session: 3
Commands Today: 47
```

### Search with Fuzzy Finder
An efficient way of searching is using `bashhub` in combination with [`fzf`](https://github.com/junegunn/fzf). Put this in your `.bashrc`.

```bash
function my_alias {
  eval $(bh | fzf)
}
```

This will make the function available globally in your terminal.

## Filtering Commands
You can filter commands from being recorded to Bashhub via a regex set to the environment variable `BH_FILTER`. These commands will be ignored and omittted from Bashhub.
```bash
# Filter out any commands for postgres or ssh
export BH_FILTER="(psql|ssh)"
ssh rcaloras@some-ip-address # will not be saved
```

You can check the configuration of this command via the `bashhub filter` subcommand.
```bash
# Check if a command is filtered by my regex
export BH_FILTER="(-p)"
bashhub filter "mysql -u root -p plain-text-password"
BH_FILTER=(-p)
mysql -u root -p plain-text-password
Is Filtered. Matched ['-p']
```

## Disabling Recording Commands
You can turn on/off recording to Bashhub via `bashhub on` and `bashhub off`. By default this only affects the current bash session.

```bash
$ bashhub off
$ echo "Recording is now disabled for this session. This command won't be saved."
....
$ bashhub on
$ echo "Recording commands is now re-enabled"
```
You can disable for all sessions by setting `bashhub off --global` this sets `save_commands = False` in your bashhub config.

## Ignoring Commands
`#ignore` added to any command will omit it from being saved. Simply add it to the end of any command and it won't be recorded in Bashhub.

```bash
$ echo "this command won't be saved" #ignore
```

## Deleting Commands
You can delete commands from Bashhub through interactive search by pressing `Delete` or `Backspace` while a command is highlighted. A small dialog box will open to confirm the commands deletion. If a command is deleted, it is permanently removed from Bashhub.

![gif](http://i.imgur.com/sHzvEJx.gif)

## Feature Requests, Bugs, and Issues
Feel free to post in:
https://github.com/rcaloras/bashhub-client/issues

You can also get support and follow updates [@Bashhub](https://twitter.com/bashhub) on Twitter.
