flof.py
=======
``flof.py`` is the work horse of the program suite. It takes a configuration file and executes the workers.


Command line arguments
----------------------
.. program:: flof.py

.. cmdoption:: -c <file>, --config <file>

    Configuration file that describes the case to work on.

.. cmdoption:: -f <pfcbfile>, --file <pfcbfile>

    Save the pyFoamCaseBuilder file to the given location and exit

.. cmdoption:: -n, --no-run

    Do not run the case. The run must be initiated through the XML-RPC method run(). This option is for internal use.

.. cmdoption:: -h, --help

    Display help on the command line arguments.

    
Control Server
--------------
For working together with ``flofqueue.py`` ``flof.py`` starts up a XML-RPC Server.

.. autoclass:: flof.ControlServer
   :members:
   :undoc-members:

