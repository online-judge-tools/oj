# Change Log

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
