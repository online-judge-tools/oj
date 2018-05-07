# Python Version: 3.x
import onlinejudge
import onlinejudge.implementation.utils as utils
import onlinejudge.implementation.logging as log
import sys
import subprocess
import time

def non_block_read(fh):
    # workaround
    import fcntl
    import os
    fd = fh.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
    try:
        return fh.read()
    except:
        return ''

split_input_auto_footer = ('__AUTO_FOOTER__', )  # this shouldn't be a string, so a tuple

def split_input(args):
    with open(args.input) as fh:
        inf = fh.read()
    if args.footer == split_input_auto_footer:
        args.footer = inf.splitlines(keepends=True)[-1]
    with subprocess.Popen(args.command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=sys.stderr) as proc:
        index = 0
        acc = ''
        for line in inf.splitlines(keepends=True):
            if args.ignore:
                args.ignore -= 1
            else:
                acc += line
            proc.stdin.write(line.encode())
            proc.stdin.flush()
            time.sleep(args.time)
            if non_block_read(proc.stdout): # if output exists
                index += 1
                path = utils.parcentformat(args.output, { 'i': str(index) })
                log.info('case found: %d', index)
                if args.header:
                    if args.header == args.header.strip():
                        acc = '\n' + acc
                    acc = args.header + acc
                if args.footer:
                    acc = acc + args.footer
                log.emit(log.bold(acc))
                with open(path, 'w') as fh:
                    fh.write(acc)
                log.success('saved to: %s', path)
                acc = ''
                while non_block_read(proc.stdout): # consume all
                    pass
