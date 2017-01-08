#!/bin/bash
set -e  # If not interactive, exit immediately if any untested command fails.
cd $(dirname $0)
[ -e test ] && rm -r test
oj -x all download $(cat url)  # -x all
diff <(md5sum test/*) md5.sum
