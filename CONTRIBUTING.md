## CONTRIBUTING.md

Pull Requests are welcome.
Even just Issues are also helpful, since this often become broken while I didn't recognize.
This program is fragile for the nature that it depends on others' web-services.

in Japanese:
Pull Requestは歓迎します。
Issueだけでも十分助かります。
自分の管理下にないWebサービスに接続しに行くという性質により、このプログラムは何もしなくても勝手に壊れてたりするためです。
言語は英語か日本語ならどちらでもよいです。
twitter経由で連絡してくれても構いませんがOSS感でるのでGitHub上でやるのがおすすめです。
メンテを手伝ってくれる人がいたら喜びます。

### source map

NOTE: this description may be old.

-   `onlinejudge/`
    -   `__init__.py`
    -   `service.py` defines an abstract class `Service` for top-level of online judges
    -   `problem.py` defines an abstract class `Problem`
    -   `submission.py` defines an abstract class `Submission`
    -   `dispatch.py` provides functions from URL to classes corresponding to the given URL
    -   files for individual online judges
        -   `atcoder.py`
        -   `codeforces.py`
        -   `topcoder.py`
        -   `yukicoder.py`
        -   `aoj.py`
        -   `anarchygolf.py`
        -   `hackerrank.py`
        -   `csacademy.py`
    -   (they are a little bit undocumented and not well-typed. refactoring is needed)
    -   `implementation/`
        -   `__init__.py`
        -   `main.py` has the entry point and help documents
        -   `version.py`
        -   `logging.py`
        -   `utils.py`
        -   `command/` contains 
            -   `__init__.py`
            -   `login.py`
            -   `download.py`
            -   `test.py` contains functions for `test` sub-command (and also `generate-output` sub-command; I should make `generate_output.py`)
            -   `submit.py`
            -   `test_reactive.py`
            -   `generate_scanner.py`
            -   `split_input.py`
            -   `code_statistics.py`
            -   `get_standings.py`
-   `tests/`
    -   `__init__.py`
    -   `download_aoj.py`
    -   `download_atcoder.py`
    -   `download_yukicoder.py`
    -   `download.py` for other services
    -   `code_statistics.py`
    -   `generate_scanner.py`
    -   `yukicoder.py`  (for API of yukicoder)
    -   (tests for other sub-commands are not written yet)
