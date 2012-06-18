import logging, os, shlex, subprocess, sys
import common
from common import norm_path

logger = logging.getLogger(__name__)


class WorkerError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

    
class BaseWorker():
    """ Base Class for all workers. Workers not inherited from BaseWorker will not be executed. """
    
    defaults = {}

    def __init__(self, name, configuration, properties=None):
        self.name = name
        self.config = {}

        # Read in default values from derived classes.
        self.config.update(self.defaults)
        
        self.config.update(configuration)

        # The directory to the case. The is no guarantee it actually exists, e.g. when it is created by the CaseBuilder.
        self.case = norm_path(self.config["case"])
        self.properties = properties

        # Setup logging: Add an additional handler for worker based logfiles
        self.logger = logging.getLogger(self.__class__.__module__ + "." + self.__class__.__name__ )
        if self._logfilename():
            handler = logging.FileHandler(self._logfilename())
        else:
            handler = logging.NullHandler() # 
            
        handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s:%(levelname)s - %(message)s"))
        self.logger.addHandler(handler)
        
    def do(self):
        """ Returns the do key of the config section. """
        return bool(self.config["do"])
    

    def abort(self):
        """ If a subprocess is alive, kill it. """
        try:
            if not self.popen.poll():
                self.popen.kill()
                self.logger.warning("Killing subprocess of worker %s.", self.name)
        except AttributeError:
            pass
        

    def start_subproc(self, command, no_shlex=False, raise_excpt=True, print_output = True, **kwargs):
        """ Starts a new subprocess using cmd. Saves it to abort it later.
        no_shlex=True to avoid shlex.split, e.g. for executing through a shell.
        raise_excpt if a WorkerError exception should be raised on a return code != 0 """

        cmd = command if no_shlex else shlex.split(command)

        # Use an additional logger without formatting for process output. 
        proclog = logging.getLogger(self.name)
        proclog.propagate = False # Process output should not propage to the main logger
        logfile = self._logfilename()
        if logfile == None:
            proclog.addHandler(logging.NullHandler())
        else:
            proclog.addHandler(logging.FileHandler(self._logfilename()))

        if print_output:
            proclog.addHandler(logging.StreamHandler())
            
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
        """ Returns a path for the log file. Creates it, if not already existing. """
        if not common.getboolean(self.config["log"]):
            return None
                                     
        logfile = norm_path(self.case, "log/", self.name)
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


        
