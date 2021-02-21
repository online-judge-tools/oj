# Getting Started for `oj` command

[このドキュメントの日本語バージョン](./getting-started.ja.md)

`oj` command is a command to automate typical tasks that exist in
competitive programming.


## How to Install

You can install with the following command if Python is already
installed.

```console
$ pip3 install --user online-judge-tools
```

Linux (including Windows Subsystem for Linux) or macOS is recommended for the OS, but it also works on Windows.

For detailed instructions, read [docs/INSTALL.md](./INSTALL.md).


## Testing with sample cases

Do you test with sample cases before submission? Have you ever felt it
troublesome and omitted? You should always test before submitting, since
submitting a solution that doesn't even pass the sample cases will just
make a penalty. It is also useful for debugging, so you should test your
program with the sample cases every time you rewrite your program.

However, "opening the problem page, copying the sample inputs, running
the program, pasting it into shell, and comparing the output result with
the sample output" is tedious tasks. Doing this for every sample case
and for every submission is quite troublesome. Doing the tedious tasks
manually is easy to be omitted or be mistaken. This problem can be
solved by automation.

By `oj` command, you can automate testing with sample cases.
Specifically, it automatically does the following:

1.  Open the problem page and get sample cases
2.  Run the program and give the sample inputs
3.  Compare program outputs with sample outputs

You can download the sample cases by `oj d URL` and test your solution
with the downloaded sample cases by `oj t`. For example:

```console
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
```

The basic feature of `oj t` is almost equivalent to prepare files such
as `test/sample-1.in`, `test/sample-1.out` and then to run
`for f in test/*.in ; do diff <(./a.out < $f) ${f/.in/.out} ; done`. If
you want to test against commands other than `./a.out` (e.g.
`python3 main.py`), use the `-c` option (e.g.
`oj t -c "python3 main.py"`). Use the `--system` option if you want to
get testcases that are used for system tests instead of samples. Run
`oj d --help` or `oj t --help` to see other features.


## Submit

When submitting your solution, you have to select "Problem to submit
for" and "Language of the solution" with your mouse, copy and paste the
source code into the text box, and click the send button. This series of
operations is tedious. Have you ever experienced a penalty when you made
a mistake in selecting the "problem" or "language" at the time of
submission? If you have any such experience, we recommend automating
submission.

By `oj` command, you can automate submission. For exampl,e if you
want to submit the file `main.cpp` to the problem
<https://codeforces.com/contest/1200/problem/F>, you can do
`oj s https://codeforces.com/contest/1200/problem/F`. The actual output
is as follows:

```console
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
```

(However, since login is required for submission, please execute
`oj login https://atcoder.jp/` in advance. If
[Selenium](https://www.seleniumhq.org/) is installed
(`apt install python3-selenium firefox-geckodriver` etc. is executed),
the GUI browser will start, so please login normally on it. (If you
don't have Selenium, you will be asked for your username and password
directly on the CUI.)

If you already executed `oj d URL` in the same directory,
`oj s main.cpp` will guess the URL and submit it. In order to prevent
URL specification mistakes, we recommend using this labor-saving form.
The language is automatically recognized and set appropriately.


## Random testing

What should you do when you get a situation where you implemented your
solution and submitted it because it passes the sample cases but it gets
WA or RE and you don't know the cause at all? In such a situation, you
can debug using randomly generated cases. Specifically:

1.  Implement a program that randomly generates test inputs that
    satisfies the constraints
2.  Prepare many test inputs with the program of (1.)
3.  (If possible, implement a straightforward solution that you can
    believe that it always outputs the correct answer, and prepare the
    test outputs for the inputs)
4.  Test your solution using the testcases generated in (2.) and (3.)
5.  Analyze the hack case found in (4.) to find bugs

`oj` command also has features to help with this. You can use the
command `oj g/i` for (2.) and the command `oj g/o` for (3.). Also, another command [online-judge-tools/template-generator](https://github.com/online-judge-tools/template-generator) can automatically generates a program of (1.).

For example, for a problem
<https://onlinejudge.u-aizu.ac.jp/courses/library/7/DPL/1/DPL_1_B>, you
can use `oj` command as follows.

```console
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
```

The basic feature of `oj g/i ./generate.py` is almost equivalent to
`for i in $(seq 100) ; do ./generate.py > test/random-$i.in ;`. And the
basic feature of `oj g/o` is almost equivalent to
`for i in test/*.in ; do ./a.out < $f > ${f/.in/.out} ; done`. There are
some ways such as `--hack` option and parallelization option `-j`, etc.,
for cases where it is difficult to find hacking cases.


## Test for problems with special judge

### Problems with accepted errors

You can use the `-e` option for problems with errors, e.g. problems
which accept answers which absolute or relative error are within
10⁻⁶. In this case, use `oj t -e 1e-6`.

### Problems with multiple solutions

You can validate simply by using
[assert](https://cpprefjp.github.io/reference/cassert/assert.html)
in your solution.

Also, you can write a program for the judge side, and use it for
test. For example, if the problem is
<https://atcoder.jp/contests/abc074/tasks/arc083_a>, write the
following program as the judge program and save it as `judge.py`,
then `oj t --judge-command "python3 judge.py"` will run the tests.

```python
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
```

A program for judge can get the input of a testcase, the output of
your program, and the expected output of the testcase, via files.
The command for judge is executed as
`<command> <input> <your_output> <expected_output>`. `<command>` is
the command specified via the option of `oj` command. `<input>`,
`<your_output>`, and `<expected_output>` are file paths of the input
of the testcase, the output of your program, and the expected output
of the testcase, respectively. If the exit code of the judge command
is 0, then the output becomes `AC`, otherwise `WA`.

### Reactive problems

There is a problem submitting a program that works interactively with
the judge program.    The command `oj t/r` is provided to run tests for
such a problem.

For example, if the problem is
<https://codeforces.com/gym/101021/problem/0>, write the following
program as the judge program and save it as `judge.py` and run
`oj t/r ./judge.py` command.

```python
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
```


## List of supported services

Please see the table at [online-judge-tools/api-client](https://github.com/online-judge-tools/api-client#supported-websites).


## Missing features

To describe "what it is", it's necessary to tell about "what it can do". But it's not sufficient. Also we should tell about "what it cannot do".

In `oj` command, there are no features like:

-   The feature to prepare the directory for a contest at once

    For the feature to prepare the directory for a contest, please use a related command, `oj-prepare` in [online-judge-tools/template-generator](https://github.com/online-judge-tools/template-generator).

    `oj` command is "a command to help with solving individual problems (mainly, with testing)", so other things are out of scope.

-   The feature to generate template code

    To analyze a problem of competitive programming and automatically generate the template code for the given problem including the main function and the input/output part, you can use `oj-template` command in [online-judge-tools/template-generator](https://github.com/online-judge-tools/template-generator).

-   The feature to automatically compile code before running tests

    `oj` command doesn't have such a feature because using shell is sufficient.
    Please use your shell. For example, `$ g++ main.cpp && oj t` does this feature.

    There are too many ways to compile and run source code of various language. Also, we don't ignore users who use minor programming languages or minor online judges. So, implementing this feature is not realistic.

-   The feature to schedule to submit code

    `oj` command doesn't have such a feature because using shell is sufficient.
    Please use your shell. For example, `$ sleep 3600 && oj s --yes main.cpp` will submit your code after one hour.


-   Configuration files

    `oj` command doesn't have such a feature because using shell is sufficient.
    Please use the configuration file of your shell (e.g. `~/.bashrc`).
    Please use aliases of shell functions.

    Configuration files introduce "implicit states" and increase the costs of maintenance and user-supporting.
    Except internal cookies for HTTP accessing (and, as an exception, the history to guess URLs to submit in `oj s`)
