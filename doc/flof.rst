flof.py
=======
``flof.py`` is the work horse of the program suite. It takes a configuration file and executes the workers.


Command line arguments
----------------------
``flof.py [options] configfile``

Options are:

.. program:: flof.py CONFIG

.. cmdoption:: -o <workers>, --only=<workers>

   Execute only the given workers, seperated by comma.

.. cmdoption:: -not <workers>, --not=<workers>

    Do not execute the given workers, seperated by comma.

.. cmdoption:: -h, --help

    Display help on the command line arguments.
