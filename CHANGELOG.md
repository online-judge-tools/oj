# Change Log

## 11.1.3 / 2021-02-21

-   [#854](https://github.com/online-judge-tools/oj/pull/854) fix a link in the help message ([@shuuji3](https://github.com/shuuji3))
-   [#857](https://github.com/online-judge-tools/oj/pull/857) add some links to the getting started page from the help message

## 11.1.2 / 2021-02-15

-   [#852](https://github.com/online-judge-tools/oj/pull/852) show a hint message when cookie.jar is broken
-   [#848](https://github.com/online-judge-tools/oj/pull/848) fix a message of generate-input command with --hack option

## 11.1.1 / 2020-11-07

-   [#839](https://github.com/online-judge-tools/oj/pull/839) improve the error messages about updating packages ([@granddaifuku](https://github.com/granddaifuku))

## 11.1.0 / 2020-10-23

-   [#833](https://github.com/online-judge-tools/oj/pull/833)
    -   add aliases `--hack-actual` and `--hack-expected` for `--hack` option of `generate-input` subcommand
    -   make `generate-input` subcommand print warnings when the given input generator doesn't generate random input cases
    -   improve `--help` messages

## 11.0.0 / 2020-09-04

-   [#816](https://github.com/online-judge-tools/oj/pull/816) (breaking changes) remove Python 3.5 support
-   [#811](https://github.com/online-judge-tools/oj/pull/811) [#790](https://github.com/online-judge-tools/oj/pull/790) (breaking changes) update the `test` subcommand
    -   `--print-input` is now default.
    -   `--ignore-spaces` option and `--ignore-spaces-and-newlines` option are added.
    -   Now it always ignores the difference between CRLF and LF.
    -   Some options are renamed or removed.
    -   The current default behavior uses exact matching but ignores the difference of CRLF and LF.
        -   The previous default used exact matching but ignored trailing spaces and newlines of files. It was the same to the matching algorithm in Anarchy Golf.
-   [#819](https://github.com/online-judge-tools/oj/pull/819) (breaking changes) remove some options from `submit`
    -   The options `--format-dos2unix`, `--format-rstrip`, `--golf` are removed. They are options for code golf.
-   [#821](https://github.com/online-judge-tools/oj/pull/821) replace the default command of `test` subcommand on Windows with `.\a.exe`
-   [#818](https://github.com/online-judge-tools/oj/pull/818) improve the output of `test` subcommand
-   [#813](https://github.com/online-judge-tools/oj/pull/813) [#819](https://github.com/online-judge-tools/oj/pull/819) update some hint messages
-   [#825](https://github.com/online-judge-tools/oj/pull/825) (breaking changes) change to print logs to stdout instead of stderr  ([@ryo-n](https://github.com/ryo-n))
    -   `--json` options of some subcommands are also removed. They used stdout.

## 10.1.3 / 2020-09-01

-   [#806](https://github.com/online-judge-tools/oj/pull/806) fix a bug of `generate-input` subcommand about logging  ([@rsk0315](https://github.com/rsk0315))
-   [#807](https://github.com/online-judge-tools/oj/pull/807) fix a bug of `generate-input` subcommand which happens when generators failed

## 10.1.2 / 2020-08-22

-   [#801](https://github.com/online-judge-tools/oj/pull/801) fix a bug of logging on Windows `cmd.exe`

## 10.1.1 / 2020-08-14

-   [#797](https://github.com/online-judge-tools/oj/pull/797) add a hint message to install WebDriver

## 10.1.0 / 2020-08-13

-   [#791](https://github.com/online-judge-tools/oj/pull/791) add WebDriver supports of more browsers
-   [#789](https://github.com/online-judge-tools/oj/pull/789) change the style of logging from [pwntools](https://github.com/Gallopsled/pwntools)'s one to Python's standard one
-   [#793](https://github.com/online-judge-tools/oj/pull/793) fix a minor bug of logging

## 10.0.5 / 2020-07-12

-   [#787](https://github.com/online-judge-tools/oj/pull/787) add a workaround for the conflict of a module name

## 10.0.4 / 2020-07-12

-   [#783](https://github.com/online-judge-tools/oj/pull/783) remove a workaround for the conflict of a module name
-   [#784](https://github.com/online-judge-tools/oj/pull/784) fix an issue about opening webbrowsers under Windows Subsystem for Linux (helped by [@orisano](https://github.com/orisano) and [@southball](https://github.com/southball))
-   [#785](https://github.com/online-judge-tools/oj/pull/785) print the versions for user support

## 10.0.3 / 2020-05-04

-   [#767](https://github.com/online-judge-tools/oj/pull/767) correct a message to recommend updating packages
-   [#766](https://github.com/online-judge-tools/oj/pull/766) clear the history of `oj download` when the `test/` directory is empty

## 10.0.2 / 2020-05-04

-   [#759](https://github.com/online-judge-tools/oj/pull/759) fix the bug that processes remain running when Ctrl-C is pressed while `oj test` runs

## 10.0.1 / 2020-05-04

-   [online-judge-tools/api-client#26](https://github.com/online-judge-tools/api-client/pull/26) [#757](https://github.com/online-judge-tools/oj/pull/757) fix the bug of the installation

## 10.0.0 / 2020-05-03

-   create the GitHub organization [online-judge-tools](https://github.com/online-judge-tools) so that projects will work even when [@kmyk](https://github.com/kmyk) is missing
    -   Now [@yosupo06](https://github.com/yosupo06) is an owner of the organization :dart:
-   move the repository to [online-judge-tools/oj](https://github.com/online-judge-tools/oj)
-   purge the library part as [online-judge-tools/api-client](https://github.com/online-judge-tools/api-client)

## 9.2.2 / 2020-05-01

-   [#739](https://github.com/kmyk/online-judge-tools/pull/739) follow the update of the submission form of AtCoder ([@serihiro](https://github.com/serihiro))
-   [#731](https://github.com/kmyk/online-judge-tools/pull/731) fix typos in messages in `--help` ([@cgschu1tz](https://github.com/cgschu1tz))

## 9.2.1 / 2020-04-19

-   [#728](https://github.com/kmyk/online-judge-tools/pull/728) fix new errors of `oj download` on Codeforces ([@njkevlani](https://github.com/njkevlani))
-   [#725](https://github.com/kmyk/online-judge-tools/pull/725) improve an error message for failure of downloading sample cases ([@kotatsugame](https://github.com/kotatsugame))

## 9.2.0 / 2020-04-09

-   [#715](https://github.com/kmyk/online-judge-tools/pull/715) add Google Code Jam support

## 9.1.1 / 2020-04-08

-   [#718](https://github.com/kmyk/online-judge-tools/pull/718) fix a bug of `oj submit` about Python and the language update of AtCoder

## 9.1.0 / 2020-03-20

-   [#704](https://github.com/kmyk/online-judge-tools/pull/704) improve error logs of `oj download` when files already exist
-   [#706](https://github.com/kmyk/online-judge-tools/pull/706) kill zombie processes caused by `--tle` option in `oj test` 
-   [#705](https://github.com/kmyk/online-judge-tools/pull/705) make `oj submit` use Python 3 by default
-   [#705](https://github.com/kmyk/online-judge-tools/pull/705) fix a bug of `--guess-python-interpreter` option
-   [#703](https://github.com/kmyk/online-judge-tools/pull/703) allow CRLF as line separators in `oj test`
-   [#702](https://github.com/kmyk/online-judge-tools/pull/702) display trailing spaces explicitly in `oj test`
-   [#700](https://github.com/kmyk/online-judge-tools/pull/700) fix a bug of `--side-by-side` option about line numbers

## 9.0.0 / 2020-02-29

-   [#692](https://github.com/kmyk/online-judge-tools/pull/692) (breaking changes) remove `split-input` subcommand
-   [#691](https://github.com/kmyk/online-judge-tools/pull/691) (breaking changes) remove support for Topcoder Marathon Match
-   [#686](https://github.com/kmyk/online-judge-tools/pull/686) fix a bug of `--side-by-side` option

## 8.0.0 / 2020-02-14

-   [#675](https://github.com/kmyk/online-judge-tools/pull/675) snip side-by-side diff display if result is long
-   [#676](https://github.com/kmyk/online-judge-tools/pull/676) `download` command support yukicoder token ([@beet-aizu](https://github.com/beet-aizu))
-   [#671](https://github.com/kmyk/online-judge-tools/pull/671) support latest library checker
-   [#665](https://github.com/kmyk/online-judge-tools/pull/665) `test` support side-by-side diff display

## 7.8.0 / 2020-02-03

-   [#665](https://github.com/kmyk/online-judge-tools/pull/665) add Sphere Online Judge support
-   [#661](https://github.com/kmyk/online-judge-tools/pull/661) allow `submit` to guess more languages ([@eggplants](https://github.com/eggplants))
-   [#660](https://github.com/kmyk/online-judge-tools/pull/660) prevent installation using unsupported versions of Python

## 7.7.0 / 2020-01-20
-   [#654](https://github.com/kmyk/online-judge-tools/pull/654) fix a bug of git pull option about Library Checker
-   [#653](https://github.com/kmyk/online-judge-tools/pull/653) add CodeChef support
-   [#649](https://github.com/kmyk/online-judge-tools/pull/649) allow `submit` to guess Common Lisp and Clojure files by the extension [@fukamachi](https://github.com/fukamachi)

## 7.6.0 / 2019-12-30

-   [#643](https://github.com/kmyk/online-judge-tools/pull/643) make efficient about Library Checker
-   [#645](https://github.com/kmyk/online-judge-tools/pull/645) recognize URLs of spare servers of Codeforces like [m1.codeforces.com](http://m1.codeforces.com/)
-   [#636](https://github.com/kmyk/online-judge-tools/pull/636) provide internal functions about sessions as a library

## 7.5.0 / 2019-12-13

-   [#630](https://github.com/kmyk/online-judge-tools/pull/630) update the User-Agent for HackerRank
-   [#628](https://github.com/kmyk/online-judge-tools/pull/628) improve the samples parser for AtCoder
-   [#627](https://github.com/kmyk/online-judge-tools/pull/627) parse HTML in AOJ when no samples are registered in the official API
-   [#626](https://github.com/kmyk/online-judge-tools/pull/626) raise errors when no samples are found
-   [#613](https://github.com/kmyk/online-judge-tools/pull/613) fix the issue of `test` subcommand with non-Unicode outputs

## 7.4.0 / 2019-11-29

-   [@kawacchu](https://github.com/kawacchu) (AtCoder: [kawacchu](https://atcoder.jp/users/kawacchu)) joined as a maintainer :tada:
-   [#584](https://github.com/kmyk/online-judge-tools/pull/584) add `--judge-command` option to `test` with special judge ([@btk15049](https://github.com/btk15049))
-   [#609](https://github.com/kmyk/online-judge-tools/issues/609) fix an issue about sizes of terminals on CI environments (reported by [@yosupo06](https://github.com/yosupo06))
-   [#624](https://github.com/kmyk/online-judge-tools/pull/624) add an internal method `LibraryCheckerProblem.download_checker_cpp()`
-   [#616](https://github.com/kmyk/online-judge-tools/pull/616) [#619](https://github.com/kmyk/online-judge-tools/pull/619) [#620](https://github.com/kmyk/online-judge-tools/pull/620) fix some bugs on AtCoder

## 7.3.0 / 2019-11-8

-   [#591](https://github.com/kmyk/online-judge-tools/pull/591) add English translation of `run-ci-on-your-library.rst`
-   [#585](https://github.com/kmyk/online-judge-tools/pull/585) fix a bug of opening browser in OSX ([@ganow](https://github.com/ganow))
-   [#582](https://github.com/kmyk/online-judge-tools/pull/582) replace `Submission.get_problem` with `Submission.download_problem` of API
-   [#581](https://github.com/kmyk/online-judge-tools/pull/581) fix a bug of `download` for problems of UTPC2011 by improving parse method for AtCoder ([@kawacchu](https://github.com/kawacchu))
-   [#589](https://github.com/kmyk/online-judge-tools/pull/589) fix a bug of `dispatch` yukicoder URL
-   [#575](https://github.com/kmyk/online-judge-tools/pull/575) remove `--overwrite` option from `download` subcommand and now abort downloading if samples already exist

## 7.2.2 / 2019-10-23

-   [#561](https://github.com/kmyk/online-judge-tools/pull/561) fix a potential bug of yukicoder problems ([@kawacchu](https://github.com/kawacchu))
-   [#560](https://github.com/kmyk/online-judge-tools/pull/560) fix a bug of `CodeforceContest.list_problems`
-   [#562](https://github.com/kmyk/online-judge-tools/pull/562) add [the English translation](https://online-judge-tools.readthedocs.io/en/master/introduction.en.html) of introduction document ([@pieceofeden](https://github.com/pieceofeden))
-   [#567](https://github.com/kmyk/online-judge-tools/pull/567) improve English of `readme.md` ([@nishanth2143](https://github.com/nishanth2143))

## 7.2.1 / 2019-10-18

-   [#557](https://github.com/kmyk/online-judge-tools/pull/557) fix a bug if `dispatch` invalid URL
-   [#554](https://github.com/kmyk/online-judge-tools/pull/554) fix a problem of `download` part of AtCoder problem ([@yoshrc](https://github.com/yoshrc))
-   [#552](https://github.com/kmyk/online-judge-tools/pull/552) fix a problem of `download` part of yukicoder problem ([@kawacchu](https://github.com/kawacchu))
-   [#549](https://github.com/kmyk/online-judge-tools/pull/549) fix a bug of `dispatch` AtCoder contest
-   [#538](https://github.com/kmyk/online-judge-tools/issues/538) add many unittests for minor options

## 7.2.0 / 2019-09-26

-   [#527](https://github.com/kmyk/online-judge-tools/pull/527) support `download` from [Library Checker](https://judge.yosupo.jp/)

## 7.1.0 / 2019-09-22

-   [#521](https://github.com/kmyk/online-judge-tools/pull/521) fix a problem of `submit` about web browsers on Windows
-   [#517](https://github.com/kmyk/online-judge-tools/pull/517) fix a problem of `login` about WebDriver on Windows
-   [#511](https://github.com/kmyk/online-judge-tools/pull/511) add [introduction.ja.html](https://online-judge-tools.readthedocs.io/en/master/introduction.ja.html) document

## 7.0.0 / 2019-09-01

-   [#508](https://github.com/kmyk/online-judge-tools/pull/508) enable to `login` with GUI browers
-   [#505](https://github.com/kmyk/online-judge-tools/pull/505) remove `get-standings` subcommand
-   [#503](https://github.com/kmyk/online-judge-tools/pull/503) add `generate-input` subcommand
-   [#492](https://github.com/kmyk/online-judge-tools/pull/492) add `CodeforcesContest` class
-   [#484](https://github.com/kmyk/online-judge-tools/pull/484) make some breaking changes in the interface as a library
-   [#461](https://github.com/kmyk/online-judge-tools/pull/461) increase a stability of `download` subcommand

## 6.6.1 / 2019-08-19

-   [#490](https://github.com/kmyk/online-judge-tools/pull/490) enable to install with old setuptools
-   [#487](https://github.com/kmyk/online-judge-tools/issues/487) fix a bug of fetch contest which has no penalty ([@hamayanhamayan](https://github.com/hamayanhamayan))

## 6.6.0 / 2019-07-15

-   [#459](https://github.com/kmyk/online-judge-tools/issues/459) make and distribute portable executables for Windows
-   [#470](https://github.com/kmyk/online-judge-tools/pull/470) add `--mle` option for `test` subcommand

## 6.5.0 / 2019-07-05

-   [#456](https://github.com/kmyk/online-judge-tools/pull/456) support `download` samples from Facebook Hacker Cup
-   [#453](https://github.com/kmyk/online-judge-tools/pull/453) make an error message better
-   [#457](https://github.com/kmyk/online-judge-tools/pull/457) add tests about throwing exceptions

## 6.4.1 / 2019-06-18

-   [#452](https://github.com/kmyk/online-judge-tools/pull/452) fix a bug of the MLE-checking and RE

## 6.4.0 / 2019-06-16

-   [#438](https://github.com/kmyk/online-judge-tools/pull/438) update `setup.cfg` to make `oj.exe` in Windows environments
-   [#439](https://github.com/kmyk/online-judge-tools/pull/439) make `test` possible to run in parallel with `--jobs N` option
-   [#442](https://github.com/kmyk/online-judge-tools/pull/442) add a feature to check MLE for `test` using GNU time
-   [#441](https://github.com/kmyk/online-judge-tools/pull/441) [#443](https://github.com/kmyk/online-judge-tools/pull/443) [#445](https://github.com/kmyk/online-judge-tools/pull/445) [#447](https://github.com/kmyk/online-judge-tools/pull/447) [#448](https://github.com/kmyk/online-judge-tools/pull/448) [#449](https://github.com/kmyk/online-judge-tools/pull/449) [#450](https://github.com/kmyk/online-judge-tools/pull/450) fix many minor bugs

## 6.3.0 / 2019-06-05

-   [#434](https://github.com/kmyk/online-judge-tools/pull/434) fix a confusing behavior of a function ([@kjnh10](https://github.com/kjnh10))
-   [#430](https://github.com/kmyk/online-judge-tools/issues/430) follow the update of Toph
-   [#429](https://github.com/kmyk/online-judge-tools/issues/429) fix the degrade about `download`-ing system cases and the limitation of the new API of AOJ
-   [#427](https://github.com/kmyk/online-judge-tools/issues/427) add `--tle` option to `generate-output` subcommand
-   [#433](https://github.com/kmyk/online-judge-tools/pull/433) fix the bug that `--tle` option makes detached processes

## 6.2.1 / 2019-04-24

-   [#314](https://github.com/kmyk/online-judge-tools/issues/314) improve outputs for large files
-   [#411](https://github.com/kmyk/online-judge-tools/issues/411) [#412](https://github.com/kmyk/online-judge-tools/issues/412) fix degressions of `download` from AtCoder
-   [#409](https://github.com/kmyk/online-judge-tools/issues/409) remove an unused dependency from `setup.cfg`

## 6.2.0 / 2019-04-06

-   [#407](https://github.com/kmyk/online-judge-tools/pull/407) update the method to read standings of Topcoder
-   [#406](https://github.com/kmyk/online-judge-tools/pull/406) add methods to read results of Topcoder
-   [#292](https://github.com/kmyk/online-judge-tools/pull/292) implement `login --check` for Topcoder
-   [#402](https://github.com/kmyk/online-judge-tools/pull/402) add a class to represent contents of AtCoder

## 6.1.0 / 2019-03-22

-   [#380](https://github.com/kmyk/online-judge-tools/issues/380) fix a bug to get input formats from old problems of AtCoder
-   [#371](https://github.com/kmyk/online-judge-tools/issues/371) support `download` from AOJ Arena
-   [#370](https://github.com/kmyk/online-judge-tools/issues/370) fix a bug for problems of Codeforces with unusual alphabets like `F1`

## 6.0.1 / 2019-03-18

-   [#393](https://github.com/kmyk/online-judge-tools/issues/393) fix the degression of the `submit` subcommand for Topcoder with `--full-submission`
-   [#391](https://github.com/kmyk/online-judge-tools/issues/391) fix a bug of `AtCoderContest.list_problems()`

## 6.0.0 / 2019-03-14

-   [#318](https://github.com/kmyk/online-judge-tools/issues/318) enable to use this project as a library :tada:
-   [#373](https://github.com/kmyk/online-judge-tools/pull/373) [#367](https://github.com/kmyk/online-judge-tools/pull/367) [#368](https://github.com/kmyk/online-judge-tools/pull/368) [#358](https://github.com/kmyk/online-judge-tools/pull/358) [#343](https://github.com/kmyk/online-judge-tools/pull/343) [#326](https://github.com/kmyk/online-judge-tools/pull/326) [#325](https://github.com/kmyk/online-judge-tools/pull/325) add features to operate things on AtCoder
-   [#349](https://github.com/kmyk/online-judge-tools/pull/349) [#347](https://github.com/kmyk/online-judge-tools/pull/347) [#342](https://github.com/kmyk/online-judge-tools/pull/342) [#340](https://github.com/kmyk/online-judge-tools/pull/340) [#335](https://github.com/kmyk/online-judge-tools/pull/335) [#324](https://github.com/kmyk/online-judge-tools/pull/324) improve the [API documents](https://online-judge-tools.readthedocs.io/en/master/)
-   [#384](https://github.com/kmyk/online-judge-tools/pull/384) [#381](https://github.com/kmyk/online-judge-tools/pull/381) remove some subcommands
-   [#356](https://github.com/kmyk/online-judge-tools/pull/356) fix a bug of `download` from yukicoder ([@tMasaaa](https://github.com/tMasaaa))

## 0.1.55 / 2019-02-26

-   [#323](https://github.com/kmyk/online-judge-tools/pull/323) support `download` and `submit` for [Toph](https://toph.co/)'s problem archive ([@kfaRabi](https://github.com/kfaRabi))
-   [#305](https://github.com/kmyk/online-judge-tools/pull/305) support `download` for [Kattis](https://open.kattis.com/)
-   [#331](https://github.com/kmyk/online-judge-tools/pull/331) snip large outputs in all subcommands
-   [#314](https://github.com/kmyk/online-judge-tools/issues/314) fix a bug of code snipping at `submit`
-   [#311](https://github.com/kmyk/online-judge-tools/pull/311) improve the [CONTRIBUTING.md](https://github.com/kmyk/online-judge-tools/blob/master/CONTRIBUTING.md)
-   [#307](https://github.com/kmyk/online-judge-tools/pull/307) fix a bug of `submit` to yukicoder

## 0.1.54 / 2019-02-07

-   [#113](https://github.com/kmyk/online-judge-tools/issues/113) support `download` from POJ
-   [#208](https://github.com/kmyk/online-judge-tools/issues/208) support `download` and `submit` for HackerRank again
-   [#275](https://github.com/kmyk/online-judge-tools/issues/275) support `submit` to Yukicoder again
-   [#276](https://github.com/kmyk/online-judge-tools/issues/276) add messages and document to login with directly editing session tokens on `cookie.jar`
-   [#200](https://github.com/kmyk/online-judge-tools/issues/200) add `--check` option to `login` command
-   [#290](https://github.com/kmyk/online-judge-tools/issues/290) add an error message for when `setuptools` is too old

## 0.1.53 / 2019-01-28

-   [@fukatani](https://github.com/fukatani) (AtCoder: [ryoryoryo111](https://atcoder.jp/users/ryoryoryo111)) joined as a maintainer :tada:
-   [#281](https://github.com/kmyk/online-judge-tools/pull/281) add `--version` option
-   [#243](https://github.com/kmyk/online-judge-tools/pull/243) add the PePy badge to `readme.md`
-   [#259](https://github.com/kmyk/online-judge-tools/pull/259) introduce code formatters to repo
-   [#257](https://github.com/kmyk/online-judge-tools/pull/257) fix regexp-injection and glob-injection bugs ([@Pachicobue](https://github.com/Pachicobue))

## 0.1.52 / 2019-01-22

-   [#251](https://github.com/kmyk/online-judge-tools/issues/251) support `submit` to Codeforces
-   [#245](https://github.com/kmyk/online-judge-tools/issues/245) guess/check problems to `submit` from the history of `download` command
-   [#247](https://github.com/kmyk/online-judge-tools/issues/247) add tests for `submit` command
-   [#246](https://github.com/kmyk/online-judge-tools/pull/246) add the help message for `--tle` option ([@fukatani](https://github.com/fukatani))

## 0.1.51 / 2019-01-06

-   [#239](https://github.com/kmyk/online-judge-tools/pull/239) fix bugs of `generate-output` and add tests ([@fukatani](https://github.com/fukatani))
-   [#234](https://github.com/kmyk/online-judge-tools/issues/234) add tests for `test` command
-   [#233](https://github.com/kmyk/online-judge-tools/pull/233) fix bugs of `test` ([@fukatani](https://github.com/fukatani))
-   [#28](https://github.com/kmyk/online-judge-tools/issues/28), [#232](https://github.com/kmyk/online-judge-tools/issues/232): fix a problem on encodings on AtCoder
-   [b8a961](https://github.com/kmyk/online-judge-tools/commit/b8a9617e0e9f8256e85a30830fa30ddc284d744f) add [CONTRIBUTING.md](https://github.com/kmyk/online-judge-tools/blob/master/CONTRIBUTING.md)

## 0.1.50 / 2019-01-02

-   [#225](https://github.com/kmyk/online-judge-tools/pull/225) heavy refactoring
-   [#224](https://github.com/kmyk/online-judge-tools/pull/224) improve auto update-checking
-   [#223](https://github.com/kmyk/online-judge-tools/pull/223) start using tags to make release

## 0.1.49 / 2019-01-02

-   [#222](https://github.com/kmyk/online-judge-tools/pull/222) created [the Gitter room](https://gitter.im/online-judge-tools/community)
-   [#219](https://github.com/kmyk/online-judge-tools/issues/219) fix a bug that type checking doesn't work on CI
-   [#218](https://github.com/kmyk/online-judge-tools/pull/218) add support for Python 3.5 ([@fukatani](https://github.com/fukatani))

## 0.1.48 / 2018-12-30

-   [#213](https://github.com/kmyk/online-judge-tools/issues/213) update the package on PyPI via Travis CI

## 0.1.47 / 2018-12-28

-   [#210](https://github.com/kmyk/online-judge-tools/issues/210) fix a bug of `download` from AtCoder

## 0.1.46 / 2018-12-17

-   [#208](https://github.com/kmyk/online-judge-tools/issues/208) features for HackerRank are removed
-   [#206](https://github.com/kmyk/online-judge-tools/issues/206) support the new `atcoder.jp` domain
-   [#202](https://github.com/kmyk/online-judge-tools/issues/202) write document
-   [#201](https://github.com/kmyk/online-judge-tools/issues/201) add `--json` option to `download` command

## 0.1.45 / 2018-11-26

-   [#193](https://github.com/kmyk/online-judge-tools/issues/193) make languages selectable with their IDs with
-   [#198](https://github.com/kmyk/online-judge-tools/issues/198) suppress leading spaces of samples at Codeforces

## 0.1.44 / 2018-11-21

-   [#193](https://github.com/kmyk/online-judge-tools/issues/193) fix an unintended behaviour of `--language` option of `submit` with `--guess` option; add some file extensions for Perl and Perl 6

## 0.1.43 / 2018-11-21

-   [#188](https://github.com/kmyk/online-judge-tools/issues/188) fix a degression of `download` system cases of AOJ
-   [#194](https://github.com/kmyk/online-judge-tools/issues/194) use the official API of AOJ
-   [#196](https://github.com/kmyk/online-judge-tools/issues/196) support the beta version of AOJ

## 0.1.42 / 2018-11-04

-   [#189](https://github.com/kmyk/online-judge-tools/issues/189) fix a degression of `submit` to AtCoder

## 0.1.41 / 2018-11-04

-   [#186](https://github.com/kmyk/online-judge-tools/pull/186) fix a problem of sample cases of AOJ and lxml ([@hachi-88](https://github.com/hachi-88))

## 0.1.40 / 2018-11-03

-   [#141](https://github.com/kmyk/online-judge-tools/issues/141) add a feature to check updating
-   [#168](https://github.com/kmyk/online-judge-tools/issues/168) use HTTPS for codeforces.com
-   [#183](https://github.com/kmyk/online-judge-tools/issues/183) add type hints

## 0.1.39 / 2018-10-06

-   [#180](https://github.com/kmyk/online-judge-tools/issues/180) add `-d DIRECTORY` option to `download` `test` `generate-output` commands

## 0.1.38 / 2018-08-27

-   update around `submit` command
-   [#177](https://github.com/kmyk/online-judge-tools/issues/177) make `--open` by default of `submit` command
-   [#177](https://github.com/kmyk/online-judge-tools/issues/177) add `--format-dos2unix` `--format-rstrip` `--golf` options for `submit` command
-   [#108](https://github.com/kmyk/online-judge-tools/issues/108) enable to guess the language to `submit`

## 0.1.37 / 2018-07-31

-   [#171](https://github.com/kmyk/online-judge-tools/issues/171) fix typos
-   [#172](https://github.com/kmyk/online-judge-tools/issues/172) fix bugs

## 0.1.36 / 2018-07-29

-   [#171](https://github.com/kmyk/online-judge-tools/pull/171) fix typos ([@fukatani](https://github.com/fukatani))
-   [#172](https://github.com/kmyk/online-judge-tools/pull/172) make easy to choose languages to `submit` ([@fukatani](https://github.com/fukatani))

## 0.1.35 / 2018-07-22

-   [#169](https://github.com/kmyk/online-judge-tools/pull/169) fix typos ([@fukatani](https://github.com/fukatani))

## 0.1.34 / 2018-07-04

-   [#167](https://github.com/kmyk/online-judge-tools/pull/167) update `login` for updating of codeforces's webpage ([@kjnh10](https://github.com/kjnh10))

## 0.1.33 / 2018-07-03

-   [#162](https://github.com/kmyk/online-judge-tools/issues/162) fix a bug of `login` for beta.atcoder.jp

## 0.1.32 / 2018-05-08

-   [#58](https://github.com/kmyk/online-judge-tools/issues/58) add `get-standings` command for TopCoder MM
-   [#154](https://github.com/kmyk/online-judge-tools/issues/154) `--shell` by default of `test`
-   [#153](https://github.com/kmyk/online-judge-tools/issues/153) use 1-based for lineno of `-1` option of `test`
-   [#152](https://github.com/kmyk/online-judge-tools/issues/152) add newline for `--header` option of `split-input` command

## 0.1.31 / 2018-03-19

-   [#147](https://github.com/kmyk/online-judge-tools/issues/147) update around CI

## 0.1.30 / 2018-03-19

-   [#54](https://github.com/kmyk/online-judge-tools/issues/54) [#60](https://github.com/kmyk/online-judge-tools/issues/60) stop using selenium to `submit` to TopCoder MM
-   [#138](https://github.com/kmyk/online-judge-tools/issues/138) improve the error message of `login` for AtCoder

## 0.1.29 / 2018-01-08

-   [#130](https://github.com/kmyk/online-judge-tools/issues/130) make `--rstrip` by default of `test`
-   [#131](https://github.com/kmyk/online-judge-tools/issues/131) add `--print-input` option to `test`

## 0.1.28 / 2018-01-06

-   [#59](https://github.com/kmyk/online-judge-tools/issues/59) add `code-statistics` command
-   [#118](https://github.com/kmyk/online-judge-tools/issues/118) remove `login` feature for yukicoder
-   [#116](https://github.com/kmyk/online-judge-tools/issues/116) ignore backup files at `test`
-   [#112](https://github.com/kmyk/online-judge-tools/issues/112) suppress wrong warnings of `download`
-   [#117](https://github.com/kmyk/online-judge-tools/issues/117) use beta.atcoder.jp for `--open` of `submit`
