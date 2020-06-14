#
# bashhub.sh
# Main file that is sourced onto our path for Bash.
#

# Avoid duplicate inclusion
if [[ "$__bh_imported" == "defined" ]]; then
    __bh_path_add "$HOME/.bashhub/bin"
    return 0
fi

__bh_imported="defined"

export BH_HOME_DIRECTORY="$HOME/.bashhub/"

BH_DEPS_DIRECTORY=${BH_DEPS_DIRECTORY:=$BH_HOME_DIRECTORY/deps}

__bh_setup_bashhub() {

    # check that we're using bash and that all our
    # dependencies are satisfied.
    if [[ -n $BASH_VERSION ]] && \
       [[ -f $BH_DEPS_DIRECTORY/lib-bashhub.sh ]] && \
       [[ -f $BH_DEPS_DIRECTORY/bash-preexec.sh ]]; then

        # Pull in our libs
        source "$BH_DEPS_DIRECTORY/lib-bashhub.sh"
        source "$BH_DEPS_DIRECTORY/bash-preexec.sh"

        # Hook bashhub into preexec and precmd.
        __bh_hook_bashhub

        # Install our tab completion
        source "$BH_DEPS_DIRECTORY/bashhub_completion_handler.sh"
    fi
}

__bh_hook_bashhub() {

    if [ -t 1 ]; then
        # Alias to bind Ctrl + B
        bind '"\C-b":"\C-ubh -i\n"'
    fi

    # Hook into preexec and precmd functions
    if ! contains_element __bh_preexec "${preexec_functions[@]}"; then
        preexec_functions+=(__bh_preexec)
    fi

    if ! contains_element __bh_precmd "${precmd_functions[@]}"; then
        # Order seems to matter here due to the fork at the end of __bh_precmd
        precmd_functions+=(__bh_bash_precmd)
        precmd_functions+=(__bh_precmd)
    fi
}

__bh_bash_precmd() {
    if [[ -e $BH_HOME_DIRECTORY/response.bh ]]; then
        local command=$(head -n 1 "$BH_HOME_DIRECTORY/response.bh")
        rm "$BH_HOME_DIRECTORY/response.bh"
        history -s "$command"
        # Save that we're executing this command again by calling bashhub's
        # preexec and precmd functions
        __bh_preexec "$command"
        echo "$command"
        eval "$command"
        __bh_precmd
     fi;
}

__bh_setup_bashhub
