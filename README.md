# online-judge-tools/oj

[![test](https://github.com/online-judge-tools/oj/workflows/test/badge.svg)](https://github.com/online-judge-tools/oj/actions)
[![PyPI](https://img.shields.io/pypi/v/online-judge-tools.svg)](https://pypi.python.org/pypi/online-judge-tools)
[![Downloads](https://pepy.tech/badge/online-judge-tools)](https://pepy.tech/project/online-judge-tools)
[![PyPI](https://img.shields.io/pypi/l/online-judge-tools.svg)](https://github.com/kmyk/online-judge-tools/blob/master/LICENSE)
[![Join the chat at https://gitter.im/online-judge-tools/community](https://badges.gitter.im/online-judge-tools/community.svg)](https://gitter.im/online-judge-tools/community)

[日本語版の `README.md`](https://github.com/online-judge-tools/oj/blob/master/README.ja.md)

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

Many online judges (Codeforces, AtCoder, HackerRank, etc.) are supported.
For the full list, see [the table of online-judge-tools/api-client](https://github.com/online-judge-tools/api-client#supported-websites).

## How to install

The package is <https://pypi.python.org/pypi/online-judge-tools> [![PyPI](https://img.shields.io/pypi/v/online-judge-tools.svg)](https://pypi.python.org/pypi/online-judge-tools).

```console
$ pip3 install online-judge-tools
```

For detailed instructions, read [docs/INSTALL.md](https://github.com/online-judge-tools/oj/blob/master/docs/INSTALL.md).


## How to use

```console
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

```console
$ oj download http://agc001.contest.atcoder.jp/tasks/agc001_a
[INFO] online-judge-tools 11.2.0 (+ online-judge-api-client 10.8.0)
[INFO] load cookie from: /home/user/.local/share/online-judge-tools/cookie.jar
[NETWORK] GET: https://atcoder.jp/contests/agc001/tasks/agc001_a
[NETWORK] 200 OK

[INFO] sample 0
[INFO] input: sample-1
2
1 3 1 2

[SUCCESS] saved to: test/sample-1.in
[INFO] output: sample-1
3

[SUCCESS] saved to: test/sample-1.out

[INFO] sample 1
[INFO] input: sample-2
5
100 1 2 3 14 15 58 58 58 29

[SUCCESS] saved to: test/sample-2.in
[INFO] output: sample-2
135

[SUCCESS] saved to: test/sample-2.out

$ cat <<EOF > main.py
#!/usr/bin/env python3
n = int(input())
a = list(map(int, input().split()))
ans = max(a)
print(ans)
EOF

$ oj t -c "python3 main.py"
[INFO] online-judge-tools 11.2.0 (+ online-judge-api-client 10.8.0)
[INFO] 2 cases found

[INFO] sample-1
[INFO] time: 0.043601 sec
[SUCCESS] AC

[INFO] sample-2
[INFO] time: 0.043763 sec
[FAILURE] WA
input:
5
100 1 2 3 14 15 58 58 58 29

output:
3

expected:
135


[INFO] slowest: 0.043763 sec  (for sample-2)
[INFO] max memory: 10.064000 MB  (for sample-2)
[FAILURE] test failed: 1 AC / 2 cases
```

## FAQ

-   Can I use Python (or Rust, D, Java, F#, Haskell, etc.) instead of C++?
    -   Yes. Please use `--command` (`-c`) option if needed. For example, for Python, you can run `$ oj t -c "python3 main.py"`.
-   I usually make one directory per one contest (or, site). Can I keep using this style?
    -   Yes, you can use the `--directory` (`-d`) option or `$ rm -rf test/`. However, we don't recommend this style, because you should make additional test cases by yourself and run stress tests to maximize your rating.
-   Can I download all sample cases of all problems at once?
    -   No, but you can use `oj-prepare` command in [kmyk/online-judge-template-generator](https://github.com/kmyk/online-judge-template-generator).
-   Can I automatically compile my source code before testing?
    -   Yes, use your shell. Run `$ g++ main.cpp && oj t`.
-   Can I automatically submit code after it passes tests?
    -   Yes, use your shell. Run `$ oj t && oj s main.cpp`. By the way, you need to take care of problems whose sample cases are not so strong.
-   Can I remove the delays and the `[y/N]` confirmation before submitting code?
    -   Yes, put `--wait=0` option and `--yes` option to `oj s` subcommand. Of course, we don't recommend this. These options exist for failsafe. For example, please consider a situation where if you save 3 seconds, you will move up 3 places on the standings. In such a case, if you get a penalty of 5 minutes, then you will move down at least 300 places on the standings.
-   Are my passwords stored?
    -   No, your passwords are not stored into any files. This program stores only your session tokens (but of course, they're still credentials). Please read [`onlinejudge/_implementation/command/login.py`](https://github.com/kmyk/online-judge-tools/blob/master/onlinejudge/_implementation/command/login.py).
-   Does the config file exist?
    -   No. You can use your `.bashrc` (or similar files) instead. It's a config file of your shell. Read [man bash](https://linux.die.net/man/1/bash) and write shell aliases or shell functions. For example, if you want to use Python code for tests by default, write `alias oj-test-python='oj t -c "python3 main.py"'` to `.bashrc` and use `$ oj-test-python`.

For other questions, use [Gitter](https://gitter.im/online-judge-tools/community) [![Join the chat at https://gitter.im/online-judge-tools/community](https://badges.gitter.im/online-judge-tools/community.svg)](https://gitter.im/online-judge-tools/community) or other SNSs.

## Resources

### Related Tools

conflicted:

-   [jmerle/competitive-companion](https://github.com/jmerle/competitive-companion)
-   [kyuridenamida/atcoder-tools](https://github.com/kyuridenamida/atcoder-tools)
-   [xalanq/cf-tool](https://github.com/xalanq/cf-tool)
-   [nodchip/OnlineJudgeHelper](https://github.com/nodchip/OnlineJudgeHelper)

not conflicted:

-   [shivawu/topcoder-greed](https://github.com/shivawu/topcoder-greed) for Topcoder Single Round Match

projects collaborating with kmyk/online-judge-tools:

-   [kmyk/online-judge-template-generator](https://github.com/kmyk/online-judge-template-generator) analyzes problems and generates templates including auto-generated input/output parts
-   [kmyk/online-judge-verify-helper](https://github.com/kmyk/online-judge-verify-helper) automates testing your library for competitive programming and generate documents
-   [Tatamo/atcoder-cli](https://github.com/Tatamo/atcoder-cli) is a thin wrapper optimized for AtCoder
-   [kjnh10/pcm](https://github.com/kjnh10/pcm) is a tool which internally uses online-judge-tools
-   [fukatani/rujaion](https://github.com/fukatani/rujaion) is an IDE for competitive-programming with Rust

## Maintainers

-   current maintainers
    -   [@kmyk](https://github.com/kmyk) (AtCoder: [kimiyuki](https://atcoder.jp/users/kimiyuki), Codeforces: [kimiyuki](https://codeforces.com/profile/kimiyuki)) (original author)
-   maintainers who are not working now
    -   [@fukatani](https://github.com/fukatani) (AtCoder: [ryoryoryo111](https://atcoder.jp/users/ryoryoryo111))
    -   [@kawacchu](https://github.com/kawacchu) (AtCoder: [kawacchu](https://atcoder.jp/users/kawacchu))

## License

MIT License
