#!/bin/bash
set -e  # If not interactive, exit immediately if any untested command fails.
cd $(dirname $0)
[ -e test ] && rm -r test
oj download http://golf.shinh.org/p.rb\?The+B+Programming+Language
diff <(md5sum test/sample-*) - <<EOF
3de90f793f16fad76da1527e09b8e528  test/sample-1.in
f67b46b3c53308d8a6414b20092a2220  test/sample-1.out
810d1189284ef048fc30f80ba7a22c6d  test/sample-2.in
d4e62449830b2a986024d914b194f129  test/sample-2.out
7361217616875a437a3d6b41612dacbb  test/sample-3.in
fcbee46b3b888607abe720d598c75b17  test/sample-3.out
EOF
