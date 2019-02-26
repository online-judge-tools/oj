# Online Judge Tools

[![Travis](https://img.shields.io/travis/kmyk/online-judge-tools/master.svg)](https://travis-ci.org/kmyk/online-judge-tools)
[![Documentation Status](https://readthedocs.org/projects/online-judge-tools/badge/?version=master)](https://online-judge-tools.readthedocs.io/en/master/)
[![PyPI](https://img.shields.io/pypi/pyversions/online-judge-tools.svg)](#)
[![PyPI](https://img.shields.io/pypi/status/online-judge-tools.svg)](#)
[![PyPI](https://img.shields.io/pypi/v/online-judge-tools.svg)](https://pypi.python.org/pypi/online-judge-tools)
[![PyPI](https://img.shields.io/pypi/l/online-judge-tools.svg)](#)
[![Downloads](https://pepy.tech/badge/online-judge-tools)](https://pepy.tech/project/online-judge-tools)
[![Join the chat at https://gitter.im/online-judge-tools/community](https://badges.gitter.im/online-judge-tools/community.svg)](https://gitter.im/online-judge-tools/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Tools for online judge services. Downloading sample cases, Testing/Submitting your code, and various utilities.

## Screencast

![screencast](https://user-images.githubusercontent.com/2203128/34708715-568b13c0-f557-11e7-97ef-9f6b646e4776.gif)

## Features

-   Download sample cases
    -   AtCoder
    -   Yukicoder
    -   Anarchy Golf
    -   Codeforces
    -   HackerRank
    -   Aizu Online Judge
    -   CS Academy
    -   PKU JudgeOnline
    -   Kattis
    -   Toph (Problem Archive)
-   Download system test cases
    -   Yukicoder
    -   Aizu Online Judge
-   Login
    -   AtCoder
    -   Yukicoder (via github.com or [session token](https://github.com/kmyk/online-judge-tools/blob/master/LOGIN_WITH_COOKIES.md))
    -   Codeforces
    -   HackerRank
    -   TopCoder
    -   Toph
-   Submit your solution
    -   AtCoder
    -   Yukicoder
    -   Codeforces
    -   HackerRank
    -   TopCoder (Marathon Match)
    -   Toph (Problem Archive)
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
$ pip3 install lxml
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

It requires Python 3.5 or later now

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

## FAQ

-   I cannot install this tool on my Windows machine. How should I do?
    -   Use Windows Subsystem for Linux (WSL). If your Windows is too and WSL is not supported, you can use virtual machines, MinGW or Cygwin, but you should buy a new machine.
-   Are there features to manage templates or snippets?
    -   No. They are not the responsibility of this tool. You should use plugins of your editor, like [thinca/vim-template](https://github.com/thinca/vim-template) or [Shougo/deoplete.nvim](https://github.com/Shougo/deoplete.nvim).
-   I usually make one directory per one contest (or, site). Is there a support for this style?
    -   Yes. You can use `--directory` (`-d`) option. However, I recommend to make one directory per one problem.
-   Can I specify problems by their IDs or names, instead of URLs?
    -   No. I have tried it once, but it is actually not so convenient and only increases the maintenance cost.
-   I don't want to give my password to this program.
    -   You can use this giving only your session tokens. Please see [here](https://github.com/kmyk/online-judge-tools/blob/master/LOGIN_WITH_COOKIES.md).

For other questions, use [Gitter](https://gitter.im/online-judge-tools/community) or other SNSs.

## Related Tools

conflicted:

-   [dj3500/hightail](https://github.com/dj3500/hightail) (GUI-based; I have never used)
-   [nodchip/OnlineJudgeHelper](https://github.com/nodchip/OnlineJudgeHelper) (buggy, not recommended)

not conflicted:

-   [shivawu/topcoder-greed](https://github.com/shivawu/topcoder-greed) for TopCoder Single Round Match
-   [FakePsyho/mmstats](https://github.com/FakePsyho/mmstats) for TopCoder Marathon Match
-   <https://community.topcoder.com/tc?module=Static&d1=applet&d2=plugins>

## License

MIT License
