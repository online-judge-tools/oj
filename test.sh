#!/bin/bash
set -e  # If not interactive, exit immediately if any untested command fails.
cd $(dirname $0)
for testcase in `find test -name test.sh` ; do
    echo $testcase
    bash $testcase
    echo PASSED
    echo
    sleep 1
done
