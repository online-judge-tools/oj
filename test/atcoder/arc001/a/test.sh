#!/bin/bash
set -e  # If not interactive, exit immediately if any untested command fails.
cd $(dirname $0)
[ -e test ] && rm -r test
oj download http://arc001.contest.atcoder.jp/tasks/arc001_1
diff <(md5sum test/sample-*) - <<EOF
ffa1fbc1d14328005da451b67c65d35a  test/sample-1.in
3e49d46d6c574dc91c9736436eb06d0a  test/sample-1.out
178aa146bf65370f626f5b0dc63d6d32  test/sample-2.in
cee9c772621fa0919c3f411e591ae81b  test/sample-2.out
57b9c678fa47979fa44d69bbe60ffadb  test/sample-3.in
b7ca7cc0db40e50e6575025472fcbeab  test/sample-3.out
EOF
