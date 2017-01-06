#!/bin/bash
set -e  # If not interactive, exit immediately if any untested command fails.
cd $(dirname $0)
[ -e test ] && rm -r test
oj download http://agc001.contest.atcoder.jp/tasks/agc001_a
diff <(md5sum test/sample-*) - <<EOF
1aba94ea0ab5e89d4a11b3724bdeb5cc  test/sample-1.in
6d7fce9fee471194aa8b5b6e47267f03  test/sample-1.out
d38a35564e44aa124f04f5088e7203d9  test/sample-2.in
615010a656a5bb29d1898f163619611f  test/sample-2.out
EOF
