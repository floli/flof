import unittest

import filecmp, os, shutil, subprocess

    

class TestRun(unittest.TestCase):
    root_target = "cavity.target"
    root_gold = "cavity.reference"

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root_target)

        
    def test_01_run(self):
        os.chdir("./run_test.data")
        ret_code = subprocess.call(["flof.py", "cavity.conf"])
        self.assertEqual(ret_code, 0)


    def test_filecompare(self):
        """ Compares each file of target case with a gold case. """
        cmp = filecmp.dircmp(self.root_gold, self.root_target, ignore=[])
        self.recursive_dircmp(cmp)

        
    def recursive_dircmp(self, cmp):
        ok_diff = ['Decomposer.logfile', 'PyFoamHistory', 'PyFoamRunner.icoFoam.logfile',
                   'PyFoamServer.info', 'PyFoamState.LastOutputSeen',
                   'PyFoamState.StartedAt', 'case.pfcb', 'pickledPlots', 'pickledData',
                   'Reconstruct', 'CasebuilderWorker', 'FoamRunner', 'Decompose']

        self.assertEqual(cmp.left_list, cmp.right_list)
        
        diff_files = cmp.diff_files
        for f in ok_diff:
            if f in diff_files:
                diff_files.remove(f)
        self.assertEqual(diff_files, [])

        for dir in cmp.subdirs.values():
            self.recursive_dircmp(dir)

            

if __name__ == '__main__':
    unittest.main()
