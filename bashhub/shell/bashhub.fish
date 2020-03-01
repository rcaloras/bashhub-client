#
# bashhub.fish
# Main file that is sourced onto our path for fish.
#

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

function __bh_path_add --argument-names item
    if [ -d "$item" ] && not contains_element "$item" "$PATH"
        set -x PATH "$item" "$PATH"
    end
end

function __bh_interactive
  fish -c "bh -i"
end

# Avoid duplicate inclusion
if [ "$__bh_imported" = "defined" ]
    __bh_path_add "$HOME/.bashhub/bin"
else
    set -Ux __bh_imported "defined"
    set -Ux BH_HOME_DIRECTORY "$HOME/.bashhub/"

    source "$BH_HOME_DIRECTORY/deps/fish/functions/__bh_check_bashhub_installation.fish"
    bind \cb __bh_interactive
end

function __bh_preexec --on-event fish_preexec
    set -g __BH_PWD "$PWD"
    set -g __BH_SAVE_COMMAND "$argv[1]"
end

function __bh_precmd --on-event fish_prompt
    set -x __BH_EXIT_STATUS $status

    if [ -e "$BH_HOME_DIRECTORY/response.bh" ]
        set -l cmd (head -n 1 "$BH_HOME_DIRECTORY/response.bh")
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
    set -l process_start_stamp (env LC_ALL=C ps -p $fish_pid -o lstart=)

    set -x process_start (bashhub util parsedate "$process_start_stamp")
    set -x exit_status "$__BH_EXIT_STATUS"

    fish -c 'bashhub save "$bh_command" "$working_directory" "$process_id" "$process_start" "$exit_status" &'
end
