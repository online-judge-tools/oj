# How to Install `oj` command

[English version of this document](./INSTALL.md)

以下の手順を順番に実行してください。

1.  もし Windows を使っているならば、まず [Windows Subsystem for Linux (WSL)](https://docs.microsoft.com/ja-jp/windows/wsl/about) を使ってください。初心者にとって、Linux (特に Ubuntu) はたいてい Windows より簡単であるためです。
    -   また、Visual Studio Code (あるいは他の IDE) のウィンドウは閉じて、しばらく忘れていてください。IDE に付属するコンソールは利用しないでください。
    -   もちろん、もしあなたが上級者であったなら、生の Windows 環境で `oj` コマンドを使うことも可能でしょう。
1.  :snake: [Python](https://www.python.org/) をインストールしてください。もし Ubuntu (WSL 内の Ubuntu を含む) を使っているなら `$ sudo apt install python3` を実行すればよいです.
1.  Python がインストールされていることを `$ python3 --version` を実行して確認してください。`Python 3.x.y` のように表示されれば成功です。
    -   もし `Command 'python3' not found` のように表示されたなら、Python のインストールに失敗しています。
    -   インストールされている Python のバージョンが古すぎる場合も失敗です。表示された `x` の位置の値は `6` 以上でなければなりません。もし `x` が `6` 未満の場合は、Python を更新してください。
1.  :package: [pip](https://pip.pypa.io/en/stable/) をインストールしてください。もし Ubuntu (WSL 内の Ubuntu を含む) を使っているなら `$ sudo apt install python3-pip` を実行すればよいです。
1.  pip がインストールされていることを `$ pip3 --version` を実行して確認してください。`pip x.y.z ...` のように表示されれば成功です。
    -   もし `Command 'pip3' not found` のように表示されたなら、pip のインストールに失敗しています。
    -   もし `pip3` が見付からなかったとしても、`pip3` の代わりに `python3 -m pip` を使うことができるかもしれません。`$ python3 -m pip --version` も試してみましょう。`pip x.y.z ...` のように表示されれば成功です。
    -   `pip` や `pip2` は使わないでください。`pip3` を使ってください。
1.  :dart: `$ pip3 install online-judge-tools` を実行して `oj` コマンドをインストールしてください。`Successfully installed online-judge-tools-x.y.z` (あるいは `Requirement already satisfied: online-judge-tools`) と表示されれば成功です。
    -   もし `Permission denied` と表示される場合は、`$ pip3 install --user online-judge-tools` や `$ sudo pip3 install online-judge-tools` を代わりに使ってください。
1.  `oj` コマンドがインストールされていることを `$ oj --version` を実行して確認してください。`online-judge-tools x.y.z` のように表示されれば成功です.
    -   もし `Command 'oj' not found` のように表示される場合は、環境変数 [`PATH`](https://en.wikipedia.org/wiki/PATH_%28variable%29) を設定する必要があります。以下の手順を順番に実行してください。
        1.  `oj` コマンドの本体のファイルのパスを `$ find / -name oj 2> /dev/null` を実行して見つけてください。このファイルはたいてい `/home/ubuntu/.local/bin/oj` か `/usr/local/bin/oj` にあります。
        1.  見つかった `oj` ファイルが本当に `oj` コマンドであることを `$ /home/ubuntu/.local/bin/oj --version` を実行して確認してください。
        1.  その `oj` ファイルの親ディレクトリを `PATH` に追加してください。たとえばもし `oj` ファイルが `/home/ubuntu/.local/bin/oj` にあるなら、あなたの `~/.bashrc` の末尾に `export PATH="/home/ubuntu/.local/bin:$PATH"` と書き加えてください。
            -   `export PATH="/home/ubuntu/.local/bin/oj:$PATH"` とは書かないでください。それはディレクトリではありません。
            -   もしあなたが bash を使っていないなら、あなたの使っているシェルに依存した適切な方法で設定をする必要があります。たとえばもしあなたが macOS を使っているなら、シェルは zsh かもしれません。zsh の場合は、bash の場合と同じコマンドを `~/.zshrc` に書いてください。
        1.  設定を読み込み直すため `source ~/.bashrc` を実行してください。
            -   もしあなたが bash を使っていないなら、あなたのシェルにおいて適切な方法を使ってください。
        1.  `PATH` が設定されたことを `$ echo $PATH` を実行して確認してください。 もしあなたが設定したように表示されれば (たとえば `/home/ubuntu/.local/bin:...`) 成功です。
    -   もし `ModuleNotFoundError: No module named 'onlinejudge'` のように表示される場合は、あなたの Python 環境は壊れており、`oj` コマンドのインストールに失敗しています。`$ pip3 install --force-reinstall online-judge-tools` を実行して強制的な再インストールを試してみてください。
    -   もし `SyntaxError: invalid syntax` のように表示される場合は、間違って `pip2` を使ってしまっていたはずです。`$ pip2 uninstall online-judge-tools` を実行してアンインストールし、もう一度やり直してください。
1.  以上

なお、もしあなたが上記の指示のほとんどの文章の意味を理解できない (たとえば、「`$ python3 --version` を実行する」がなにをすることなのか分からないなど) のであれば、誰か親切な友人に直接教えてもらうのがおすすめです。
