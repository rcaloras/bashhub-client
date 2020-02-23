#
# bashhub.fish
# Main file that is sourced onto our path for fish.
#

# Avoid duplicate inclusion
# if [ "$__bh_imported" = "defined" ]
#     __bh_path_add "$HOME/.bashhub/bin"
#     return 0
# else
#     set -x __bh_imported "defined"
# end

function __bh_path_add --argument-names item
    if [ -d "$item" ] && not contains_element "$item" "$PATH"
        set -x PATH "$item" "$PATH"
    end
end

#
# Checks if an element is present in an array.
#
# @param The element to check if present
# @param the array to check in
# @return 0 if present 1 otherwise
#
function contains_element --argument-names element array
    for e in $array
        [ "$e" = "$element" ] && return 0
    end

    return 1
end

# Make sure our bin directory is on our path
__bh_path_add "$HOME/.bashhub/bin"

function __bh_preexec --on-event fish_preexec
    set -g __BH_PWD "$PWD"
    set -g __BH_SAVE_COMMAND "$argv[1]"
end

function __bh_precmd --on-event fish_prompt
    set -x __BH_EXIT_STATUS $status

    if [ -e "$BH_HOME_DIRECTORY/response.bh" ]
        set -l cmd "`head -n 1 $BH_HOME_DIRECTORY/response.bh`"
        rm "$BH_HOME_DIRECTORY/response.bh"
        echo $cmd
    end

    if [ -n "$BH_HOME_DIRECTORY" ]
        set -g bashhub_dir "$BH_HOME_DIRECTORY"
    else
        set -g bashhub_dir "~/.bashhub"
    end

    set -x working_directory "$__BH_PWD"
    set -x cmd "$__BH_SAVE_COMMAND"
    set -x process_id $fish_pid

    if [ -n "$__BH_SAVE_COMMAND" ]
        set -e __BH_SAVE_COMMAND
    else
        return 0
    end

    if [ -e "$bashhub_dir" ]
        fish -c '__bh_process_command "$cmd" "$working_directory" "$process_id" &' >> "$bashhub_dir"/log.txt 2>&1
    end
end

#
# Send our command to the server if everything
# looks good.
#
function __bh_process_command --argument-names cmd dir pid
    set -x bh_command (string trim $cmd)

    # sanity check
    if [ -z "$bh_command" ]
        return 0
    end

    # ensure that bashhub is installed
    if not type "bashhub" > /dev/null 2>&1
        return 0
    end

    set -x working_directory "$dir"
    set -x process_id "$pid"

    # This is non-standard across systems. As GNU and BSD Date convert epochs
    # differently, use python for cross-system compatibility.
    set -l process_start_stamp (LC_ALL=C ps -p $fish_pid -o lstart=)

    set -x process_start (bashhub util parsedate "$process_start_stamp")
    set -x exit_status "$__BH_EXIT_STATUS"

    fish -c 'bashhub save "$bh_command" "$working_directory" "$process_id" "$process_start" "$exit_status" &'
end

# Small function to check our Bashhub installation.
# It's added to our precmd functions. On its initial run
# it removes itself from the precmd function array.
# This means it runs exactly once.
function __bh_check_bashhub_installation
    set -l ret 0
    set -l config_path "$BH_HOME_DIRECTORY/config"
    if [ -n "$FISH_VERSION" && -n "$__bh_enable_subshells" && "(trap)" -ne *"__bh_preexec_invoke_exec"* ]
        echo "Bashhub's preexec hook is being overriden and is not saving commands. Please resolve what may be holding the DEBUG trap."
        set ret 1
    else if [ -f "$config_path" ]
        echo "Missing Bashhub config file. Please run 'bashhub setup' to generate one."
        set ret 2
    else if not grep -Fq "access_token" "$config_path"
        echo "Missing Bashhub access token. Please run 'bashhub setup' to re-login."
        set ret 3
    else if not grep -Fq "system_name" "$config_path"
        echo "Missing system name. Please run 'bashhub setup' to re-login."
        set ret 4
    else if grep -Fq "save_commands = False" "$config_path"
        echo "Bashhub is currently disabled. Run 'bashhub on' to re-enable."
        set ret 5
    end

    # TODO: remove self from preexec once the session starts
    set -l delete (__bh_check_bashhub_installation)

    return $ret
end

set -x BH_HOME_DIRECTORY "$HOME/.bashhub/"
