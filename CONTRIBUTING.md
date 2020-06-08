#  Contribution and Hacking Guide

## For committer of this online-judge-tools

-   See also the [CONTRIBUTING.md](https://github.com/online-judge-tools/.github/blob/master/.github/CONTRIBUTING.md) of this GitHub organization.
-   The code to interact with web servers of online judges exist in [online-judge-tools/api-client](https://github.com/online-judge-tools/api-client) repository.

## For developpers of programs which uses online-judge-tools

TL;DR: Use [online-judge-tools/api-client](https://github.com/online-judge-tools/api-client).

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
