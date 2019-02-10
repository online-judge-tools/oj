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

-   Test your PR branch on local by `python3 setup.py test`.
-   Write friendly code to the reviewers.
    -   Diffs need to be limited to the PR purpose.   
    -   Split commits appropriately.
    -   Comment on the code where you are not confident of.
-   If you want to add feature, it is desirable discuss in advance that before writing code.

基本的にはどんなものでも歓迎します。

ただし常にそのまま merge されるとは限らないので注意してください。
なにかまずいところがあっても修正を要求するだけなので質は問いません (なにか分からないところがあればとりあえずできたところまでで投げてくれてもよいです) が、以下に従っておくと merge されるまでの時間は短くなるでしょう。

-   手元でテストをする (`python3 setup.py test` を実行する)
    -   CI が通らない限りは merge はできません
-   レビュアーにやさしいコードを書く
    -   変更箇所は必要最低限にする
    -   commit は適切に分割する
    -   怪しげなところにはコメントを書いておく
-   機能追加をする場合は事前に確認をする
    -   「そういう機能は入れません」で弾かれてせっかくの実装が無駄になるとお互いに不幸なためです


# Internal Structure / 内部構造

## philosophy of design / 設計の方針

Our first purpose is "to help get the top in the programming contests".
Especially, we are focusing on "online-judge-tools does not cause the penalties".
To make it possible, online-judge-tools automates "mistakable manual work".

第一義は「コンテストで上位を取ることに役立つこと」です。
特に「ペナルティを出させないこと」に注力しています。
これを実現する手段として「手動だと間違えたりさぼったりしやすい作業を自動化する」を用いています。

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

## formatter

We use `isort` adn `yapf`.
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
$ mypy oj onlinejudge
$ python3 setup.py test
```

テストは開発の際には機能ごとに単体で実行すると楽です。
例えば `download` コマンドの AtCoder に関してのテストの実行は次でできます。

```
$ python3 setup.py test -s tests.command_download_atcoder.DownloadAtCoderTest
```

なお `python3 setup.py test` は formatter が利用されているかの確認もするように設定されています。

## CI

`master` `develop` に関する commit や pull request について CI が走ります。
`python3 setup.py test` の実行でも同等の処理が行われるように設定されているので、手元でこれを実行しているなら気にする必要はありません。

## deployment

Travis CI から PyPI 上へ upload を仕掛けるように設定されています。

手順:

1.  `onlinejudge/__about__.py` 中の `__version_info__` の値を bump して commit する
    -   このとき同時に `CHANGELOG.md` も修正する
    -   例: [3a24dc](https://github.com/kmyk/online-judge-tools/commit/3a24dc64b56d898e387dee56cf9915be3ab0f7e2)
2.  `v0.1.23` の形で Git tag を打って GitHub 上へ push する
    -   これにより Travis CI の機能が呼び出され PyPI への upload がなされる

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
