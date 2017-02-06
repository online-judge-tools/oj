#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import onlinejudge
import onlinejudge.implementation.utils as utils
import onlinejudge.implementation.logging as log
import bs4
import sympy
import sympy.parsing.sympy_parser as sympy_parser
import colorama
import collections
import sys

def tokenize(pre):
    it = []
    for y, line in enumerate(pre.splitlines()):
        line = line.replace('$', '').replace('\\(', '').replace('\\)', '')
        line = line.replace('\\ ', ' ').replace('\\quad', ' ')
        it += [ [] ]
        for x, s in enumerate(line.split()):
            if s in [ '..', '...', '\\dots', '…', '⋯' ]:
                it[-1] += [ { 'kind': 'dots', 'dir': ['hr', 'vr'][x == 0] } ]
            elif s in [ ':', '\\vdots', '⋮' ]:
                it[-1] += [ { 'kind': 'dots', 'dir': 'vr' } ]
            elif '\\' in s:
                assert False
            elif '_' in s:
                assert s.count('_') == 1
                s, ix = s.split('_')
                if ix.startswith('{') and ix.endswith('}'):
                    ix = ix[1:-1]
                if ',' in ix:
                    raise NotImplementedError
                it[-1] += [ { 'kind': 'indexed', 'name': s, 'index': ix } ]
            else:
                it[-1] += [ { 'kind': 'fixed', 'name': s } ]
    return it

def merge_ops(xs):
    ys = []
    for x in xs:
        if ys and ys[-1]['kind'] == x['kind'] and x['kind'] in [ 'decl', 'decl-vector',  'read', 'read-indexed'  ]:
            ys[-1]['targets'] += x['targets']
        else:
            ys += [ x ]
    return ys

def simplify(s):
    transformations = sympy_parser.standard_transformations + ( sympy_parser.implicit_multiplication_application ,)
    local_dict = { 'N': sympy.Symbol('N') }
    return str(sympy_parser.parse_expr(s, local_dict=local_dict, transformations=transformations))

def parse(tokens):
    env = collections.defaultdict(dict)
    for y, line in enumerate(tokens):
        for x, item in enumerate(line):
            if item['kind'] == 'indexed':
                f = env[item['name']]
                if item['index'] in 'ijk': # for A_1 \dots A_i \dots A_N
                    continue
                if 'l' not in f or item['index'] < f['l']:
                    f['l'] = item['index']
                if 'r' not in f or f['r'] < item['index']:
                    f['r'] = item['index']
    for name in env:
        env[name]['n'] = simplify('{}-{}+1'.format(env[name]['r'], env[name]['l']))
    it = []
    used = set()
    for y, line in enumerate(tokens):
        for x, item in enumerate(line):
            decls = []
            reads = []
            if item['kind'] == 'fixed':
                decls += [ { 'kind': 'decl', 'names': [ item['name'] ] } ]
                reads += [ { 'kind': 'read', 'names': [ item['name'] ] } ]
            elif item['kind'] == 'indexed':
                pass
            elif item['kind'] == 'dots':
                it += merge_ops(decls) + merge_ops(reads)
                decls = []
                reads = []
                if item['dir'] == 'hr':
                    assert line[x-1]['kind'] == 'indexed'
                    name = line[x-1]['name']
                    if name in used:
                        continue
                    n = env[name]['n']
                    it += [ { 'kind': 'decl-vector', 'targets': [ { 'name': name, 'length': n } ] } ]
                    it += [ { 'kind': 'loop', 'length': n, 'body': [ { 'kind': 'read-indexed', 'targets': [ { 'name': name, 'index': 0 } ] } ] } ]
                    used.add(name)
                elif item['dir'] == 'vr':
                    names = []
                    for item in tokens[y-1]:
                        if item['kind'] != 'indexed':
                            raise NotImplementedError
                        name = item['name']
                        if name in used:
                            continue
                        names += [ name ]
                        used.add(name)
                    if not names:
                        continue
                    acc = []
                    n = env[names[0]]['n']
                    for name in names:
                        assert env[name]['n'] == n
                        decls += [ { 'kind': 'decl-vector',  'targets': [ { 'name': name, 'length': n } ] } ]
                        reads += [ { 'kind': 'read-indexed', 'targets': [ { 'name': name, 'index': 0 } ] } ]
                    it += merge_ops(decls)
                    it += [ { 'kind': 'loop', 'length': n, 'body': merge_ops(reads) } ]
                    decls = []
                    reads = []
                else:
                    assert False
            else:
                assert False
            it += merge_ops(decls) + merge_ops(reads)
    return it

def paren_if(n, lr):
    l, r = lr
    if n:
        return l + n + r
    else:
        return n

def export(it, repeat_macro=None, use_scanf=False):
    def go(it, nest):
        if it['kind'] == 'decl':
            if it['names']:
                return 'int {}; '.format(', '.join(it['names']))
        elif it['kind'] == 'decl-vector':
            if it['targets']:
                return 'vector<int> {}; '.format(', '.join(map(lambda x: x['name'] + paren_if(x['length'], '()'), it['targets'])))
        elif it['kind'] in [ 'read', 'read-indexed' ]:
            if it['kind'] == 'read':
                items = it['names']
            elif it['kind'] == 'read-indexed':
                items = list(map(lambda x: x['name'] + '[' + 'ijk'[nest - x['index'] - 1] + ']', it['targets']))
            if use_scanf:
                return 'scanf("{}", {});\n'.format('%d' * len(items), ', '.join(map(lambda s: '&'+s, items)))
            else:
                return 'cin >> {};\n'.format(' >> '.join(items))
        elif it['kind'] == 'loop':
            s = ''
            i = 'ijk'[nest]
            if repeat_macro is None:
                s += 'for (int {} = 0; {} < {}; ++ {}) '.format(i, i, it['length'], i)
            else:
                s += '{} ({},{}) '.format(repeat_macro, i, it['length'])
            if len(it['body']) == 0:
                s += ';'
            elif len(it['body']) == 1:
                s += go(it['body'][0], nest+1)
            else:
                s += '{ '
                for line in it['body']:
                    s += go(line, nest+1).rstrip() + ' '
                s += '}\n'
            return s
        else:
            assert False
    s = ''
    for line in it:
        s += go(line, 0)
    return s

def generate_scanner(args):
    if not args.silent:
        log.warning('This feature is ' + log.red('experimental') + '.')
    if args.silent:
        for handler in log.logger.handlers:
            log.removeHandler(handler)
    problem = onlinejudge.dispatch.problem_from_url(args.url)
    if problem is None:
        sys.exit(1)
    with utils.session(cookiejar=args.cookie) as sess:
        it = problem.get_input_format(session=sess)
    if not it:
        log.error('input format not found')
        sys.exit(1)
    try:
        it = tokenize(it)
        it = parse(it)
        it = export(it, use_scanf=args.scanf, repeat_macro=args.repeat_macro)
    except:
        log.error('somethin wrong')
        raise
    log.success('success:')
    print(log.bold(it.rstrip()))  # to stdout
