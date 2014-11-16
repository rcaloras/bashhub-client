source ~/.bashhub/.config
export BH_HOME_DIRECTORY="$HOME/.bashhub/"
export BH_EXEC_DIRECTORY="$HOME/.bashhub/env/bin"

# Alias to bind Ctrl + B
bind '"\C-b":"\C-u\C-kbh -i\n"'

BH_PROCESS_COMMAND()
{

    local BH_COMMAND=$@

    # Check to make sure we have a new command
    if [[ $BH_PREV_COMMAND = $BH_COMMAND ]];
    then
        exit 0;
    fi;

    # Check to make sure we have valid tokens
    if [[ -z "$BH_USER_ID" ]] || [[ -z "$BH_SYSTEM_ID" ]];
    then
        exit 0;
    fi;

    # Check to make sure bashhub is still installed. Otherwise, this will
    # simply fail and spam the user that files dont exist.
    if [[ ! -f $BH_EXEC_DIRECTORY/bashhub ]];
    then
        exit 0;
    fi;

    local PROCESS_ID=$$

    # This is non-standard across systems. GNU Date and BSD Date
    # both convert to epoch differently. Using python for cross system
    # compatibility.
    local PROCESS_START_STAMP
    PROCESS_START_STAMP=$(ps -p $$ -o lstart | sed -n 2p)

    local PROCESS_START=$($BH_EXEC_DIRECTORY/bashhub util parsedate "$PROCESS_START_STAMP")

    local WORKING_DIRECTORY=$(pwd)

    ($BH_EXEC_DIRECTORY/bashhub save "$BH_COMMAND" "$WORKING_DIRECTORY" \
    "$PROCESS_ID" "$PROCESS_START"&)
}

BH_TRIM_WHITESPACE() {
    local var=$@
    var="${var#"${var%%[![:space:]]*}"}"   # remove leading whitespace characters
    var="${var%"${var##*[![:space:]]}"}"   # remove trailing whitespace characters
    echo -n "$var"
}

BH_GET_LAST_COMMAND() {
    # GRAB LAST OF COMMAND
    local HISTORY_LINE=$(history 1)
    local TRIMMED_COMMAND=`BH_TRIM_WHITESPACE $HISTORY_LINE`
    local NO_LINE_NUMBER=`echo "$TRIMMED_COMMAND" | cut -d " " -f2-`
    BH_TRIM_WHITESPACE $NO_LINE_NUMBER
}

BH_ON_PROMPT_COMMAND() {
    BH_PREV_COMMAND=$BH_COMMAND;
    BH_COMMAND=`BH_GET_LAST_COMMAND`;
    (BH_PROCESS_COMMAND $BH_COMMAND);
}

PROMPT_COMMAND="BH_ON_PROMPT_COMMAND; $PROMPT_COMMAND"

bh()
{
    $BH_EXEC_DIRECTORY/bh "$@"
    if [[ -e $BH_HOME_DIRECTORY/response.bh ]];
    then
        local COMMAND=$(head -n 1 $BH_HOME_DIRECTORY/response.bh)
        rm $BH_HOME_DIRECTORY/response.bh
        history -s $COMMAND
        eval $COMMAND
     fi;
}
