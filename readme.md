# Online Judge Tools

[![Travis](https://img.shields.io/travis/kmyk/online-judge-tools.svg)](https://travis-ci.org/kmyk/online-judge-tools)
![PyPI](https://img.shields.io/pypi/l/online-judge-tools.svg)
![PyPI](https://img.shields.io/pypi/pyversions/online-judge-tools.svg)
![PyPI](https://img.shields.io/pypi/status/online-judge-tools.svg)
[![PyPI](https://img.shields.io/pypi/v/online-judge-tools.svg)](https://pypi.python.org/pypi/online-judge-tools)

Tools for online judge services. Downloading sample cases, Testing/Submitting your code, and various utilities.

## Screencast

![screencast](https://user-images.githubusercontent.com/2203128/34708715-568b13c0-f557-11e7-97ef-9f6b646e4776.gif)

## Features

-   Download sample cases
    -   AtCoder
    -   Yukicoder
    -   Anarchy Golf
    -   Codeforces
    -   HackerRank (using `Run Code`)
    -   Aizu Online Judge
    -   CS Academy
-   Download system test cases
    -   Yukicoder
    -   Aizu Online Judge
-   Login
    -   AtCoder
    -   Yukicoder (via github.com)
    -   Codeforces
    -   HackerRank
    -   TopCoder
-   Submit your solution
    -   AtCoder
    -   ~~Yukicoder~~ (removed)
    -   HackerRank
    -   TopCoder (Marathon Match)
-   Generate scanner for input  (experimental)
    -   AtCoder
    -   Yukicoder
-   Test your solution
-   Test your solution for reactive problem
-   Generate output files from input and reference implementation
-   Split an input file with many cases to files
-   Print the code statistics used in Anarchy Golf

## How to install

from PyPI: <https://pypi.python.org/pypi/online-judge-tools>

``` sh
$ pip3 install online-judge-tools
```

or

``` sh
$ pip3 install requests
$ pip3 install beautifulsoup4
$ pip3 install colorama
$ pip3 install sympy
and
$ git clone https://github.com/kmyk/online-judge-tools
$ cat <<EOF > ~/bin/oj
#!/bin/sh
exec $PWD/online-judge-tools/oj "\$@"
EOF
$ chmod +x ~/bin/oj
```

## How to use

``` sh
$ oj [download,login] URL
$ oj submit URL FILE [-l LANGUAGE]
$ oj test [-c COMMAND] [TEST...]
```

For details, see `--help`.

## Example

``` sh
$ oj download http://agc001.contest.atcoder.jp/tasks/agc001_a
[+] problem recognized: <onlinejudge.atcoder.AtCoder object at 0x7f2925a5df60>
[x] GET: http://agc001.contest.atcoder.jp/tasks/agc001_a
[+] 200 OK

[*] sample 0
[x] input: 入力例 1
2
1 3 1 2
[+] saved to: test/sample-1.in
[x] output: 出力例 1
3
[+] saved to: test/sample-1.out

[*] sample 1
[x] input: 入力例 2
5
100 1 2 3 14 15 58 58 58 29
[+] saved to: test/sample-2.in
[x] output: 出力例 2
135
[+] saved to: test/sample-2.out

[*] sample 2
[x] input: Sample Input 1
2
1 3 1 2
[+] saved to: test/sample-3.in
[x] output: Sample Output 1
3
[+] saved to: test/sample-3.out

[*] sample 3
[x] input: Sample Input 2
5
100 1 2 3 14 15 58 58 58 29
[+] saved to: test/sample-4.in
[x] output: Sample Output 2
135
[+] saved to: test/sample-4.out
```

## License

MIT License
