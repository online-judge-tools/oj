How to run CI on your library for competitive programming (English)
===================================================================

If you are a competitive programmer, you probably have an in-house library for competition programming for yourself.
Such libraries are normally tested manually by submissions using the library to existing contest problems and checking the result is AC or not.

But this is a very cumbersome task. And it's frequently forgotten or omitted.
For example, "the changes are small and I can skip the test!".

However, such a library can have bugs.

What should we do?
Of course this issue can be solved by automation.


Test Script
-----------

online-judge-tools has features for testing libraries.
By this feature, the test can be automated.

For example, the following shell script should be written.
First, create a file like ``test.cpp``.
In ``test.cpp``, specify the problem in the form of ``#define PROBLEM http://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=DSL_2_A&``.
ex. `union_find_tree.test.cpp <https://github.com/kmyk/competitive-programming-library/blob/d4e35b5afe641bffb18cc2d6404fa1a67765b5ba/data_structure/union_find_tree.test.cpp>`_.
The script then looks for files with matched extensions, automatically compiles the code and obtains system test inputs and outputs, and tests them.
Since it can be executed locally, the contest server workload is light.

.. code-block:: bash

   #!/bin/bash
   set -e
   oj --version

   CXX=${CXX:-g++}
   CXXFLAGS="${CXXFLAGS:--std=c++14 -O2 -Wall -g}"
   ulimit -s unlimited

   run() {
       file="$1"
       url="$(grep -o '^# *define \+PROBLEM \+\(https\?://.*\)' < "$file" | sed 's/.* http/http/')"
       dir=test/$(echo -n "$url" | md5sum | sed 's/ .*//')
       mkdir -p ${dir}
       $CXX $CXXFLAGS -I . -o ${dir}/a.out "$file"
       if [[ -n ${url} ]] ; then
           if [[ ! -e ${dir}/test ]] ; then
               sleep 2
               oj download --system "$url" -d ${dir}/test
           fi
           oj test --tle 10 --c ${dir}/a.out -d ${dir}/test
       else
           ${dir}/a.out
       fi
   }

   if [ $# -eq 0 ] ; then
       for f in $(find . -name \*.test.cpp) ; do
           run $f
       done
   else
       for f in "$@" ; do
           run "$f"
       done
   fi

However, please note that currently only `AOJ <https://onlinejudge.u-aizu.ac.jp/home>`_ and `Library Checker <https://judge.yosupo.jp>`_ are supported.
Since Codeforces doesn't distribute system test cases, and AtCoder distributes it via DropBox, but automated download is difficult.

This script is only an example, and if you have requests such as "I want to support Python" or "I want to test only the differences",
please extend this script by yourself.


Continuous Integration
----------------------

It's not enough just to have a script to run tests.
Since the script itself has to be executed manually by humans every time, you may forget to execute it.
The solution to this issue is called Continuous Integration (CI).

CI is a mechanism and operation that automatically and continuously tests the software.
An example would be to have a test run automatically each time a commit is added to a GitHub repository.

If you host your library on GitHub, CI is easy to implement.
You can use Travis CI, one of the CI services.

1. Register to the Travis CI from https://travis-ci.org/.
2. Enable the linkage with the GitHub repository of the library.
3. Create the shell script in the previous section as ``test.sh``,
4. Create ``.travis.yml`` with the following content,

.. code-block:: yaml

   language: cpp
   compiler:
       - clang
       - gcc
   dist: xenial
   addons:
       apt:
           packages:
               - python3
               - python3-pip
               - python3-setuptools

   before_install:
       - pip3 install -U setuptools
       - pip3 install -U online-judge-tools=='7.*'
   script:
       - bash test.sh

That' all.

You can check the CI results on Travis CI pages. (ex.: https://travis-ci.org/kmyk/competitive-programming-library)
The badge like |badge| can be generated from URL ``https://img.shields.io/travis/USER/REPO/master.svg``.
It is good practice to paste this badge on your ``README``.
The color of this badge changes depending on the success or failure of CI.

.. |badge| image:: https://img.shields.io/travis/kmyk/competitive-programming-library/master.svg
   :target: https://travis-ci.org/kmyk/competitive-programming-library


Examples
--------

The following are two examples that run CI by online-judge-tools.

- https://github.com/kmyk/competitive-programming-library
- https://github.com/beet-aizu/library

There are other competitive programming libraries that use CI, for example:

- https://github.com/asi1024/competitive-library
- https://github.com/blue-jam/ProconLibrary
