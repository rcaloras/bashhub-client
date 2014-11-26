#
# lib-bashhub.sh
# This file should contain the common bashhub
# shell functions between bash and zsh
#

export PATH=$PATH:"$HOME/.bashhub/bin"

#
# Prepare and send our command to be processed.
#
# @param The command just entered.
#
BH_PREEXEC() {
    local command
    command=$(BH_TRIM_WHITESPACE "$1")
    (BH_PROCESS_COMMAND "$command"&)
}

#
# Send our command to the server if everything
# looks good.
#
# @param A trimmed command from the command line
#
BH_PROCESS_COMMAND() {

    local bh_command="$1"

    # Sanity empty check
    if [[ -z "$bh_command" ]];
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

    local process_id=$$

    # This is non-standard across systems. GNU Date and BSD Date
    # both convert to epoch differently. Using python for cross system
    # compatibility.
    local process_start_stamp
    process_start_stamp=$(ps -p $$ -o lstart | sed -n 2p)

    local process_start=$($BH_EXEC_DIRECTORY/bashhub util parsedate "$process_start_stamp")

    local working_directory=$(pwd)

    ($BH_EXEC_DIRECTORY/bashhub save "$bh_command" "$working_directory" \
    "$process_id" "$process_start"&)
}

BH_TRIM_WHITESPACE() {
    local var=$@
    var="${var#"${var%%[![:space:]]*}"}"   # remove leading whitespace characters
    var="${var%"${var##*[![:space:]]}"}"   # remove trailing whitespace characters
    echo -n "$var"
}
