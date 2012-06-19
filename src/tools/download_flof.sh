#!/bin/sh

echo "Checking out flof"
svn checkout https://github.com/horus107/flof/trunk flof

echo "Checking out PyFoam"
svn checkout https://openfoam-extend.svn.sourceforge.net/svnroot/openfoam-extend/trunk/Breeder/other/scripting/PyFoam
