update_prompt()
{
    PROCESS_ID=$$
    PROCESS_START=`ps -p $$ -o lstart | sed -n 2p`
    USER_ID="52364ac5b52d605f31a78c44"
    SYSTEM_ID="52364af1b52d605f4a3b49e9"
    WORKING_DIRECTORY=`pwd`

    if [[ $1 != "bash_command=" ]]
    then
       (~/.bashhub/bashhub.py "$1" $USER_ID $SYSTEM_ID $PROCESS_ID \
           "$PROCESS_START" "$WORKING_DIRECTORY"&)
    fi;
}
trap 'previous_command=$this_command; this_command=$BASH_COMMAND' DEBUG
PROMPT_COMMAND='bash_command=$previous_command; if [[ $bash_command ]]; then update_prompt "$bash_command"; bash_command=; fi;'
