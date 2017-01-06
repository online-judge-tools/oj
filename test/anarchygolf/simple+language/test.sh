#!/bin/bash
set -e  # If not interactive, exit immediately if any untested command fails.
cd $(dirname $0)
[ -e test ] && rm -r test
oj download http://golf.shinh.org/p.rb?simple+language
diff <(md5sum test/sample-*) - <<EOF
9b3c9ece5285bb1bcd1164cec8aa4243  test/sample-1.in
48a24b70a0b376535542b996af517398  test/sample-1.out
10e10b554ef9bc07d56a514d2f6dab26  test/sample-2.in
48a24b70a0b376535542b996af517398  test/sample-2.out
f201f3f6606e56f561f8452c9a60210b  test/sample-3.in
c4211571f7a72cfad092b4dac7b15144  test/sample-3.out
EOF
