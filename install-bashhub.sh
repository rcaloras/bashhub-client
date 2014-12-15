#!/bin/bash -e
#
# Bashhub.com Installation shell script
#
# Ryan Caloras (ryan@bashhub.com)
#
# http://www.gnu.org/s/hello/manual/autoconf/Portable-Shell.html
#
# The only shell it won't ever work on is cmd.exe.

bash_profile_hook='
### Bashhub.com Installation
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

bashhub_config=~/.bashhub/.config
backup_config=~/.bashhub.config.backup
zshprofile=~/.zshrc

# Optional parameter to specify a github branch
# to pull from.
github_branch=${1:-'0.0.5'}

install_bashhub () {
    check_dependencies
    check_already_installed
    setup_bashhub_files
}


download_and_install_env () {
    # Select current version of virtualenv:
    VERSION=1.9.1
    # Name your first "bootstrap" environment:
    INITIAL_ENV=env
    # Options for your first environment:
    ENV_OPTS='--no-site-packages --distribute'
    # Set to whatever python interpreter you want for your first environment:
    PYTHON=$(which python)
    URL_BASE=http://pypi.python.org/packages/source/v/virtualenv

    # --- Real work starts here ---
    echo $URL_BASE/virtualenv-$VERSION.tar.gz
    curl -OL  $URL_BASE/virtualenv-$VERSION.tar.gz
    tar xzf virtualenv-$VERSION.tar.gz
    # Create the first "bootstrap" environment.
    $PYTHON virtualenv-$VERSION/virtualenv.py $ENV_OPTS $INITIAL_ENV
    # Don't need this anymore.
    rm -rf virtualenv-$VERSION
    # Install the environment.
    $INITIAL_ENV/bin/pip -q install virtualenv-$VERSION.tar.gz
    # Don't need this anymore either.
    rm virtualenv-$VERSION.tar.gz
}

check_dependencies () {
    if [ -z "$(which python)" ]; then
        die "\n Sorry you need to have 'python' installed. Please install python and rerun this script." 1
    fi
}

check_already_installed () {
    if [ -e ~/.bashhub ]; then
        echo -e "\nLooks like the bashhub client is already installed.
        \nLets go ahead and update it.\n"

        # Copy our user credentials so we don't have to ask you for them again.
        if [ -e "$bashhub_config" ]; then
            cp "$bashhub_config" "$backup_config"
        fi

        rm -r ~/.bashhub
    fi
}

install_hooks_for_zsh () {
    cp bashhub/shell/bashhub.zsh ~/.bashhub/
    # Add our file to our bashprofile if it doesn't exist yet
    if grep -q "source ~/.bashhub/bashhub.zsh" "$zshprofile"
    then
        :
    else
        echo "$zsh_profile_hook" >> "$zshprofile"
    fi

}

setup_bashhub_files () {

    local bashprofile=$(find_users_bash_file)

    # Have to have this. Error out otherwise.
    if [ -z "$bashprofile" ]; then
        die "No bashfile (e.g. .profile, .bashrc, etc) could be found" 1
    fi

    mkdir ~/.bashhub
    cd ~/.bashhub
    download_and_install_env

    # Grab the code from master off github.
    curl -sL https://github.com/rcaloras/bashhub-client/archive/${github_branch}.tar.gz -o client.tar.gz
    tar -xvf client.tar.gz
    cd bashhub-client*

    # Copy over our sh files.
    cp bashhub/shell/bashhub.sh ~/.bashhub/
    # Copy over our dependencies.
    cp -r bashhub/shell/deps ~/.bashhub/

    # Add our file to our bashprofile if it doesn't exist yet
    if grep -q "source ~/.bashhub/bashhub.sh" $bashprofile
    then
        :
    else
        echo "$bash_profile_hook" >> $bashprofile
    fi

    # If we're using zsh, install our zsh hooks
    if [ -e ~/.zshrc ]; then
        install_hooks_for_zsh
    fi

    # install our packages. bashhub and dependencies.
    echo "Pulling down a few dependencies...(this may take a moment)"
    ../env/bin/pip -q install .

    # Check if we already have a config. If not run setup.
    if [ -e $backup_config ]; then
        cp $backup_config $bashhub_config
        rm $backup_config
    else
        # Setup our config file
        ../env/bin/bashhub setup
    fi

    # Wire up our bin directory
    mkdir ~/.bashhub/bin
    ln -s ../env/bin/bashhub ~/.bashhub/bin/bashhub
    ln -s ../env/bin/bashhub-setup ~/.bashhub/bin/bashhub-setup
    ln -s ../env/bin/bh ~/.bashhub/bin/bh

    # Clean up what we downloaded
    cd ~/.bashhub
    rm client.tar.gz
    rm -r bashhub-client*
    echo "Should be good to go! Please close and restart your terminal session."
}

#
# Find a users active bash file based on
# which looks the largest. The idea being the
# largest is probably the one they actively use.
#
find_users_bash_file () {

    bash_file_array=( ~/.profile ~/.bashrc ~/.bash_profile)

    local largest_file_size=0
    for file in "${bash_file_array[@]}"
    do
        if [ -e $file ]; then
            # Get our file size.
            local file_size=$(wc -c "$file" | awk '{print $1}')

            if [ $file_size -gt $largest_file_size ]; then
                local largest_file_size=$file_size
                local largest_file=$file
            fi
        fi
     done

    # If we found the largest file, return it
    if [ -n "$largest_file" ]; then
        echo $largest_file
        return 0
    fi
}

die () { echo -e $1; exit $2; }

install_bashhub
