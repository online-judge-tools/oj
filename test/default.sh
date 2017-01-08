#!/bin/bash
set -e  # If not interactive, exit immediately if any untested command fails.
[ $# -eq 1 ]
cd $1
[ -e test ] && rm -r test
python3 $(git rev-parse --show-toplevel)/main.py download $(cat url)
diff <(md5sum test/*) md5.sum
