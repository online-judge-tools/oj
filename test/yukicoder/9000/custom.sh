#!/bin/bash
set -e  # If not interactive, exit immediately if any untested command fails.
cd $(dirname $0)
[ -e test ] && rm -r test
python3 $(git rev-parse --show-toplevel)/main.py -x all download $(cat url)
diff <(md5sum test/*) md5.sum
