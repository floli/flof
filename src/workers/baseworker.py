import logging, os, shlex, subprocess, sys
import xml.etree.ElementTree as ET
logger = logging.getLogger(__name__)

import common
from common import norm_path


class WorkerRegistry():
    """ Central registry. All workers need to register before they can be used from a configuration file. """

    workers = {}
    
    @classmethod
    def register(self, tagname, cls):
        """ Register a worker with a tagname and a corresponding class. """
        logger.debug("Registered worker, tag: %s, class: %s", tagname, cls)
        self.workers[tagname] = cls

    
class WorkerFactory():
    def __init__(self, config, context = None):
        self.conf_root = config.getroot()
        if context is None: # You should not use context={} as default value
            context = {}
            
        self.context = context

    def workers(self):
        """ Yields all workers in order of the XML file, even if they are not activated. """
        workers = WorkerRegistry.workers
        for node in self.conf_root:
            if node.tag in workers:
                conf_etree = ET.ElementTree(node)
                cls = workers[node.tag]
                obj = cls(conf_etree, self.context)
                yield obj


    def execute(self):
        """ Executes all workers. """
        for w in self.workers():
            if w.do():
                w.run()


class WorkerError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

    
class BaseWorker():
    """ Base Class for all workers. """

    _do_recursive_string_interpolation = True
        
    def __init__(self, configuration, context):
        # The directory to the case. The is no guarantee it actually exists, e.g. when it is created by the CaseBuilder.
        self.context = context
        self.config = configuration.getroot()
        self.do_string_interpolation(recurse=self._do_recursive_string_interpolation)
        if "name" in context:
            self.case = norm_path(context["name"])
        else:
            self.case = None
    
        # Setup logging: Add an additional handler for worker based logfiles
        self.logger = logging.getLogger(self.__class__.__module__ + "." + self.__class__.__name__ )
        if self._logfilename():
            handler = logging.FileHandler(self._logfilename())
            handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s:%(levelname)s - %(message)s"))
            self.logger.addHandler(handler)
            
        
    def do(self):
        """ Returns the do attribute. """
        return common.getboolean(self.config.get("do", "True"))
    

    def abort(self):
        """ If a subprocess is alive, kill it. """
        try:
            if not self.popen.poll():
                self.popen.kill()
                self.logger.warning("Killing subprocess of worker %s.", self.name)
        except AttributeError:
            pass
        

    def start_process(self, command, no_shlex=False, raise_excpt=True, print_output = True, **kwargs):
        """ Starts a new subprocess using cmd. Saves it to abort it later.
        no_shlex=True to avoid shlex.split, e.g. for executing through a shell.
        raise_excpt if a WorkerError exception should be raised on a return code != 0 """
        cmd = command if no_shlex else shlex.split(command)

        # Use an additional logger without formatting for process output. 
        proclog = logging.getLogger(self.config.tag)
        proclog.propagate = False # Process output should not propagate to the main logger
        proclog.setLevel(logging.INFO)
        logfile = self._logfilename()

        if logfile:
            proclog.addHandler(logging.FileHandler(logfile))
            
        if print_output:
            proclog.addHandler(logging.StreamHandler(sys.stdout))

        self.popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=0, **kwargs)
        while True:
            output = self.popen.stdout.readline().decode()
            if output == "" and self.popen.poll() != None:
                break
            proclog.info(output.rstrip("\n"))
                            
        ret_code = self.popen.returncode

        self.logger.debug("%s returned with %i", command, ret_code)        

        if ret_code != 0 and raise_excpt:
            raise WorkerError("%s returned with a non-zero exit code %i" % (cmd, ret_code))
        else:
            return ret_code

    def _logfilename(self):
        """ Returns a path for the case log file. Creates it, if not already existing. """
        if not common.getboolean(self.config.get("log", True)) or self.case is None:
            return None
                                     
        logfile = norm_path(self.case, "log/", self.config.tag)
        try:
            os.makedirs(os.path.dirname(logfile))
        except OSError:
            pass
        return logfile
        
    def info(self):
        """ Returns a dictionary of arbitrary information that is displayed. """
        if self.name == "":
            return {}
        else:
            return {"name" : self.name}

        
    def pretty_print(self):
        """ Prints some formatted info on that worker. """
        print ET.tostring(self.config) # Well, not exactly pretty, but better than nothing

    def do_string_interpolation(self, recurse=True):
        """ Replace all strings like {U} with the value from the context dictionary if it exists. Workers that can have subworkers should not recurse. """
        if recurse:
            selection = ".//*"
        else:
            selection = "."

        for n in self.config.findall(selection):
            try: n.text = n.text.format(**self.context)
            except (AttributeError, KeyError): pass
            for a in n.attrib:
                try: n.attrib[a] = n.attrib[a].format(**self.context)
                except KeyError: pass
                
        


import casecreator, foamutility, workers

def register_bundled_workers():
    """ Registers the workers that are bundled with flof at the WorkerRegistry. """
    WorkerRegistry.register("case", workers.Case)
    WorkerRegistry.register("variation", workers.Variation)    
    WorkerRegistry.register("create", casecreator.CaseCreator)
    WorkerRegistry.register("solve", foamutility.Solver)
    WorkerRegistry.register("decompose", foamutility.Decomposer)
    WorkerRegistry.register("report", workers.Report)
