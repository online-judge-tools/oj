#!/bin/bash
set -e  # If not interactive, exit immediately if any untested command fails.
cd $(dirname $0)
[ -e test ] && rm -r test
oj download $(cat url)
diff <(md5sum test/sample-*) md5.sum
