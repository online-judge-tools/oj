#!/bin/bash
set -e  # If not interactive, exit immediately if any untested command fails.
cd $(dirname $0)
[ -e test ] && rm -r test
oj download http://jag2013spring.contest.atcoder.jp/tasks/icpc2013spring_a
diff <(md5sum test/sample-*) - <<EOF
b0fba7805dabe2ee3cf299d97a2f6ec2  test/sample-1.in
3ae2ea0c3867b219ef54d914437e76be  test/sample-1.out
9121f567aad63b98115e8c793a0e2e72  test/sample-2.in
3ae2ea0c3867b219ef54d914437e76be  test/sample-2.out
d797a450bb87f8000cda4b45991fc894  test/sample-3.in
e14b420b7266f69a2b2b457f3bbec804  test/sample-3.out
0ef2e8b0c0a59602c1b4390b58948498  test/sample-4.in
e14b420b7266f69a2b2b457f3bbec804  test/sample-4.out
9c8befefed86e886539c9baa85e6724a  test/sample-5.in
3ae2ea0c3867b219ef54d914437e76be  test/sample-5.out
EOF
