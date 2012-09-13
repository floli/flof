import common
from baseworker import BaseWorker

import os, re 

class Solver(BaseWorker):
    def num_proc(self):
        regexp = "processor[0-9]*"
        count = 0
        for d in os.listdir(self.case):
            if re.match(regexp, d):
                count += 1

        return count


    def run(self):
        solver = self.config.attrib["name"]
        import pdb; pdb.set_trace() 
        if common.getboolean(self.config.get("parallel", True)):
            num_proc = self.num_proc()
            cmd = "mpirun -n %s %s -parallel" % (num_proc, solver)
        else:
            cmd = solver

        print cmd

        
    
import tempfile

class ChangeDictionary(BaseWorker):
    def run(self):
        changes = self.config.text
        tmp = tempfile.NamedTemporaryFile()
        tmp.write(changes)
        tmp.flush()
        args = self.config.get("args", "")
        import pdb; pdb.set_trace() 

        cmd = "changeDictionary -case %s %s -dict %s" % (self.case, args, tmp.name)
        self.start_process(cmd)





class FoamUtility(BaseWorker):
    """ Executes standard OpenFOAM utilities for post-processing.

    Configuration options are:
    
    utility
        The utility to run.

    time
        Optional, run for a specific timestep. Can be either a timestep or latestTime.

    parallel
        Autosense a decomposed case and run in parallel. Defaults to True.
    """

    position = 1000

    defaults = {"parallel":True}

    
    def run(self):
        self.logger.info("Running %s FOAM utility", self.config["utility"])
        if "time" not in self.config:
            time = ""
        elif self.config["time"] == "latestTime":
            time = "-latestTime"
        else:
            time = "-time %s" % self.config["time"]

        if common.getboolean(self.config["parallel"]):
            parallel = "--autosense-parallel"
        else:
            parallel = ""
        
        cmd = "pyFoamRunner.py %s %s %s -case %s" % (parallel, self.config["utility"], time, self.case)

        self.start_subproc(cmd)
        


class ReconstructCase(BaseWorker):
    """ Reconstructs a case. Usually executed at the very end.

    Configuration options are:

    time
        Optional, reconstruct specific timestep or latestTime
    """

    position = 1100

    def run(self):
        if "time" not in self.config:
            time = ""
        elif self.config["time"] == "latestTime":
            time = "-latestTime"
        else:
            time = "-time %s" % self.config["time"]

        cmd = "reconstructPar %s -case %s" % (time, self.case)

        self.start_subproc(cmd)
