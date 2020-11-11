# How to Install `oj` command

[このドキュメントの日本語バージョン](./INSTALL.ja.md)

Do following steps.

1.  If you use a Windows environment, use [Windows Subsystem for Linux (WSL)](https://docs.microsoft.com/en-us/windows/wsl/about). For beginners, Linux (especially, Ubuntu) is often easier than Windows.
    -   Also, if you use Visual Studio Code (or other IDEs), close it and forget it for a while. Don't use consoles in IDEs.
    -   Of course, if you were a professional, you could use `oj` command in the raw Windows environment.
1.  :snake: Install [Python](https://www.python.org/). If you use Ubuntu (including Ubuntu in WSL), run `$ sudo apt install python3`.
1.  Check your Python with running `$ python3 --version`. If it says like `Python 3.x.y`, it's OK.
    -   If it says something like `Command 'python3' not found`, you have failed to install Python.
    -   If the version of Python is too old, it's not OK. The `x` must be greater than or equal to `6`. If `x` is lower than `6`, upgrade your Python.
1.  :package: Install [pip](https://pip.pypa.io/en/stable/). If you use Ubuntu (including Ubuntu in WSL), run `$ sudo apt install python3-pip`.
1.  Check your pip with running `$ pip3 --version`. If it says something like `pip x.y.z ...`, it's OK.
    -   If it says something like `Command 'pip3' not found`, you have failed to install pip.
    -   Even if `pip3` is not found, you may be able to use `python3 -m pip` instead of `pip3`. Try `$ python3 -m pip --version`. If it says `pip x.y.z ...`, it's OK.
    -   Don't use `pip` or `pip2`. Use `pip3`.
1.  :dart: Run `$ pip3 install online-judge-tools` to install `oj` command. If it says `Successfully installed online-judge-tools-x.y.z` (or, `Requirement already satisfied: online-judge-tools`), it's OK.
    -   If it says `Permission denied`, run `$ pip3 install --user online-judge-tools` or `$ sudo pip3 install online-judge-tools`.
1.  Check `oj` command with `$ oj --version`. If it says something like `online-judge-tools x.y.z`, it's OK.
    -   If it says something like `Command 'oj' not found`, you need to set [`PATH`](https://en.wikipedia.org/wiki/PATH_%28variable%29). Do following steps.
        1.  Find the path of the `oj` file with running `$ find / -name oj 2> /dev/null`. The file is often at `/home/ubuntu/.local/bin/oj` or `/usr/local/bin/oj`.
        1.  Check the found `oj` file is actually `oj`, with running `$ /home/ubuntu/.local/bin/oj --version`.
        1.  Add the directory which contains the `oj` to your `PATH`. For example, if `oj` is `/home/ubuntu/.local/bin/oj`, write `export PATH="/home/ubuntu/.local/bin:$PATH"` in the end of `~/.bashrc`.
            -   Don't write `export PATH="/home/ubuntu/.local/bin/oj:$PATH"`. It's not a directory.
            -   If you don't use bash, write a right settings to the right file depending on your shell. For example, if you use macOS, your shell might zsh. For zsh, write the same command to `~/.zshrc`.
        1.  Reload the configuration with `source ~/.bashrc`.
            -   If you don't use bash, use the appropriate way for your shell.
        1.  Check your `PATH` with `$ echo $PATH`. If it says as you specified (e.g. `/home/ubuntu/.local/bin:...`), it's OK.
    -   If it says something like `ModuleNotFoundError: No module named 'onlinejudge'`, your Python environment is broken and you have failed to install `oj` command. Run `$ pip3 install --force-reinstall online-judge-tools` to reinstall ignoring the old one.
    -   If it says something like `SyntaxError: invalid syntax`, you have used `pip2` by mistake. Run `$ pip2 uninstall online-judge-tools`, and retry to install.
1.  That's all.

If you couldn't read many sentences of above instructions (e.g. if you didn't know what "run `$ python3 --version`" means), please ask your friends for help.
