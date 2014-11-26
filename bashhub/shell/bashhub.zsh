source ~/.bashhub/.config
source ~/.bashhub/lib-bashhub.sh

export BH_HOME_DIRECTORY="$HOME/.bashhub/"
export BH_EXEC_DIRECTORY="$HOME/.bashhub/env/bin"

function bh_preexec() {
  (BH_PREEXEC $1)
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
