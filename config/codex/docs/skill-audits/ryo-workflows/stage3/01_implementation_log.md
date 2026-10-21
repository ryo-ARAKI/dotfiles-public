# Stage 3 実装記録

2026-10-21。採用決定は [00_decisions.md](00_decisions.md)、検証は [02_test_results.md](02_test_results.md)、最終状態は [03_final_handoff.md](03_final_handoff.md) を参照する。
ここでの「完了」は隔離worktreeのsource-only受入を指す。
active deploymentとLLM selectionの成功を含めない。

## 環境・保全

primary repositoryは `/home/ryo/github/dotfiles-public`、作業worktreeは同repository内の `.worktrees/ryo-workflows-stage3-c1`、branchは `codex/ryo-workflows-stage3-c1` である。
HEADは監査対象と同じ `737ba2926d72ad51dccfc0cf6b26cd4d2994a44d` で、変更は未commitである。
既存worktreeは再利用・移動・削除していない。
`.worktrees/` は既存ignoreにより除外され、ignore変更は不要だった。
ユーザー提供のAGENTS規約を適用し、対象repository内・ancestorに追加のAGENTS.mdは見つからなかった。

Stage 1/2の原本8件を先に読み、未追跡文書をcopyして元SHA-256を [input_hashes.json](input_hashes.json) に保存した。
production変更前に決定記録を作成した。
作業前のprimaryの136fileとindex/statusを保存し、最終保全照合の結果は検証報告に示す。
source追加・変更はこのworktreeに限定した。

## T-001 — resource identity

**完了。関連: D-001のsource側の識別不足。active環境の版ずれ自体は未解消。**

変更fileは `scripts/skill_audits/ryo_workflows/identity.py`、同directoryの `README.md`、`tests/test_ryo_workflows_identity.py` である。
manifestをpublic payloadのpath/modeの根拠とし、HEAD、関連dirty state、manifest SHA-256、各resourceのSHA-256/type/mode/size/mtime、content集合ID、metadata versionをJSON化した。
欠落、追加、空の追加directory、変更、symlink、非通常type、mode差を区別する。
symlinkを辿らず、未知fileの内容は収集しない。
private overlayは明示されたpath/hash/mode/承認originだけを比較上の期待値にできる。
実際のprivate overlayを読んだり変更したりしていない。

CLIはmatch=0、mismatch=1、入力・I/O異常=2で、新しいevidence fileを排他的に作成する。
11テストで一致・差分・symlink・mode・承認overlay・CLI statusを検証した。
metadata versionとcontent IDを分離し、catalog visibility / actual loaded resourcesは常に別の未検証欄とした。
ファイル比較をskill選択成功の証拠にしない。

## T-002 — focused評価準備

**準備完了。独立LLM比較は未実行。関連: D-001 / D-004およびStage 2 M-001〜M-008。**

変更fileは `scripts/skill_audits/ryo_workflows/` の `run_eval.py`、`original_prompts.json`、`cases.json`、`oracles.json`、`fixtures/`、`README.md`、および `tests/test_ryo_workflows_evaluation.py` である。
原P/N/Bの12promptを元文書hashとともにimmutable groupとして保存し、implicitとdisabledは同文、explicitだけskill名prefixを付ける。
修正したacceptanceを元promptから分離し、B-02のownerを既存figure skillに固定した。

focused順序はB-02、B-01、B-03、N-01で、B-02が3 mode、残りがimplicit/disabledの計9条件である。
source/fixture hash、runtime/model/normal/planning effort、実際に読まれたresource、実測usage、artifactと未検証項目のrecord templateを用意した。
oracleは評価者用としinputにはcopyしない。
B-02の区間上端とlegendの既知不整合、正しいB-01/B-03基準図、N-01のread-only fish sourceをdisposable fixtureに用意した。
全9条件を準備し、計9 PDFを既存Typstで生成して代表出力を実際に目視確認した。

preflightはtask専用 `/tmp` 配下の宣言されたcatalogとreadable rootsだけを検査し、target6 entrypoint/hash、controlからのtarget/router除外、名前を変えた既知resource混入、source/fixture不変を検査する。
model実効値、認証境界、予算、権限、実行承認のevidence不足をblockerとして返す。
11テストが成功した。
準備済みtemplateから実行済み成功を作らず、resource観測なしのselection確定・根拠なしのusage数値を拒否する。

これは供給された証拠のoffline検査であり、runnerの実効sandbox・認証・予算制御を証明しない。
LLM起動adapterは追加せず、live runnerと比較baselineの未確立を明示した。
P-02/P-06の全fixture、X系列、LLM実行、usage測定は未実行である。
改善率・速度向上・selection成功率は主張しない。

## T-003 — audit文書の分離

**隔離worktreeで完了。primary側の残存cleanupは未実施。関連: D-006。**

`config/codex/docs/skill-audits/ryo-workflows/{stage1,stage2,stage3}/` を作成した。
Stage 1原本4件はbyte一致のままcopyし、Stage 2 copy4件はStage 1を指す機能するrelative linkだけを新配置に直した。
C2を含む歴史的提案、観測、hash、revision、測定を改変していない。
元文書とlink置換の関係を検証し、原本hashを保持した。

worktreeのruntime plugin内にはaudit資料を置かず、manifest集合一致の厳格な既存検査を維持した。
追加したnegative testはruntime内のaudit file混入とresource欠落を検出する。
ignore拡大は行っていない。
primaryの元 `skills/stage1/` 4件を削除していないため、primaryの従来の配布境界問題は別途残る。

## T-004 — output path保護

**完了。関連: D-003。**

`extrip-to-ics/scripts/build_ics.py`、同skillの `SKILL.md`、plugin `README.md`、`tests/test_extrip_publication.py` を変更した。
指定pathの字句上の `..` を拒否し、既存directory componentをrootから `lstat` で検査する。
output directory、途中component、leaf/dangling symlink、非通常targetを公開前に拒否し、各公開直前にも確認する。
空白を含む通常pathを維持した。

owner管理のtrusted directoryを前提とし、正当なsymlink aliasも拒否する互換性変更を明記した。
外部sentinel、非対象file、既存hard-link inodeを保護するfixture試験が成功した。
非協調writerや悪意あるraceへの完全防御は主張しない。

## T-005 — C1 publication

**完了。関連: D-002。Stage 2のC2をユーザー選択C1へ置換。**

T-004と同じhelper・文書・新テストを変更した。
全event/filename/collisionと全ICS bodyを先に検証・構築し、outputと同じfilesystemのprivate 0700 directoryへ全fileをstageする。
各fileをcloseし再読一致を確認してから最初の公開へ進む。
既存permission bitsは再読後に適用し、write-only targetも扱う。

overwriteは `os.replace`、no-clobberは完成stageから `os.link` で公開する。
後者が未対応なら安全に失敗し、finalへの直接streamingにfallbackしない。
公開途中の失敗では停止し、成功operation record、失敗名、未試行、batch完了、観測、uncertainty、cleanup残存を `PublicationError(OSError)` で返す。
CLIは従来同様に非zeroとなり、予約bodyをerrorへ含めない。
成功returnのないoperationを観測だけで成功扱いしない。
全公開後のcleanupだけの失敗は通常returnと `PublicationCleanupWarning` で通知する。

公開済みの完全新版を保ち、未試行の旧版を戻す処理は行わない。
旧file backup、rollback、journal、persistent lock、recovery interfaceを追加していない。
19件の障害注入・filesystemテストと既存ICS7件が成功した。
公開単位のinodeは変わり、ACL/xattr・hard-link関係の維持、停電耐久性、crash recovery、batch snapshotは保証しない。
`generate(events, output_dir, combined="trips.ics", overwrite=False)` と成功counts、CLI/JSON、calendar生成関数を維持した。

## T-006 — figure read-only review

**source説明の更新完了。LLM discoveryの効果は未評価。関連: D-004。**

`creating-and-editing-typst-figures/SKILL.md` のdescriptionと操作表、read-only手順、返却物を限定更新した。
plugin `README.md` とmetadataの説明・default promptも整合させた。
保存値・点・区間端・series・legendをsource/data根拠と照合し、findingsを返すmodeを明記した。
read-onlyでは既存sourceと配布成果物を保持し、必要なcompileはdisposable outputを使う。

figure実装・科学的表示確認はfigure、論旨・文脈caption・page compositionはreport、抽出・移設はexportという既存責任を維持した。
font-only/caption-only依頼を別workflowへ拡張しない。
名前・6-skill構成・参照文書の数値不変条件は維持した。
frontmatter、local link、packaging、fixture基準PDFを検証したが、選択率改善の証拠とはしていない。

## T-007 — arXiv completion scope

**完了。関連: D-005。**

`creating-arxiv-diff-pdfs/SKILL.md` のCompletion節だけを変更した。
公式source identity、原version baseline、raw diffのcommand/hash/不変、本文・bibliography・appendix coverage、最終log/PDF一致、fatal/関連warning、structure、実際のfirst/middle/last目視をmandatoryとして残した。
必要なら追加page確認を行い、helperやsample image生成だけでcoverage/目視を代替しない。

未検証mandatoryがあるPDFを完成扱いせず、依頼外の上流科学再現や任意調査を区別する。
verifier実装・troubleshooting referenceは変更していない。
既存12テストが成功した。
本sessionで公式arXivの全文diff PDFは生成しておらず、このテストをend-to-end成功とは扱わない。

## T-008 — packaging metadata

**source上で完了。関連: D-001 / D-006。**

plugin `.codex-plugin/plugin.json` と `README.md` を更新した。
現metadata、Git履歴、既存manifest方式を確認し、sourceのrelease labelを `0.1.1` とした。
skill名・19 public resource path・manifest・deployed mode `0644`・private合成方式を維持した。
内容・source/observed identity・catalog・actual loadを区別し、version更新だけではactive cacheを更新しないと記述した。

既存installerを `/tmp` の新規destinationだけに適用し、19 fileのbyte/modeとidentity一致を確認した。
strict配布テスト3件を維持し、2件の追加テストで6-skill集合とnegative配布境界を固定した。
active install、private overlay、vendor cache、standalone skillは変更していない。

## T-009 — regressionと最終検証

**source-onlyの必須検証完了。LLM比較・active runtime検証は未実行。**

既存22件を削除・弱化せず、新規43件を加えた関連65件が成功した。
既存ICS7件、arXiv12件の実装・テストは変更していない。
6 frontmatter、runtime local links、audit配置/link、manifest集合・mode、source identity、final diff、primary保全を確認した。
設計したが実行していないLLM/X/C2関連試験を、実行済みの決定的試験と区別した。

最終reviewはsubagentを使わずself-reviewで行った。
確認範囲・具体的結果・制限は検証報告に示す。
T-010、commit、push、deployment、global config変更、依存導入、認証copy、外部API writeは行っていない。
