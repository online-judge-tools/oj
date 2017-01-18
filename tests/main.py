#!/usr/bin/env python3
import unittest

import subprocess
import glob
import os.path
import sys
import shutil
import time

class MainTest(unittest.TestCase):
    def test_main(self):
        cwd = os.getcwd()
        ojtools = os.path.join( cwd, 'oj' )
        for name in glob.glob('**/md5.sum', recursive=True):
            os.chdir(os.path.dirname(name))
            with open('url') as fh:
                url = fh.read().rstrip()
            with open('md5.sum') as fh:
                md5sum = fh.read()
            if os.path.exists('custom.sh'):
                cmds = [ 'env', 'MAIN=' + ojtools, 'bash', 'custom.sh' ]
            else:
                cmds = [ ojtools, 'download', url ]
            if os.path.exists('test'):
                shutil.rmtree('test')
            subprocess.check_call(cmds, stdout=sys.stdout, stderr=sys.stderr)
            result = subprocess.check_output([ 'md5sum' ] + sorted(glob.glob('test/*'))).decode()
            assert md5sum == result
            os.chdir(cwd)
            time.sleep(1)

if __name__ == '__main__':
    unittest.main()
