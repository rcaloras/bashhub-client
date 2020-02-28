#
# __bh_check_bashhub_installation.fish
# Should only be sourced once following installation.
#

# Small function to check our Bashhub installation.
function __bh_check_bashhub_installation
    set -l ret 0
    set -l config_path "$BH_HOME_DIRECTORY/config"
    if [ -n "$FISH_VERSION" ] && [ -n "$__bh_enable_subshells" ] && [ "(trap)" -ne *"__bh_preexec_invoke_exec"* ]
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

    return $ret
end

__bh_check_bashhub_installation
