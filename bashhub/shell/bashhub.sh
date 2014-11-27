source ~/.bashhub/.config
source ~/.bashhub/lib-bashhub.sh

export BH_HOME_DIRECTORY="$HOME/.bashhub/"
export BH_EXEC_DIRECTORY="$HOME/.bashhub/env/bin"

# Alias to bind Ctrl + B
bind '"\C-b":"\C-u\C-kbh -i\n"'
BH_GET_LAST_COMMAND() {
    # GRAB LAST OF COMMAND
    local HISTORY_LINE=$(history 1)
    local TRIMMED_COMMAND=`BH_TRIM_WHITESPACE $HISTORY_LINE`
    local NO_LINE_NUMBER=`echo "$TRIMMED_COMMAND" | cut -d " " -f2-`
    BH_TRIM_WHITESPACE $NO_LINE_NUMBER
}

BH_ON_PROMPT_COMMAND() {

    BH_PREV_COMMAND="$BH_COMMAND"
    BH_COMMAND=$(BH_GET_LAST_COMMAND)

    # Check to make sure we have a new command
    if [[ "$BH_COMMAND" = "$BH_PREV_COMMAND" ]]; then
        return 0
    fi;

    BH_PREEXEC "$BH_COMMAND"
}

# Hook into Bash's PROMPT_COMMAND.
PROMPT_COMMAND="BH_ON_PROMPT_COMMAND; $PROMPT_COMMAND"

bh()
{
    $BH_EXEC_DIRECTORY/bh "$@"
    if [[ -e $BH_HOME_DIRECTORY/response.bh ]]; then
        local command=$(head -n 1 $BH_HOME_DIRECTORY/response.bh)
        rm $BH_HOME_DIRECTORY/response.bh
        history -s "$command"
        echo "$command"
        eval "$command"
     fi;
}
