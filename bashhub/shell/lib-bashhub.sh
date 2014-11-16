#
# lib-bashhub.sh
# This file should contain the common bashhub
# shell functions between bash and zsh
#

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
