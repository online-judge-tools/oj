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
WIPなPRはコードをベースに議論していくことができるという点で有用です。

# Internal Structure / 内部構造

## philosophy of design / 設計の方針

online-judge-tools の目的はまず第一に「コンテストで上位を取ることに役立つこと」です。
これを実現する手段として「手動だと間違えたりさぼったりしやすい作業を自動化する」を用いています。

また、「ペナルティを出させないこと」に注力しています。
Web scraping をする性質により動作は必然的に不安定であり、これは「ペナルティを出させないこと」の壁となります。
これへの対応として「誤動作の起こりやすい機能は避ける」「誤動作があったときに誤動作があると気付きやすいようにする」などを重要視しています。
その実践の例としては「取得したサンプルケースを(ファイルに出力するだけでなく)画面に見やすく表示する」が分かりやすいでしょう。
そのような画面への出力がない場合、サンプルケースの取得ミスはかなりの時間のロスを引き起すことが知られています。

さて、「ある罠を回避するための設計」のようなものはその罠について知っていないと理解しにくいです。
どのような理由でそのような設計にしたかについては、そのようにしなかったらどうなるかを含めて後の節で詳細に説明します。
ところでそれらの「自然に実装すると陥りがちな罠」についての知識は主に、先発のプロジェクトである [nodchip/OnlineJudgeHelper](https://github.com/nodchip/OnlineJudgeHelper) の利用やこれへのコントリビュートの過程で得られたものです。
online-judge-tools は OnlineJudgeHelper を参考にしてその欠点を改善しつつ書かれたものであり、感謝の気持ちがあることを表明しておきます。

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
$ isort --recursive onlinejudge tests
$ yapf --in-place --recursive onlinejudge tests
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

GitHub Actions から PyPI 上へ upload を仕掛けるように設定されています。

手順:

1.  `onlinejudge/__about__.py` 中の `__version_info__` の値を bump して commit する
    -   このとき同時に `CHANGELOG.md` も修正する
    -   メンテナ以外のコントリビュータからpull requests をもらっていた場合は、その作成者の名前を `CHANGELOG.md` に併記する
2.  GitHub release のページから release を生成する
    -   これにより Travis CI の機能が呼び出され PyPI への upload がなされる
    -   説明文には `CHANGELOG.md` に書いたものをコピペする

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
1.  update `README.md` (Add Features description)

## detailed description of philosophy of design / 設計の方針の詳しい説明

### 重要: 取得したサンプルケースはきちんと表示する

サンプルケースを自動で取得するプログラムを使うとき、ユーザは取得された結果のサンプルケースをきちんとすべて確認するでしょうか？
ほぼ確実に、そのような面倒なことはしないと思います。
さてもしそのようなとき、取得されたサンプルケースの内容が画面に表示されず、かつ実は取得結果が間違っていたとすれば、事故が起こります。
具体的には、絶対に通らないサンプルケースをそうと気づかず通そうとして頑張り続けて 10 分から最大で 1 時間ほどが失われる、という結果になります。
これは実際に複数回発生した事態であることを強調しておきます。これが起こると本当につらいです。
ですので、もし何かが壊れていたとき、ユーザがそうと気づけるようにします。

ところでこの問題はサンプルケース取得の精度を上げることでは解決しません。
たとえば AtCoder などは「サンプルケースは作問者が手で HTML を操作して表示させている」ようなので、どう実装をしても稀に取得に失敗することは回避できません。
そして精度が上がってサンプルケース取得の失敗の頻度が下がれば下がるほど、滅多にない事態であるところの取得失敗に気づくための時間は増えるためです。

### 一般論: HTMLの解析に正規表現を使ってはいけない

とても有名なアンチパターンです。
HTML パーサを使うのが適切です。

### 一般論: テストを書き、CIを回す

テストはできるだけ書くようにします。
テストがあってもバグは残るのに、テストがなければもちろんバグだらけです。

### 一般論: 何か怪しい状況ならプログラムを適切に異常終了させる

プログラムが実は壊れたままそうと走り続けることほど怖いことはありません。
嘘を出力する可能性があるぐらいなら早めに停止させます。

幸いにも、online-judge-tools は突然動かなくなっても致命的な結果にはなりません。

### 一般論: 必要十分な表示をする

プログラムがいま何をしているかをユーザに伝えることは重要です。
いま何をどのように処理していてどれくらいまで進んだのかが分からないと、本当に処理が進んでいるのか不安になりやすく、また長時間待たされているように感じられるためです。

ただし、大量の表示をすることは避けます。そのほとんどはユーザの視界に入らず、重要な表示が隠されてしまうだけだからです。

### 一般論: 自然な振舞いをさせる

プログラムの動作に驚きは必要ありません。
一般的な慣習に従い、そう動くと自然に予想される通りに動くような、つまらないプログラムを書くようにします。
一見便利そうな機能は、実装してみると単なるお節介でしかなかったりするので注意していきましょう。

### 一般論: 破壊的変更を避ける

いままで動いていたコードが何もしていないのに急に動かなくなるのはかなり不快です。
破壊的変更が必要な場合も、semantic versioning に従って適切なバージョン番号を付けます。

コマンドラインオプションなら基本的に人間が使うものなのである程度の融通は効きますが、online-judge-tools は競プロ用ライブラリの CI などからも利用されていることには注意します。

### 不要な機能は作らず、消す

ほとんど使われていない機能というのは、バグが残りがちなだけでなく、コードを膨らませ可読性を落とし、ただ存在するだけでもユーザにとっての選択肢を無闇に増やし混乱を生みます。
消すべきと判断したなら消してしまうようにします。
もちろん「破壊的変更を避ける」こととは相反しますし、「消すべきかどうか」の判断は難しいですが、うまくやっていきましょう。

また、そもそも不要な機能を実装しないのが最善です。
「ないよりはあった方がいいかもね」ぐらいの気持ちで無闇にすべての要望を受け入れることはせず、プルリクエストが来てももし reject するべきだと判断すればきちんと reject するようにします。

### 設定ファイルを作ることを避ける

一般に、設定ファイルという機能を作るとどんどん機能が増えます。
機能が増えるとテストのコストが増え、バグも増えます。
そういうものが必要なときはコマンドラインオプションで対応できないか検討するようにします。
そもそも何も設定しなくてもいい感じに動くのが最善なので、これを目指していきましょう。

加えて、状態を持つことも避けたいです。
プログラムの振舞いはできるだけ与えられたコマンドだけから予測できるようにします。
今まで動いていたプログラムが動かなくなったとき、設定ファイルの中でミスをしていたり壊れたデータがキャッシュの中に残っていることが原因であることは多いですが、この方針はそのような理由での不具合を防ぎます。
ただし、提出先 URL の推測は利便性と安全性のための例外となっています。

もちろんこれらは開発リソースが潤沢なら選択肢に入るでしょうが、おそらく online-judge-tools に関連する別プロジェクトとして開発するのがよいでしょう。

### 特定のコンテストサイトに特有の設計を避ける

コンテストに個別の要素を含む機能については、どんな機能を追加するにせよまず特定のコンテストサイトで動作させ、次に対応するコンテストサイトを増やしていくことになると思います。
このとき、最初からできるだけ一般的な枠組みを考えます。

この種類でよくあるのはユーザに問題を指定させるときに AtCoder のみを想定し `$ oj download ABC123 D` のように「コンテスト ID + アルファベット」を要求することだと思われます。
この形式では Codeforces や AOJ にも対応することが不可能です。
AtCoder だけに限っても、コンテスト ID と問題 ID とアルファベットの間に (傾向はあるにせよ) 特に規則が存在せず問題ページの URL を復元することが困難であること、やたら長いコンテスト ID や問題 ID が存在することなどが問題となります。
単に問題をその URL によって指定させればこれらの問題はすべて消えます。

また、ログイン処理には HTML のフォームを読んでリクエストを投げるのではなく、Selenium などの一般的な機構を使うことをおすすめします。
ログイン処理の周辺は OAuth や不正ログイン対策などによりかなり複雑でかつ頻繁に変更が発生し、しかも頻繁に使う機能ではないのでバグに気づきにくいためです。

### 特定の流儀に特有の設計を避ける

できるだけ中立で単純あるいは一般的な方式を採用します。
下手な方式を選んでしまうと、別の方式にも対応したくなってしまい、コードが肥大化します。

具体的には、問題ごとのテストケースの置き場所とファイル名、コンテストごとや問題ごとなどのディレクトリ構造、スペシャルジャッジのためのジャッジプログラムの仕様、などが問題になります。

### コンテストごとでなく問題ごとに処理する

あるコンテストの問題のサンプルケースをまとめて取得するといった機能を追加する際には、注意深い設計が必要です。
主にすでに説明した方針「取得したサンプルケースはきちんと表示する」「特定の流儀に特有の設計を避ける」に違反するためです。

サンプルケース取得の精度ももはや十分高いですし、利便性の意味では価値があると思いますが、おそらく online-judge-tools に関連する別プロジェクトとして開発するのがよいでしょう。

### 特定のプログラミング言語に依存するような機能の追加を避ける

たとえば、ある機能があり、それが C++ と Python に対応したものであるとしましょう。
しばらくすると Rust や F# にも対応させてほしいという要望が上がるでしょうし、それに対応しても次の言語が待っています。
対応言語すべてについてテストをするためには対応言語すべての環境構築をする必要があるなど、メンテナンスコストの問題が発生し、当然バグも発生しやすくなります。
よって、もしそのようなものが必要だとしても、主要な少数の言語以外への対応は積極的に拒否していくか、汎用的な機構と特定の言語に対応して設定ファイルなどという形にうまくまとめて本体のコード中には特定のプログラミング言語の名前が現れないものを目指します。

そのような機能は面白くかつ価値のあるものであることが多いですが、おそらく online-judge-tools に関連する別プロジェクトとして開発するのがよいでしょう。
