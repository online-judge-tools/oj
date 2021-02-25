# online-judge-tools/oj

[![test](https://github.com/online-judge-tools/oj/workflows/test/badge.svg)](https://github.com/online-judge-tools/oj/actions)
[![PyPI](https://img.shields.io/pypi/v/online-judge-tools.svg)](https://pypi.python.org/pypi/online-judge-tools)
[![Downloads](https://pepy.tech/badge/online-judge-tools)](https://pepy.tech/project/online-judge-tools)
[![PyPI](https://img.shields.io/pypi/l/online-judge-tools.svg)](https://github.com/kmyk/online-judge-tools/blob/master/LICENSE)
[![Join the chat at https://gitter.im/online-judge-tools/community](https://badges.gitter.im/online-judge-tools/community.svg)](https://gitter.im/online-judge-tools/community)

`oj` is a command to help solving problems on various online judges. This command automates downloading sample cases, generating additional test cases, testing for your code, and submitting it.

## Screencast

![screencast](https://user-images.githubusercontent.com/2203128/34708715-568b13c0-f557-11e7-97ef-9f6b646e4776.gif)

## Features

-   Download sample cases
-   Download system test cases
-   Login
-   Submit your code
-   Test your code
-   Test your code for reactive problems
-   Generate input files from generators
-   Generate output files from input and reference implementation

For the detailed documentation, read [docs/getting-started.md](https://github.com/online-judge-tools/oj/blob/master/docs/getting-started.md).
For Japanese: 日本語バージョンのドキュメントは [docs/getting-started.ja.md](https://github.com/online-judge-tools/oj/blob/master/docs/getting-started.ja.md) にあります。

Many online judges (Codeforces, AtCoder, HackerRank, etc.) are supported.
For the full list, see [the table of online-judge-tools/api-client](https://github.com/online-judge-tools/api-client#supported-websites).

## How to install

The package is <https://pypi.python.org/pypi/online-judge-tools> [![PyPI](https://img.shields.io/pypi/v/online-judge-tools.svg)](https://pypi.python.org/pypi/online-judge-tools).

``` sh
$ pip3 install online-judge-tools
```

For detailed instructions, read [docs/INSTALL.md](https://github.com/online-judge-tools/oj/blob/master/docs/INSTALL.md).
For Japanese: 日本語バージョンのドキュメントは [docs/INSTALL.ja.md](https://github.com/online-judge-tools/oj/blob/master/docs/INSTALL.ja.md) にあります。


## How to use

``` sh
$ oj download [--system] URL
$ oj login URL
$ oj submit [URL] FILE
$ oj test [-c COMMAND] [TEST...]
$ oj test-reactive [-c COMMAND] JUDGE_COMMAND
$ oj generate-input GENERATOR_COMMAND
$ oj generate-output [-c COMMAND] [TEST...]
```

For details, see `$ oj --help`.

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

-   I usually make one directory per one contest (or, site). Can I keep using this style?
    -   Yes, you can use the `--directory` (`-d`) option or `$ rm -rf test/`. However, we don't recommend this style, because you should make additional test cases by yourself and run stress tests to maximize your rating.
-   Can I download all sample cases of all problems at once?
    -   No, but you can use `oj-prepare` command in [kmyk/online-judge-template-generator](https://github.com/kmyk/online-judge-template-generator).
-   Can I automatically compile my source code before testing?
    -   Yes, use your shell. Run `$ g++ main.cpp && oj t`.
-   Can I automatically submit code after it passes tests?
    -   Yes, use your shell. Run `$ oj t && oj s main.cpp`. By the way, you need to take care of problems whose sample cases are not so strong.
-   Can I remove the delays and the `[y/N]` confirmation before submitting code?
    -   Yes, put `--wait=0` option and `--yes` option to `oj s` subcommand. Of course, we don't recommend this. They exist for failsafe. For example, please consider a situation where if you save 3 seconds, you will move up 3 places on the standings. In such a case, if you get a penalty of 5 minutes, then you will move down at least 300 places on the standings.
-   Can I clear my download history to omit the URL of the problem to submit?
    -   Yes, remove the history file, whose name is `download-history.jsonl`.
-   Is my password stored?
    -   Your password is not stored into any files. This program stores only your session tokens (but of course, it's still credentials). Please read [onlinejudge/_implementation/command/login.py](https://github.com/kmyk/online-judge-tools/blob/master/onlinejudge/_implementation/command/login.py).
-   Can I specify problems by their IDs or names, instead of URLs?
    -   No. It may sound nice, but actually, hard to use and maintain.
-   Does the config file exist?
    -   No. You can use your `.bashrc` (or similar files) instead. It's a config file of your shell. Read [man bash](https://linux.die.net/man/1/bash) and write shell aliases or shell functions. For example, if you want to use Python code for tests by default, write `alias oj-test-python='oj t -c "python3 main.py"'` (alias) to `.bashrc` and use `$ oj-test-python`, or write `function oj-test-python() { FILE="$1" ; shift ; oj t -c "python3 '$FILE'" "$@" ; }` (function) and use `oj-test-python main.py`.

For other questions, use [Gitter](https://gitter.im/online-judge-tools/community) [![Join the chat at https://gitter.im/online-judge-tools/community](https://badges.gitter.im/online-judge-tools/community.svg)](https://gitter.im/online-judge-tools/community) or other SNSs.

## Resources

### Articles

in Japanese:

-   [online-judge-toolsを導入しよう！ &#183; ますぐれメモ](https://blog.masutech.work/posts/compro/oj-introduction/)
-   [online-judge-toolsをVimから呼んで楽をする - Leverage Copy](https://maguroguma.hatenablog.com/entry/2020/08/19/090000)
-   [VSCodeでAtCoderのサンプルケースをサクッとテストする - Qiita](https://qiita.com/danpe919/items/7c5697df25fb567f1e71)

### Related Tools

conflicted:

-   [jmerle/competitive-companion](https://github.com/jmerle/competitive-companion)
-   [kyuridenamida/atcoder-tools](https://github.com/kyuridenamida/atcoder-tools)
-   [xalanq/cf-tool](https://github.com/xalanq/cf-tool)
-   [nodchip/OnlineJudgeHelper](https://github.com/nodchip/OnlineJudgeHelper)

not conflicted:

-   [shivawu/topcoder-greed](https://github.com/shivawu/topcoder-greed) for Topcoder Single Round Match
-   [FakePsyho/mmstats](https://github.com/FakePsyho/mmstats) for Topcoder Marathon Match
-   <https://community.topcoder.com/tc?module=Static&d1=applet&d2=plugins>

projects depending on kmyk/online-judge-tools:

1.  wrappers:
    -   [Tatamo/atcoder-cli](https://github.com/Tatamo/atcoder-cli) is a thin wrapper optimized for AtCoder
    -   [kjnh10/pcm](https://github.com/kjnh10/pcm) is a tool which internally uses online-judge-tools
    -   some people use `oj` via Visual Studio Code
1.  libraries using this for CI:
    -   [kmyk/competitive-programming-library](https://kmyk.github.io/competitive-programming-library/) is my library for competitive programming, which uses `oj` via [kmyk/online-judge-verify-helper](https://github.com/kmyk/online-judge-verify-helper)
    -   [beet-aizu/library](https://beet-aizu.github.io/library/) also uses [kmyk/online-judge-verify-helper](https://github.com/kmyk/online-judge-verify-helper)
    -   [blue-jam/ProconLibrary](https://github.com/blue-jam/ProconLibrary) uses `oj` for CI from their own scripts
1.  others:
    -   [kmyk/online-judge-verify-helper](https://github.com/kmyk/online-judge-verify-helper) automates testing your library for competitive programming and generate documents
    -   [kmyk/online-judge-template-generator](https://github.com/kmyk/online-judge-template-generator) analyzes problems and generates templates including auto-generated input/output parts
    -   [fukatani/rujaion](https://github.com/fukatani/rujaion) is an IDE for competitive-programming with Rust

## Maintainers

-   current maintainers
    -   [@kmyk](https://github.com/kmyk) (AtCoder: [kimiyuki](https://atcoder.jp/users/kimiyuki), Codeforces: [kimiyuki](https://codeforces.com/profile/kimiyuki)) (original author)
-   maintainers who are not working now
    -   [@fukatani](https://github.com/fukatani) (AtCoder: [ryoryoryo111](https://atcoder.jp/users/ryoryoryo111))
    -   [@kawacchu](https://github.com/kawacchu) (AtCoder: [kawacchu](https://atcoder.jp/users/kawacchu))

## License

MIT License
