import ConfigParser, os, shutil

import xml.etree.ElementTree as ET


import common
from baseworker import BaseWorker, WorkerError, WorkerFactory
from common import norm_path

class RootWorker(BaseWorker):
    """ A worker that just adds its attributes to the context so they can be evaluated by sub workers.
    that are run in a WorkerFactory loop. This worker is usually called directly.

    Example configuration:

    ::

      <flof loglevel=10
            mpi_command = "mpirun -n {numProc} {command} -parallel">
      </flof>     
    """
    
    def __init__(self, configuration, context):
        context.update(configuration.getroot().attrib)
        self._do_recursive_string_interpolation = False
        BaseWorker.__init__(self, configuration, context)
        assert(self.config.tag == "flof")
        

    def run(self):
        """ Runs its subworkers. """
        wf = WorkerFactory(ET.ElementTree(self.config), self.context)
        wf.execute()


class Case(BaseWorker):
    """ Mostly a container class that contains subworkers that operate on a case. Runs its subworkers.
    The ``name`` attribute is added to the context which contains the corresponding attribute. If you need to have the full path to the case, use the self.case attibute (set in BaseWorker).

    Example Configuration:

    ::

      <case name="new_case">
      </case>
    """
    
    def __init__(self, configuration, context):
        self._do_recursive_string_interpolation = False
        BaseWorker.__init__(self, configuration, context)
        self.context["name"] = configuration.getroot().attrib["name"]

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
   
            
        
class ExternalCommand(BaseWorker):
    """Executes an external command.

    ::

      <external fail_on_error="True" command="ls -1 {name}" />

    command
        Command to be executed.

    fail_on_error
        If True the worker fails if command returns a non-zero exitcode. Defaults to True.
    """
    
    @property
    def cmd(self):
        """ Returns the command from the configuration. """
        return self.config.attrib["command"]
 

    def run(self):
        fail_on_error = common.getboolean(self.config.get("fail_on_error", True))
        ret_code = self.start_process(self.cmd, no_shlex=True, raise_excpt=fail_on_error, shell=True)
        self.logger.info("External command %s return with %s.", self.cmd, ret_code)
        
    
                
class Variation(BaseWorker):
    def __init__(self, configuration, context):
        self._do_recursive_string_interpolation = False
        BaseWorker.__init__(self, configuration, context)
    
    def run(self):
        # Since the workers are modifying the configuration tree when doing the string interpolation
        # we save it as a string and replay it each iteration.
        original_node = ET.tostring(self.config)
        var_name = self.config.attrib["variable"]
        var_range = eval(self.config.attrib["range"])
        self.logger.info("Starting variation loop, variable: %s, range: %s", var_name, var_range)
        wd = os.getcwd()
        for var in var_range:
            ctx = self.context
            ctx.update( {var_name : var} )
            self.logger.info("Doing variation, variable: %s, value: %s", var_name, var)
            os.chdir(wd)
            wf = WorkerFactory(ET.ElementTree(self.config), self.context)
            wf.execute()
            self.config = ET.fromstring(original_node)
            




class Report(BaseWorker):
    def run(self):
        os.mkdir(os.path.join(self.case, "report"))
        report = os.path.join(self.case, "report", "FullReport.txt")
        cmd = "pyFoamCaseReport.py --full-report %s > %s" % (self.case, report)
        self.start_process(cmd, no_shlex=True, shell=True)

        for output in self.config.findall("./output"):
            try:
                send = output.attrib["send"]
            except KeyError:
                send = None
            if output.attrib["format"] == "html":
                self.html_output(report, send)
            
                

    def html_output(self, input, send = None):
        """ Generate HTML output. Needs the rst2html2 utility. """
        output = input.rsplit(".")[0] + ".html"
        cmd = "rst2html2 %s %s" % (input, output)
        self.start_process(cmd)
                    

        
                 
