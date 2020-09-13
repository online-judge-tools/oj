import json
import pathlib
import time
import traceback
from logging import getLogger
from typing import *

import onlinejudge_command.utils as utils
from onlinejudge.type import Problem

logger = getLogger(__name__)


class DownloadHistory:
    def __init__(self, path: pathlib.Path = utils.user_cache_dir / 'download-history.jsonl'):
        self.path = path

    def add(self, problem: Problem, *, directory: pathlib.Path) -> None:
        logger.info('append the downloading history: %s', self.path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, 'a') as fh:
            fh.write(json.dumps({
                'timestamp': int(time.time()),  # this should not be int, but Python's strptime is too weak and datetime.fromisoformat is from 3.7
                'directory': str(directory),
                'url': problem.get_url(),
            }) + '\n')
        self._flush()

    def remove(self, *, directory: pathlib.Path) -> None:
        if not self.path.exists():
            return
        logger.info('clear the downloading history for this directory: %s', self.path)
        with open(self.path) as fh:
            history_lines = fh.readlines()
        with open(self.path, 'w') as fh:
            pred = lambda line: pathlib.Path(json.loads(line)['directory']) != directory
            fh.write(''.join(filter(pred, history_lines)))

    def _flush(self) -> None:
        # halve the size if it is more than 1MiB
        if self.path.stat().st_size >= 1024 * 1024:
            with open(self.path) as fh:
                history_lines = fh.readlines()
            with open(self.path, 'w') as fh:
                fh.write(''.join(history_lines[:-len(history_lines) // 2]))
            logger.info('halve history at: %s', self.path)

    def get(self, *, directory: pathlib.Path) -> List[str]:
        if not self.path.exists():
            return []

        logger.info('read history from: %s', self.path)
        found = set()
        with open(self.path) as fh:
            for line in fh:
                try:
                    data = json.loads(line)
                except json.decoder.JSONDecodeError:
                    logger.warning('corrupted line found in: %s', self.path)
                    logger.debug('%s', traceback.format_exc())
                    continue
                if pathlib.Path(data['directory']) == directory:
                    found.add(data['url'])
        logger.info('found urls in history:\n%s', '\n'.join(found))
        return list(found)
