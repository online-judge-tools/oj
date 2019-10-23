# Contribute Guide / 開発を手伝ってくれる人へ

TODO: translate this document to English

## language / 言語について

In the source code and documents for end users, we should use English.
For other place, both English and Japanese are acceptable.

ソースコード中とエンドユーザが目にする部分はすべて英語で書いてください。
それ以外の部分は英語でも日本語でもかまいません。

## issues / issue について

Not only sending Pull Requests, feature requests and bug reports are welcome.

機能要求やバグ報告は気軽にしてください。
コードを書くことだけが開発ではありません。

## pull requests / プルリクについて

PR is always welcome.

However, please note that PR is not always merged as it is.
To improve PR quality, reviewers may ask you change requests.

-   Create your branch from `master`.
-   Test your PR branch on local by `pytest tests/*.py -v`.
-   Write code easy to understand.
    -   Don't make diff which is unnecessary for the purpose of PR.
    -   Split commits appropriately.
    -   Comment on the code where you are not confident of.
-   If you want to add a feature, it would be better to discuss before writing code.
    -   because your feature is not always merged.
    
Even if your code is not complete, you can send a pull request as a work-in-progress PR by putting the [WIP] prefix to the PR title.
If you write a precise explanation about the PR, maintainers and other contributors can join the discussion about how to proceed the PR.
WIP PR is also useful to have discussions based on a concrete code.

基本的にはどんなものでも歓迎します。

ただし常にそのまま merge されるとは限らないので注意してください。
なにかまずいところがあっても修正を要求するだけなので質は問いません (なにか分からないところがあればとりあえずできたところまでで投げてくれてもよいです) が、以下に従っておくと merge されるまでの時間は短くなるでしょう。

-   `master`ブランチからブランチを切る
-   手元でテストをする (`pytest tests/*.py -v` を実行する)
    -   CI が通らない限りは merge はできません
-   レビュアーにやさしいコードを書く
    -   変更箇所はPRの目的に沿った必要最低限のものにする
    -   commit は適切に分割する
    -   怪しげなところにはコメントを書いておく
-   機能追加をする場合は事前に確認をする
    -   「そういう機能は入れません」で弾かれてせっかくの実装が無駄になるとお互いに不幸なためです

もしあなたのPRが完成されていない場合でも、[WIP]とタイトルにつけてPRを送って頂いて構いません。
やりたいことをわかりやすくかいていただければ、メンテナや他の開発者がどうやってマージまで進めていくか相談に乗ることができます。
WIPなPRはコードをベースに議論していくこたができるという点で有用です。

# Internal Structure / 内部構造

## philosophy of design / 設計の方針

第一義は「コンテストで上位を取ることに役立つこと」です。
これを実現する手段として「手動だと間違えたりさぼったりしやすい作業を自動化する」を用いています。

また、「ペナルティを出させないこと」に注力しています。
Web scraping をする性質により動作は必然的に不安定であり、これは「ペナルティを出させないこと」の壁となります。
これへの対応として「誤動作の起こりやすい機能は避ける」「誤動作があったときに誤動作があると気付きやすいようにする」などを重要視しています。
その実践の例としては「取得したサンプルケースを(ファイルに出力するだけでなく)画面に見やすく表示する」が分かりやすいでしょう。
そのような画面への出力がない場合、サンプルケースの取得ミスはかなりの時間のロスを引き起すことが知られています。

## module structure

The structure is as follows:

-   `onlinejudge/`
    -   `type.py`: contains all 
    -   `dispatch.py`: resolves classes from URL
    -   `implementation/`
        -   `main.py`
        -   `command/`: has the bodies of commands like `download`, `submit`, etc.
            -   `download.py`
            -   `submit.py`
            -   ...
    -   `service/`: has classes for services like AtCoder, Codeforces, etc.
        -   `atcoder.py`
        -   `codeforces.py`
        -   ...
-   `tests/`

## install

You can install online-judge-tools from your local directory with the following command.

``` sh
$ pip install -e .[dev,docs]
```

## formatter

We use `isort` and `yapf`.
You can run them with the following commands:

``` sh
$ isort --recursive oj onlinejudge
$ yapf --in-place --recursive oj onlinejudge
```

The line width is set as infinity.

## tests

We use static type checking and unit testing.
You can run them with the following commands:

``` sh
$ mypy onlinejudge setup.py tests
$ pylint --disable=all --enable=unused-import onlinejudge
$ pytest tests/*.py -v  # if you use linux
```

If you use Windows PowerShell:
``` sh
$ pytest -v $(dir tests/*.py | % {$_.FullName})
```

When developing, it is easy to run the test separately for each module.
You can run tests of downloading AtCoder with the following commands:

``` sh
$ pytest tests/command_download_atcoder.py -v
```

## CI

Travis CI and AppVeyor will run automatically when you commit or send PR on `master` or `develop` branch.
The same test as that by `python3 setup.py test` is executed.

`master` `develop` に関する commit や pull request について CI が走ります。
`python3 setup.py test` の実行によるものと同等のテストが行われます。

## Measurement Test Coverage

Coveralls will run when CI passed on your PR.
For reliability, higher test coverage is desirable. 
Therefore, when you add a new feature and but unittests are not covered your feature, reviewers may ask you to add unittests to increase test coverage.

We also welcome PR to add unittests for uncovered areas.
However, there are some areas that are not covered due to the difficulty of testing on CI, such as features that require login.

## deployment

Travis CI から PyPI 上へ upload を仕掛けるように設定されています。

手順:

1.  `onlinejudge/__about__.py` 中の `__version_info__` の値を bump して commit する
    -   このとき同時に `CHANGELOG.md` も修正する
    -   pull requests をもらっていた場合は、その作成者の名前を `readme.md` にある一覧へ追加する
    -   例: [3a24dc](https://github.com/kmyk/online-judge-tools/commit/3a24dc64b56d898e387dee56cf9915be3ab0f7e2)
2.  `v0.1.23` の形で Git tag を打って GitHub 上へ push する
    -   これにより Travis CI の機能が呼び出され PyPI への upload がなされる
    -   これにより AppVeyor の機能が呼び出され GitHub release の生成とその assets への実行ファイル `oj.exe` の追加がなされる
3.  GitHub release のページから、生成された release を編集して説明文を加える
    -   `CHANGELOG.md` に書いたものをコピペするとよい

## how to add a new contest platform / 対応サービスの追加の手順

Short version: see files for other platforms like `onlinejudge/service/poj.py` or `onlinejudge/service/codeforces.py`, and `tests/command_download_hackerrank.py` or `https://github.com/kmyk/online-judge-tools/blob/master/tests/command_submit.py` for tests

Long version:

1.  make the file `onlinejudge/service/${NAME}.py`
1.  write the singleton class `${NAME}Service` inheriting `onlinejudge.type.Service`
    -   You must implement at least methods `get_url()` `get_name()` and `cls.from_url()`, and you can ignore others.
1.  write the class `${NAME}Problem` inheriting `onlinejudge.type.Problem`
    -   You must implement at least methods `download_sample_cases()` `get_url()` `get_service()` and `cls.from_url()`, and you can ignore others.
1.  register the classes to the lists `onlinejudge.dispatch.services` and `onlinejudge.dispatch.problems`
1.  register the module to the `onlinejudge/service/__init__.py`
1.  write tests for your platform
    -   You should make `tests/command_download_${NAME}.py` and/or append to `tests/command_submit.py`. Please see other existing tests.
