#!/bin/bash
set -e  # If not interactive, exit immediately if any untested command fails.
cd $(dirname $0)
[ -e test ] && rm -r test
oj download http://yukicoder.me/problems/100
diff <(md5sum test/sample-*) - <<EOF
c8a8eeb947c8a1d6700d6f7fd151cb00  test/sample-1.in
3bb50ff8eeb7ad116724b56a820139fa  test/sample-1.out
3b6feb4b7d767c8e7314f59a1749d544  test/sample-2.in
9f4c0b1fca5cb6f886aa2e54442b1e1b  test/sample-2.out
c12ec911666a5d65bf53e234291e402c  test/sample-3.in
63a98316f78c5127e702db8fbea612a6  test/sample-3.out
EOF
