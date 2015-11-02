<img src="https://bashhub.com/assets/images/bashhub-logo.png" alt="Bashhub Logo">
==========
Bashhub saves every terminal command entered across all sessions and systems and provides powerful querying across all commands.

[![Build Status](https://travis-ci.org/rcaloras/bashhub-client.svg)](https://travis-ci.org/rcaloras/bashhub-client)

###Bashhub provides
- Super command search by using context about how commands are executed. 
  - e.g. the directory, session, system, exit status, etc.
- Unlimited detailed terminal history stored in the cloud.
- Support across systems. Access your terminal history from anywhere!
- Support for Bash and Zsh with a sweet cli for everything. 

![gif](http://i.imgur.com/02ABZxn.gif)

##Quick Install
```bash
curl -OL https://bashhub.com/setup && bash setup
```
For Zsh
```zsh
curl -OL https://bashhub.com/setup && zsh setup
```

Detailed install at https://github.com/rcaloras/bashhub-client/wiki/Install

#Usage
Bashhub can be accessed from the command line in a couple ways:

- `bh` for searching
- `bashhub` for everything else

It also provides a key binding of `ctrl + b` for quickly dropping into interactive search.
##Search
You can search through your commands in a lot of different ways. Check `bh --help` for more specifics. By default `bh` will output the most recently used unique commands to standard out. Adding the `-i` argument to any `bh` search will make it **interactive**. There are also several arguments to pass to filter, query, and get more specific about your searches!


##Examples

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
###Directory based searching

The last commands you executed in this directory.
```bash
$ bh -d
```
The last 10 things you vim'd in this directory
```bash
$ bh -d -n 10 "vim"
```

###System based searching

The last 10 curl commands you produced on this system

```bash
$ bh -sys -n 10 "curl"
```

###How search results are ordered
By default results are sorted by **most recently** used, and are **unique**. This means frequent commands like `git status` or `ls` will only appear once in the position they were most recently invoked.

This can be altered by using the `-dups` command to include duplicates

Your git commands including duplicates.

```bash
$ bh -dups "git"
```

##Interactive Search
One of the most useful features is interactive search which is accessed via `bh -i` or `ctrl + b`. This is similar to reverse search i.e. `ctrl + r`. Interactive search drops you into a small menu where you can select a command to run on the command line.

Enter interactive search for all the rsync commands executed in this directory
```bash
$ bh -i -d
(bashhub-i-search): rsync
```

### Command Details
From interactive search you can also access detailed information on each command by hitting `i` or `space` on any listed command.

![Command Details](http://i.imgur.com/is0gNnB.png)


##Bashhub Status
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




##Ignoring Commands
`#ignore` added to any command will omit it from being saved. Simply add it to the end of any command and it won't be recorded in Bashhub.

```bash
$ echo "this command won't be saved" #ignore
```

## Feature Requests, Bugs, and Issues
Feel free to post in:
https://github.com/rcaloras/bashhub-client/issues

You can also check out and add to our Trello board:
https://trello.com/b/m6VZdrnQ/bashhub
