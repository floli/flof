pfcbcreator
===========
``pfcbcreator.py`` is a small helper tool that creates a pyFoamCaseBuilder (PFCB) file for a given case. This file can be taken as a starting point for grouping the boundary conditions.

Command line arguments
----------------------
``pfcbcreator.py [options] case pfcbfile``

Options are:

.. program:: pfcbcreator.py

.. cmdoption:: -t <timestep>, --timestep=<timestep>

    Timestep to take the boundary condition from. Defaults to 0.

.. cmdoption:: -v <variable>, --variable=<variable> 

    Variable to take boundary information form. Defaults to U.

Code
----
.. automodule:: pfcbcreator
   :members:
   :undoc-members:

