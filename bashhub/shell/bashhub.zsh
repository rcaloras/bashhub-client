source ~/.bashhub/.config
export BH_HOME_DIRECTORY="$HOME/.bashhub/"
export BH_EXEC_DIRECTORY="$HOME/.bashhub/env/bin"

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

    # Should get process start time in seconds.
    #local PROCESS_START=`ps -p $$ -o lstart | sed -n 2p | date +%s%3N -f -`
    # Converting back to old way in python
    local PROCESS_START=`ps -p $$ -o lstart | sed -n 2p | date +"%s"`

    local WORKING_DIRECTORY=`pwd`

    ($BH_EXEC_DIRECTORY/bashhub "$BH_COMMAND" "$WORKING_DIRECTORY" \
    "$PROCESS_ID" "$PROCESS_START"&)
}

function bh_preexec() {
    BH_PREV_COMMAND=$BH_COMMAND;
    BH_COMMAND=$1;
    (BH_PROCESS_COMMAND $BH_COMMAND);
}

function bh_precmd() {
if [[ -e $BH_HOME_DIRECTORY/response.bh ]];
    then
        local COMMAND="`head -n 1 $BH_HOME_DIRECTORY/response.bh`"
        rm $BH_HOME_DIRECTORY/response.bh
        print -z $COMMAND
     fi;
}

# Hook into preexec functions
preexec_functions+=bh_preexec
precmd_functions+=bh_precmd

bh()
{
    $BH_EXEC_DIRECTORY/bh "$@"
}
