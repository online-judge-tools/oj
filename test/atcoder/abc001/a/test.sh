#!/bin/bash
set -e  # If not interactive, exit immediately if any untested command fails.
cd $(dirname $0)
[ -e test ] && rm -r test
oj download http://abc001.contest.atcoder.jp/tasks/abc001_1
diff <(md5sum test/sample-*) - <<EOF
ec7562c808cc6c106a4d62d212daefd9  test/sample-1.in
1dcca23355272056f04fe8bf20edfce0  test/sample-1.out
c4da2b805df8425bccc182ad4db8422a  test/sample-2.in
897316929176464ebc9ad085f31e7284  test/sample-2.out
e49623ffecc4347eaa5b3e235d5752bd  test/sample-3.in
0735cf297f0e794bcfa7515f25d189fc  test/sample-3.out
EOF
