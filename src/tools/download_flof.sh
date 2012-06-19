#!/bin/sh

echo "Checking out flof"
svn checkout https://github.com/horus107/flof/trunk flof

echo "Checking out PyFoam"
svn checkout https://openfoam-extend.svn.sourceforge.net/svnroot/openfoam-extend/trunk/Breeder/other/scripting/PyFoam

if [ ! -f env_setup.sh ]; then
    echo "Copying env_setup.sh to $PWD. Please edit this file and change the BASE variable according to your needs. This usually means the local directory."
    cp flof/src/tools/env_setup.sh .
fi
