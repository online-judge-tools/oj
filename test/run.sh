#!/bin/bash
set -e  # If not interactive, exit immediately if any untested command fails.
cd $(dirname $0)
for url in `find . -name url` ; do
    testcase=$(dirname $url)
    echo $testcase $(cat $url)
    if [ -e $testcase/custom.sh ] ; then
        bash $testcase/custom.sh
    else
        bash default.sh $testcase
    fi
    echo PASSED
    echo
    sleep 1
done
