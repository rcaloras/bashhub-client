#!/bin/bash -e
#
# Bashhub.com Installation shell script
#
# Ryan Caloras (ryan@bashhub.com)
#
# http://www.gnu.org/s/hello/manual/autoconf/Portable-Shell.html
#
# The only shell it won't ever work on is cmd.exe.

set -e

bash_profile_hook='
### Bashhub.com Installation.
### This Should be at the EOF. https://bashhub.com/docs
if [ -f ~/.bashhub/bashhub.sh ]; then
    source ~/.bashhub/bashhub.sh
fi
'
zsh_profile_hook='
### Bashhub.com Installation
if [ -f ~/.bashhub/bashhub.zsh ]; then
    source ~/.bashhub/bashhub.zsh
fi
'
fish_config_hook='
### Bashhub.com Installation
if [ -f "$HOME/.bashhub/bashhub.fish" ]
    source "$HOME/.bashhub/bashhub.fish"
end
'

bash_config_source='
if [ -f ~/.bashrc ]; then
    source ~/.bashrc
fi
'

bashhub_config="$HOME/.bashhub/config"
backup_config="$HOME/.bashhub.config.backup"
zshprofile="$HOME/.zshrc"
fish_config="${XDG_CONFIG_HOME:-$HOME/.config}/fish/config.fish"
uv_python_version=${UV_PYTHON_VERSION:-'3.13'}

# Optional parameter to specify a Bashhub version from PyPI.
if [[ -z "$bashhub_install_test" ]]; then
    bashhub_version=${1:-''}
else
    bashhub_version=${bashhub_version:-''}
fi

install_bashhub() {
    check_dependencies
    check_already_installed
    setup_bashhub_files
}

check_dependencies() {
    if [ -z "$(detect_shell_type)" ]; then
        die "\nSorry, couldn't detect your shell type. Bashhub only supports bash, fish, or zsh. Your defualt shell is $SHELL." 1
    fi;

    if ! find_uv_command &> /dev/null && ! command -v curl &> /dev/null; then
        die "\nSorry, Bashhub needs curl to install uv." 1
    fi
}

check_already_installed() {
    if [ -e "$HOME/.bashhub" ]; then
        echo -e "\nLooks like Bashhub is already installed.
        \nLets go ahead and update it.\n"

        # Copy our user credentials so we don't have to ask you for them again.
        if [ -e "$bashhub_config" ]; then
            cp "$bashhub_config" "$backup_config"
        fi

        rm -r "$HOME/.bashhub"
    fi
}

find_uv_command() {
    if command -v uv &> /dev/null; then
        command -v uv
        return 0
    elif [ -x "$HOME/.local/bin/uv" ]; then
        echo "$HOME/.local/bin/uv"
        return 0
    fi

    return 1
}

install_uv() {
    echo "Installing uv..." >&2

    if ! curl -LsSf https://astral.sh/uv/install.sh | env UV_NO_MODIFY_PATH=1 sh -s -- --quiet; then
        die "\nSorry, Bashhub couldn't install uv. Please check your network connection and rerun this script." 1
    fi
}

ensure_uv() {
    local uv_command
    uv_command=$(find_uv_command || true)

    if [ -z "$uv_command" ]; then
        install_uv
        uv_command=$(find_uv_command || true)
    fi

    if [ -z "$uv_command" ]; then
        die "\nSorry, Bashhub couldn't install or find uv." 1
    fi

    echo "$uv_command"
}

install_or_upgrade_bashhub_package() {
    local uv_command=$1

    "$uv_command" python install "$uv_python_version" --quiet

    if [ -n "$bashhub_version" ]; then
        echo "Installing bashhub $bashhub_version..."
        "$uv_command" tool install --python "$uv_python_version" --reinstall "bashhub==$bashhub_version" --quiet
    elif "$uv_command" tool list | grep -q "^bashhub "; then
        echo "Updating bashhub..."
        "$uv_command" tool upgrade bashhub --quiet
    else
        echo "Installing bashhub..."
        "$uv_command" tool install --python "$uv_python_version" bashhub --quiet
    fi
}

copy_shell_files() {
    local shell_dir
    shell_dir=$(bashhub util shell-dir)

    if [ -z "$shell_dir" ] || [ ! -d "$shell_dir" ]; then
        die "\nSorry, Bashhub couldn't find its installed shell files." 1
    fi

    cp -r "$shell_dir/deps" "$HOME/.bashhub/"
    cp "$shell_dir"/bashhub.* "$HOME/.bashhub/"
}

run_bashhub_setup() {
    # Check if we already have a config. If not run setup.
    if [ -e "$backup_config" ]; then
        cp "$backup_config" "$bashhub_config"
        rm "$backup_config"

        if ! bashhub util update-system-info; then
            # Run setup if we run into any issues updating our system info
            bashhub setup
        fi
    else
        # Setup our config file
        bashhub setup
    fi
}

install_hooks_for_zsh() {
    # If we're using zsh, install our zsh hooks
    if [ ! -e "$HOME/.zshrc" ]; then
        die "No zshfile (.zshrc could be found)" 1
    fi

    # Add our file to our bashprofile if it doesn't exist yet
    if grep -q "source ~/.bashhub/bashhub.zsh" "$zshprofile"
    then
        :
    else
        echo "$zsh_profile_hook" >> "$zshprofile"
    fi

}

install_hooks_for_fish() {
    if [ ! -e "$fish_config" ]; then
        die "No fish config cound be found" 1
    fi

    if grep -q "bashhub.fish" "$fish_config"
    then
        :
    else
        echo "$fish_config_hook" >> "$fish_config"
    fi
}


# Create two config files .bashrc and .bash_profile since
# OS X and Linux shells use them diffferently. Source .bashrc
# from .bash_profile and everything should work the same now.
generate_bash_config_file() {
    touch "$HOME/.bashrc"
    touch "$HOME/.bash_profile"
    echo "$bash_config_source" >> "$HOME/.bash_profile"
    echo "Created ~/.bash_profile and ~/.bashrc"
}


install_hooks_for_bash() {
    local bashprofile=$(find_users_bash_file)


    # If we don't have a bash profile ask if we should generate one.
    if [ -z "$bashprofile" ]; then
        echo "Couldn't find a bash confg file."

        while true; do
            read -p "Would you like to generate one? (y/n): " yn
            case $yn in
                [Yy]* ) generate_bash_config_file; bashprofile="$HOME/.bashrc"; break;;
                [Nn]* ) break;;
                * ) echo "Please answer yes or no.";;
            esac
        done
    fi

    # Have to have this. Error out otherwise.
    if [ -z "$bashprofile" ]; then
        die "No bashfile (e.g. .profile, .bashrc, etc) could be found." 1
    fi

    # Add our file to our bashprofile if it doesn't exist yet
    if grep -q "source ~/.bashhub/bashhub.sh" "$bashprofile"
    then
        :
    else
        echo "$bash_profile_hook" >> "$bashprofile"
    fi

}

detect_shell_type() {
    if [ -n "$ZSH_VERSION" ]; then
        echo 'zsh'
    elif [ -n "$FISH_VERSION" ]; then
        echo 'fish'
    elif [ -n "$BASH_VERSION" ]; then
        echo 'bash'
    else
        :
    fi
}

install_hooks_for_shell() {
    local shell_type
    shell_type=$(detect_shell_type)

    case $shell_type in
        "zsh")
            install_hooks_for_zsh
            ;;
        "fish")
            install_hooks_for_fish
            ;;
        "bash")
            install_hooks_for_bash
            ;;
        *)
        die "\nBashhub only supports bash, fish, or zsh. Your default shell is $SHELL." 1
    esac
}


setup_bashhub_files() {
    local uv_command

    mkdir -p "$HOME/.bashhub"
    uv_command=$(ensure_uv)
    export PATH="$HOME/.local/bin:$PATH"

    install_or_upgrade_bashhub_package "$uv_command"
    copy_shell_files
    install_hooks_for_shell
    run_bashhub_setup

    # Make sure our config is only readable to us.
    chmod 600 "$bashhub_config"
    chmod 700 "$HOME/.bashhub"

    if [ -e "$bashhub_config" ]; then
        echo "Should be good to go! Please close and restart your terminal session."
    else
        echo "Please run 'bashhub setup' after restarting your terminal session."
    fi
}

#
# Find a users active bash file based on
# which looks the largest. The idea being the
# largest is probably the one they actively use.
#
find_users_bash_file() {

    bash_file_array=( "$HOME/.bash_profile" "$HOME/.bashrc" "$HOME/.profile")

    local largest_file_size=0
    for file in "${bash_file_array[@]}"
    do
        if [ -e "$file" ]; then
            # Get our file size.
            local file_size=$(wc -c "$file" | awk '{print $1}')

            if [ "$file_size" -gt "$largest_file_size" ]; then
                local largest_file_size=$file_size
                local largest_file=$file
            fi
        fi
     done

    # If we found the largest file, return it
    if [ -n "$largest_file" ]; then
        echo "$largest_file"
        return 0
    fi
}

die () { echo -e $1; exit $2; }

# Run our install so long as we're not in test.
if [[ -z "$bashhub_install_test" ]]; then
    install_bashhub
fi;
