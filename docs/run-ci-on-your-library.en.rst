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

For example, you can write a shell script like below.
First, create a file which has a name ending with ``.test.cpp`` and contains a line in the form of ``#define PROBLEM "http://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=DSL_2_A"``,
e.g. `union_find_tree.test.cpp <https://github.com/kmyk/competitive-programming-library/blob/d4e35b5afe641bffb18cc2d6404fa1a67765b5ba/data_structure/union_find_tree.test.cpp>`_.
The script finds such files, automatically compiles codes and obtains system test inputs and outputs, and tests them.
Since it can be executed locally, the contest server workload is light.

.. code-block:: bash

   #!/bin/bash
   set -e
   oj --version

   CXX=${CXX:-g++}
   CXXFLAGS="${CXXFLAGS:--std=c++14 -O2 -Wall -g}"
   ulimit -s unlimited  # make the stack size unlimited

   # list files to test
   for file in $(find . -name \*.test.cpp) ; do

       # get the URL for verification
       url="$(sed -e 's/^# *define \+PROBLEM \+"\(https\?:\/\/.*\)"/\1/ ; t ; d' "$file")"
       if [[ -z ${url} ]] ; then
           continue
       fi

       dir=cache/$(echo -n "$url" | md5sum | sed 's/ .*//')
       mkdir -p ${dir}

       # download sample cases
       if [[ ! -e ${dir}/test ]] ; then
           sleep 2
           oj download --system "$url" -d ${dir}/test
       fi

       # run test
       $CXX $CXXFLAGS -I . -o ${dir}/a.out "$file"
       oj test --tle 10 --c ${dir}/a.out -d ${dir}/test
   done


This script is just an example to show how we can use online-judge-tools for this purpose.
You can extend this by yourself or use a tool `online-judge-verify-helper <https://github.com/kmyk/online-judge-verify-helper>`_ .


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

(Caution: This section have been written before GitHub Actions is released. Now, I also recommend GitHub Actions not only Travis CI.)


Examples
--------

The following are two examples that run CI by online-judge-tools via `online-judge-verify-helper <https://github.com/kmyk/online-judge-verify-helper>`_ .

- https://github.com/kmyk/competitive-programming-library
- https://github.com/beet-aizu/library

There are other competitive programming libraries that use CI, for example:

- https://github.com/asi1024/competitive-library
- https://github.com/blue-jam/ProconLibrary
