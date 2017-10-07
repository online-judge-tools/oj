# Python Version: 3.x
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

def tokenize(pre):  # => [ [ dict ] ]
    for y, line in enumerate(pre.splitlines()):
        # remove mathjax tokens
        line = line.replace('$', '').replace('\\(', '').replace('\\)', '')
        line = line.replace('\\ ', ' ').replace('\\quad', ' ')
        # tokenize each line
        tokens = []
        for x, s in enumerate(line.split()):
            if s in [ '..', '...', '\\dots', '…', '⋯' ]:
                tokens += [ { 'kind': 'dots', 'dir': ['hr', 'vr'][x == 0] } ]
            elif s in [ ':', '\\vdots', '⋮' ]:
                tokens += [ { 'kind': 'dots', 'dir': 'vr' } ]
            elif '\\' in s:
                assert False
            elif '_' in s:
                assert s.count('_') == 1
                s, ix = s.split('_')
                if ix.startswith('{') and ix.endswith('}'):
                    ix = ix[1:-1]
                if ',' in ix:
                    raise NotImplementedError
                tokens += [ { 'kind': 'indexed', 'name': s, 'index': ix } ]
            else:
                tokens += [ { 'kind': 'fixed', 'name': s } ]
        yield tokens

def simplify_expr(s):
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
        env[name]['n'] = simplify_expr('{}-{}+1'.format(env[name]['r'], env[name]['l']))
    used = set()
    for y, line in enumerate(tokens):
        for x, item in enumerate(line):
            if item['kind'] == 'fixed':
                yield { 'kind': 'decl', 'names': [ item['name'] ] }
                yield { 'kind': 'read', 'names': [ item['name'] ] }
            elif item['kind'] == 'indexed':
                pass
            elif item['kind'] == 'dots':
                if item['dir'] == 'hr':
                    assert line[x-1]['kind'] == 'indexed'
                    name = line[x-1]['name']
                    if name in used:
                        continue
                    n = env[name]['n']
                    yield { 'kind': 'decl-vector', 'targets': [ { 'name': name, 'length': n } ] }
                    yield { 'kind': 'loop', 'length': n, 'body': [ { 'kind': 'read-indexed', 'targets': [ { 'name': name, 'index': 0 } ] } ] }
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
                    body = []
                    for name in names:
                        assert env[name]['n'] == n
                        yield { 'kind': 'decl-vector',  'targets': [ { 'name': name, 'length': n } ] } 
                        body += [ { 'kind': 'read-indexed', 'targets': [ { 'name': name, 'index': 0 } ] } ]
                    yield { 'kind': 'loop', 'length': n, 'body': body }
                    decls = []
                    reads = []
                else:
                    assert False
            else:
                assert False

def get_names(targets):
    return list(map(lambda target: target['name'], targets))

def postprocess(it):
    def go(it):
        i = 0
        while i < len(it):
            if i - 1 >= 0 and it[i - 1]['kind'] == 'read' and it[i]['kind'] == 'decl':
                if not set(it[i - 1]['names']).intersection(it[i]['names']):
                    it[i - 1], it[i] = it[i], it[i - 1]
                    i -= 2
            elif i - 1 >= 0 and it[i - 1]['kind'] == it[i]['kind'] and it[i]['kind'] in [ 'decl', 'decl-vector', 'read', 'read-indexed' ]:
                if it[i]['kind'] in [ 'read', 'decl' ]:
                    it[i - 1]['names'] += it[i]['names']
                else:
                    it[i - 1]['targets'] += it[i]['targets']
                del it[i]
                i -= 1
            elif it[i]['kind'] == 'loop':
                it[i]['body'] = go(it[i]['body'])
            i += 1
        return it
    it = go(it)
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
                s += '{} ({}, {}) '.format(repeat_macro, i, it['length'])
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
    with utils.with_cookiejar(utils.new_default_session(), path=args.cookie) as sess:
        it = problem.get_input_format(session=sess)
    if not it:
        log.error('input format not found')
        sys.exit(1)
    try:
        log.debug('original data: %s', repr(it))
        it = list(tokenize(it))
        log.debug('tokenized: %s', str(it))
        it = list(parse(it))
        log.debug('parsed: %s', str(it))
        it = postprocess(it)
        log.debug('postprocessed: %s', str(it))
        it = export(it, use_scanf=args.scanf, repeat_macro=args.repeat_macro)
        log.debug('result: %s', repr(it))
    except:
        log.error('something wrong')
        raise
    log.success('success:')
    print(log.bold(it.rstrip()))  # to stdout
