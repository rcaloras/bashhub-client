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
        return 0;
    fi;

    # Check to make sure bashhub is still installed. Otherwise, this will
    # simply fail and spam the user that files dont exist.
    if ! type "bashhub" &> /dev/null; then
        return 0;
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

# Small function to check our Bashhub installation.
# It's added to our precmd functions. On its initial run
# it removes itself from the precmd function array.
# This means it runs exactly once.
__bh_check_bashhub_installation() {
    local ret
    ret=0
    if [[ -n "$BASH_VERSION" && -n "$__bp_enable_subshells" && "$(trap)" != *"__bp_preexec_invoke_exec"* ]]; then
        echo "Bashhub's preexec hook is being overriden and is not saving commands. Please resolve what may be holding the DEBUG trap."
        ret=1
    elif [[ ! -f "$BH_HOME_DIRECTORY/config" ]]; then
        echo "Missing Bashhub config file. Please run 'bashhub setup' to generate one."
        ret=2
    elif ! grep -Fq "access_token" "$BH_HOME_DIRECTORY/config"; then
        echo "Missing Bashhub access token. Please run 'bashhub setup' to re-login."
        ret=3
    elif ! grep -Fq "system_name" "$BH_HOME_DIRECTORY/config"; then
        echo "Missing system name. Please run 'bashhub setup' to re-login."
        ret=4
    elif grep -Fq "save_commands = False" "$BH_HOME_DIRECTORY/config"; then
        echo "Bashhub is currently disabled. Run 'bashhub on' to re-enable."
        ret=5
    fi;

    # Remove from precmd_functions so it only runs once when the session starts.
    local delete
    delete=(__bh_check_bashhub_installation)
    precmd_functions=( "${precmd_functions[@]/$delete}" )

    return $ret
}

# Allows bashhub to manipulate session state by
# manipulating variables when invoked by precmd.
__bh_precmd_run_script() {
    if [[ -e $BH_HOME_DIRECTORY/script.bh ]]; then
        local command
        command=$(head -n 1 "$BH_HOME_DIRECTORY/script.bh")
        rm "$BH_HOME_DIRECTORY/script.bh"
        eval "$command"
     fi;
}

# Check our bashhub installation when the session starts.
precmd_functions+=(__bh_check_bashhub_installation)
precmd_functions+=(__bh_precmd_run_script)

__bh_trim_whitespace() {
    local var=$@
    var="${var#"${var%%[![:space:]]*}"}"   # remove leading whitespace characters
    var="${var%"${var##*[![:space:]]}"}"   # remove trailing whitespace characters
    echo -n "$var"
}
