import unittest

import sys
# Add the ptdraft folder path to the sys.path list
sys.path.append('..')
import exec_externals as ee


class TestExecExternalCommandWrapper(unittest.TestCase):
    """Simple test for class ExternalCommandWrapper"""

    def test_cmd_wo_args(self):
        """Test commands without arguments"""
        for command in ['cd', 'pwd', 'ls']:
            cmd = ee.ExternalCommandWrapper(cmd=command, verbose=True, shell=True)
            cmd.run()

    def test_cmd_w_args(self):
        """Test commands with arguments"""
        for command in ['latex', 'pdflatex', 'latexmk']:
            cmd = ee.ExternalCommandWrapper(cmd=command,
                                            cmd_args=['sample.tex'],
                                            verbose=True)
            cmd.run()


if __name__ == '__main__':
    unittest.main()

