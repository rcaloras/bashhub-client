#
# bashhub.zsh
# Main file that is sourced onto our path for Zsh.
#

export BH_HOME_DIRECTORY="$HOME/.bashhub/"
export BH_EXEC_DIRECTORY="$HOME/.bashhub/env/bin"

BH_DEPS_DIRECTORY=${BH_DEPS_DIRECTORY:=$BH_HOME_DIRECTORY/deps}

# Import our dependencies
if [[ -f $BH_DEPS_DIRECTORY/lib-bashhub.sh ]]; then
    source $BH_DEPS_DIRECTORY/lib-bashhub.sh
fi

function bh_precmd() {
    if [[ -e $BH_HOME_DIRECTORY/response.bh ]]; then
        local COMMAND="`head -n 1 $BH_HOME_DIRECTORY/response.bh`"
        rm $BH_HOME_DIRECTORY/response.bh
        print -z $COMMAND
    fi;
}

# Hook into preexec and precmd functions if they're not already
# present there.
if ! contains_element BH_PREEXEC $preexec_functions; then
    preexec_functions+=(BH_PREEXEC)
fi

if ! contains_element bh_precmd $precmd_functions; then
    precmd_functions+=(bh_precmd)
fi
