import common
from baseworker import BaseWorker

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
