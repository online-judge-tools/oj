import os
import unittest

import tests.utils


class GenerateInputTest(unittest.TestCase):
    def snippet_call_generate_input(self, args, input_files, expected_values, disallowed_files=None):
        with tests.utils.sandbox(input_files) as _:
            tests.utils.run(['generate-input'] + args, check=True)
            for expect in expected_values:
                self.assertTrue(os.path.exists(expect['path']))
                if expect['data'] is not None:
                    with open(expect['path']) as f:
                        self.assertEqual(''.join(f.readlines()), expect['data'])
            if disallowed_files is not None:
                for file in disallowed_files:
                    self.assertFalse(os.path.exists(file))

    def test_call_generate_input_parallel(self):
        self.snippet_call_generate_input(
            args=[tests.utils.python_script('generate.py'), '-j', '4'],
            input_files=[
                {
                    'path': 'generate.py',
                    'data': 'print("Hello, world!")\n'
                },
            ],
            expected_values=[{
                'path': 'test/random-{}.in'.format(str(i).zfill(3)),
                'data': 'Hello, world!\n'
            } for i in range(100)],
            disallowed_files=[
                'test/random-100.in',
            ],
        )

    def test_call_generate_input_with_output(self):
        expected_values = []
        for i in range(20):
            expected_values += [{
                'path': 'test/random-{}.in'.format(str(i).zfill(3)),
                'data': None,
            }]
            expected_values += [{
                'path': 'test/random-{}.out'.format(str(i).zfill(3)),
                'data': None,
            }]
        self.snippet_call_generate_input(
            args=[tests.utils.python_script('generate.py'), '20', '--command', tests.utils.python_script('main.py')],
            input_files=[
                {
                    'path': 'generate.py',
                    'data': 'import random\nprint(random.randrange(100))\n'
                },
                {
                    'path': 'main.py',
                    'data': 'print(int(input()) * 2)\n'
                },
            ],
            expected_values=expected_values,
            disallowed_files=[
                'test/random-100.in',
            ],
        )

    def test_call_generate_input_hack(self):
        self.snippet_call_generate_input(args=[tests.utils.python_script('generate.py'), '--command', tests.utils.python_script('ac.py'), '--hack', tests.utils.python_script('wa.py')], input_files=[
            {
                'path': 'generate.py',
                'data': 'import random\nprint(random.randint(1, 10))\n'
            },
            {
                'path': 'ac.py',
                'data': 'print(int(input()) // 10)\n'
            },
            {
                'path': 'wa.py',
                'data': 'print(0)\n'
            },
        ], expected_values=[
            {
                'path': 'test/hack-000.in',
                'data': '10\n'
            },
            {
                'path': 'test/hack-000.out',
                'data': '1\n'
            },
        ])

    def test_call_generate_input_hack_parallel(self):
        self.snippet_call_generate_input(args=[tests.utils.python_script('generate.py'), '--command', tests.utils.python_script('ac.py'), '--hack', tests.utils.python_script('wa.py'), '-j', '4'], input_files=[
            {
                'path': 'generate.py',
                'data': 'import random\nprint(random.randint(1, 100))\n'
            },
            {
                'path': 'ac.py',
                'data': 'print(int(input()) // 100)\n'
            },
            {
                'path': 'wa.py',
                'data': 'print(0)\n'
            },
        ], expected_values=[
            {
                'path': 'test/hack-000.in',
                'data': '100\n'
            },
            {
                'path': 'test/hack-000.out',
                'data': '1\n'
            },
        ])

    def test_call_generate_input_hack_with_re(self):
        self.snippet_call_generate_input(args=[tests.utils.python_script('generate.py'), '--hack-actual', tests.utils.python_script('err.py'), '-j', '4'], input_files=[
            {
                'path': 'generate.py',
                'data': 'import random\nprint(random.randint(0, 10))\n'
            },
            {
                'path': 'err.py',
                'data': 'n = int(input())\nassert n != 0\nprint(n)\n'
            },
        ], expected_values=[
            {
                'path': 'test/hack-000.in',
                'data': '0\n'
            },
        ])

    def test_call_generate_input_failure(self):
        self.snippet_call_generate_input(
            args=[tests.utils.python_script('generate.py'), '3'],
            input_files=[
                {
                    'path': 'generate.py',
                    'data': 'raise RuntimeError()\n'
                },
            ],
            expected_values=[],
            disallowed_files=['test/random-{}.in'.format(str(i).zfill(3)) for i in range(3)],
        )
