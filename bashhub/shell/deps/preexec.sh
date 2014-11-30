#!/bin/bash

# preexec.bash -- Bash support for ZSH-like 'preexec' and 'precmd' functions.

# The 'preexec' function is executed before each interactive command is
# executed, with the interactive command as its argument.  The 'precmd'
# function is executed before each prompt is displayed.

# To use, in order:

#  1. source this file
#  2. define 'preexec' and/or 'precmd' functions (AFTER sourcing this file),
#  3. as near as possible to the end of your shell setup, run 'preexec_install'
#     to kick everything off.

# Note: this module requires 2 bash features which you must not otherwise be
# using: the "DEBUG" trap, and the "PROMPT_COMMAND" variable.  preexec_install
# will override these and if you override one or the other this _will_ break.

# This variable describes whether we are currently in "interactive mode";
# i.e. whether this shell has just executed a prompt and is waiting for user
# input.  It documents whether the current command invoked by the trace hook is
# run interactively by the user; it's set immediately after the prompt hook,
# and unset as soon as the trace hook is run.
preexec_interactive_mode=""

# Default do-nothing implementation of preexec.
preexec() {
    :
}

# Default do-nothing implementation of precmd.
precmd() {
    :
}

# This function is installed as the PROMPT_COMMAND; it is invoked before each
# interactive prompt display.  It sets a variable to indicate that the prompt
# was just displayed, to allow the DEBUG trap, below, to know that the next
# command is likely interactive.
preexec_invoke_cmd() {
    last_hist_ent="$(history 1)";
    precmd;
    preexec_interactive_mode="on";
}

# This function is installed as the DEBUG trap.  It is invoked before each
# interactive prompt display.  Its purpose is to inspect the current
# environment to attempt to detect if the current command is being invoked
# interactively, and invoke 'preexec' if so.
preexec_invoke_exec() {
    if [[ -n "$COMP_LINE" ]]
    then
        # We're in the middle of a completer.  This obviously can't be
        # an interactively issued command.
        return
    fi
    if [[ -z "$preexec_interactive_mode" ]]
    then
        # We're doing something related to displaying the prompt.  Let the
        # prompt set the title instead of me.
        return
    else
        # If we're in a subshell, then the prompt won't be re-displayed to put
        # us back into interactive mode, so let's not set the variable back.
        # In other words, if you have a subshell like
        #   (sleep 1; sleep 2)
        # You want to see the 'sleep 2' as a set_command_title as well.
        if [[ 0 -eq "$BASH_SUBSHELL" ]]
        then
            preexec_interactive_mode=""
        fi
    fi

    if [[ "preexec_invoke_cmd" == "$BASH_COMMAND" ]]
    then
        # Sadly, there's no cleaner way to detect two prompts being displayed
        # one after another.  This makes it important that PROMPT_COMMAND
        # remain set _exactly_ as below in preexec_install.  Let's switch back
        # out of interactive mode and not trace any of the commands run in
        # precmd.

        # Given their buggy interaction between BASH_COMMAND and debug traps,
        # versions of bash prior to 3.1 can't detect this at all.
        preexec_interactive_mode=""
        return
    fi

    local hist_ent="$(history 1)";
    local this_command="$(echo "$hist_ent" | sed -e "s/^[ ]*[0-9]*[ ]*//g")";

    # If none of the previous checks have returned out of this function, then
    # the command is in fact interactive and we should invoke the user's
    # preexec hook with the running command as an argument.
    if [ -n "$this_command" ]; then
        preexec "$this_command";
    fi
}

# Execute this to set up preexec and precmd execution.
preexec_install() {

    # Finally, install the actual traps.
    PROMPT_COMMAND="${PROMPT_COMMAND} preexec_invoke_cmd";
    trap 'preexec_invoke_exec' DEBUG;
}
