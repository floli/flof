Installation
============
1. Download and save the `download_flof.sh <https://raw.github.com/Horus107/flof/master/src/tools/download_flof.sh>`_ script. Execute the script. This will download ``flof`` and ``pyFoam`` from the source code repositories.
2. The file ``env_setup.sh`` is copied from src/tools/env_setup.sh to the current directory if it doesn't exist. Customize the ``BASE`` variable to your needs (usually the directory where you have saved the script).
3. Each time you open a new shell session you need to execute env_setup.sh, add it to your .bashrc resp. if you want. Upgrade flof and pyFoam to the latest version by executing ``download_flof.sh``. For OpenFOAM execution it must be initialized correctly.

