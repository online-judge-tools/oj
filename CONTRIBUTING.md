#  Contribution and Hacking Guide

links:

-   [CONTRIBUTING.md](https://github.com/online-judge-tools/.github/blob/master/CONTRIBUTING.md) of [online-judge-tools](https://github.com/online-judge-tools) organization
-   [DESIGN.md](https://github.com/online-judge-tools/oj/blob/master/DESIGN.md)


## For committer of `oj` command / `oj` コマンド本体への貢献者へ

-   See also the [CONTRIBUTING.md](https://github.com/online-judge-tools/.github/blob/master/CONTRIBUTING.md) of this GitHub organization. / この GitHub organization の [CONTRIBUTING.md](https://github.com/online-judge-tools/.github/blob/master/CONTRIBUTING.md) も読んでください。
-   See also the [DESIGN.md](https://github.com/online-judge-tools/oj/blob/master/DESIGN.md) of this repository, if possible. / 可能なら、この repository の [DESIGN.md](https://github.com/online-judge-tools/oj/blob/master/DESIGN.md) も読んでください。
-   The code to interact with web servers of online judges exist in [online-judge-tools/api-client](https://github.com/online-judge-tools/api-client) repository. / オンラインジャッジのサーバと直接通信するコードは [online-judge-tools/api-client](https://github.com/online-judge-tools/api-client) レポジトリにあります。


## For developpers of programs which uses `oj` command / `oj` コマンドを用いたツールの開発者へ

TL;DR: Use [online-judge-tools/api-client](https://github.com/online-judge-tools/api-client) instead for programs. / プログラムからの利用には代わりに [online-judge-tools/api-client](https://github.com/online-judge-tools/api-client) を使ってください

There are many ways to use online-judge-tools for your tool.

1.  `oj-api` command (in [online-judge-tools/api-client](https://github.com/online-judge-tools/api-client))
    -   `oj-api` command is the best choice in most cases because it makes things loose coupling and has .
    -   You should also check [jmerle/competitive-companion](https://github.com/jmerle/competitive-companion).
    -   Now, there are some missing features in `oj-api` command (e.g. logging in via web browsers). So you may need to use `oj` command for such features.
1.  [`onlinejudge` module](https://online-judge-tools.readthedocs.io/) of Python (in [online-judge-tools/api-client](https://github.com/online-judge-tools/api-client))
    -   `onlinejudge` module is the most flexible interface, but it makes tight coupling. You should avoid it unless you really need to optimize.
1.  `oj` command
    -   `oj` command is basically an interface to humans, not to programs. You can use this for your tool, but please be careful.
    -   You can re-implement the core functionality of any subcommand of `oj` command with a single-line shell script.
