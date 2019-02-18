# Python Version: 3.x
import datetime
import json
import pathlib
import time
import traceback
from typing import *

import onlinejudge
import onlinejudge._implementation.logging as log
import onlinejudge._implementation.utils as utils
import onlinejudge.type


class DownloadHistory(object):
    def __init__(self, path: pathlib.Path = utils.cache_dir / 'download-history.jsonl'):
        self.path = path

    def add(self, problem: onlinejudge.type.Problem, directory: pathlib.Path = pathlib.Path.cwd()) -> None:
        now = datetime.datetime.now(datetime.timezone.utc).astimezone()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(str(self.path), 'a') as fh:
            fh.write(json.dumps({
                'timestamp': int(time.time()),  # this should not be int, but Python's strptime is too weak and datetime.fromisoformat is from 3.7
                'directory': str(directory),
                'url': problem.get_url(),
            }) + '\n')
        log.status('append history to: %s', self.path)
        self._flush()

    def _flush(self) -> None:
        # halve the size if it is more than 1MiB
        if self.path.stat().st_size >= 1024 * 1024:
            with open(str(self.path)) as fh:
                history_lines = fh.readlines()
            with open(str(self.path), 'w') as fh:
                fh.write(''.join(history_lines[:-len(history_lines) // 2]))
            log.status('halve history at: %s', self.path)

    def get(self, directory: pathlib.Path = pathlib.Path.cwd()) -> List[str]:
        if not self.path.exists():
            return []

        log.status('read history from: %s', self.path)
        found = set()
        with open(str(self.path)) as fh:
            for line in fh:
                try:
                    data = json.loads(line)
                except json.decoder.JSONDecodeError as e:
                    log.warning('corrupted line found in: %s', self.path)
                    log.debug('%s', traceback.format_exc())
                    continue
                if pathlib.Path(data['directory']) == directory:
                    found.add(data['url'])
        log.status('found urls in history:\n%s', '\n'.join(found))
        return list(found)
