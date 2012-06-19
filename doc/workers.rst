workers
=======
Workers provide independent functionality which can be combined to a workflow. All included workers are derived from the :class:`~workers.baseworker.Baseworker`. Configuration options common to all workers are:

class
   Must be set. Sets the class that implements the worker.

do
   Defaults to ``True``. Enable/disable execution of that worker.

position
   Default is worker dependent. Execution order position.

case
   Case to work on. Is used by most workers. Since usually all workers in a configuration file work on the same case this is set in the ``[DEFAULT]`` section. See :doc:`configuration`.

log
   Defaults to ``True``. Write a logfile to the ``log`` inside the case.




.. automodule:: workers.baseworker
   :members:
   :undoc-members:

.. automodule:: workers.workers
   :members:
   :undoc-members:

.. automodule:: workers.casebuilder
   :members:
   :undoc-members:

.. automodule:: workers.foamutility
   :members:
   :undoc-members:
