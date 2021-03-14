# Getting Started for `oj` command (日本語)

[English version of this document](./getting-started.md)

`oj` コマンドは競技プログラミングを行う上で存在する典型作業を自動化するためのコマンドです。


## インストール

Python が導入されている環境であれば、次のコマンドだけでインストールができます。

```console
$ pip3 install --user online-judge-tools
```

OS には Linux (Windows Subsystem for Linux を含む) か macOS を推奨しますが、Windows 上でも動作します。

詳細な手順については [docs/INSTALL.ja.md](./INSTALL.ja.md) を読んでください。


## サンプルケースのテスト

あなたは提出前にサンプルケースを使ったテストをしていますか？
面倒に感じて省略してしまったことはありませんか？
サンプルすら合っていない実装を提出しても無為にペナルティを増やすだけなので、提出前には常にテストを行なうべきです。
デバッグの際にも有用であり、プログラムを書き換えるたびにサンプルケースを試すとよいでしょう。

しかし、「問題ページを開いてサンプル入力をコピーし、プログラムを実行しそこに貼り付け、出力結果とサンプル出力を比較する」という作業をサンプルケースの個数だけ行なう、これを毎回やるのはかなり面倒です。
面倒な作業を手動で行うのは省略されたり間違えたりしやすく、よくありません。
この問題は、自動化によって解決できます。

`oj` コマンドを使えばサンプルケースのテストの自動化が可能です。
具体的には以下を自動でしてくれます:

1.  問題ページを開いてサンプルを取得する
2.  プログラムを実行してサンプルを入力として与える
3.  プログラムの出力とサンプルの出力を比較する

サンプルのダウンロードは `oj d URL`
で行なえ、ダウンロードしたサンプルに対するテストは `oj t` で行なえます。
たとえば以下のように使います。

```console
$ oj d https://atcoder.jp/contests/agc001/tasks/agc001_a
[x] problem recognized: AtCoderProblem.from_url('https://atcoder.jp/contests/agc001/tasks/agc001_a')
[x] load cookie from: /home/ubuntu/.local/share/online-judge-tools/cookie.jar
[x] GET: https://atcoder.jp/contests/agc001/tasks/agc001_a
[x] 200 OK
[x] save cookie to: /home/ubuntu/.local/share/online-judge-tools/cookie.jar
[x] append history to: /home/ubuntu/.cache/online-judge-tools/download-history.jsonl

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

$ g++ main.cpp

$ oj t
[*] 2 cases found

[*] sample-1
[x] time: 0.003978 sec
[+] AC

[*] sample-2
[x] time: 0.004634 sec
[-] WA
output:
3

expected:
135


[x] slowest: 0.004634 sec  (for sample-2)
[x] max memory: 2.344000 MB  (for sample-1)
[-] test failed: 1 AC / 2 cases
```

`oj t` の基本的な機能は `test/sample-1.in`, `test/sample-1.out`
などのファイルを用意した上で
`for f in test/*.in ; do diff <(./a.out < $f) ${f/.in/.out} ; done`
を実行するのとほぼ等価です。 `./a.out` 以外のコマンド (たとえば
`python3 main.py`) に対してテストをしたい場合は `-c`
オプションを使ってください (たとえば `oj t -c "python3 main.py"`)。
サンプルでなくシステムテストに使われるテストケースを取得したい場合は
`--system` オプションを使ってください。 その他の機能について確認するには
`oj d --help` や `oj t --help` を実行してください。


## 提出

実装した解法の提出を行う際には、「プログラムの提出先となる問題」と「提出するプログラムの実装言語」をマウスで選択しソースコードをテキストボックスにコピペして送信ボタンを押すことが一般的です。
ところで、提出時に「提出先の問題」「提出の言語」の選択を間違えてしまいペナルティを食らった経験はありますか？
もしそのような経験が一度でもあるのなら、提出を自動化することをおすすめします。

`oj` コマンドを使えば提出の自動化が可能です。 たとえば、問題
<https://codeforces.com/contest/1200/problem/F> にファイル `main.cpp`
を提出したいときは `oj s https://codeforces.com/contest/1200/problem/F`
を実行すればよいです。実際に実行したときの出力は次のようになります:

```console
$ oj s https://codeforces.com/contest/1200/problem/F main.cpp
[x] read history from: /home/ubuntu/.cache/online-judge-tools/download-history.jsonl
[x] found urls in history:
https://codeforces.com/contest/1200/problem/F
[x] problem recognized: CodeforcesProblem.from_url('https://codeforces.com/contest/1200/problem/F'): https://codeforces.com/contest/1200/problem/F
[*] code (2341 byte):
#include <bits/stdc++.h>
#define REP(i, n) for (int i = 0; (i) < (int)(n); ++ (i))
using namespace std;


constexpr int MAX_M = 10;
constexpr int MOD = 2520;  // lcm of { 1, 2, 3, ..., 10 }
int main() {
    // config
    int n; scanf("%d", &n);
... (62 lines) ...

    // query
    int q; scanf("%d", &q);
    while (q --) {
        int x, c; scanf("%d%d", &x, &c);
        -- x;
        printf("%d\n", solve1(x, c));
        }
    return 0;
}

[x] load cookie from: /home/ubuntu/.local/share/online-judge-tools/cookie.jar
[x] GET: https://codeforces.com/contest/1200/problem/F
[x] 200 OK
[x] both GCC and Clang are available for C++ compiler
[x] use: GCC
[*] chosen language: 54 (GNU G++17 7.3.0)
[x] sleep(3.00)
Are you sure? [y/N] y
[x] GET: https://codeforces.com/contest/1200/problem/F
[x] 200 OK
[x] POST: https://codeforces.com/contest/1200/problem/F
[x] redirected: https://codeforces.com/contest/1200/my
[x] 200 OK
[+] success: result: https://codeforces.com/contest/1200/my
[x] open the submission page with: sensible-browser
[1513:1536:0910/223148.485554:ERROR:browser_process_sub_thread.cc(221)] Waited 5 ms for network service
Opening in existing browser session.
[x] save cookie to: /home/ubuntu/.local/share/online-judge-tools/cookie.jar
```

(ただし、提出にはログインが必要なので、事前に
`oj login https://atcoder.jp/` を実行しておいてください。
[Selenium](https://www.seleniumhq.org/) が導入
(`apt install python3-selenium firefox-geckodriver` などを実行)
されていれば GUI
ブラウザが起動するので、その上で普通にログインをしてください。 Selenium
がない場合は CUI 上で直接ユーザ名とパスワードが聞かれます。)

同じディレクトリで以前に `oj d URL` を実行したことがあれば、単に
`oj s main.cpp` とするだけで URL を推測して提出してくれます。 URL
の指定ミスを防ぐために、こちらの省力形の利用を推奨しています。
また、言語は自動で認識され適切に設定されます。


## ランダムテスト

「実装をしてサンプルが合ったので提出をしたのに、 WA や RE
になってしまった。しかし原因がまったく分からない」という状況になったとき、どうすればいいでしょうか？
これにはランダム生成したケースを使ってのデバッグが有効です。
具体的には次のようにします。

1.  制約を満たす入力をランダムに生成するようなプログラムを実装する
2.  (1.) のプログラムを使ってテストケースの入力をたくさん用意する
3.  (もし可能なら、遅くても確実に正しい答えを出力するような愚直解を実装し、対応する出力をたくさん用意する)
4.  (2.), (3.)
    で作ったテストケースを使って、問題のプログラムをテストする
5.  (4.) で見つかった撃墜ケースを分析してバグを見つける

`oj` コマンドには、これを助ける機能もあります。 (2.) には `oj g/i`
というコマンド、 (3.) には `oj g/o` というコマンドが使えます。 また (1.)
のプログラムを半自動生成するためのツール
[online-judge-tools/template-generator](https://github.com/online-judge-tools/template-generator)
も用意されています。

たとえば
<https://onlinejudge.u-aizu.ac.jp/courses/library/7/DPL/1/DPL_1_B>
に対して以下のように利用します。

```console
$ cat generate.py
#!/usr/bin/env python3
import random
N = random.randint(1, 100)
W = random.randint(1, 10000)
print(N, W)
for _ in range(N):
    v = random.randint(1, 1000)
    w = random.randint(1, 1000)
    print(v, w)

$ oj g/i ./generate.py

[*] random-000
[x] generate input...
[x] time: 0.041610 sec
input:
1 4138
505 341

[+] saved to: test/random-000.in

...

[*] random-099
[x] generate input...
[x] time: 0.036598 sec
input:
9 2767
868 762
279 388
249 673
761 227
958 971
589 590
34 100
689 635
781 361

[+] saved to: test/random-099.in

$ cat tle.cpp
#include <bits/stdc++.h>
#define REP(i, n) for (int i = 0; (i) < (int)(n); ++ (i))
using namespace std;

int main() {
    // input
    int N, W; cin >> N >> W;
    vector<int> v(N), w(N);
    REP (i, N) {
        cin >> v[i] >> w[i];
    }

    // solve
    int answer = 0;
    REP (x, 1 << N) {
        int sum_v = 0;
        int sum_w = 0;
        REP (i, N) if (x & (1 << i)) {
            sum_v += v[i];
            sum_w += w[i];
        }
        if (sum_w <= W) {
            answer = max(answer, sum_v);
        }
    }

    // output
    cout << answer << endl;
    return 0;
}

$ g++ tle.cpp -o tle

$ oj g/o -c ./tle
[*] 102 cases found

[*] random-000
[x] time: 0.003198 sec
505

[+] saved to: test/random-000.out

...

[*] random-099
[x] time: 0.005680 sec
3722

[+] saved to: test/random-099.out

[*] sample-1
[*] output file already exists.
[*] skipped.

[*] sample-2
[*] output file already exists.
[*] skipped.
```

`oj g/i ./generate.py` の基本的な機能は
`for i in $(seq 100) ; do ./generate.py > test/random-$i.in ; done`
とだいたい等価であり、 `oj g/o` の基本的な機能は
`for i in test/*.in ; do ./a.out < $f > ${f/.in/.out} ; done`
とだいたい等価です。
なかなか撃墜ケースが見つからない場合のために、より効率的に行なうオプション
`--hack` や並列化オプション `-j` なども用意されています。


## 特殊な形式の問題に対するテスト

### 誤差ジャッジ

「絶対誤差あるいは相対誤差で 10⁻⁶
以内の出力を正答とします」のような問題に対するテストは、 `-e`
オプションで対応できます。 たとえば `oj t -e 1e-6` とします。

### 解が複数ある問題

実装したプログラムの中で
[assert](https://cpprefjp.github.io/reference/cassert/assert.html)
を用いることで、解答の正当性を簡易にチェックすることが可能です。

あるいは、複雑なチェックが必要な場合や想定解答の内容をチェックに用いたい場合は、ジャッジ側のプログラムを自作して解答の正否の判定に用いることができます。
たとえば問題 <https://atcoder.jp/contests/abc074/tasks/arc083_a>
であれば、次のようなジャッジ側プログラムを書いて `judge.py`
という名前で保存し、 `oj t --judge-command "python3 judge.py"`
とすればテストが実行されます。

```python
import sys
# input
with open(sys.argv[1]) as testcase:
    A, B, C, D, E, F = list(map(int, testcase.readline().split()))
with open(sys.argv[2]) as your_output:
    y_all, y_sugar = list(map(int, your_output.readline().split()))
with open(sys.argv[3]) as expected_output:
    e_all, e_sugar = list(map(int, expected_output.readline().split()))
# check
assert 100 * A <= y_all <= F
y_water = y_all - y_sugar
assert any(100 * A * i + 100 * B * j == y_water for i in range(3001) for j in range(3001))
assert any(C * i + D * j == y_sugar for i in range(3001) for j in range(3001))
assert y_sugar <= E * y_water / 100
assert y_sugar * e_all == e_sugar * y_all
assert (e_sugar > 0 and y_sugar == 0) is False
```

ジャッジ側のプログラムは、テストケースの入力、解答（あなたのプログラムの出力）、想定解答をファイル入力を用いて取得することができます。
judgeのコマンドは `<command> <input> <your_output> <expected_output>`
のように実行され、 `<command>`
には引数で指定したジャッジの実行コマンドが入ります。 `<input>` ,
`<your_output>` , `<expected_output>`
にはそれぞれ、テストケースの入力、解答、想定解答が格納されたファイルのパスが入ります。
サンプルに示すようにコマンドライン引数を用いて各ファイルを読み込み、解答の正否を判定してください。
ジャッジプログラムの終了コードが0になった場合に正答(AC)となり、それ以外は誤答(WA)となります。

### リアクティブ問題

ジャッジプログラムと対話的に動作するプログラムを提出する問題があります。
これをテストするためのコマンド `oj t/r` が用意されています。

たとえば問題 <https://codeforces.com/gym/101021/problem/0>
であれば、次のようなジャッジ側プログラムを書いて `judge.py`
という名前で保存し、 `oj t/r ./judge.py`
とすればテストが実行されます。

```python
#!/usr/bin/env python3
import sys
import random
n = random.randint(1, 10 ** 6)
print('[*] n =', n, file=sys.stderr)
for i in range(25 + 1):
    s = input()
    if s.startswith('!'):
        x = int(s.split()[1])
        assert x == n
        exit()
    else:
        print('<' if n < int(s) else '>=')
        sys.stdout.flush()
assert False
```


## 対応しているサービスの一覧

[online-judge-tools/api-client](https://github.com/online-judge-tools/api-client#supported-websites) にある表を参照してください。


## 存在しない機能

「それが何であるか」を説明するには「何ができるか」を言う必要がありますが、それだけでは十分ではありません。
「何ができないか」についても言うべきです。

`oj` コマンドには、次のような機能は存在しません:

-   コンテストのためのディレクトリを一括で用意する機能

    「コンテストのためのディレクトリを一括で用意する機能」は `oj` コマンドには含まれていません。この機能がほしい場合は [online-judge-tools/template-generator](https://github.com/online-judge-tools/template-generator/blob/master/README.ja.md) に含まれている `oj-prepare` コマンドや、[@Tatamo](https://github.com/Tatamo) が作成している [Tatamo/atcoder-cli](https://github.com/Tatamo/atcoder-cli) など) を利用してください。

    `oj` コマンドは「個々の問題を解くことを (主にテストの実行によって) 助ける」ためのコマンドであり、それ以外は責任の範囲外です。

-   テンプレートを生成する機能

    競技プログラミングの問題を解析してその問題専用の main 関数や入出力部分を生成するには、[online-judge-tools/template-generator](https://github.com/online-judge-tools/template-generator/blob/master/README.ja.md) に含まれている `oj-tempate` コマンドを使ってください。
    同様の機能は [kyuridenamida/atcoder-tools](https://github.com/kyuridenamida/atcoder-tools) にもあります。

-   自動でコンパイルする機能

    シェルの機能を使えば十分であるため、そのような機能はありません。
    テストの前に再コンパイルしたいのなら `$ g++ main.cpp && oj t` などとしてください。

    また、コンパイルの方法などは言語や環境の数だけ無数にあり、すべて対応していくのはかなり大変なためです。また、マイナー言語のユーザやマイナーなオンラインジャッジのユーザを無視したくはありません。

-   提出予約をする機能

    シェルの機能を使えば十分であるため、そのような機能はありません。
    たとえば 1 時間後に提出するには `$ sleep 3600 && oj s --yes main.cpp` としてください。

-   設定ファイル

    シェルの設定ファイル (`~/.bashrc` など) を代わりに利用してください。
    alias やシェル関数を書いてください。

    設定ファイルはある種の「隠れた状態」を導入し、メンテナンスやサポートのコストを増大させるためです。
    内部で HTTP の通信に使っているクッキー (+ 例外として、提出先 URL の推測 `oj s` のための履歴) 以外は、入力されたコマンドのみに依存して動作します。
