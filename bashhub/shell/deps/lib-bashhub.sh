#
# lib-bashhub.sh
# This file should contain the common bashhub
# shell functions between bash and zsh
#

__bh_path_add() {
    if [ -d "$1" ] && [[ ":$PATH:" != *":$1:"* ]]; then
        PATH="${PATH:+"$PATH:"}$1"
    fi
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

# Make sure our bin directory is on our path
__bh_path_add "$HOME/.bashhub/bin"

#
# Function to be run by our preexec hook.
#
# Saves the directory this command is being executed in to track (cd-ing), and
# sets a variable so we know that a command was just executed and should be
# saved.
#
# GLOBALS:
#   __BH_PWD The directory this command is being executed in
#   __BH_SAVE_COMMAND The command that is being executed and to be saved.
#
# Arguments:
#  $1 The command just entered, about to be executed.
#
__bh_preexec() {
    __BH_PWD="$PWD"
    __BH_SAVE_COMMAND="$1"
}

__bh_precmd() {

    # Set this initially to properly catch the exit status.
    __BH_EXIT_STATUS="$?"

    local bashhub_dir
    bashhub_dir=${BH_HOME_DIRECTORY:=~/.bashhub}

    local command="$__BH_SAVE_COMMAND"

    # Check if we need to process a command. If so, unset it as it will be
    # processed and saved.
    if [[ -n "$__BH_SAVE_COMMAND" ]]; then
        unset __BH_SAVE_COMMAND
    else
        return 0
    fi

    if [[ -e "$bashhub_dir" ]]; then
        (__bh_process_command "$command"&) >> "$bashhub_dir"/log.txt 2>&1
    fi;
}

#
# Send our command to the server if everything
# looks good.
#
# @param A trimmed command from the command line
#
__bh_process_command() {

    local bh_command
    bh_command=$(__bh_trim_whitespace "$1")

    # Sanity empty check
    if [[ -z "$bh_command" ]]; then
        exit 0;
    fi;

    # Check to make sure bashhub is still installed. Otherwise, this will
    # simply fail and spam the user that files dont exist.
    if ! type "bashhub" &> /dev/null; then
        exit 0;
    fi;

    local process_id=$$

    # This is non-standard across systems. GNU Date and BSD Date
    # both convert to epoch differently. Using python for cross system
    # compatibility.
    local process_start_stamp
    process_start_stamp=$(LC_ALL=C ps -p $$ -o lstart=)

    local process_start=$(bashhub util parsedate "$process_start_stamp")
    local working_directory="$__BH_PWD"
    local exit_status="$__BH_EXIT_STATUS"

    (bashhub save "$bh_command" "$working_directory" \
    "$process_id" "$process_start" "$exit_status"&)
}

__bh_trim_whitespace() {
    local var=$@
    var="${var#"${var%%[![:space:]]*}"}"   # remove leading whitespace characters
    var="${var%"${var##*[![:space:]]}"}"   # remove trailing whitespace characters
    echo -n "$var"
}
