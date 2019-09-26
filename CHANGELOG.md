# Change Log

## 7.2.0 / 2019-09-26

-   [#527](https://github.com/kmyk/online-judge-tools/pull/527) suppoert `download` from [Library Checker](https://judge.yosupo.jp/)

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
