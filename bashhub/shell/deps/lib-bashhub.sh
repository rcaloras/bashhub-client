#
# lib-bashhub.sh
# This file should contain the common bashhub
# shell functions between bash and zsh
#

export PATH=$PATH:"$HOME/.bashhub/bin"

BH_INCLUDE() {
    [[ -f "$1" ]] && source "$1"
}

#
# Checks if an element is present in an array.
#
# @param The element to check if present
# @param the array to check in
# @return 0 if present 1 otherwise
#
contains_element() {
  local e
  for e in "${@:2}"; do [[ "$e" == "$1" ]] && return 0; done
  return 1
}

# Include our user configuration
BH_INCLUDE ~/.bashhub/.config

#
# Prepare and send our command to be processed redirecting
# all output to our log file.
#
# @param The command just entered.
#
BH_PREEXEC() {
    (BH_PROCESS_COMMAND "$1"&) >> $BH_HOME_DIRECTORY/log.txt 2>&1
}

#
# Send our command to the server if everything
# looks good.
#
# @param A trimmed command from the command line
#
BH_PROCESS_COMMAND() {

    local bh_command
    bh_command=$(BH_TRIM_WHITESPACE "$1")

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
