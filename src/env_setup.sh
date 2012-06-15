# Quick and dirty script to be sourced in order to setup the flof and pyfoam environment. Edit BASE accordingly to your paths.

BASE=$HOME/software/flof-dist

FLOF=$BASE/flof
PF=$BASE/PyFoam
export PATH=$PATH:$PF/bin:$PF/sbin:$FLOF/src
export PYTHONPATH=$PF:$PF/PyFoam:$$FLOF/src
