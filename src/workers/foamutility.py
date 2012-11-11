import common
from baseworker import BaseWorker

import os, re


class FoamRunner(BaseWorker):
    """ Base class for workers that run a OpenFOAM application. Provides methods to get decomposition and the MPI run command. """
    
    def num_proc(self):
        regexp = "processor[0-9]*"
        count = 0
        for d in os.listdir(self.case):
            if re.match(regexp, d):
                count += 1

        return count

    def time(self):
        """ Returns the time argument for the utility. """
        
        if "time" not in self.config.attrib:
            time = ""
        elif self.config.attrib["time"] == "latestTime":
            time = "-latestTime"
        else:
            time = "-time %s" % self.config.attrib["time"]

        return time

    def cmd(self, args = ""):
        """ Construct the commandl line, including MPI run command, additional args can be supplied as a string. """
        cmd = self.config.attrib["name"]
        cmd += " -case %s" % self.case
        cmd += " " + args
        
        if common.getboolean(self.config.get("parallel", True)):
            num_proc = self.num_proc()
        else:
            num_proc = 0

        if num_proc > 0:
            cmd = self.context["mpi_command"].format(numProc=num_proc, command=app)

        return cmd

        
    

class Solver(FoamRunner):
    """ Solve the case using an OpenFOAM solver. Runs in parallel if the case is decomposed and ``parallel`` is set.

    ::

      <solve name="simpleFoam" parallel="True" />

    ``parallel`` defaults to ``True``.
    """


    def run(self):
        print self.start_process(self.cmd())


from PyFoam.RunDictionary.ParsedParameterFile import WriteParameterFile

class Decomposer(BaseWorker):
    """ Decomposes the case for computation on multiple processors.

    ::

      <decompose n="2" method="simple">
        <n>(2 1 1)</n>
        <delta>0.001></delta>
      </decompose>

    All childen, e.g. n, delta are added to the corresponding Coeffs dictionary..
    """
        
    def run(self):
        method = self.config.attrib["method"]
        n = self.config.attrib["n"]
        self.logger.info("Decomposing case for %s domains using method %s.", n, method)
        decomposeParDict = WriteParameterFile(os.path.join(self.case, "system/decomposeParDict"), createZipped=False)
        decomposeParDict["method"] = method
        decomposeParDict["numberOfSubdomains"] = n
        coeffs = {}
        for i in self.config:
            coeffs[i.tag] = i.text
            
        decomposeParDict[method + "Coeffs"] = coeffs
        decomposeParDict.writeFile()

        self.start_process("decomposePar -case %s" % self.case)
        
    
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





class FoamUtility(FoamRunner):
    """ Executes standard OpenFOAM utilities for post-processing.

    ::

      <utility name="wallShearStress" time="latestTime" parallel="true" />

    ``parallel`` defaults to ``True``. 
    """

    def run(self):
        self.logger.info("Running %s utility", self.config.attrib["name"])
    
        
        cmd = self.cmd(self.time())

        self.start_process(cmd)
        


class Reconstruct(FoamRunner):
    """ Reconstructs a case. Usually executed at the very end.

    ::

      <reconstruct time="100" />
    """

    def run(self):
        self.logger.info("Reconstructing case")
        if self.num_proc() == 0:
            self.logger.warning("Case not decomposed, skipping reconstruct.")
            return
        
        cmd = "reconstructPar %s -case %s" % (self.time(), self.case)

        self.start_process(cmd)
