import os, re, shutil
from os.path import join

from baseworker import BaseWorker
from common import norm_path


class CaseCreator(BaseWorker):

    def _copy_rec(self, rel_dir, dir_node):
        src_dir = norm_path(self.config.attrib["template"], rel_dir)
        target = join(self.case, rel_dir)
        for f in os.listdir(src_dir):
            if os.path.isfile(join(src_dir, f)):
                for tag in dir_node.findall("./file"):
                    if re.match(tag.attrib["name"], f):
                        print "COPY FROM %s TO %s"  % (join(src_dir, f), join(target,f ))
                        try:
                            os.makedirs(target)
                        except OSError:
                            pass # Directory already exists
                        shutil.copy( join(src_dir, f), join(target, f) )
            elif os.path.isdir(join(src_dir, f)):
                for tag in dir_node.findall("./directory"):
                    if re.match(tag.attrib["name"], f):
                        self._copy_rec( os.path.join(rel_dir, f), tag)
        
                                               
        
    
    def copy_files(self):
        files_tag = self.config.find("files")
        self._copy_rec("", files_tag)


    def run(self):
        self.copy_files()
