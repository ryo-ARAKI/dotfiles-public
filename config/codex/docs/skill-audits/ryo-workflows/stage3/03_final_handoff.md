# Stage 3 最終引継ぎ

2026-10-21。隔離worktreeで承認済みsource実装と決定的検証を完了し、ユーザーreviewに渡せる状態である。
commit/merge/push/deployment、独立LLM比較、active runtime検証は行っていない。
T-010は開始していない。

## 対象と実装状況

repositoryは `/home/ryo/github/dotfiles-public`、worktreeは `.worktrees/ryo-workflows-stage3-c1`、branchは `codex/ryo-workflows-stage3-c1` である。
base HEADは `737ba2926d72ad51dccfc0cf6b26cd4d2994a44d`。
未commitのsource release labelは `0.1.1`、public payload IDは `9fb05b6cec98d4e57624706ebe11fcffafeb21017665386fad4d2d212385feeb`。
個別hash/modeは [source_identity.json](source_identity.json) にある。

| Task | 実際の状態 |
| --- | --- |
| T-001 | runtime外のread-only identity tool、JSON/差分/overlay/type/mode、11テスト完了 |
| T-002 | 元12prompt保持、focused9条件、fixture/record/preflight、11テスト完了。LLM0 run |
| T-003 | worktree内Stage 1/2/3をruntime外に配置。primary原本cleanupは残存 |
| T-004 | symlink/非通常target/字句上 `..` 拒否、trusted-directory前提の実装と試験完了 |
| T-005 | C1 stage-all/per-file atomic replace/no-clobber、部分状態report、19テスト完了 |
| T-006 | figure review description/手順/metadata更新完了。実selection効果は未評価 |
| T-007 | arXiv mandatory gateと任意調査の境界を明確化。verifier維持 |
| T-008 | metadata/README/19-file manifest互換を確認。active cache更新なし |
| T-009 | 関連65テスト、6 frontmatter、link/配布/identity/final diff/保全の必須source検証完了 |

詳細は [01_implementation_log.md](01_implementation_log.md)、実行/未実行の区別は [02_test_results.md](02_test_results.md)、決定は [00_decisions.md](00_decisions.md) を参照する。

## 現在の6-skill構成

1. `dotfiles-deploy`: managed source/overlayと承認deployment。
2. `creating-arxiv-diff-pdfs`: 公式sourceの完全diff PDFと必須acceptance。
3. `creating-and-editing-typst-figures`: 科学図の作成・改訂・read-only表示review。
4. `export-editable-typst-figures`: 編集可能bundleの抽出・来歴・portability。
5. `writing-typst-research-reports`: 論旨・保存結果・caption・page composition。
6. `extrip-to-ics`: 予約Markdownからreview済みJSONを経るICS作成。

既存名を維持し、新skill/router/shared runtimeは追加していない。
font-onlyはfigure、caption/layout-onlyはreportに保つ。
数値・condition tuple・normalization・interval端・figure identity/provenance・lossless exportの既存規則を維持した。

## 診断別の判定

| Finding | source-only受入 | 残る事項 |
| --- | --- | --- |
| D-001 版/実行resource不一致 | identityと証拠分離を実装 | **active解消は未確認**。実install/catalog/actual read・execute path/hashが必要 |
| D-002 ICS部分更新 | C1として受入。全stage・atomic公開・部分reportを検証 | 旧新版混在は選択C1の許容状態。batch rollbackなし |
| D-003 symlink越境 | path policyとsentinel試験に合格 | trusted directory前提。悪意あるrace/非協調writerは保証外 |
| D-004 figure review discovery | description/read-only mode更新 | LLM効果・改善率は未測定 |
| D-005 arXiv完了scope | mandatory PDF acceptanceと任意調査を区別 | 新しい公式全文PDFのend-to-end評価なし |
| D-006 audit/payload干渉 | worktree配置とstrict配布検査に合格 | primary元Stage 1の4件は別途cleanupが必要 |

新たな未解決の重大な決定的failureはない。
checkout0664/deployed0644をcontent差と分離した。
reviewで見つけたwrite-only targetのstage再読順序は修正して回帰テストを追加した。
cleanup-only warningとreplaceによるinode/ACL/xattr互換性はreview対象である。

## C1の確定契約と制限

全event/name/collision/payloadを検証し、全bodyを同filesystemへstage/close/再読後に公開する。
準備/stage失敗は旧finalを変更しない。
`os.replace`、no-clobber `os.link` により各finalを完全fileとして公開する。
既存/公開時競合を上書きせず、未対応filesystemではfinal直接書込へfallbackしない。

途中失敗で停止し、公開済み完全新版と未試行旧版/未作成を保持する。
成功operation、失敗、未試行、完了flag、観測、不確実性、cleanupを区別する。
publication失敗は `PublicationError(OSError)` とCLI非zero、全公開後cleanupのみの失敗は通常countsと `PublicationCleanupWarning` である。
予約bodyをerrorへ含めない。

batch全体atomic、rollback、cross-file snapshot、journal、persistent lock、手動recovery、SIGKILL回復、停電耐久性は提供しない。
trusted directoryと対応filesystem semanticsを前提とし、正当なpath aliasも拒否する。
普通の `lstat` は悪意あるraceや非協調writerからのisolationを保証しない。

## 必須検証と証拠

既存22 + 新規43 = **65テスト成功**。
C1-F01〜F10、6 frontmatter、19 public fileのmanifest/byte/mode、functional links、copy履歴、final diff、primary保全を確認した。
9 fixture PDFを生成し代表3種類を目視確認した。
arXiv12件にはmock toolを含み、LLM/公式全文PDF成功を意味しない。
無関係な全repository suiteは再実行していない。

原文8件は [input_hashes.json](input_hashes.json)、検証集約は [validation_evidence.json](validation_evidence.json) にある。
一次evidence/preview/planは `/tmp/ryo-workflows-stage3-oyi6eyba/` にあり長期保存は保証しない。
外部runner準備は [source audit tools](../../../../../../scripts/skill_audits/ryo_workflows/README.md) に記載した。

## 未完了とeventual deployment前のreview

1. C1部分公開、cleanup-only warning、alias拒否、inode/ACL/xattr差、source version `0.1.1` をユーザーがreviewする。
2. primaryの未追跡Stage 1原本4件は未変更である。source統合時に新docsと照合し、対象を明示した別承認のcleanupとして扱う。primaryでは従来の配布境界failureが残り得る。
3. LLM実行にはcatalog/filesystem/instruction隔離、実効client/model/両effort、runner-native認証、承認予算、workspace権限、実行承認が必要である。元baselineも0 runで、after-onlyを改善率にしない。
4. deploymentは別途具体的targetへの承認後とする。public/private revisionと承認overlayを固定し、既存manifest方式の生成/dry-runを確認する。
5. 許可されたdeploy後にfile identityを照合し、別にfresh catalogと実際に読まれたpath/hashを確認する。source versionだけでactive cache更新やD-001解消を主張しない。

実施しなかった操作はT-010、commit/push/merge、deployment、active/vendor/global/standalone/private overlay変更、依存導入、認証copy、Calendar/remote write、subagent、C2回復機構の実装である。
source-only実装の終了地点で停止する。
