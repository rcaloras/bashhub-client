#
# bashhub.zsh
# Main file that is sourced onto our path for Zsh.
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

    # check that we're using zsh and that all our
    # dependencies are satisfied.
    if [[ -n $ZSH_VERSION ]] && [[ -f $BH_DEPS_DIRECTORY/lib-bashhub.sh ]]; then

        # Pull in our library.
        source $BH_DEPS_DIRECTORY/lib-bashhub.sh

        # Hook bashhub into preexec and precmd.
        __bh_hook_bashhub

        # Install our tab completion.
        autoload compinit && compinit
        autoload bashcompinit && bashcompinit
        source $BH_DEPS_DIRECTORY/bashhub_completion_handler.sh

        # Turn on Bash style comments. Otherwise zsh tries to execute #some-comment.
        setopt interactivecomments

    fi
}

__bh_hook_bashhub() {

    # Bind ctrl + b to bh -i
    bindkey -s '^b' "bh -i\n"

    # Hook into preexec and precmd functions if they're not already
    # present there.
    if ! contains_element __bh_preexec $preexec_functions; then
        preexec_functions+=(__bh_preexec)
    fi

    if ! contains_element __bh_precmd  $precmd_functions; then
        precmd_functions+=(__bh_zsh_precmd)
        precmd_functions+=(__bh_precmd)
    fi
}

__bh_zsh_precmd() {
    if [[ -e $BH_HOME_DIRECTORY/response.bh ]]; then
        local COMMAND="`head -n 1 $BH_HOME_DIRECTORY/response.bh`"
        rm $BH_HOME_DIRECTORY/response.bh
        print -z $COMMAND
    fi;
}

__bh_setup_bashhub
