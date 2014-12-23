#
# bashhub.sh
# Main file that is sourced onto our path for Bash.
#

export BH_HOME_DIRECTORY="$HOME/.bashhub/"
export BH_EXEC_DIRECTORY="$HOME/.bashhub/env/bin"

BH_DEPS_DIRECTORY=${BH_DEPS_DIRECTORY:=$BH_HOME_DIRECTORY/deps}

__bh_setup_bashhub() {

    # check that we're using bash and that all our
    # dependencies are satisfied.
    if [[ -n $BASH_VERSION ]] && \
       [[ -f $BH_DEPS_DIRECTORY/lib-bashhub.sh ]] && \
       [[ -f $BH_DEPS_DIRECTORY/bash-preexec.sh ]]; then

        # Pull in our library.
        source $BH_DEPS_DIRECTORY/lib-bashhub.sh

        # Check to make sure preexec isn't already installed.
        if [[ -z $(type -t preexec_and_precmd_install) ]]; then
            source $BH_DEPS_DIRECTORY/bash-preexec.sh
            preexec_and_precmd_install
        fi

        # Hook bashhub into preexec and precmd.
        __bh_hook_bashhub
    fi
}

__bh_hook_bashhub() {

    # Alias to bind Ctrl + B
    bind '"\C-b":"\C-u\C-kbh -i\n"'

    # Hook into preexec and precmd functions
    if ! contains_element BH_PREEXEC $preexec_functions; then
        preexec_functions+=(BH_PREEXEC)
    fi

    if ! contains_element BH_PRECMD $precmd_functions; then
        precmd_functions+=(__bh_precmd)
    fi
}

__bh_precmd() {
    if [[ -e $BH_HOME_DIRECTORY/response.bh ]]; then
        local command=$(head -n 1 $BH_HOME_DIRECTORY/response.bh)
        rm $BH_HOME_DIRECTORY/response.bh
        history -s "$command"
        echo "$command"
        eval "$command"
     fi;
}

__bh_setup_bashhub
