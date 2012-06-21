Configuration
=============
``flof`` uses a Unix-style configuration format. It consists of named sections with key/value pairs::

    [section]
        key = value

A special section called ``[DEFAULT]`` exists which sets default values for all other sections. For a more complete reference, see the Python `ConfigParser <http://docs.python.org/library/configparser.html>`_ documentation.

Interpolation
-------------
:class:`~configuration.Configuration` inherits the string interpolation feature from Pythons ``SafeConfigParser`` and extends it. In addition to the original feature set you can reference values from other section using a ``section.key`` syntax::

    [Casebuilder]
        mesh = mymesh.msh
        # Reference value from same section or DEFAULT section:
        case_template = %(mesh)s.pfcb

    [ExternalCommand]
        # Reference value from the Casebuilder section above:
       	command = ls %(Casebuilder.mesh)s


Example configuration
---------------------
A full example configuration:

.. literalinclude:: example.conf



.. automodule:: configuration
   :members:
   :undoc-members:

