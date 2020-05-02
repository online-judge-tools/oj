# Online Judge Tools

[![test](https://github.com/online-judge-tools/oj/workflows/test/badge.svg)](https://github.com/online-judge-tools/oj/actions)
[![Documentation Status](https://readthedocs.org/projects/online-judge-tools/badge/?version=master)](https://online-judge-tools.readthedocs.io/en/master/)
[![PyPI](https://img.shields.io/pypi/v/online-judge-tools.svg)](https://pypi.python.org/pypi/online-judge-tools)
[![Downloads](https://pepy.tech/badge/online-judge-tools)](https://pepy.tech/project/online-judge-tools)
[![PyPI](https://img.shields.io/pypi/l/online-judge-tools.svg)](https://github.com/kmyk/online-judge-tools/blob/master/LICENSE)
[![Join the chat at https://gitter.im/online-judge-tools/community](https://badges.gitter.im/online-judge-tools/community.svg)](https://gitter.im/online-judge-tools/community)

Tools to help solving problems on various online judges. This automates downloading sample cases, generating additional test cases, testing for your code, and submitting it.

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

Many online judges (Codeforces, AtCoder, HackerRank, etc.) are supported.
For details, see [the table of online-judge-tools/api-client](https://github.com/online-judge-tools/api-client#supported-websites).

## How to install

The package is <https://pypi.python.org/pypi/online-judge-tools> [![PyPI](https://img.shields.io/pypi/v/online-judge-tools.svg)](https://pypi.python.org/pypi/online-judge-tools).

``` sh
$ pip3 install online-judge-tools
```

For detailed instructions, read [the FAQ](#faq).


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

### I cannot install online-judge-tools. What is `$ pip3 install online-judge-tools`? Please help!

Do following steps.

1.  If you use a Windows environment, use [Windows Subsystem for Linux (WSL)](https://docs.microsoft.com/en-us/windows/wsl/about). For beginners, Linux (especially, Ubuntu) is often easier than Windows.
    -   Also, if you use Visual Studio Code (or other IDEs), close it and forget it for a while. Don't use consoles in IDEs.
1.  :snake: Install [Python](https://www.python.org/). If you use Ubuntu (including Ubuntu in WSL), run `$ sudo apt install python3`.
1.  Check your Python with running `$ python3 --version`. If it says `Python 3.x.y`, it's OK.
    -   If it says something like `Command 'python3' not found`, you have failed to install Python.
    -   If the version of Python is too old, it's not OK. The `x` must be greater than or equal to `5`. If `x` is lower than `5`, upgrade your Python.
1.  :package: Install [pip](https://pip.pypa.io/en/stable/). If you use Ubuntu (including Ubuntu in WSL), run `$ sudo apt install python3-pip`.
1.  Check your pip with running `$ pip3 --version`. If it says something like `pip x.y.z ...`, it's OK.
    -   If it says something like `Command 'pip3' not found`, you have failed to install pip.
    -   Even if `pip3` is not found, you may be able to use `python3 -m pip` instead of `pip3`. Try `$ python3 -m pip --version`. If it says `pip x.y.z ...`, it's OK.
    -   Don't use `pip` or `pip2`. Use `pip3`.
1.  :dart: Run `$ pip3 install online-judge-tools` to install online-judge-tools. If it says `Successfully installed online-judge-tools-x.y.z` (or, `Requirement already satisfied: online-judge-tools`), it's OK.
    -   If it says `Permission denied`, run `$ sudo pip3 install online-judge-tools` or `$ pip3 install --user online-judge-tools`.
1.  Check online-judge-tools with `$ oj --version`. If It must say something like `online-judge-tools x.y.z`.
    -   If it says something like `Command 'oj' not found`, you need to set [`PATH`](https://en.wikipedia.org/wiki/PATH_%28variable%29).
        1.  Find the path of the `oj` file with running `$ find / -name oj 2> /dev/null`. The file is often at `/home/ubuntu/.local/bin/oj` or `/usr/local/bin/oj`.
        1.  Check the found `oj` file is actually `oj`, with running `$ /home/ubuntu/.local/bin/oj --version`.
        1.  Add the directory which contains the `oj` to your `PATH`. For example, if `oj` is `/home/ubuntu/.local/bin/oj`, write `export PATH="/home/ubuntu/.local/bin:$PATH"` in the end of `~/.bashrc`.
            -   Don't write `export PATH="$PATH:/home/ubuntu/.local/bin/oj"`. It's not a directory.
            -   If you don't use bash, write a right settings to the right file depending on your shell. For example, if you use Mac OS, your shell might zsh. For zsh, write the same command to `~/.zshrc`.
        1.  Reload the configuration with `source ~/.bashrc`.
            -   If you don't use bash, use an appropriate way.
        1.  Check your `PATH` with `$ echo $PATH`. If it says `/home/ubuntu/.local/bin:...`, it's OK.
    -   If it says something like `ModuleNotFoundError: No module named 'onlinejudge'`, you have failed to install online-judge-tools and your environment is broken. Run `$ pip3 install --force-reinstall online-judge-tools` to reinstall.
    -   If it says something like `SyntaxError: invalid syntax`, you have used `pip2` by mistake. Run `$ pip2 uninstall online-judge-tools`, and retry to install.
1.  That's all.

If you couldn't read many sentences of above instructions (e.g. if you didn't know what "run `$ python3 --version`" means), please ask your friends for help.
If you cannot install online-judge-tools even following the instructions, please add comments to [this issue](https://github.com/kmyk/online-judge-tools/issues/717).

### Other questions

-   I usually make one directory per one contest (or, site). Can I keep using this style?
    -   Yes, you can use the `--directory` (`-d`) option. However, we don't recommend this style, because you should make additional test cases by yourself and run stress tests to maximize your rating.
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

## Related Tools

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


## Contributing

See [CONTRIBUTING.md](https://github.com/kmyk/online-judge-tools/blob/master/CONTRIBUTING.md)

### Hall-Of-Fame

[![](https://sourcerer.io/fame/kmyk/kmyk/online-judge-tools/images/0)](https://sourcerer.io/fame/kmyk/kmyk/online-judge-tools/links/0)[![](https://sourcerer.io/fame/kmyk/kmyk/online-judge-tools/images/1)](https://sourcerer.io/fame/kmyk/kmyk/online-judge-tools/links/1)[![](https://sourcerer.io/fame/kmyk/kmyk/online-judge-tools/images/2)](https://sourcerer.io/fame/kmyk/kmyk/online-judge-tools/links/2)[![](https://sourcerer.io/fame/kmyk/kmyk/online-judge-tools/images/3)](https://sourcerer.io/fame/kmyk/kmyk/online-judge-tools/links/3)[![](https://sourcerer.io/fame/kmyk/kmyk/online-judge-tools/images/4)](https://sourcerer.io/fame/kmyk/kmyk/online-judge-tools/links/4)[![](https://sourcerer.io/fame/kmyk/kmyk/online-judge-tools/images/5)](https://sourcerer.io/fame/kmyk/kmyk/online-judge-tools/links/5)[![](https://sourcerer.io/fame/kmyk/kmyk/online-judge-tools/images/6)](https://sourcerer.io/fame/kmyk/kmyk/online-judge-tools/links/6)[![](https://sourcerer.io/fame/kmyk/kmyk/online-judge-tools/images/7)](https://sourcerer.io/fame/kmyk/kmyk/online-judge-tools/links/7)

For the full list of contributors, see [CHANGELOG.md](https://github.com/kmyk/online-judge-tools/blob/master/CHANGELOG.md) or [the contributors page](https://github.com/kmyk/online-judge-tools/graphs/contributors) of GitHub.

### maintainers

-   [@kmyk](https://github.com/kmyk) (AtCoder: [kimiyuki](https://atcoder.jp/users/kimiyuki), Codeforces: [kimiyuki](https://codeforces.com/profile/kimiyuki)) (owner)
-   [@fukatani](https://github.com/fukatani) (AtCoder: [ryoryoryo111](https://atcoder.jp/users/ryoryoryo111)) (collaborator)
-   [@kawacchu](https://github.com/kawacchu) (AtCoder: [kawacchu](https://atcoder.jp/users/kawacchu))

## License

MIT License
