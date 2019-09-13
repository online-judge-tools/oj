Introduction to online-judge-tools (Japanese)
=============================================

online-judge-tools は競技プログラミングを行う上で存在する典型作業を自動化するためのツールです。


インストール
------------

Python が導入されている環境であれば、次のコマンドだけでインストールができます。

.. code-block:: console

   $ pip3 install --user online-judge-tools

OS には Linux か Mac OS を推奨しますが、 Windows 上でも動作します。


サンプルケースのテスト
----------------------

あなたは提出前にサンプルケースを使ったテストをしていますか？
面倒に感じて省略してしまったことはありませんか？
サンプルすら合っていない実装を提出しても無為にペナルティを増やすだけなので、提出前には常にテストを行なうべきです。
デバッグの際にも有用であり、プログラムを書き換えるたびにサンプルケースを試すとよいでしょう。

しかし、「問題ページを開いてサンプル入力をコピーし、プログラムを実行しそこに貼り付け、出力結果とサンプル出力を比較する」という作業をサンプルケースの個数だけ行なう、これを毎回やるのはかなり面倒です。
面倒な作業を手動で行うのは省略されたり間違えたりしやすく、よくありません。
この問題は、自動化によって解決できます。

online-judge-tools を使えばサンプルケースのテストの自動化が可能です。
具体的には以下を自動でしてくれます:

#. 問題ページを開いてサンプルを取得する
#. プログラムを実行してサンプルを入力として与える
#. プログラムの出力とサンプルの出力を比較する

サンプルのダウンロードは ``oj d URL`` で行なえ、ダウンロードしたサンプルに対するテストは ``oj t`` で行なえます。
たとえば以下のように使います。

.. code-block:: console

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


``oj t`` の基本的な機能は ``test/sample-1.in``, ``test/sample-1.out`` などのファイルを用意した上で ``for f in test/*.in ; do diff <(./a.out < $f) ${f/.in/.out} ; done`` を実行するのとほぼ等価です。
``./a.out`` 以外のコマンド (たとえば ``python3 main.py``) に対してテストをしたい場合は ``-c`` オプションを使ってください (たとえば ``oj t -c "python3 main.py"``)。
サンプルでなくシステムテストに使われるテストケースを取得したい場合は ``--system`` オプションを使ってください。
その他の機能について確認するには ``oj d --help`` や ``oj t --help`` を実行してください。


提出
----

実装した解法の提出を行う際には、「プログラムの提出先となる問題」と「提出するプログラムの実装言語」をマウスで選択しソースコードをテキストボックスにコピペして送信ボタンを押すことが一般的です。
ところで、提出時に「提出先の問題」「提出の言語」の選択を間違えてしまいペナルティを食らった経験はありますか？
もしそのような経験が一度でもあるのなら、提出を自動化することをおすすめします。

online-judge-tools を使えば提出の自動化が可能です。
問題 https://codeforces.com/contest/1200/problem/F にファイル ``main.cpp`` を提出したいときは ``oj s https://codeforces.com/contest/1200/problem/F`` を実行すればよいです。実際に実行したときの出力は次のようになります:

.. code-block:: console

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


(ただし、提出にはログインが必要なので、事前に ``oj login https://atcoder.jp/`` を実行しておいてください。
`Selenium <https://www.seleniumhq.org/>`_ が導入 (``apt install python3-selenium firefox-geckodriver`` などを実行) されていれば GUI ブラウザが起動するので、その上で普通にログインをしてください。
Selenium がない場合は CUI 上で直接ユーザ名とパスワードが聞かれます。)

同じディレクトリで以前に ``oj d URL`` を実行したことがあれば、単に ``oj s main.cpp`` とするだけで URL を推測して提出してくれます。
URL の指定ミスを防ぐために、こちらの省力形の利用を推奨しています。
また、言語は自動で認識され適切に設定されます。


ストレステスト
--------------

「実装をしてサンプルが合ったので提出をしたのに、 WA や RE になってしまった。しかし原因がまったく分からない」という状況になったとき、どうすればいいでしょうか？
これにはランダム生成したケースを使ってのデバッグが有効です。
具体的には次のようにします。

#. 制約を満たす入力をランダムに生成するようなプログラムを実装し、テストケースの入力をたくさん用意する
#. (もし可能なら、遅くても確実に正しい答えを出力するような愚直解を実装し、対応する出力をたくさん用意する)
#. (1.), (2.) で作ったテストケースを使って、問題のプログラムをテストする
#. (3.) で見つかった撃墜ケースを分析してバグを見つける

online-judge-tools には、これを助ける機能もあります。
(1.) には ``oj g/i`` というコマンド、 (2.) には ``oj g/o`` というコマンドが使えます。
たとえば https://onlinejudge.u-aizu.ac.jp/courses/library/7/DPL/1/DPL_1_B に対して以下のように利用します。

.. code-block:: console

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



``oj g/i ./generate.py`` の基本的な機能は ``for i in $(seq 100) ; do ./generate.py > test/random-$i.in ; done`` とだいたい等価であり、 ``oj g/o`` の基本的な機能は ``for i in test/*.in ; do ./a.out < $f > ${f/.in/.out} ; done`` とだいたい等価です。
なかなか撃墜ケースが見つからない場合のために、より効率的に行なうオプション ``--hack`` や並列化オプション ``-j`` なども用意されています。


特殊な形式の問題に対するテスト
------------------------------

-   誤差ジャッジ

   「絶対誤差あるいは相対誤差で 10⁻⁶ 以内の出力を正答とします」のような問題に対するテストは、 ``-e`` オプションで対応できます。
   たとえば ``oj t -e 1e-6`` とします。

-   解が複数ある問題

   直接は対応していません。
   実装したプログラムの中で `assert <https://cpprefjp.github.io/reference/cassert/assert.html>`_ をしてください。

   たとえば問題 https://atcoder.jp/contests/agc022/tasks/agc022_b であれば、以下のような形で実装をして ``oj t`` を実装することでテストが行なえます。

   .. code-block:: c++

      #include <bits/stdc++.h>
      #define REP(i, n) for (int i = 0; (i) < (int)(n); ++ (i))
      #define ALL(x) begin(x), end(x)
      using namespace std;
      
      vector<int> solve(int n) {
          ...
      }
      
      int main() {
          int n; cin >> n;
          vector<int> s = solve(n);
          REP (i, s.size()) {
              if (i) cout << ' ';
              cout << s[i];
          }
          cout << endl;
      
          // check
          int sum_s = accumulate(ALL(s), 0);
          REP (i, n) {
              assert (1 <= s[i] and s[i] <= 30000);
              assert (gcd(s[i], sum_s - s[i]) != 1);
          }
          assert (set<int>(ALL(s)).size() == s.size());
          assert (accumulate(ALL(s), 0, [&](int a, int b) { return gcd(a, b); }) == 1);
          return 0;
      }

-   リアクティブ問題

   ジャッジプログラムと対話的に動作するプログラムを提出する問題があります。
   これをテストするためのコマンド ``oj t/r`` が用意されています。

   たとえば問題 https://codeforces.com/gym/101021/problem/A であれば、次のようなジャッジ側プログラムを書いて ``judge.py`` という名前で保存し、 ``oj t/r ./judge.py`` とすればテストが実行されます。

   .. code-block:: python

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


対応しているサービスの一覧
--------------------------

オンラインジャッジのサーバーと通信を行なうような機能については利用できるサービスが制限されることがあります。
``v7.0.0`` (2019-09-01) 時点での対応サービスは以下のようになります。

サンプルのダウンロード (``oj d``):

-  `Aizu Online Judge (Arena) <https://onlinejudge.u-aizu.ac.jp/services/arena.html>`_
-  `Aizu Online Judge <https://onlinejudge.u-aizu.ac.jp/home>`_
-  `Anarchy Golf <http://golf.shinh.org/>`_
-  `AtCoder <https://atcoder.jp/>`_
-  `Codeforces <https://codeforces.com/>`_
-  `CS Academy <https://csacademy.com/>`_
-  `Facebook Hacker Cup <https://www.facebook.com/hackercup/>`_
-  `HackerRank <https://www.hackerrank.com/>`_
-  `Kattis <https://open.kattis.com/>`_
-  `PKU JudgeOnline <http://poj.org/>`_
-  `Toph (Problem Archive) <https://toph.co/>`_
-  `yukicoder <https://yukicoder.me/>`_

ログイン (``oj login``):

-  すべてのサービス (Selenium 使用時)
-  AtCoder (パスワード直入力)
-  Codeforces (パスワード直入力)

提出 (``oj s``)

-  AtCoder
-  Codeforces
-  Topcoder (Marathon Match)
-  yukicoder
-  HackerRank
-  Toph (Problem Archive)

システムケースのダウンロード (``oj d --system``):

-  Aizu Online Judge
-  yukicoder


存在しない機能
--------------

「それが何であるか」を説明するには「何ができるか」を言う必要がありますが、それだけでは十分ではありません。
「何ができないか」についても言うべきです。

online-judge-tools には、次のような機能は存在しません:

-  コンテストに対応するディレクトリを用意する機能

   online-judge-tools は「個々の問題を解くことを助ける」ためのツールであり、それ以外は責任の範囲外です。
   これに対応するための機能は内部的には存在する (`onlinejudge.type.Contest.list_problems <https://online-judge-tools.readthedocs.io/en/master/onlinejudge.type.html#onlinejudge.type.Contest.list_problems>`_) ので、必要なら各自でこれを利用するスクリプトを書いてください。既存の wrapper (`Tatamo/atcoder-cli <https://github.com/Tatamo/atcoder-cli>`_ など) を利用することもできます。

   同様の理由で、たとえば「精進の進捗を管理する機能」なども存在しません。

-  テンプレートを生成する機能

   テンプレートの生成はプログラミング一般の領域の問題であるので online-judge-tools の責任の範囲外です。
   たとえば Vim なら `thinca/vim-template <https://github.com/thinca/vim-template/blob/master/doc/template.jax>`_ などのプラグインでより汎用的に対応できます。

   たとえば「ソースコードを自動で診断してバグのありそうな所を探す機能」なども同様の「より一般的なツールとして存在する」という理由によって存在しません。

-  自動でコンパイルする機能

   シェルの機能を使えば十分です。
   また、コンパイルの方法などは言語や環境の数だけ無数にあり、いちいち対応するのはかなり大変なためです。
   テストの前に再コンパイルしたいのなら ``g++ main.cpp && oj t`` などとしてください。

-  入力を受けとる部分のコードを自動生成する機能

   過去には存在していましたが、 `kyuridenamida/atcoder-tools <https://github.com/kyuridenamida/atcoder-tools>`_ に任せることにして削除しました。そちらを利用してください。

-  提出予約をする機能

   シェルの機能を使えば十分であるため、そのような指定をするオプションはありません。
   たとえば 1 時間後に提出するには ``sleep 3600 && oj s --yes main.cpp`` としてください。

-  提出結果を解析する機能

   存在しません。あまりやりすぎると問題になることが予想されるためです。
   これを実装するための機能は内部的には存在する (`onlinejudge.service.atcoder.AtCoderSubmissionData <https://online-judge-tools.readthedocs.io/en/master/onlinejudge.service.atcoder.html#onlinejudge.service.atcoder.AtCoderSubmissionData>`_) ので、必要なら各自でこれを利用するスクリプトを書いてください。

-  設定ファイル

   存在しません。
   設定ファイルはある種の「隠れた状態」を導入し、メンテナンスやサポートのコストを増大させるためです。
   内部で HTTP の通信に使っているクッキー (+ 例外として、提出先 URL の推測 ``oj s`` のための履歴) 以外は、入力されたコマンドのみに依存して動作します。
