#!/bin/bash
set -e  # If not interactive, exit immediately if any untested command fails.
cd $(dirname $0)
[ -e test ] && rm -r test
oj download http://yukicoder.me/problems/no/9002
diff <(md5sum test/sample-*) - <<EOF
b026324c6904b2a9cb4b88d6d61c81d1  test/sample-1.in
b026324c6904b2a9cb4b88d6d61c81d1  test/sample-1.out
5b6b41ed9b343fed9cd05a66d36650f0  test/sample-2.in
a403d4dbee7bd783539da3efa43c4399  test/sample-2.out
EOF
