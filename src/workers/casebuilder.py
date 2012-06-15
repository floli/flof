import os, re, shutil, tempfile
from os.path import join
from xml.etree import ElementTree

from baseworker import BaseWorker
from common import norm_path

from PyFoam.Applications.CaseBuilder import CaseBuilder


class Casebuilder(BaseWorker):
    """ Worker that creates the actual case from a template using pyFoamCaseBuilder. """
    
    position = 500

    defaults = {"mesh_arguments":"", "overwrite":True}

    def mesh_prep(self, pfcb_etree):
        """ Fills in the mesh preparation method in the pfcb file. """
        method = self.config["mesh_method"]
        if method == "spider":
            spider = Spider({"configuration": self.config["mesh"]})
            mesh = spider.output_file
        else:
            mesh = self.config["mesh"]
            
        args = self.config["mesh_arguments"]
                    
        meshprep = pfcb_etree.find("meshpreparation")
        if meshprep == None:
            meshprep = ElementTree.SubElement(pfcb_etree.getroot(), "meshpreparation")
        else:
            meshprep.clear()

        if method == "fluent":
            meshprep.attrib["mode"] = "utility"
            utility = ElementTree.SubElement(meshprep, "utility")
            utility.attrib["command"] = "fluentMeshToFoam"
            utility.attrib["arguments"] = mesh + " " + args
        elif method == "copy":
            copy = ElementTree.SubElement(meshprep, "copy")
            copy.attrib["template"] = mesh

            
    def create_pfcb(self, f, template_dir):
        """ Creates the pyFoamCaseBuilder control file from the template. """
        self.logger.info("Creating pyFoamCaseBuilder control file %s", f.name)
        pfcb_etree = ElementTree.ElementTree()
        pfcb_etree.parse(self.config["casebuilder_template"])

        pfcb_etree.getroot().attrib["template"] = template_dir
        self.mesh_prep(pfcb_etree)

        pfcb_etree.write(f)
        f.flush()


    def run_pfcb(self, pfcb_file):
        """ Runs the pyFoamCaseBuilder. """
        self.logger.info("Creating case.")

        args = pfcb_file.name + " " + self.case
        if self.config["overwrite"]:
            args += " --force"
        self.logger.debug("Running pyFoamCaseBuilder with %s" % args)
        CaseBuilder(args=args)

        # Copy the pyFoamCaseBuilder file to the case we just have created
        shutil.copy(pfcb_file.name, norm_path(self.case, "case.pfcb"))

    def partial_match(self, lst, expr):
        """ Finds all elements in l that start with expr. Returns the element if the match in unique. """
        matches = [ i for i in lst if i.startswith(expr) ]
        if len(matches) == 1:
            return matches[0]

    def cp_case_to_tmp(self, target_dir):
        """ Copies the template case to a temp directory, files are being renamed:
        - Do not match the regular expression: no rename, just copy.
        - Match the regexp but section and key do not exist in config: file is discarded. (this may be open to dispute)
        - Match the regexp, section and key exist but value is not equal: file is discarded
        - Match the regexp, section and key exist, value is equal: file is renamed to the basename (first subgroup of the regexp) and copied.

        Possible problem: A file is copied twice, first if no match, just the plain file.
        Second if a match and valid key/value exist. This probably won't cause a problem,
        because of the alphabetic ordering. But keep it in mind!
        """

        regexp = re.compile(r"(.+)\.(.+)\.(.+)\.(.+)")
        case_template = self.config["case_template"]
        configuration = self.properties["configuration"]

        for path, dirs, files in os.walk(case_template):
            for f in files:
                cp_target = ""
                match = regexp.match(f)
                if match:
                    base_filename, section, key, value = match.group(1, 2, 3, 4)
                    section = self.partial_match(configuration.sections(), section)
                    if section:
                        key = self.partial_match([i[0] for i in configuration.items(section)], key)
                        if key:
                            if configuration.get(section, key) == value:
                                # Pattern and condition matched, file will be copied and renamed.
                                self.logger.debug("Selecting file: %s --> %s", f, base_filename)
                                cp_target = base_filename
                else:
                     # No special action: file will be copied as it is.
                    cp_target = f

                if cp_target:
                    dest_dir = join(target_dir, os.path.relpath(path, case_template))
                    if not os.path.isdir(dest_dir):
                        os.makedirs(dest_dir)
                    shutil.copy(join(path, f), join(dest_dir, cp_target)) # Create dir



    def _logfilename(self):
        """ Returns a temporary filename since the case directory does not necessarily exists
        when executing this worker. Save the file for moving it """
        self.tmplog = tempfile.NamedTemporaryFile()
        return self.tmplog.name


    def __del__(self):
        # logfile = super(Casebuilder, self)._logfilename()
        logfile = BaseWorker._logfilename(self)
        # logfile = norm_path(self.case, "log/", self.name)
        # try:
        #     os.makedirs(os.path.dirname(logfile))
        # except OSError:
        #     pass
        shutil.copyfile(self.tmplog.name, logfile)
    
                  
    def run(self):
        os.chdir(os.path.dirname(self.properties["configuration"].case_config))
        pfcb_target = tempfile.NamedTemporaryFile()
        template_dir = tempfile.mkdtemp()
        self.cp_case_to_tmp(template_dir)
        
        
        self.create_pfcb(pfcb_target, template_dir)
        self.run_pfcb(pfcb_target)

        self.logger.debug("Cleaning up temporary directory: %s", template_dir)
        shutil.rmtree(template_dir)

 
