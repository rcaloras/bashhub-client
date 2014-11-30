#
# bashhub.zsh
# Main file that is sourced onto our path for Zsh.
#

export BH_HOME_DIRECTORY="$HOME/.bashhub/"
export BH_EXEC_DIRECTORY="$HOME/.bashhub/env/bin"

BH_DEPS_DIRECTORY=$BH_HOME_DIRECTORY/deps

# Import our dependencies
if [[ -f $BH_DEPS_DIRECTORY/lib-bashhub.sh ]]; then
    source $BH_DEPS_DIRECTORY/lib-bashhub.sh
fi


function bh_preexec() {
  BH_PREEXEC $1 &> ~/.bashhub/log.txt
}

function bh_precmd() {
    if [[ -e $BH_HOME_DIRECTORY/response.bh ]]; then
        local COMMAND="`head -n 1 $BH_HOME_DIRECTORY/response.bh`"
        rm $BH_HOME_DIRECTORY/response.bh
        print -z $COMMAND
    fi;
}

# Hook into preexec and precmd functions
preexec_functions+=(bh_preexec)
precmd_functions+=(bh_precmd)

bh()
{
    $BH_EXEC_DIRECTORY/bh "$@"
}
