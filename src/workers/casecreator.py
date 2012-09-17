import ast, os, re, shutil
from os.path import join

from PyFoam.RunDictionary.ParsedParameterFile import ParsedBoundaryDict, WriteParameterFile
import common
from baseworker import BaseWorker
from common import norm_path


_OF_dimensions = {
    "U" : "[0 1 -1 0 0 0 0]",
    "p" : "[0 2 -2 0 0 0 0]"
    }


class CaseCreator(BaseWorker):

    def _copy_rec(self, rel_dir, dir_node):
        src_dir = norm_path(self.config.attrib["template"], rel_dir)
        target = join(self.case, rel_dir)
        for f in os.listdir(src_dir):
            if os.path.isfile(join(src_dir, f)):
                for tag in dir_node.findall("./file"):
                    if re.match(tag.attrib["name"], f):
                        try:
                            os.makedirs(target)
                        except OSError:
                            pass # Directory already exists
                        self.logger.debug("Copy file from  %s to %s"  % (join(src_dir, f), join(target,f )))
                        shutil.copy( join(src_dir, f), join(target, f) )
            elif os.path.isdir(join(src_dir, f)):
                for tag in dir_node.findall("./directory"):
                    if re.match(tag.attrib["name"], f):
                        self._copy_rec( os.path.join(rel_dir, f), tag)
        
                                               
        
    
    def copy_files(self):
        files_tag = self.config.find("files")
        self._copy_rec("", files_tag)


    def create_mesh(self):
        if self.config.find("./mesh/fluent") is not None:
            tag = self.config.find("./mesh/fluent")
            mesh = norm_path(tag.attrib["mesh"])
            cmd = "fluentMeshToFoam -case %s %s %s" % (self.case, tag.get("arguments", ""), mesh)
            self.logger.info("Creating mesh from fluent mesh file %s", mesh)
            self.start_process(cmd)
        elif self.config.find("./mesh/copy") is not None:
            tag = self.config.find("./mesh/copy")
            src_case = norm_path(tag.get("source", self.config.attrib["template"]))
            time = tag.get("time", "constant")
            src_path = join(src_case, time, "polyMesh")
            self.logger.info("Copy mesh from %s", src_path)
            shutil.copytree(src_path, join(self.case, "constant/polyMesh"))


    def create_BCs(self):
        self.logger.info("Creating the mesh from XML fields description.")
        mesh_BCs = ParsedBoundaryDict(join(self.case, "constant/polyMesh/boundary"))
    
        os.mkdir(join(self.case, "0"))
        for field in self.config.findall("./fields/field"):
            field_name = field.attrib["name"]
            field_file = WriteParameterFile(join(self.case, "0", field_name))
            field_file.content["internalField"] = "uniform " + field.find("./ic").attrib["value"]
            field_file.content["dimensions"] = _OF_dimensions[field_name]
            boundaryField = {}
            for mesh_BC in mesh_BCs:  
                for BC_pattern in field.findall("./bc"):
                    if re.match(BC_pattern.attrib["pattern"], mesh_BC):
                        boundaryField[mesh_BC] = { "type" : BC_pattern.attrib["type"] }
                        value = ast.literal_eval("{" + BC_pattern.attrib.get("parameters", "") + "}")
                        boundaryField[mesh_BC].update(value)
                        break
                        
            field_file["boundaryField"] = boundaryField
            field_file.writeFile()


    def copy_0_time(self):
        template = norm_path(self.config.attrib["template"])
        node = self.config.find("./zeroTime")
        timestep = node.attrib.get("timestep", "0")
        if timestep == "latestTime":
            casedirs = []
            for d in [i for i in os.listdir(template) if os.path.isdir(i) ]:
                try:
                    casedirs.append(float(d))
                except ValueError:
                    pass
            timestep = max(casedirs)

        src = join(template, timestep)
        self.logger.info("Copy 0 timestep from %s", src)
        os.mkdir(join(self.case, "0"))
        for f in os.listdir(src):
            shutil.copy( join(src, f), join(self.case, "0") )

            

    def run(self):
        if os.path.isdir(self.case):
            if common.getboolean(self.config.get("overwrite", True)):
                shutil.rmtree(self.case)
            else:
                raise WorkerError("Case directory %s exists and overwrite == False" % self.case)
                                     

        self.copy_files()
        self.create_mesh()

        # There are two methods to create the boundary conditions. Either copy them from a zero time
        # directory of the template or create them from a <fields> node. These methods a mutually exclusice
        # The first encontered tag is used, the other one discarded.
        for tag in self.config:
            if tag.tag == "zeroTime":
                self.copy_0_time()
                break
            if tag.tag == "fields":
                self.create_BCs()
                break
            

