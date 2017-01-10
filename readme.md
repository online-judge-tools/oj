# Online Judge Tools

A sample case downloader for online judges.

## todo

-   使ってくれて不具合見つけて報告してくれる人探す
-   hackerrank, aoj あたりは対応したい
    -   他はそのうち
    -   atcoder/codeforcesのsubmitも
-   テストケース増やす
-   設定ファイルを作る
-   他の細かいツールをmergeする
-   submitの時の言語指定どうしよう

## How to setup

Requirements:

``` sh
$ pip3 install requests
$ pip3 install beautifulsoup4
$ pip3 install colorama
```

## How to use

``` sh
$ ./main.py [download,login,submit] URL
```

Example:

``` sh
$ ./main.py download http://agc001.contest.atcoder.jp/tasks/agc001_a
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

## Features

-   Download sample cases
    -   AtCoder
    -   Yukicoder
    -   Yukicoder (テストケース一括ダウンロード) (with `-x all` option)
    -   Anarchy Golf
    -   Codeforces
-   Login
    -   AtCoder
    -   Yukicoder
    -   Codeforces
-   Submit your solution
    -   Yukicoder

## License

MIT License
