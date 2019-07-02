import argparse
import hashlib
import os
import subprocess
import sys

import tests.utils

import onlinejudge._implementation.utils as utils
from onlinejudge._implementation.command.download import download


def get_files_from_json(samples):
    files = {}
    for i, sample in enumerate(samples):
        for ext in ('in', 'out'):
            if 'name' in sample:
                name = sample['name'] + '.' + ext
            else:
                name = 'sample-{}.{}'.format(i + 1, ext)
            files[name] = hashlib.md5(sample[ext + 'put'].encode()).hexdigest()
    return files


def snippet_call_download(self, url, files, is_system=False, is_silent=False, type='files'):
    assert type in 'files' or 'json'
    if type == 'json':
        files = get_files_from_json(files)

    ojtools = os.path.abspath('oj')
    with tests.utils.sandbox([]):
        cmd = [ojtools, 'download', url]
        if is_system:
            cmd += ['--system']
        if is_silent:
            cmd += ['--silent']
        subprocess.check_call(cmd, stdout=sys.stdout, stderr=sys.stderr)
        result = {}
        if os.path.exists('test'):
            for name in os.listdir('test'):
                with open(os.path.join('test', name)) as fh:
                    result[name] = hashlib.md5(fh.buffer.read()).hexdigest()
        self.assertEqual(files, result)


def snippet_call_download_raises(self, expected_exception, url, is_system=False, is_silent=False):
    args = argparse.Namespace(url=url, system=is_system, silent=is_silent, format=None, directory=None, dry_run=True, cookie=utils.default_cookie_path)
    with self.assertRaises(expected_exception):
        download(args)
