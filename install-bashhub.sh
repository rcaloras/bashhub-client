#!/bin/bash -e
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
    setup_bashhub_files
    #wget bashhub.com/setup
    #python bashhub-setup.py
}


download_and_install_env () {
    # Select current version of virtualenv:
    VERSION=1.6.4
    # Name your first "bootstrap" environment:
    INITIAL_ENV=env
    # Options for your first environment:
    ENV_OPTS='--no-site-packages --distribute'
    # Set to whatever python interpreter you want for your first environment:
    PYTHON=$(which python)
    URL_BASE=http://pypi.python.org/packages/source/v/virtualenv

    # --- Real work starts here ---
    echo $URL_BASE/virtualenv-$VERSION.tar.gz
    wget $URL_BASE/virtualenv-$VERSION.tar.gz
    tar xzf virtualenv-$VERSION.tar.gz
    # Create the first "bootstrap" environment.
    $PYTHON virtualenv-$VERSION/virtualenv.py $ENV_OPTS $INITIAL_ENV
    # Don't need this anymore.
    rm -rf virtualenv-$VERSION
    # Install the environment.
    $INITIAL_ENV/bin/pip install virtualenv-$VERSION.tar.gz
}
check_already_installed () {
    if [ -e ~/.bashhub ]; then
        die "\nLooks like the bashhub client is already installed.
        \nrm -r ~/.bashhub to install again" 1
    fi
}

setup_bashhub_files () {
    mkdir ~/.bashhub
    cd ~/.bashhub
    download_and_install_env
    # should kick off python from here
    echo "should be good to go"
}

die () { echo -e $1; exit $2; }

install_bashhub
