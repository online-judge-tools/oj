# online-judge-tools/oj

[![test](https://github.com/online-judge-tools/oj/workflows/test/badge.svg)](https://github.com/online-judge-tools/oj/actions)
[![PyPI](https://img.shields.io/pypi/v/online-judge-tools.svg)](https://pypi.python.org/pypi/online-judge-tools)
[![Downloads](https://pepy.tech/badge/online-judge-tools)](https://pepy.tech/project/online-judge-tools)
[![PyPI](https://img.shields.io/pypi/l/online-judge-tools.svg)](https://github.com/kmyk/online-judge-tools/blob/master/LICENSE)
[![Join the chat at https://gitter.im/online-judge-tools/community](https://badges.gitter.im/online-judge-tools/community.svg)](https://gitter.im/online-judge-tools/community)

[English version of `README.md`](https://github.com/online-judge-tools/oj/blob/master/README.md)

`oj` コマンドは様々なオンラインジャッジの問題を解くことを助けるツールです。
このコマンドは、サンプルケースの取得、追加のテストケースの生成、テストの実行、コードの提出などを自動化します。

## Screencast

![screencast](https://user-images.githubusercontent.com/2203128/34708715-568b13c0-f557-11e7-97ef-9f6b646e4776.gif)

## Features

-   サンプルケースを取得
-   システムケースを取得
-   ログイン
-   コードを提出
-   テストを実行
-   リアクティブ問題のテストを実行
-   テストケース生成器からテストケースの入力を生成
-   テストケースの入力と愚直解からテストケースの出力を生成

詳しいドキュメントは [docs/getting-started.ja.md](https://github.com/online-judge-tools/oj/blob/master/docs/getting-started.ja.md) にあります。

様々なオンラインジャッジ (Codeforces, AtCoder, HackerRank など) をサポートしています。
その完全なリストには [the table of online-judge-tools/api-client](https://github.com/online-judge-tools/api-client#supported-websites) を見てください。

## How to install

Python package は <https://pypi.python.org/pypi/online-judge-tools> [![PyPI](https://img.shields.io/pypi/v/online-judge-tools.svg)](https://pypi.python.org/pypi/online-judge-tools) です。

```console
$ pip3 install online-judge-tools
```

より詳しい説明には [docs/INSTALL.ja.md](https://github.com/online-judge-tools/oj/blob/master/docs/INSTALL.ja.md) を読んでください。


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

詳細は `$ oj --help` を見てください。

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

-   私は C++ でなく Python (あるいは Rust, D, Java, F#, Haskell など) を使っています。それでも利用できますか？
    -   はい。必要なら `--command` (`-c`) オプションを利用してください。たとえば Python なら `$ oj t -c "python3 main.py"` のようにします。
-   私はいつもひとつのコンテストごとにひとつのディレクトリを使っています。このスタイルのままでも利用できますか？
    -   はい。`--directory` (`-d`) オプションや `$ rm -rf test/` コマンドを利用してください。しかし、レートの最大化のためには追加のテストケースを自分で生成するべきであり、それをする上ではひとつの問題ごとにひとつのディレクトリを使う方がよいでしょう。
-   コンテストごとに一括でサンプルケースを取得できませんか？
    -   いいえ、`oj` コマンドではできません。代わりに [kmyk/online-judge-template-generator](https://github.com/kmyk/online-judge-template-generator) の `oj-prepare` コマンドを利用してください。
-   テストの前に自動でコードをコンパイルするようにはできますか？
    -   はい。シェルの機能を使ってください。`$ g++ main.cpp && oj t` のように実行してください。
-   テストが通ったら自動で提出するようにはできますか？
    -   はい。シェルの機能を使ってください。`$ oj t && oj s main.cpp` のように実行してください。ところで、サンプルケースがあまり強くない問題の存在には注意が必要です。
-   提出の際のディレイや `[y/N]` の確認をなしにできますか？
    -   はい。`--wait=0` オプションや `--yes` オプションを利用してください。しかしこれは推奨されません。これらの機能は安全性のためにあるものです。たとえば、もし 3 秒速く提出できていれば順位が 3 位上がるような状況を考えてみましょう。そのような状況で提出ミスをして 5 分のペナルティを受ければ、順位は 300 位は下がるでしょう。
-   入力したパスワードは保存されますか？
    -   いいえ。パスワードはどのファイルにも保存されません。セッショントークンなど (ただしこれも機密情報です) のみを保存します。必要であれば [`onlinejudge/_implementation/command/login.py`](https://github.com/kmyk/online-judge-tools/blob/master/onlinejudge/_implementation/command/login.py) などを読んで確認してください。
-   設定ファイルはありますか？
    -   いいえ。シェルの `.bashrc` (あるいはそれに相当するファイル) を利用してください。[man bash](https://linux.die.net/man/1/bash) を読み、シェル alias やシェル関数を書いてください。たとえば、もしテストの実行の際に Python をデフォルトで使いたいのなら `alias oj-test-python='oj t -c "python3 main.py"'` と `.bashrc` に書いて `$ oj-test-python` と実行してください。

ここにない質問には [Gitter](https://gitter.im/online-judge-tools/community) [![Join the chat at https://gitter.im/online-judge-tools/community](https://badges.gitter.im/online-judge-tools/community.svg)](https://gitter.im/online-judge-tools/community) やその他の SNS を使ってください。

## Resources

### Articles

-   [online-judge-toolsを導入しよう！ &#183; ますぐれメモ](https://blog.masutech.work/posts/compro/oj-introduction/)
-   [online-judge-toolsをVimから呼んで楽をする - Leverage Copy](https://maguroguma.hatenablog.com/entry/2020/08/19/090000)
-   [VSCodeでAtCoderのサンプルケースをサクッとテストする - Qiita](https://qiita.com/danpe919/items/7c5697df25fb567f1e71)

### Related Tools

競合:

-   [jmerle/competitive-companion](https://github.com/jmerle/competitive-companion)
-   [kyuridenamida/atcoder-tools](https://github.com/kyuridenamida/atcoder-tools)
-   [xalanq/cf-tool](https://github.com/xalanq/cf-tool)
-   [nodchip/OnlineJudgeHelper](https://github.com/nodchip/OnlineJudgeHelper)

非競合:

-   [shivawu/topcoder-greed](https://github.com/shivawu/topcoder-greed) for Topcoder Single Round Match

kmyk/online-judge-tools と連携するツール:

-   [kmyk/online-judge-template-generator](https://github.com/kmyk/online-judge-template-generator) は競プロの問題を解析して解法コードの入出力部分などを自動生成します
-   [kmyk/online-judge-verify-helper](https://github.com/kmyk/online-judge-verify-helper) は競プロライブラリの verify とドキュメントの生成を自動化します
-   [Tatamo/atcoder-cli](https://github.com/Tatamo/atcoder-cli) は AtCoder に特化した `oj` コマンドの薄い wrapper です
-   [kjnh10/pcm](https://github.com/kjnh10/pcm) は内部で `oj` コマンドを利用しています
-   [fukatani/rujaion](https://github.com/fukatani/rujaion) は Rust で競プロをすることに特化した IDE です

## Maintainers

-   current maintainers
    -   [@kmyk](https://github.com/kmyk) (AtCoder: [kimiyuki](https://atcoder.jp/users/kimiyuki), Codeforces: [kimiyuki](https://codeforces.com/profile/kimiyuki)) (original author)
-   maintainers who are not working now
    -   [@fukatani](https://github.com/fukatani) (AtCoder: [ryoryoryo111](https://atcoder.jp/users/ryoryoryo111))
    -   [@kawacchu](https://github.com/kawacchu) (AtCoder: [kawacchu](https://atcoder.jp/users/kawacchu))

## License

MIT License
