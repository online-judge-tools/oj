import hashlib
import os

import tests.utils
from onlinejudge_command.main import get_parser
from onlinejudge_command.subcommand.download import download


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


def snippet_call_download_raises(self, expected_exception, url, is_system=False, is_silent=False):
    args = ["download", url]
    if is_system:
        args.append("--system")
    if is_silent:
        args.append("--silent")
    args = get_parser().parse_args(args=args)
    with self.assertRaises(expected_exception):
        download(args)


def snippet_call_download_twice(self, url1, url2, files, is_system=False, is_silent=False, type='files'):
    assert type in 'files' or 'json'
    if type == 'json':
        files = get_files_from_json(files)

    with tests.utils.sandbox([]):
        args = ['download', url1]
        if is_system:
            args += ['--system']
        if is_silent:
            args += ['--silent']
        args = get_parser().parse_args(args=args)
        download(args)

        args = ['download', url2]
        if is_system:
            args += ['--system']
        if is_silent:
            args += ['--silent']
        args = get_parser().parse_args(args=args)
        # download from url2 should be aborted.
        with self.assertRaises(FileExistsError):
            download(args)

        # check download from url1 is not overwritten
        result = {}
        if os.path.exists('test'):
            for name in os.listdir('test'):
                with open(os.path.join('test', name)) as fh:
                    result[name] = hashlib.md5(fh.buffer.read()).hexdigest()
        self.assertEqual(files, result)
