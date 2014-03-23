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
#

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


rm -r ~/.bashhub
bashprofile=`find_users_bash_file`
cp $bashprofile "$bashprofile.backup"

grep -v "source ~/.bashhub/bashhub.sh" $bashprofile > temp
mv temp $bashprofile
