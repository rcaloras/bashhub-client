update_prompt()
{
    if [[ $1 != "bash_command=" ]]
    then
        ~/git/bashhub-client/bashhub.py "$1"
    fi;
}
trap 'previous_command=$this_command; this_command=$BASH_COMMAND' DEBUG
PROMPT_COMMAND='bash_command=$previous_command; if [[ $bash_command ]]; then update_prompt "$bash_command"; bash_command=; fi;'
