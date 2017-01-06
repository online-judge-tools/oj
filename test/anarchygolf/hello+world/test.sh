#!/bin/bash
set -e  # If not interactive, exit immediately if any untested command fails.
cd $(dirname $0)
[ -e test ] && rm -r test
oj download http://golf.shinh.org/p.rb?hello+world
diff <(md5sum test/sample-*) - <<EOF
d41d8cd98f00b204e9800998ecf8427e  test/sample-1.in
746308829575e17c3331bbcb00c0898b  test/sample-1.out
EOF
