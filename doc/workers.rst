Workers
=======
Workers provide independent functionality which can be combined to a workflow. All included workers are derived from the :class:`~workers.baseworker.Baseworker`. 

Each worker posseses a context that is inherited. The context is a Python dictionary. It is used when doing string interpolation and modifies certain workers behavior.

String Interpolation
--------------------
String Interpolation as described in the `Python Documentation <http://docs.python.org/library/string.html#format-string-syntax>`_. In short, a string ``Hallo {Ort}!`` and a ``context = { "Ort" : "Welt" }`` will result in a replacement ``Hallo Welt!``. This replacement is done in all attributes and text of tags, but in not the tag name. There a some names used in the context which are reserved for internal use, they can, however be used for string interpolation. Changing them will usually result in undesired behavior.

name
  The name of the case, given in ``<case name=...>``.

mpi_command
  The command used to execute solvers in parallel. For example ``mpirun -n {numProc} {command} -parallel``. ``numProc`` and ``command`` are placeholders for string interpolation.

local
  foo bar



RootWorker
----------
.. autoclass:: workers.workers.RootWorker
    :members:
    :undoc-members:


CaseWorker
----------
.. autoclass:: workers.workers.Case
    :members:
    :undoc-members:


CaseCreator
-----------
.. autoclass:: workers.casecreator.CaseCreator
    :members:
    :undoc-members:

Decomposer
----------
.. autoclass:: workers.foamutility.Decomposer
    :members:
    :undoc-members:

PotentialFoam
-------------
.. autoclass:: workers.workers.PotentialFoam
    :members:
    :undoc-members:

Solver
----------
.. autoclass:: workers.foamutility.Solver
    :members:
    :undoc-members:

FoamUtility
-----------
.. autoclass:: workers.foamutility.FoamUtility
    :members:
    :undoc-members:

ReconstructCase
---------------
.. autoclass:: workers.foamutility.ReconstructCase
    :members:
    :undoc-members:

ExternalCommand
---------------
.. autoclass:: workers.workers.ExternalCommand
    :members:
    :undoc-members:

