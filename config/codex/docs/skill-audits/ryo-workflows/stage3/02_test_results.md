# Stage 3 検証結果

2026-10-21。決定的source検証は合格、独立LLM評価とactive runtime検証は未実行である。
機械可読集約は [validation_evidence.json](validation_evidence.json)、public比較は [source_identity.json](source_identity.json) に保存する。

## 環境とidentity

worktreeは `/home/ryo/github/dotfiles-public/.worktrees/ryo-workflows-stage3-c1`、branchは `codex/ryo-workflows-stage3-c1` である。
HEAD `737ba2926d72ad51dccfc0cf6b26cd4d2994a44d` は監査版と一致するが、今回の検証対象は未commit差分を含む。
Python 3.12.3、Git 2.43.0、Typst 0.15.1（commit表示unknown）、既存DejaVu fontsとPopplerを使った。
`/tmp` のfilesystem type表示は `ext2/ext3` だった。他filesystemでの成功を主張しない。

| Identity | 内容 |
| --- | --- |
| audited public 19 file | `c151389fc6ffe21c12624ce7db6f2f024fe0b27912e0d1c76317528d0aaa162c` |
| 今回のpublic 19 file | `9fb05b6cec98d4e57624706ebe11fcffafeb21017665386fad4d2d212385feeb` |
| source metadata label | `0.1.1` |

identityはmanifestと相対path/SHA-256集合を根拠とし、mode/type/size/mtimeを別に記録する。
checkout実mode0664とmanifest deployed mode0644は異なる。
初期source自身の比較はmode差19件でexit 1、内容集合は一致した。完全なfile identity一致とは報告しない。
既存installerで新規 `/tmp/ryo-workflows-stage3-oyi6eyba/packaging-check/plugin` へcopyした19 fileは、内容/type/mode/集合が全て一致しidentity CLI exit 0だった。
active destinationは使用していない。

## 今回実行したregression tests

command形式は `python3 -B -m unittest discover -s tests -p PATTERN -v`、cwdはworktree rootである。
`-B` でpayload内bytecode生成を避けた。

| Pattern | 結果 | 範囲 |
| --- | ---: | --- |
| `test_extrip_to_ics.py` | 7/7 | 既存ICS semantics、CLI、UID、日時、encoding、validation |
| `test_arxiv_diff_pdf_verifier.py` | 12/12 | 既存verifier unit/CLI。external tool mockを含む |
| `test_ryo_workflows_plugin.py` | 5/5 | 既存3件 + 配布negative・固定6-skill集合 |
| `test_extrip_publication.py` | 19/19 | C1障害注入、path、cleanup、permission |
| `test_ryo_workflows_identity.py` | 11/11 | 一致/差分、type/mode、overlay、CLI status |
| `test_ryo_workflows_evaluation.py` | 11/11 | 元prompt、focused準備、preflight、evidence境界 |
| 合計 | **65/65** | 既存22件保持、新規43件 |

identity/evaluation/pluginは `test_ryo_workflows*.py` でも実行し、その後evaluationに2件追加して11件全て再実行した。
重複runをtest件数へ加算していない。
Stage 1/2の過去22件とは別の今回の実測である。
無関係な全repository suiteは再実行していない。

## C1-F01〜F10

| ID | 実行内容と結果 |
| --- | --- |
| C1-F01 | 不正event/name、combined衝突、後続payload生成失敗。全final不変で公開前に失敗 |
| C1-F02 | 後続stageのENOSPC、読戻し不一致。公開0、全旧final不変、通常cleanup完了 |
| C1-F03 | replace直前の完全旧final、全stage完了、同filesystem、640/200 permissionを確認。新finalは完全body、counts保持 |
| C1-F04 | a公開後bでEIO、またはb replace後に例外。aは新版、未試行は旧版。成功returnのないbはuncertainと観測を分離 |
| C1-F05 | 既存targetと公開時の新競合を上書きしない。先に公開したaは残る |
| C1-F06 | 個別a/b公開後combinedを失敗。a/b完全新版、combined旧版、batch未完了report |
| C1-F07 | leaf/dangling/output-dir/途中parent symlinkを両modeで拒否。非通常targetと字句上 `..` も拒否。外部sentinel・hard-link外部inode不変、空白path正常 |
| C1-F08 | 部分/全公開後cleanup失敗とstage内未知fileを注入。残存を報告、rollbackを装わず、非対象fileを削除しない |
| C1-F09 | 既存7件と成功return、公開失敗CLIのexit 2/stderr。部分成功をstdoutで成功扱いしない |
| C1-F10 | `os.link` EOPNOTSUPPを注入。未対応を報告しfinalへstreamingしない |

全て使い捨てfixtureで実行した。
ENOSPC/EIO/EOPNOTSUPPはfault injectionで、実disk満杯や未対応filesystemの実機検証ではない。
成功operation、失敗、未試行、完了flag、事後観測、uncertain、cleanupを区別した。
全公開後のcleanupだけの失敗では、通常countsとwarningを返すことも実行して確認した。
各replace/linkのatomic性は対応OS/filesystem契約を前提とする。
並行reader stress、停電耐久、非協調writer、悪意あるrace、SIGKILL回復は試験していない。
C2のrollback/journal/lock/recovery試験は採用契約外である。

## semantics・arXiv・配布・保全

`escape`、`fold`、`required`、`validate`、`calendar` のASTは監査HEADと一致する。
既存ICS/arXiv test、arXiv verifier/referenceのbyte不変も確認した。
列車/宿泊stayごとのevent、checkout既定とexclusive end、UTC、UID、Maps、UTF-8/CRLF、escape/fold、JSONとfilenameを保持した。
arXivの12件は新しい公式全文PDFの完成証拠ではない。
最終diffでは公式source/raw identity、本文・bibliography・appendix coverage、log/PDF、fatal/関連warning、structure、実際の目視のmandatory維持を確認した。

6 frontmatterは既存 `skill-creator/scripts/quick_validate.py` に全合格した。
runtime link/anchorは既存配布テストがdisposable copy上で検証した。
audit Stage 1/2/3と新tool説明のfunctional local linkも検査した。
public payloadは19 file・6 entrypointで、audit/tool/testはruntime外にある。
未知audit混入とrequired file欠落を拒否するnegative testを追加し、配布検査を緩和していない。
Stage 1 copy4件のbyte一致と、Stage 2 copy4件の指定relative linkだけの置換を照合した。
原本8件のSHA-256は保存値と一致した。
primaryの136 fileのhash/mode/type、HEAD/status/indexもsnapshotと一致した。
追跡diffと新規source/test/fixture/reportをself-reviewし、`git diff --check` が成功した。

## fixture compile・目視

`run_eval.py prepare --source-repo . --destination /tmp/ryo-workflows-stage3-oyi6eyba/focused-preparation --compile-fixtures` を実行した。
9条件でfigure7 PDFとreport2 PDFを生成した。
代表B-02/B-01/B-03をPopplerで画像化し、実際に目視確認した。
4 tupleを保持し、B-02には意図したA/tau=1上端2.4（保存2.2）と逆legend色、正しい基準図とreportのcaption/配置、user edit保持sentinelが確認できた。
これはfixture準備の成功であり、LLMが発見/修正した結果ではない。
PDF/preview/planはtask専用 `/tmp` にあり、repositoryへbinary/authをcopyしていない。

## 未実行と制限

独立LLM評価は **0 run**、usage/costは未測定の `null` である。
準備済み9条件への空prerequisite preflightはexit 2、`llm_executed=false` と不足blockerを返した。
実効catalog隔離、client/model/normal/planning effort、認証境界、承認予算、workspace権限、実行承認が未確立である。
unit testのsynthetic完備evidenceはoffline validatorの試験であり、live条件成立を意味しない。
元before LLM baselineもなく、after-onlyを実行しても絶対評価となる。
selection改善、font/caption/read-only scope遵守、性能改善は未評価である。
P-02/P-06全fixture、X系列、公式arXiv全文生成、全filesystemは未実行である。
active install/catalog/actual load/private overlay/standaloneは今回再検証していない。
重大な決定的testの未解決failureはないが、C1旧新版混在、一時残存、alias拒否の明示的制限は残る。
