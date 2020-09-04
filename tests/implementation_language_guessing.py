import pathlib
import textwrap
import unittest

import onlinejudge_command.subcommand.submit as submit
from onlinejudge.type import Language, LanguageId

# https://atcoder.jp/contests/language-test-ver1
languages_atcoder_3 = [
    Language(id=LanguageId('3001'), name='Bash (GNU bash v4.3.11)'),
    Language(id=LanguageId('3002'), name='C (GCC 5.4.1)'),
    Language(id=LanguageId('3003'), name='C++14 (GCC 5.4.1)'),
    Language(id=LanguageId('3004'), name='C (Clang 3.8.0)'),
    Language(id=LanguageId('3005'), name='C++14 (Clang 3.8.0)'),
    Language(id=LanguageId('3006'), name='C# (Mono 4.6.2.0)'),
    Language(id=LanguageId('3007'), name='Clojure (1.8.0)'),
    Language(id=LanguageId('3008'), name='Common Lisp (SBCL 1.1.14)'),
    Language(id=LanguageId('3009'), name='D (DMD64 v2.070.1)'),
    Language(id=LanguageId('3010'), name='D (LDC 0.17.0)'),
    Language(id=LanguageId('3011'), name='D (GDC 4.9.4)'),
    Language(id=LanguageId('3012'), name='Fortran (gfortran v4.8.4)'),
    Language(id=LanguageId('3013'), name='Go (1.6)'),
    Language(id=LanguageId('3014'), name='Haskell (GHC 7.10.3)'),
    Language(id=LanguageId('3015'), name='Java7 (OpenJDK 1.7.0)'),
    Language(id=LanguageId('3016'), name='Java8 (OpenJDK 1.8.0)'),
    Language(id=LanguageId('3017'), name='JavaScript (node.js v5.12)'),
    Language(id=LanguageId('3018'), name='OCaml (4.02.3)'),
    Language(id=LanguageId('3019'), name='Pascal (FPC 2.6.2)'),
    Language(id=LanguageId('3020'), name='Perl (v5.18.2)'),
    Language(id=LanguageId('3021'), name='PHP (5.6.30)'),
    Language(id=LanguageId('3022'), name='Python2 (2.7.6)'),
    Language(id=LanguageId('3023'), name='Python3 (3.4.3)'),
    Language(id=LanguageId('3024'), name='Ruby (2.3.3)'),
    Language(id=LanguageId('3025'), name='Scala (2.11.7)'),
    Language(id=LanguageId('3026'), name='Scheme (Gauche 0.9.3.3)'),
    Language(id=LanguageId('3027'), name='Text (cat)'),
    Language(id=LanguageId('3028'), name='Visual Basic (Mono 4.0.1)'),
    Language(id=LanguageId('3029'), name='C++ (GCC 5.4.1)'),
    Language(id=LanguageId('3030'), name='C++ (Clang 3.8.0)'),
    Language(id=LanguageId('3501'), name='Objective-C (GCC 5.3.0)'),
    Language(id=LanguageId('3502'), name='Objective-C (Clang3.8.0)'),
    Language(id=LanguageId('3503'), name='Swift (swift-2.2-RELEASE)'),
    Language(id=LanguageId('3504'), name='Rust (1.15.1)'),
    Language(id=LanguageId('3505'), name='Sed (GNU sed 4.2.2)'),
    Language(id=LanguageId('3506'), name='Awk (mawk 1.3.3)'),
    Language(id=LanguageId('3507'), name='Brainfuck (bf 20041219)'),
    Language(id=LanguageId('3508'), name='Standard ML (MLton 20100608)'),
    Language(id=LanguageId('3509'), name='PyPy2 (5.6.0)'),
    Language(id=LanguageId('3510'), name='PyPy3 (2.4.0)'),
    Language(id=LanguageId('3511'), name='Crystal (0.20.5)'),
    Language(id=LanguageId('3512'), name='F# (Mono 4.0)'),
    Language(id=LanguageId('3513'), name='Unlambda (0.1.3)'),
    Language(id=LanguageId('3514'), name='Lua (5.3.2)'),
    Language(id=LanguageId('3515'), name='LuaJIT (2.0.4)'),
    Language(id=LanguageId('3516'), name='MoonScript (0.5.0)'),
    Language(id=LanguageId('3517'), name='Ceylon (1.2.1)'),
    Language(id=LanguageId('3518'), name='Julia (0.5.0)'),
    Language(id=LanguageId('3519'), name='Octave (4.0.2)'),
    Language(id=LanguageId('3520'), name='Nim (0.13.0)'),
    Language(id=LanguageId('3521'), name='TypeScript (2.1.6)'),
    Language(id=LanguageId('3522'), name='Perl6 (rakudo-star 2016.01)'),
    Language(id=LanguageId('3523'), name='Kotlin (1.0.0)'),
    Language(id=LanguageId('3524'), name='PHP7 (7.0.15)'),
]

# https://atcoder.jp/contests/judge-update-202004
languages_atcoder_4 = [
    Language(id=LanguageId('4001'), name='C (GCC 9.2.1)'),
    Language(id=LanguageId('4002'), name='C (Clang 10.0.0)'),
    Language(id=LanguageId('4003'), name='C++ (GCC 9.2.1)'),
    Language(id=LanguageId('4004'), name='C++ (Clang 10.0.0)'),
    Language(id=LanguageId('4005'), name='Java (OpenJDK 11.0.6)'),
    Language(id=LanguageId('4006'), name='Python (3.8.2)'),
    Language(id=LanguageId('4007'), name='Bash (5.0.11)'),
    Language(id=LanguageId('4008'), name='bc (1.07.1)'),
    Language(id=LanguageId('4009'), name='Awk (GNU Awk 4.1.4)'),
    Language(id=LanguageId('4010'), name='C# (.NET Core 3.1.201)'),
    Language(id=LanguageId('4011'), name='C# (Mono-mcs 6.8.0.105)'),
    Language(id=LanguageId('4012'), name='C# (Mono-csc 3.5.0)'),
    Language(id=LanguageId('4013'), name='Clojure (1.10.1.536)'),
    Language(id=LanguageId('4014'), name='Crystal (0.33.0)'),
    Language(id=LanguageId('4015'), name='D (DMD 2.091.0)'),
    Language(id=LanguageId('4016'), name='D (GDC 9.2.1)'),
    Language(id=LanguageId('4017'), name='D (LDC 1.20.1)'),
    Language(id=LanguageId('4018'), name='Dart (2.7.2)'),
    Language(id=LanguageId('4019'), name='dc (1.4.1)'),
    Language(id=LanguageId('4020'), name='Erlang (22.3)'),
    Language(id=LanguageId('4021'), name='Elixir (1.10.2)'),
    Language(id=LanguageId('4022'), name='F# (.NET Core 3.1.201)'),
    Language(id=LanguageId('4023'), name='F# (Mono 10.2.3)'),
    Language(id=LanguageId('4024'), name='Forth (gforth 0.7.3)'),
    Language(id=LanguageId('4025'), name='Fortran(GNU Fortran 9.2.1)'),
    Language(id=LanguageId('4026'), name='Go (1.14.1)'),
    Language(id=LanguageId('4027'), name='Haskell (GHC 8.8.3)'),
    Language(id=LanguageId('4028'), name='Haxe (4.0.3); js'),
    Language(id=LanguageId('4029'), name='Haxe (4.0.3); Java'),
    Language(id=LanguageId('4030'), name='JavaScript (Node.js 12.16.1)'),
    Language(id=LanguageId('4031'), name='Julia (1.4.0)'),
    Language(id=LanguageId('4032'), name='Kotlin (1.3.71)'),
    Language(id=LanguageId('4033'), name='Lua (Lua 5.3.5)'),
    Language(id=LanguageId('4034'), name='Lua (LuaJIT 2.1.0)'),
    Language(id=LanguageId('4035'), name='Dash (0.5.8)'),
    Language(id=LanguageId('4036'), name='Nim (1.0.6)'),
    Language(id=LanguageId('4037'), name='Objective-C (Clang 10.0.0)'),
    Language(id=LanguageId('4038'), name='Common Lisp (SBCL 2.0.3)'),
    Language(id=LanguageId('4039'), name='OCaml (4.10.0)'),
    Language(id=LanguageId('4040'), name='Octave (5.2.0)'),
    Language(id=LanguageId('4041'), name='Pascal (FPC 3.0.4)'),
    Language(id=LanguageId('4042'), name='Perl (5.26.1)'),
    Language(id=LanguageId('4043'), name='Raku (Rakudo 2020.02.1)'),
    Language(id=LanguageId('4044'), name='PHP (7.4.4)'),
    Language(id=LanguageId('4045'), name='Prolog (SWI-Prolog 8.0.3)'),
    Language(id=LanguageId('4046'), name='PyPy2 (7.3.0)'),
    Language(id=LanguageId('4047'), name='PyPy3 (7.3.0)'),
    Language(id=LanguageId('4048'), name='Racket (7.6)'),
    Language(id=LanguageId('4049'), name='Ruby (2.7.1)'),
    Language(id=LanguageId('4050'), name='Rust (1.42.0)'),
    Language(id=LanguageId('4051'), name='Scala (2.13.1)'),
    Language(id=LanguageId('4052'), name='Java (OpenJDK 1.8.0)'),
    Language(id=LanguageId('4053'), name='Scheme (Gauche 0.9.9)'),
    Language(id=LanguageId('4054'), name='Standard ML (MLton 20130715)'),
    Language(id=LanguageId('4055'), name='Swift (5.2.1)'),
    Language(id=LanguageId('4056'), name='Text (cat 8.28)'),
    Language(id=LanguageId('4057'), name='TypeScript (3.8)'),
    Language(id=LanguageId('4058'), name='Visual Basic (.NET Core 3.1.101)'),
    Language(id=LanguageId('4059'), name='Zsh (5.4.2)'),
    Language(id=LanguageId('4060'), name='COBOL - Fixed (OpenCOBOL 1.1.0)'),
    Language(id=LanguageId('4061'), name='COBOL - Free (OpenCOBOL 1.1.0)'),
    Language(id=LanguageId('4062'), name='Brainfuck (bf 20041219)'),
    Language(id=LanguageId('4063'), name='Ada2012 (GNAT 9.2.1)'),
    Language(id=LanguageId('4064'), name='Unlambda (2.0.0)'),
    Language(id=LanguageId('4065'), name='Cython (0.29.16)'),
    Language(id=LanguageId('4066'), name='Sed (4.4)'),
    Language(id=LanguageId('4067'), name='Vim (8.2.0460)'),
]

# 2020-04-05
languages_codeforces = [
    Language(id=LanguageId('43'), name='GNU GCC C11 5.1.0'),
    Language(id=LanguageId('52'), name='Clang++17 Diagnostics'),
    Language(id=LanguageId('42'), name='GNU G++11 5.1.0'),
    Language(id=LanguageId('50'), name='GNU G++14 6.4.0'),
    Language(id=LanguageId('54'), name='GNU G++17 7.3.0'),
    Language(id=LanguageId('2'), name='Microsoft Visual C++ 2010'),
    Language(id=LanguageId('59'), name='Microsoft Visual C++ 2017'),
    Language(id=LanguageId('61'), name='GNU G++17 9.2.0 (64 bit, msys 2)'),
    Language(id=LanguageId('9'), name='C# Mono 5.18'),
    Language(id=LanguageId('28'), name='D DMD32 v2.091.0'),
    Language(id=LanguageId('32'), name='Go 1.14'),
    Language(id=LanguageId('12'), name='Haskell GHC 8.6.3'),
    Language(id=LanguageId('60'), name='Java 11.0.5'),
    Language(id=LanguageId('36'), name='Java 1.8.0_162'),
    Language(id=LanguageId('48'), name='Kotlin 1.3.70'),
    Language(id=LanguageId('19'), name='OCaml 4.02.1'),
    Language(id=LanguageId('3'), name='Delphi 7'),
    Language(id=LanguageId('4'), name='Free Pascal 3.0.2'),
    Language(id=LanguageId('51'), name='PascalABC.NET 3.4.2'),
    Language(id=LanguageId('13'), name='Perl 5.20.1'),
    Language(id=LanguageId('6'), name='PHP 7.2.13'),
    Language(id=LanguageId('7'), name='Python 2.7.15'),
    Language(id=LanguageId('31'), name='Python 3.7.2'),
    Language(id=LanguageId('40'), name='PyPy 2.7 (7.2.0)'),
    Language(id=LanguageId('41'), name='PyPy 3.6 (7.2.0)'),
    Language(id=LanguageId('8'), name='Ruby 2.0.0p645'),
    Language(id=LanguageId('49'), name='Rust 1.42.0'),
    Language(id=LanguageId('20'), name='Scala 2.12.8'),
    Language(id=LanguageId('34'), name='JavaScript V8 4.8.0'),
    Language(id=LanguageId('55'), name='Node.js 9.4.0'),
]


class LanguageGuessingCPlusPlusTest(unittest.TestCase):
    def test_atcoder_3_gcc(self):
        languages = languages_atcoder_3
        filename = 'main.cpp'
        code = 'int main() {}\n'
        cxx_latest = True
        cxx_compiler = 'gcc'
        expected = ['3003']

        language_dict = {language.id: language.name for language in languages}  # type: Dict[LanguageId, str]
        self.assertEqual(submit.guess_lang_ids_of_file(filename=pathlib.Path(filename), code=code.encode(), language_dict=language_dict, cxx_latest=cxx_latest, cxx_compiler=cxx_compiler), expected)

    def test_atcoder_3_clang(self):
        languages = languages_atcoder_3
        filename = 'main.cpp'
        code = 'int main() {}\n'
        cxx_latest = True
        cxx_compiler = 'clang'
        expected = ['3005']

        language_dict = {language.id: language.name for language in languages}  # type: Dict[LanguageId, str]
        self.assertEqual(submit.guess_lang_ids_of_file(filename=pathlib.Path(filename), code=code.encode(), language_dict=language_dict, cxx_latest=cxx_latest, cxx_compiler=cxx_compiler), expected)

    def test_atcoder_4_gcc(self):
        languages = languages_atcoder_4
        filename = 'main.cpp'
        code = 'int main() {}\n'
        cxx_latest = True
        cxx_compiler = 'gcc'
        expected = ['4003']

        language_dict = {language.id: language.name for language in languages}  # type: Dict[LanguageId, str]
        self.assertEqual(submit.guess_lang_ids_of_file(filename=pathlib.Path(filename), code=code.encode(), language_dict=language_dict, cxx_latest=cxx_latest, cxx_compiler=cxx_compiler), expected)

    def test_atcoder_4_clang(self):
        languages = languages_atcoder_4
        filename = 'main.cpp'
        code = 'int main() {}\n'
        cxx_latest = True
        cxx_compiler = 'clang'
        expected = ['4004']

        language_dict = {language.id: language.name for language in languages}  # type: Dict[LanguageId, str]
        self.assertEqual(submit.guess_lang_ids_of_file(filename=pathlib.Path(filename), code=code.encode(), language_dict=language_dict, cxx_latest=cxx_latest, cxx_compiler=cxx_compiler), expected)

    def test_codeforces_gcc(self):
        languages = languages_codeforces
        filename = 'main.cpp'
        code = 'int main() {}\n'
        cxx_latest = True
        cxx_compiler = 'gcc'
        expected = ['61']

        language_dict = {language.id: language.name for language in languages}  # type: Dict[LanguageId, str]
        self.assertEqual(submit.guess_lang_ids_of_file(filename=pathlib.Path(filename), code=code.encode(), language_dict=language_dict, cxx_latest=cxx_latest, cxx_compiler=cxx_compiler), expected)

    def test_codeforces_clang(self):
        languages = languages_codeforces
        filename = 'main.cpp'
        code = 'int main() {}\n'
        cxx_latest = True
        cxx_compiler = 'clang'
        expected = ['52']

        language_dict = {language.id: language.name for language in languages}  # type: Dict[LanguageId, str]
        self.assertEqual(submit.guess_lang_ids_of_file(filename=pathlib.Path(filename), code=code.encode(), language_dict=language_dict, cxx_latest=cxx_latest, cxx_compiler=cxx_compiler), expected)


class LanguageGuessingPythonTest(unittest.TestCase):
    def test_atcoder_3_python_2(self):
        languages = languages_atcoder_3
        filename = 'main.py'
        code = textwrap.dedent("""\
            #!/usr/bin/env python2
            print("hello")
            """)
        python_version = 'auto'
        python_interpreter = 'cpython'
        expected = ['3022']

        language_dict = {language.id: language.name for language in languages}  # type: Dict[LanguageId, str]
        self.assertEqual(submit.guess_lang_ids_of_file(filename=pathlib.Path(filename), code=code.encode(), language_dict=language_dict, python_version=python_version, python_interpreter=python_interpreter), expected)

    def test_atcoder_3_python_3(self):
        languages = languages_atcoder_3
        filename = 'main.py'
        code = 'print("hello")\n'
        python_version = 'auto'
        python_interpreter = 'cpython'
        expected = ['3023']

        language_dict = {language.id: language.name for language in languages}  # type: Dict[LanguageId, str]
        self.assertEqual(submit.guess_lang_ids_of_file(filename=pathlib.Path(filename), code=code.encode(), language_dict=language_dict, python_version=python_version, python_interpreter=python_interpreter), expected)

    def test_atcoder_3_pypy_2(self):
        languages = languages_atcoder_3
        filename = 'main.py'
        code = textwrap.dedent("""\
            #!/usr/bin/env python2
            print("hello")
            """)
        python_version = 'auto'
        python_interpreter = 'pypy'
        expected = ['3509']

        language_dict = {language.id: language.name for language in languages}  # type: Dict[LanguageId, str]
        self.assertEqual(submit.guess_lang_ids_of_file(filename=pathlib.Path(filename), code=code.encode(), language_dict=language_dict, python_version=python_version, python_interpreter=python_interpreter), expected)

    def test_atcoder_3_pypy_3(self):
        languages = languages_atcoder_3
        filename = 'main.py'
        code = 'print("hello")\n'
        python_version = 'auto'
        python_interpreter = 'pypy'
        expected = ['3510']

        language_dict = {language.id: language.name for language in languages}  # type: Dict[LanguageId, str]
        self.assertEqual(submit.guess_lang_ids_of_file(filename=pathlib.Path(filename), code=code.encode(), language_dict=language_dict, python_version=python_version, python_interpreter=python_interpreter), expected)

    def test_atcoder_4_python_3(self):
        languages = languages_atcoder_4
        filename = 'main.py'
        code = 'print("hello")\n'
        python_version = 'auto'
        python_interpreter = 'cpython'
        expected = ['4006']

        language_dict = {language.id: language.name for language in languages}  # type: Dict[LanguageId, str]
        self.assertEqual(submit.guess_lang_ids_of_file(filename=pathlib.Path(filename), code=code.encode(), language_dict=language_dict, python_version=python_version, python_interpreter=python_interpreter), expected)

    def test_atcoder_4_pypy_2(self):
        languages = languages_atcoder_4
        filename = 'main.py'
        code = textwrap.dedent("""\
            #!/usr/bin/env python2
            print("hello")
            """)
        python_version = 'auto'
        python_interpreter = 'pypy'
        expected = ['4046']

        language_dict = {language.id: language.name for language in languages}  # type: Dict[LanguageId, str]
        self.assertEqual(submit.guess_lang_ids_of_file(filename=pathlib.Path(filename), code=code.encode(), language_dict=language_dict, python_version=python_version, python_interpreter=python_interpreter), expected)

    def test_atcoder_4_pypy_3(self):
        languages = languages_atcoder_4
        filename = 'main.py'
        code = 'print("hello")\n'
        python_version = 'auto'
        python_interpreter = 'pypy'
        expected = ['4047']

        language_dict = {language.id: language.name for language in languages}  # type: Dict[LanguageId, str]
        self.assertEqual(submit.guess_lang_ids_of_file(filename=pathlib.Path(filename), code=code.encode(), language_dict=language_dict, python_version=python_version, python_interpreter=python_interpreter), expected)

    def test_codeforces_python_2(self):
        languages = languages_codeforces
        filename = 'main.py'
        code = textwrap.dedent("""\
            #!/usr/bin/env python2
            print("hello")
            """)
        python_version = 'auto'
        python_interpreter = 'cpython'
        expected = ['7']

        language_dict = {language.id: language.name for language in languages}  # type: Dict[LanguageId, str]
        self.assertEqual(submit.guess_lang_ids_of_file(filename=pathlib.Path(filename), code=code.encode(), language_dict=language_dict, python_version=python_version, python_interpreter=python_interpreter), expected)

    def test_codeforces_python_3(self):
        languages = languages_codeforces
        filename = 'main.py'
        code = 'print("hello")\n'
        python_version = 'auto'
        python_interpreter = 'cpython'
        expected = ['31']

        language_dict = {language.id: language.name for language in languages}  # type: Dict[LanguageId, str]
        self.assertEqual(submit.guess_lang_ids_of_file(filename=pathlib.Path(filename), code=code.encode(), language_dict=language_dict, python_version=python_version, python_interpreter=python_interpreter), expected)

    def test_codeforces_pypy_2(self):
        languages = languages_codeforces
        filename = 'main.py'
        code = textwrap.dedent("""\
            #!/usr/bin/env python2
            print("hello")
            """)
        python_version = 'auto'
        python_interpreter = 'pypy'
        expected = ['40']

        language_dict = {language.id: language.name for language in languages}  # type: Dict[LanguageId, str]
        self.assertEqual(submit.guess_lang_ids_of_file(filename=pathlib.Path(filename), code=code.encode(), language_dict=language_dict, python_version=python_version, python_interpreter=python_interpreter), expected)

    def test_codeforces_pypy_3(self):
        languages = languages_codeforces
        filename = 'main.py'
        code = 'print("hello")\n'
        python_version = 'auto'
        python_interpreter = 'pypy'
        expected = ['41']

        language_dict = {language.id: language.name for language in languages}  # type: Dict[LanguageId, str]
        self.assertEqual(submit.guess_lang_ids_of_file(filename=pathlib.Path(filename), code=code.encode(), language_dict=language_dict, python_version=python_version, python_interpreter=python_interpreter), expected)


class LanguageGuessingOthersTest(unittest.TestCase):
    def test_atcoder_3_rust(self):
        languages = languages_atcoder_3
        filename = 'main.rs'
        code = 'fn main() { println!("Hello, world!"); }\n'
        expected = ['3504']

        language_dict = {language.id: language.name for language in languages}  # type: Dict[LanguageId, str]
        self.assertEqual(submit.guess_lang_ids_of_file(filename=pathlib.Path(filename), code=code.encode(), language_dict=language_dict), expected)

    def test_atcoder_4_fsharp(self):
        languages = languages_atcoder_4
        filename = 'Main.fs'
        code = 'open System\nprintfn "Hello, world!"\n'
        expected = ['4022', '4023']

        language_dict = {language.id: language.name for language in languages}  # type: Dict[LanguageId, str]
        self.assertEqual(submit.guess_lang_ids_of_file(filename=pathlib.Path(filename), code=code.encode(), language_dict=language_dict), expected)

    def test_codeforces_haskell(self):
        languages = languages_codeforces
        filename = 'Main.hs'
        code = 'main = return ()\n'
        expected = ['12']

        language_dict = {language.id: language.name for language in languages}  # type: Dict[LanguageId, str]
        self.assertEqual(submit.guess_lang_ids_of_file(filename=pathlib.Path(filename), code=code.encode(), language_dict=language_dict), expected)
