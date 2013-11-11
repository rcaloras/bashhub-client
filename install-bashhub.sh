#!/bin/bash
#
# Bashhub.com Installation shell script
#
# Ryan Caloras (ryan@bashhub.com)
#
# It must work everywhere, including on systems that lack
# a /bin/bash, map 'sh' to ksh, ksh97, bash, ash, or zsh,
# and potentially have either a posix shell or bourne
# shell living at /bin/sh.
#
# See this helpful document on writing portable shell scripts:
# http://www.gnu.org/s/hello/manual/autoconf/Portable-Shell.html
#
# The only shell it won't ever work on is cmd.exe.


install_bashhub () {
    check_already_installed
    check_install_dependencies
    setup_bashhub_files
    #wget bashhub.com/setup
    #python bashhub-setup.py
}

check_already_installed () {
    if [ -e ~/.bashhub ]; then
        die "\nLooks like the bashhub client is already installed.
        \nrm -r ~/.bashhub to install again" 1
    fi
}

setup_bashhub_files () {
    mkdir ~/.bashhub
    mkdir ~/.bashhub/.python
    cp -r src/python/*.py ~/.bashhub/.python/
    cp -r src/python/model ~/.bashhub/.python/
    cp src/shell/bashhub.sh ~/.bashhub/
    cp src/shell/.config ~/.bashhub/.config

    local bashprofile=`find_users_bash_file`

# Add our file to .bashrc or .profile
echo "source ~/.bashhub/bashhub.sh" >> $bashprofile

echo "Should be all setup. Good to go!"
}


find_users_bash_file () {

    # possible bash files to use, order matters
    bash_file_array=( ~/.bashrc ~/.bash_profile ~/.profile)

    for file in "${bash_file_array[@]}"
    do
        if [ -e $file ]; then
            echo $file
            return 0
        fi
     done

     die "No bashfile (e.g. .profile, .bashrc, ect) could be found" 1
}

check_install_dependencies () {
    dependency_array=(python wget pip virtualenv)
    echo "Checking dependencies...."

    for i in "${dependency_array[@]}"
    do
       #Check each dependency
       check_dependency $i
    done
    echo "Awesome looks like we have everything we need!"
}

check_dependency () {
    dep=`which $1 2>&1`
    ret=$?
    if [ $ret -eq 0 ] && [ -x "$dep" ]; then
        echo " $1 was found"
    else
        die "$1 could not be found. please install $1 and retry this script."
    fi
}

die () { echo -e $1; exit $2; }

install_bashhub
