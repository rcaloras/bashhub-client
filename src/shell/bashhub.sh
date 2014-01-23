source ~/.bashhub/.config

BH_PROCESS_COMMAND()
{
    # Check to make sure we have a new command
    if [[ $BH_PREV_HISTORY = $BH_RAW_HISTORY ]];
    then
        exit 0;
    fi;

    local BH_COMMAND=$(echo "$BH_RAW_HISTORY" |  cut -d " " -f4-)
    local PROCESS_ID=$$
    local PROCESS_START=`ps -p $$ -o lstart | sed -n 2p`
    local USER_ID=$BH_USER_ID
    local SYSTEM_ID=$BH_SYSTEM_ID
    local WORKING_DIRECTORY=`pwd`

    # Had this previously, think it was part of the trap. DELETE ME later if
    # still not useful :)
    #local PARSED_COMMAND=`echo "$BH_COMMAND" | sed -e 's/^ *//g' -e 's/ *$//g'`

    (cd $BH_EXEC_DIRECTORY && ./bashhub.py "$BH_COMMAND" $USER_ID $SYSTEM_ID $PROCESS_ID \
        "$PROCESS_START" "$WORKING_DIRECTORY"&)
}

PROMPT_COMMAND='BH_PREV_HISTORY=$BH_RAW_HISTORY;
                BH_RAW_HISTORY=$(history 1);
                (BH_PROCESS_COMMAND);'
bh()
{
    (cd $BH_EXEC_DIRECTORY && ./bh.py "$@")
}
