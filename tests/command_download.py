import hashlib
import os
import unittest

import onlinejudge_command.subcommand.download as subcommand_download
import tests.utils
from onlinejudge_command.main import get_parser


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
    assert type in ('files', 'json')
    if type == 'json':
        files = get_files_from_json(files)

    with tests.utils.sandbox([]):
        args = ['download', url]
        if is_system:
            args += ['--system']
        if is_silent:
            args += ['--silent']
        tests.utils.run(args, check=True)
        result = {}
        if os.path.exists('test'):
            for name in os.listdir('test'):
                with open(os.path.join('test', name)) as fh:
                    result[name] = hashlib.md5(fh.buffer.read()).hexdigest()
        self.assertEqual(files, result)


def snippet_call_download_failure(self, url, is_system=False, is_silent=False):
    args = ["download", url]
    if is_system:
        args.append("--system")
    if is_silent:
        args.append("--silent")
    args = get_parser().parse_args(args=args)
    self.assertFalse(subcommand_download.run(args))


def snippet_call_download_twice(self, url1, url2, files, is_system=False, is_silent=False, type='files'):
    assert type in ('files', 'json')
    if type == 'json':
        files = get_files_from_json(files)

    with tests.utils.sandbox([]):
        args = ['download', url1]
        if is_system:
            args += ['--system']
        if is_silent:
            args += ['--silent']
        args = get_parser().parse_args(args=args)
        self.assertTrue(subcommand_download.run(args))

        args = ['download', url2]
        if is_system:
            args += ['--system']
        if is_silent:
            args += ['--silent']
        args = get_parser().parse_args(args=args)
        # download from url2 should be aborted.
        self.assertFalse(subcommand_download.run(args))

        # check download from url1 is not overwritten
        result = {}
        if os.path.exists('test'):
            for name in os.listdir('test'):
                with open(os.path.join('test', name)) as fh:
                    result[name] = hashlib.md5(fh.buffer.read()).hexdigest()
        self.assertEqual(files, result)


class DownloadTest(unittest.TestCase):
    """DownloadTest is a class to test `download` subcommand itself. Don't try to test sample parsers.
    """
    def snippet_call_download(self, *args, **kwargs):
        tests.command_download.snippet_call_download(self, *args, **kwargs)

    def snippet_call_download_failure(self, *args, **kwargs):
        tests.command_download.snippet_call_download_failure(self, *args, **kwargs)

    def test_call_download_atcoder_abc114_c(self):
        self.snippet_call_download('https://atcoder.jp/contests/abc114/tasks/abc114_c', [
            {
                "input": "575\n",
                "output": "4\n"
            },
            {
                "input": "3600\n",
                "output": "13\n"
            },
            {
                "input": "999999999\n",
                "output": "26484\n"
            },
        ], type='json')

    def test_call_download_atcoder_abc003_4(self):
        self.snippet_call_download('https://atcoder.jp/contests/abc003/tasks/abc003_4', [
            {
                "input": "3 2\n2 2\n2 2\n",
                "output": "12\n"
            },
            {
                "input": "4 5\n3 1\n3 0\n",
                "output": "10\n"
            },
            {
                "input": "23 18\n15 13\n100 95\n",
                "output": "364527243\n"
            },
            {
                "input": "30 30\n24 22\n145 132\n",
                "output": "976668549\n"
            },
        ], type='json')

    def test_call_download_invalid_url(self):
        self.snippet_call_download_failure('http://abc001.contest.atcoder.jp/tasks/abc001_100')

    def test_call_download_413(self):
        # This task is not supported.
        self.snippet_call_download_failure('https://chokudai001.contest.atcoder.jp/tasks/chokudai_001_a')


class DownloadInvalidTest(unittest.TestCase):
    def snippet_call_download_failure(self, *args, **kwargs):
        tests.command_download.snippet_call_download_failure(self, *args, **kwargs)

    def snippet_call_download_twice(self, *args, **kwargs):
        tests.command_download.snippet_call_download_twice(self, *args, **kwargs)

    def test_call_download_invalid(self):
        self.snippet_call_download_failure('https://not_exist_contest.jp/tasks/001_a')

    def test_call_download_no_sample_found(self):
        self.snippet_call_download_failure('https://atcoder.jp/contests/tenka1-2013-quala/tasks/tenka1_2013_qualA_a')
        self.snippet_call_download_failure('https://open.kattis.com/problems/hello')

    def test_call_download_twice(self):
        self.snippet_call_download_twice('https://atcoder.jp/contests/abc114/tasks/abc114_c', 'https://atcoder.jp/contests/abc003/tasks/abc003_4', [
            {
                "input": "575\n",
                "output": "4\n"
            },
            {
                "input": "3600\n",
                "output": "13\n"
            },
            {
                "input": "999999999\n",
                "output": "26484\n"
            },
        ], type='json')
