import ConfigParser, os, shutil

import xml.etree.ElementTree as ET


import common
from baseworker import BaseWorker, WorkerError, WorkerFactory
from common import norm_path

class RootWorker(BaseWorker):
    """ A worker that just add its attributes to the context so they can be evaluated by sub workers.
    that are run in a WorkerFactory loop. This worker is usually called directly.

    Example configuration:

    ::

      <flof loglevel=10
            mpi_command = "mpirun -n {numProc} {command} -parallel">
      </flof>     
    """
    
    def __init__(self, configuration, context={}):
        context.update(configuration.getroot().attrib)
        BaseWorker.__init__(self, configuration, context, recursive_string_interpolation=False)
        assert(self.config.tag == "flof")
        

    def run(self):
        """ Runs its subworkers. """
        wf = WorkerFactory(ET.ElementTree(self.config), self.context)
        wf.execute()


class Case(BaseWorker):
    """ Mostly a container class that contains subworkers that operate on a case. Runs its subworkers.
    The ``name`` attribute is added to the context.

    Example Configuration:

    ::

      <case name="new_case">
      </case>
    """
    
    def __init__(self, configuration, context):
        context.update( { "name" : configuration.getroot().attrib["name"] } )
        BaseWorker.__init__(self, configuration, context, recursive_string_interpolation=False)

    def run(self):
        """ Runs its subworkers. """
        wf = WorkerFactory(ET.ElementTree(self.config), self.context)
        wf.execute()

        
    


class Spider(BaseWorker):
    """ Worker that executes spider which meshes geometry data.

    overwrite
        Overwrite existing msh mesh file if it exists. Defaults to False.
    """
    
    position = 100

    defaults = {"overwrite":False}

    @property
    def output_file(self):
        """ Return the location of the spider output file, relative to its config file. """
        
        spider_conf = norm_path(self.config["configuration"])
        
        # Extract the output filename from the spider configuration,
        # assumes that the line after the keyword OUTFILENAME contains it.
        with open(spider_conf) as f:
            for line in f:
                if "OUTFILENAME" in line:
                    break

            return norm_path(os.path.dirname(spider_conf), f.next().strip())
        
        
    def run(self):
        spider_conf = norm_path(self.config["configuration"])

        if not self.config["overwrite"]:
            if os.path.isfile(self.output_file):
                self.logger.info("Spider output file %s exists, not recreating mesh.", self.output_file)
                return

        cmd = "spider " + spider_conf

        ret_code = self.start_subproc(cmd, cwd = os.path.dirname(spider_conf))       
   
            
        

class PotentialFoam(BaseWorker):
    """ Executes ``potentialFoam`` to generate inital values.

    Configuration options are:

    backup_0_to
        If given the worker performs a backup of the '0' dir to given location before running potentialFoam.

    overwrite
        Overwrite an already existing backup of the 0 directory.

    no_function_objects
        Corresponds to the -noFunctionObjects switch of potentialFoam. Omits execution of function objects.
    """

    position = 800

    defaults = {"overwrite":False, "backup_0_to":"", "no_function_objects":True}
    
    def backup_0_dir(self, target, overwrite):
        """ Does a backup of the directory 0 with the starting conditions before potentialFoam overwrites it. """
        target = norm_path(self.case, target)
        
        if os.path.isdir(target) and overwrite:
            self.logger.debug("Deleting directory %s.", target)
            shutil.rmtree(target)
        elif os.path.isdir(target) and not overwrite:
            # Directory exists but should not be overwritten.
            return

        self.logger.info("Backup 0 dir to %s.", target)
        shutil.copytree(norm_path(self.case, "0"), target)
       
        
    def run(self):
        backup_dir = self.config["backup_0_to"]
        if backup_dir == "":
            self.logger.debug("NOT doing backup of 0 before running potentialFoam.")
        else:
            self.backup_0_dir(backup_dir, self.config["overwrite"])

        no_f_objects = self.config["no_function_objects"] 

        cmd = "pyFoamRunner.py --autosense-parallel potentialFoam -case %s %s" % (self.case,  "-noFunctionObjects" if no_f_objects else "")

        self.start_subproc(cmd)


class ExternalCommand(BaseWorker):
    """ Executes an external command. No default position thus it must be specified in config.

    command
        Command to be executed.

    fail_on_error
        If True the worker fails if command returns a non-zero exitcode. Defaults to True.
    """
    
    defaults = {"fail_on_error":True}
        

    @property
    def cmd(self):
        """ Returns the command from the configuration. """
        return self.config["command"]
 

    def info(self):
        return {"name": self.name, "command": self.cmd}

    def run(self):
        fail_on_error = common.getboolean(self.config["fail_on_error"])

        ret_code = self.start_subproc(self.cmd, no_shlex=True, raise_excpt=fail_on_error, shell=True)
                              
    
                
class Variation(BaseWorker):
    def __init__(self, configuration, context):
        BaseWorker.__init__(self, configuration, context, False)
    
    def run(self):
        # Since the workers are modifying the configuration tree when doing the string interpolation
        # we save it as a string and replay it each iteration.
        original_node = ET.tostring(self.config)
        var_name = self.config.attrib["variable"]
        var_range = eval(self.config.attrib["range"])
        self.logger.info("Starting variation loop, variable: %s, range: %s", var_name, var_range)
        for var in var_range:
            ctx = self.context
            ctx.update( {var_name : var} )
            self.logger.info("Doing variation, variable: %s, value: %s", var_name, var)
            wf = WorkerFactory(ET.ElementTree(self.config), self.context)
            wf.execute()
            self.config = ET.fromstring(original_node)
            




