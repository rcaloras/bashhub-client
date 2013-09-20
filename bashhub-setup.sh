#!/bin/bash
# 
# Bashhub.com Setup script
#
# Author; Ryan Caloras
#

mkdir ~/.bashhub
cp src/python/bashhub.py ~/.bashhub/
cp src/shell/bashhub.sh ~/.bashhub/

# Add our file to .bashrc
echo "source ~/.bashhub/bashhub.sh" >> ~/.bashrc

echo "Should be all setup. Good to go!"


