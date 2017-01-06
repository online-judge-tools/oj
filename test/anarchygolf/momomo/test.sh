#!/bin/bash
set -e  # If not interactive, exit immediately if any untested command fails.
cd $(dirname $0)
[ -e test ] && rm -r test
oj download http://golf.shinh.org/p.rb\?momomo
diff <(md5sum test/sample-*) - <<EOF
281e30fff54f179881c67c4d0564633e  test/sample-1.in
d67adc236dd84fd82fb4598922d5cf32  test/sample-1.out
EOF
