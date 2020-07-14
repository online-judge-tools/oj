"""
isort: skip_file
"""

# This is a workaround for the issue https://github.com/online-judge-tools/oj/issues/755
# You can reproduce this issue with:
#     $ pip3 uninstall online-judge-tools online-judge-api-client
#     $ pip3 install online-judge-tools==9.2.2
#     $ pip3 install online-judge-api-client
# pylint: disable=unused-import,ungrouped-imports
try:
    import onlinejudge.__about__  # type: ignore
except ImportError:
    import sys
    import textwrap
    print(textwrap.dedent("""\
        You failed to upgrade online-judge-tools because you upgraded from a too old verion (< 10.0.0).
        Please execute:

            1. Uninstall online-judge-tools and online-judge-api-client.
                $ pip3 uninstall online-judge-tools online-judge-api-client

            2. Check if they are completely uninstalled. It has successfully uninstalled when the following commands say something like "not found".
                $ command oj
                oj: command not found

                $ python3 -c 'import pathlib, sys ; print(*[path for path in sys.path if (pathlib.Path(path) / "onlinejudge").exists()] or ["not installed"])'
                not installed

                $ pip3 show online-judge-tools online-judge-api-client
                (no output)

            3. Reinstall online-judge-tools.
                $ pip3 install online-judge-tools"""), file=sys.stderr)
    sys.exit(1)
# pylint: enable=unused-import,ungrouped-imports
