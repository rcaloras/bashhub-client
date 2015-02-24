#
# bashhub.zsh
# Main file that is sourced onto our path for Zsh.
#

# Avoid duplicate inclusion
if [[ "$__bh_imported" == "defined" ]]; then
    return 0
fi
__bh_imported="defined"


export BH_HOME_DIRECTORY="$HOME/.bashhub/"
export BH_EXEC_DIRECTORY="$HOME/.bashhub/env/bin"

BH_DEPS_DIRECTORY=${BH_DEPS_DIRECTORY:=$BH_HOME_DIRECTORY/deps}

__bh_setup_bashhub() {

    # check that we're using zsh and that all our
    # dependencies are satisfied.
    if [[ -n $ZSH_VERSION ]] && [[ -f $BH_DEPS_DIRECTORY/lib-bashhub.sh ]]; then

        # Pull in our library.
        source $BH_DEPS_DIRECTORY/lib-bashhub.sh

        # Hook bashhub into preexec and precmd.
        __bh_hook_bashhub
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
        precmd_functions+=(__bh_precmd)
        precmd_functions+=(__bh_zsh_precmd)
    fi
}

function __bh_zsh_precmd() {
    if [[ -e $BH_HOME_DIRECTORY/response.bh ]]; then
        local COMMAND="`head -n 1 $BH_HOME_DIRECTORY/response.bh`"
        rm $BH_HOME_DIRECTORY/response.bh
        print -z $COMMAND
    fi;
}

__bh_setup_bashhub
