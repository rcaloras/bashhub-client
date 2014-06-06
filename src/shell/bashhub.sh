source ~/.bashhub/.config
export BH_EXEC_DIRECTORY="~/.bashhub/env/bin/"

BH_PROCESS_COMMAND()
{
    # Check to make sure we have a new command
    if [[ $BH_PREV_HISTORY = $BH_RAW_HISTORY ]];
    then
        exit 0;
    fi;

    local BH_COMMAND=$(echo "$BH_RAW_HISTORY" |  cut -d " " -f4-)
    local PROCESS_ID=$$
    # Should get process start time in seconds.
    local PROCESS_START=`ps -p $$ -o lstart | sed -n 2p | date +%s%3N -f -`
    local WORKING_DIRECTORY=`pwd`

    # Had this previously, think it was part of the trap. DELETE ME later if
    # still not useful :)
    #local PARSED_COMMAND=`echo "$BH_COMMAND" | sed -e 's/^ *//g' -e 's/ *$//g'`

    ($BH_EXEC_DIRECTORY/bashhub "$BH_COMMAND" "$WORKING_DIRECTORY" $PROCESS_ID \
        "$PROCESS_START"&)
}

PROMPT_COMMAND='BH_PREV_HISTORY=$BH_RAW_HISTORY;
                BH_RAW_HISTORY=$(history 1);
                (BH_PROCESS_COMMAND);'
bh()
{
    ($BH_EXEC_DIRECTORY/bh "$@")
}
