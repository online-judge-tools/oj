Introduction to online-judge-tools (English)
=============================================

online-judge-tools is a tool for automating typical tasks that exist in competitive programming.


Install
------------

If Python is installed, you can install it with just the following command.

.. code-block:: console

   $ pip3 install --user online-judge-tools

Linux or Mac OS is recommended for the OS, but it also works on Windows.


Sample case test
----------------------

Do you test with sample cases before submission?
Have you ever been troublesome and omitted?
You should always test before submitting, since submitting an implementation that doesn't even pass the sample cases will only incur a wrong answer penalty.
It is also useful for debugging, and testing your program with the sample cases every time you rewrite is good practice.

However, "open the problem page, copy the sample input, run the program and paste it into shell, and compare the output result with the sample output" for the number of sample cases, it is quite troublesome.
Doing the tedious work manually is easy to omit or mistake.
This problem can be solved by automation.

By online-judge-tools, you can automate sample case testing.
Specifically, it automatically does the following:

#. Open the problem page and get a sample
#. Run the program and give the sample as input
#. Compare program output with sample output

You can download the sample with ``oj d URL`` and test the downloaded sample with ``oj t``.
For example, use:

.. code-block:: console

   $ oj d https://atcoder.jp/contests/agc001/tasks/agc001_a
   [x] problem recognized: AtCoderProblem.from_url('https://atcoder.jp/contests/agc001/tasks/agc001_a')
   [x] load cookie from: /home/ubuntu/.local/share/online-judge-tools/cookie.jar
   [x] GET: https://atcoder.jp/contests/agc001/tasks/agc001_a
   [x] 200 OK
   [x] save cookie to: /home/ubuntu/.local/share/online-judge-tools/cookie.jar
   [x] append history to: /home/ubuntu/.cache/online-judge-tools/download-history.jsonl

   [*] sample 0
   [x] input: Input example 1
   2
   1 3 1 2
   [+] saved to: test/sample-1.in
   [x] output: Input example 1
   3
   [+] saved to: test/sample-1.out

   [*] sample 1
   [x] input: Input example 2
   5
   100 1 2 3 14 15 58 58 58 29
   [+] saved to: test/sample-2.in
   [x] output: Sample output 2
   135
   [+] saved to: test/sample-2.out

   $ g++ main.cpp

   $ oj t
   [*] 2 cases found

   [*] sample-1
   [x] time: 0.003978 sec
   [+] AC

   [*] sample-2
   [x] time: 0.004634 sec
   [-] WA
   output:
   3

   expected:
   135


   [x] slowest: 0.004634 sec  (for sample-2)
   [x] max memory: 2.344000 MB  (for sample-1)
   [-] test failed: 1 AC / 2 cases


The basic function of ``oj t`` is almost equivalent to prepare files such as ``test/sample-1.in``, ``test/sample-1.out`` and then to run ``for f in test/*.in ; do diff <(./a.out < $f) ${f/.in/.out} ; done``.
If you want to test against commands other than ``./a.out`` (e.g. ``python3 main.py``), use the ``-c`` option (e.g. ``oj t -c "python3 main.py"``).
Use the ``--system`` option if you want to get test cases that are used for system tests instead of samples.
Run ``oj d --help`` or ``oj t --help`` to see other features.


Submit
----

When submitting your implemented solution, you have to select "Problem to be submitted to the program" and "Implement language of the program to be submitted" with the mouse, copy and paste the source code into the text box, and press the send button. This series of operations is troublesome.
Have you ever experienced a penalty when you made a mistake in selecting the “submission issue” or “submission language” at the time of submission?
If you have any such experience, we recommend automating the submission.

By online-judge-tools, you can automate submissions.
If you want to submit the file to the problem https://codeforces.com/contest/1200/problem/F, you can do it. The actual output is as follows: ``main.cpp`` ``oj s https://codeforces.com/contest/1200/problem/F``

.. code-block:: console

   $ oj s https://codeforces.com/contest/1200/problem/F main.cpp
   [x] read history from: /home/ubuntu/.cache/online-judge-tools/download-history.jsonl
   [x] found urls in history:
   https://codeforces.com/contest/1200/problem/F
   [x] problem recognized: CodeforcesProblem.from_url('https://codeforces.com/contest/1200/problem/F'): https://codeforces.com/contest/1200/problem/F
   [*] code (2341 byte):
   #include <bits/stdc++.h>
   #define REP(i, n) for (int i = 0; (i) < (int)(n); ++ (i))
   using namespace std;
   
   
   constexpr int MAX_M = 10;
   constexpr int MOD = 2520;  // lcm of { 1, 2, 3, ..., 10 }
   int main() {
       // config
       int n; scanf("%d", &n);
   ... (62 lines) ...
   
       // query
       int q; scanf("%d", &q);
       while (q --) {
           int x, c; scanf("%d%d", &x, &c);
           -- x;
           printf("%d\n", solve1(x, c));
           }
       return 0;
   }
   
   [x] load cookie from: /home/ubuntu/.local/share/online-judge-tools/cookie.jar
   [x] GET: https://codeforces.com/contest/1200/problem/F
   [x] 200 OK
   [x] both GCC and Clang are available for C++ compiler
   [x] use: GCC
   [*] chosen language: 54 (GNU G++17 7.3.0)
   [x] sleep(3.00)
   Are you sure? [y/N] y
   [x] GET: https://codeforces.com/contest/1200/problem/F
   [x] 200 OK
   [x] POST: https://codeforces.com/contest/1200/problem/F
   [x] redirected: https://codeforces.com/contest/1200/my
   [x] 200 OK
   [+] success: result: https://codeforces.com/contest/1200/my
   [x] open the submission page with: sensible-browser
   [1513:1536:0910/223148.485554:ERROR:browser_process_sub_thread.cc(221)] Waited 5 ms for network service
   Opening in existing browser session.
   [x] save cookie to: /home/ubuntu/.local/share/online-judge-tools/cookie.jar


(However, since login is required for submission, please execute ``oj login https://atcoder.jp/`` in advance.
If `Selenium <https://www.seleniumhq.org/>`_ is installed (``apt install python3-selenium firefox-geckodriver`` etc. is executed), the GUI browser will start, so please login normally on it.
(If you don't have Selenium, you will be asked for your username and password directly on the CUI.)

If you already executed ``oj d URL`` in the same directory, ``oj s main.cpp`` will guess the URL and submit it.
In order to prevent URL specification mistakes, we recommend using this labor-saving form.
The language is automatically recognized and set appropriately.


Stress test
--------------

What should I do when I get a situation where I implemented and submitted the sample because it matched, but it turned out to be WA or RE, but I don't know the cause at all?
This can be debugged using a randomly generated case.
Specifically:

#. Implement a program that randomly generates input that satisfies the constraints, and prepare many test case inputs
#. (If possible, implement a straightforward solution to ensure that the correct answer is output at the latest, and provide a lot of corresponding output)
#. Test the program in question using the test cases created in (1.) and (2.)
#. Analyze the shooting case found in (3.) to find bugs

online-judge-tools also has a feature to help with this.
You can use the command ``oj g/i`` for (1.) and the command ``oj g/o`` for (2.).
For example https://onlinejudge.u-aizu.ac.jp/courses/library/7/DPL/1/DPL_1_B is used as follows.

.. code-block:: console

   $ cat generate.py
   #!/usr/bin/env python3
   import random
   N = random.randint(1, 100)
   W = random.randint(1, 10000)
   print(N, W)
   for _ in range(N):
       v = random.randint(1, 1000)
       w = random.randint(1, 1000)
       print(v, w)
   
   $ oj g/i ./generate.py
   
   [*] random-000
   [x] generate input...
   [x] time: 0.041610 sec
   input:
   1 4138
   505 341
   
   [+] saved to: test/random-000.in
   
   ...
   
   [*] random-099
   [x] generate input...
   [x] time: 0.036598 sec
   input:
   9 2767
   868 762
   279 388
   249 673
   761 227
   958 971
   589 590
   34 100
   689 635
   781 361
   
   [+] saved to: test/random-099.in

   $ cat tle.cpp
   #include <bits/stdc++.h>
   #define REP(i, n) for (int i = 0; (i) < (int)(n); ++ (i))
   using namespace std;
   
   int main() {
       // input
       int N, W; cin >> N >> W;
       vector<int> v(N), w(N);
       REP (i, N) {
           cin >> v[i] >> w[i];
       }
   
       // solve
       int answer = 0;
       REP (x, 1 << N) {
           int sum_v = 0;
           int sum_w = 0;
           REP (i, N) if (x & (1 << i)) {
               sum_v += v[i];
               sum_w += w[i];
           }
           if (sum_w <= W) {
               answer = max(answer, sum_v);
           }
       }
   
       // output
       cout << answer << endl;
       return 0;
   }

   $ g++ tle.cpp -o tle

   $ oj g/o -c ./tle
   [*] 102 cases found
   
   [*] random-000
   [x] time: 0.003198 sec
   505
   
   [+] saved to: test/random-000.out
   
   ...
   
   [*] random-099
   [x] time: 0.005680 sec
   3722
   
   [+] saved to: test/random-099.out
   
   [*] sample-1
   [*] output file already exists.
   [*] skipped.
   
   [*] sample-2
   [*] output file already exists.
   [*] skipped.



The basic function of ``oj g/i ./generate.py`` is almost equivalent to ``for i in $(seq 100) ; do ./generate.py > test/random-$i.in ;``. And the basic function of ``oj g/o`` is almost equivalent to ``for i in test/*.in ; do ./a.out < $f > ${f/.in/.out} ; done``.
There are also more efficient options such as ``--hack`` and parallelization option ``-j``, etc., for cases where it is difficult to find a failure testcase.


Test for special forms of problem
------------------------------

-   Error judge

    Tests for problems such as “Absolute or relative error within 10⁻⁶ as correct answer” can be handled with the ``-e`` option.
    For example, ``oj t -e 1e-6``.

-   Problems with multiple solutions

    You can validate simply by using `assert <https://cpprefjp.github.io/reference/cassert/assert.html>`_ in the implemented program.
    If you want to use complex method (also, you need expected output of testcase) for validating, you can write a program on the judge side, and use it for test.

    For example, if the problem is https://atcoder.jp/contests/abc074/tasks/arc083_a, write the following program on the judge side and save it as ``judge.py`` and ``oj t --judge-command "python3 judge.py"`` will run the test.

   .. code-block:: python

      import sys
      # input
      with open(sys.argv[1]) as testcase:
          A, B, C, D, E, F = list(map(int, testcase.readline().split()))
      with open(sys.argv[2]) as your_output:
          y_all, y_sugar = list(map(int, your_output.readline().split()))
      with open(sys.argv[3]) as expected_output:
          e_all, e_sugar = list(map(int, expected_output.readline().split()))
      # check
      assert 100 * A <= y_all <= F
      y_water = y_all - y_sugar
      assert any(100 * A * i + 100 * B * j == y_water for i in range(3001) for j in range(3001))
      assert any(C * i + D * j == y_sugar for i in range(3001) for j in range(3001))
      assert y_sugar <= E * y_water / 100
      assert y_sugar * e_all == e_sugar * y_all
      assert (e_sugar > 0 and y_sugar == 0) is False

    A program on the judge side can get the input of a testcase, the output of your program and the expected output through the file input.
    The judge command is ran as ``<command> <input> <your_output> <expected_output>``. ``<command>`` is a runnable command specified by argument. 
    ``<input>``, ``<your_output>`` and ``<expected_output>`` are file path of the input of a testcase, the output of your program and the expected output given by problem statement respectively.
    Please get those using commandline arguments and validate a correctness of your answer as the above example.
    If exit code of the judge command is 0, ``AC`` is shown, otherwise `WA`.


-   Reactive problem

    There is a problem submitting a program that works interactively with the judge program.
    The command ``oj t/r`` is provided to test this.

    For example, if the problem is https://codeforces.com/gym/101021/problem/A, write the following program on the judge         side and save it as ``judge.py``  and ``oj t/r ./judge.py`` will run the test.

    .. code-block:: python

      #!/usr/bin/env python3
      import sys
      import random
      n = random.randint(1, 10 ** 6)
      print('[*] n =', n, file=sys.stderr)
      for i in range(25 + 1):
          s = input()
          if s.startswith('!'):
              x = int(s.split()[1])
              assert x == n
              exit()
          else:
              print('<' if n < int(s) else '>=')
              sys.stdout.flush()
      assert False


List of supported services
--------------------------

For services that communicate with online judge servers, the services available may be limited.
Supported service as of ``v7.2.0`` (2019-09-27) is as follows.

Download sample (``oj d``):

-  `Aizu Online Judge (Arena) <https://onlinejudge.u-aizu.ac.jp/services/arena.html>`_
-  `Aizu Online Judge <https://onlinejudge.u-aizu.ac.jp/home>`_
-  `Anarchy Golf <http://golf.shinh.org/>`_
-  `AtCoder <https://atcoder.jp/>`_
-  `Codeforces <https://codeforces.com/>`_
-  `CS Academy <https://csacademy.com/>`_
-  `Facebook Hacker Cup <https://www.facebook.com/hackercup/>`_
-  `HackerRank <https://www.hackerrank.com/>`_
-  `Kattis <https://open.kattis.com/>`_
-  `PKU JudgeOnline <http://poj.org/>`_
-  `Toph (Problem Archive) <https://toph.co/>`_
-  `yukicoder <https://yukicoder.me/>`_
-  `Library Checker <https://judge.yosupo.jp>`_

Login (``oj login``):

-  All services (when using Selenium)
-  AtCoder (direct password input)
-  Codeforces (direct password input)

Submit (``oj s``)

-  AtCoder
-  Codeforces
-  Topcoder (Marathon Match)
-  yukicoder
-  HackerRank
-  Toph (Problem Archive)

Download system case (``oj d --system``):

-  Aizu Online Judge
-  yukicoder


Missing features
--------------

To explain what online-judge-tools is, we need to say what we can do, but that is not enough.
You should also say "what you can't do".

online-judge-tools does not have the following features:

-  Ability to prepare a directory corresponding to the contest

   online-judge-tools is a tool for “helping to solve individual problems”, otherwise it is out of responsibility.
   There is a function to support this internally (`onlinejudge.type.Contest.list_problems <https://online-judge-tools.readthedocs.io/en/master/onlinejudge.type.html#onlinejudge. type.Contest.list_problems>`_), so if necessary, write your own script. You can also use existing wrappers (such as `Tatamo / atcoder-cli <https://github.com/Tatamo/atcoder-cli>`_).

   For the same reason, for example, there is no function to manage the progress of training.

-  Ability to generate templates

Template generation is a general programming issue and is not the responsibility of online-judge-tools.
For example, in Vim, it can be supported more generically with plug-ins such as `thinca / vim-template <https://github.com/thinca/vim-template/blob/master/doc/template.jax>`_.

For example, “the ability to automatically diagnose source code and search for potential bugs” does not exist for the same reason as “it exists as a more general tool”.

-  Ability to compile automatically

It is enough to use shell functions.
In addition, there are too many compiling methods as many as the number of languages ​​and environments.
If you want to recompile before testing, use something like ``g++ main.cpp && oj t``.

-  Function to automatically generate code for the part that receives input

Although it existed in the past, it was deleted by leaving it to `kyuridenamida / atcoder-tools <https://github.com/kyuridenamida/atcoder-tools>`_. Please use that.

-  Ability to make submission reservations

Since it is sufficient to use the shell functions, there is no option to do so.
For example, to submit after 1 hour, use ``sleep 3600 && oj s --yes main.cpp``.

-  Ability to analyze submission results

do not exist. If we do too much, we can have trouble to maintain library.
There is a function to implement this internally (`onlinejudge.service.atcoder.AtCoderSubmissionData <https://online-judge-tools.readthedocs.io/en/master/onlinejudge.service.atcoder.html# onlinejudge.service.atcoder.AtCoderSubmissionData>`_) So if necessary, write your own script.

-  setting file

do not exist.
The configuration file introduces a kind of “hidden state” to increase maintenance and support costs.
Except for the cookies used for HTTP communication internally (+ as an exception, the history for guessing the submission URL ``oj s``), it depends only on the command entered.
   
