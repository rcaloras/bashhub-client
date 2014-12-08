#
# bashhub.sh
# Main file that is sourced onto our path for Bash.
#

export BH_HOME_DIRECTORY="$HOME/.bashhub/"
export BH_EXEC_DIRECTORY="$HOME/.bashhub/env/bin"

BH_DEPS_DIRECTORY=${BH_DEPS_DIRECTORY:=$BH_HOME_DIRECTORY/deps}

# Import our dependencies
if [[ -f $BH_DEPS_DIRECTORY/lib-bashhub.sh ]]; then
    source $BH_DEPS_DIRECTORY/lib-bashhub.sh
fi

# Import prexec
if [[ -f $BH_DEPS_DIRECTORY/bash-preexec.sh ]]; then
    source $BH_DEPS_DIRECTORY/bash-preexec.sh
fi

# Alias to bind Ctrl + B
bind '"\C-b":"\C-u\C-kbh -i\n"'

BH_PREEXEC_WRAPPER() {
    BH_PREEXEC "$1" &> ~/.bashhub/log.txt
}

BH_PRECMD() {
    if [[ -e $BH_HOME_DIRECTORY/response.bh ]]; then
        local command=$(head -n 1 $BH_HOME_DIRECTORY/response.bh)
        rm $BH_HOME_DIRECTORY/response.bh
        history -s "$command"
        echo "$command"
        eval "$command"
     fi;
}

# Hook into preexec and precmd functions
preexec_functions+=(BH_PREEXEC_WRAPPER)
precmd_functions+=(BH_PRECMD)
