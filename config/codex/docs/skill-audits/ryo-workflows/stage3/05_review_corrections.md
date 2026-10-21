# Stage 3 レビュー後修正

2026-10-21（Asia/Tokyo）。[独立レビュー](04_independent_code_review.md)のCR-001〜CR-004を修正し、関連90テストが成功した。
指定worktree内のsource修正はGit統合に進める状態と判断する。
実際のGit統合、active deployment、独立LLM評価は実施していない。
offline preflightの成功は、実行時隔離やskill選択の正しさを証明しない。

## 対象と保全

worktreeは `/home/ryo/github/dotfiles-public/.worktrees/ryo-workflows-stage3-c1`、branchは `codex/ryo-workflows-stage3-c1`、HEADは `737ba2926d72ad51dccfc0cf6b26cd4d2994a44d` のままである。
[決定記録](00_decisions.md)、[実装記録](01_implementation_log.md)、[既存検証報告](02_test_results.md)を参照し、C1とsource-onlyの境界を維持した。
開始時の追跡・未追跡163ファイルをSHA-256で記録し、既存のStage 3変更を今回の差分から区別した。
今回の変更は既存6ファイルと新規3ファイルの計9ファイルだけで、他の開始時ファイルの内容は不変である。
indexに変更はなく、commit、merge、push、deploy、subagent、依存導入、認証情報のcopyは行っていない。

独立レビューは歴史的証拠としてbyte単位で保全した。
そのSHA-256は `9f504a4aba1fa546c49e0ee35fec898586370e430f7cd6bd746598cf9b897417` である。
既存の `source_identity.json` と `validation_evidence.json` も過去の検証対象の記録として変更していない。
今回の修正後public payload SHA-256は `1ca88fceecef524fe2e06a2ed62495de09278703334bc81155e180ff760c566e` で、release labelは引き続き `0.1.1` である。
このcontent identityはactive環境との一致や実loadの証拠ではない。

## 修正状況

| 指摘 | 状況 | 修正内容 |
| --- | --- | --- |
| CR-001 | 完了 | 現行と監査版の既知skill資源、未掲載の既知entrypoint、router、評価者oracleを宣言済み可読root内で検出 |
| CR-002 | 完了 | 各runの実prompt bytes・SHA-256・原group・case/modeを記録し、preflightと結果recordで照合 |
| CR-003 | 完了 | 公開直前検査の失敗と公開helper呼出後の失敗をphaseと試行フラグで区別し、API・CLI・説明を整合 |
| CR-004 | 完了 | 外部結果JSONの型と参照構造を明示的に検証し、不正recordを終了コード2で制御されたエラーにする |

### CR-001 — 評価隔離の静的preflight

現行manifest内のskill資源ハッシュに加え、監査commitの17資源のSHA-256を固定表として追加した。
回帰テストで全17件のpath・hash・revisionを実Gitオブジェクトと照合する。
controlでは別名の完全copyも禁止し、targetでは既知資源を現行manifestの所定pathに限って許可する。
既知6skillと旧routerのdirectory名、先頭8192 bytes内の単純なfrontmatter `name` も検査し、catalog未掲載の入口を検出する。
通常のLFとCRLFに対応し、変更された本文や別名ファイルでも既知名を持つ入口を検出する。
両modeで現行oracleのhashと予約名 `oracles.json` を拒否する。
正常targetと無関係な匿名control fixtureは引き続き受理する。

これは現在の評価設計に必要な既知資源検査である。
任意の変形・言い換え、未知の履歴版、一般的なYAML解釈、未宣言root、runtime mount、instruction、raceを網羅するscannerではない。
実効filesystem・catalog・instruction隔離の強制は、別途承認されたrunnerと人による証拠確認の責任として残る。

### CR-002 — prompt identity

各runと保存templateに `prompt_path`、末尾LFを含む `prompt_utf8`、`prompt_sha256`、`original_prompts_sha256` を記録する。
UTF-8 bytesを直接書き、読戻した実file、記録text、SHA-256をcase/modeから得られる原promptと照合する。
Stage 1原group digestは `aa6ea58c2c85635c8857590fc5a5f956cc8cfd8cc00d6593889b888c19a6deb9` に固定した。
groupの中身と自己申告hashを同時に変更しても受理しない。
implicitとdisabledは同一bytesで、explicitだけ既存のskill prefixを付ける。
一文字追加、LFからCRLFへの変更、欠落、hash不一致、explicit/implicitの取り違え、disabledだけの変更、case/mode/revisionの不一致を拒否する。
結果recordの検査でも実promptを要求するため、旧plan/templateは再生成が必要である。
意図的なprompt変更は別の評価revisionとして扱う。

### CR-003 — 公開試行境界

公開直前のpath/target再検査中は `phase=pre-publication`、helperを呼ぶ直前からは `phase=publication` とする。
`PublicationError.report` と例外属性、CLIに `failed_publication_attempted` を追加した。

| 状態 | 報告 |
| --- | --- |
| 公開operationが成功return | `published_names` |
| 再検査で停止し、失敗fileの公開は未呼出 | `failed_name`、`phase=pre-publication`、`failed_publication_attempted=false`。失敗fileを `uncertain_names` に加えない |
| 公開helperを呼んだが成功returnなし | `failed_name`、`phase=publication`、`failed_publication_attempted=true`、`uncertain_names` |
| 失敗fileより後のfile | 両公開phaseとも `unattempted_names` |

成功operationの記録とpost-failure観測は引き続き分離する。
すでに公開済みのfileでも、現在の内容を確認できなければ既存の観測上のuncertaintyを残す。
staging失敗では全finalが未試行で、全公開後のcleanup失敗は通常countsと `PublicationCleanupWarning` のままである。
公開中の失敗時はCLI終了コード2、成功countsのstdout出力なしを維持する。

### CR-004 — 不正な結果record

`loaded_resources` のlistと各object、参照のpath/hash、`usage`・`timing`・`artifact_hashes`、観測文字列listをアクセス前に検証する。
null、誤ったlist要素、ネストした不正path/evidence、数値の代わりのlist、bool token、非有限cost等を拒否する。
非負の整数を不用意にfloat変換せず、巨大なJSON整数による `OverflowError` も避ける。
APIは不正recordに `False` を返し、CLIは `Invalid evaluation result record` と終了コード2を返す。
不正なJSON構文も同じ分類で扱う。
`AttributeError` や `TypeError` を包括的に捕捉する処理は追加していないため、プログラム上の不具合を入力エラーとして隠さない。

## 正確な変更ファイル

以下はこの修正session開始時からの差分であり、以前から存在したStage 3変更全体の一覧ではない。

| ファイル | 種別・目的 |
| --- | --- |
| [scripts/skill_audits/ryo_workflows/run_eval.py](../../../../../../scripts/skill_audits/ryo_workflows/run_eval.py) | 変更。CR-001/002/004の検査・記録・CLI |
| [scripts/skill_audits/ryo_workflows/audited_skill_hashes.json](../../../../../../scripts/skill_audits/ryo_workflows/audited_skill_hashes.json) | 新規。監査版17資源のrevision/path/hash |
| [scripts/skill_audits/ryo_workflows/README.md](../../../../../../scripts/skill_audits/ryo_workflows/README.md) | 変更。静的検査の範囲、prompt、record形式 |
| [config/codex/plugins/ryo-workflows/skills/extrip-to-ics/scripts/build_ics.py](../../../../plugins/ryo-workflows/skills/extrip-to-ics/scripts/build_ics.py) | 変更。CR-003のphaseとAPI/CLI報告 |
| [config/codex/plugins/ryo-workflows/skills/extrip-to-ics/SKILL.md](../../../../plugins/ryo-workflows/skills/extrip-to-ics/SKILL.md) | 変更。公開前失敗と公開結果不明の読み方 |
| [config/codex/plugins/ryo-workflows/README.md](../../../../plugins/ryo-workflows/README.md) | 変更。同じ公開分類の説明 |
| [tests/test_ryo_workflows_evaluation.py](../../../../../../tests/test_ryo_workflows_evaluation.py) | 変更。既存正常record試験に実promptを与える3行のみ追加 |
| [tests/test_ryo_workflows_review_corrections.py](../../../../../../tests/test_ryo_workflows_review_corrections.py) | 新規。25回帰テストとそのsynthetic fixture |
| [config/codex/docs/skill-audits/ryo-workflows/stage3/05_review_corrections.md](05_review_corrections.md) | 新規。本報告 |

## 再現と回帰証拠

修正実装を反映する前に最初の16回帰test methodを実行し、4指摘の元経路を再現した。
不足する新metadataによる失敗も含め、subtest集計は26 failures・15 errorsだった。
初期logは `/tmp/ryo-stage3-corrections-baseline/red-tests.log` に保存した。

| 指摘 | 修正前に観測した経路 | 修正後の回帰 |
| --- | --- | --- |
| CR-001 | control内の監査版別名copy、未掲載router、oracleがblockerにならない | 現行/監査版の別名入口・support resource、未掲載入口、両modeのoracleを拒否。target側は正常payloadを変えず別の宣言rootへ混入させて検査 |
| CR-002 | `prompt.txt` 改変・欠落を検出しない | 全9条件のbytes/hash保存と正常受理、三modeの改変・欠落、prompt交換、記録hashだけ更新、原group再hash改変を検査 |
| CR-003 | a公開後のb再検査失敗で、b公開呼出なしでも `uncertain_names=('b.ics',)` | path/target検査、公開前競合、replace/link後例外、CLIを検査。b未呼出時の旧bytesまたは競合bytesと後続未試行を保全 |
| CR-004 | `loaded_resources=['bad']`、`usage=null`、不正path値で例外。CLIはtraceback付き終了コード1 | null・不正要素・ネスト・不正JSONをAPI/CLIで検査し、`False`／制御された終了コード2を確認 |

CR-001/002の正常preflight試験はsynthetic evidenceを用いたoffline unit testである。
PDF準備フラグは試験内で設定しており、実PDF検証、live runnerの成立、実行許可を示さない。
追加の境界試験でCRLF frontmatterと巨大整数の問題も失敗を確認してから修正した。

## 実行した検証

Python 3.12.3、worktree rootをcwdとし、`python3 -B` で実行した。
影響moduleを個別実行した後、既存6patternの65件と新規25件を `unittest.TestLoader.discover` で一つのsuiteへまとめ、最終treeで再実行した。

| module / 検査 | 結果 |
| --- | ---: |
| `test_extrip_to_ics.py` | 7/7 |
| `test_arxiv_diff_pdf_verifier.py` | 12/12 |
| `test_ryo_workflows_plugin.py` | 5/5 |
| `test_extrip_publication.py` | 19/19 |
| `test_ryo_workflows_identity.py` | 11/11 |
| `test_ryo_workflows_evaluation.py` | 11/11 |
| `test_ryo_workflows_review_corrections.py` | 25/25（CR-001: 8、CR-002: 7、CR-003: 4、CR-004: 6） |
| 統合suite | **90/90、failures=0、errors=0** |
| 6 skill frontmatter | 既存 `quick_validate.py` で6/6有効 |
| runtime linkとanchor・19資源のmanifest/mode/copy | 既存配布testで成功。書込先はdisposable `/tmp` のみ |
| 関連Markdown link | 変更文書を含むaudit/tool/runtimeのlocal link 130件、欠落0 |
| `git diff --check` と未追跡差分の空白検査 | 成功 |
| 今回の全9ファイル差分 | 開始時snapshotとの比較でself-review済み。対象外変更なし |

最終suiteの実行script、件数JSON、logはそれぞれ `/tmp/ryo-stage3-corrections-baseline/{run_relevant_suite.py,test-counts.json,combined-tests.log}` にある。
一時領域の長期保存は保証しないため、主要結果は本報告にも記録した。
無関係なrepository全suiteは実行していない。

## C1とイベント内容の保全

既存C1-F01〜F10の19件とICS内容7件がすべて成功した。
全payload準備、全stageのclose、同一filesystemでのper-file atomic replace/no-clobber、準備失敗時の旧出力保全、途中公開後の新版保全、cleanup警告を維持する。
`escape`、`fold`、`required`、`validate`、`calendar` は開始時および監査HEADとASTが一致した。
さらに `_publish_one`、`_write_stage`、path/target検査、cleanup、観測helperも開始時とASTが一致した。
日時・Maps・UID・encoding・folding・成功counts・CLI入力形式を変更していない。
batch rollback、transaction journal、永続lockは追加していない。

## 制限・推奨からの差分・Git統合判断

必須推奨からの逸脱はない。
独立レビューでは任意改善だったCR-004も今回の明示承認に従って実装した。
CR-002はplan/preflightに加えて結果recordも同じprompt契約で検証し、CR-004は直接再現経路に隣接する数値・参照構造も検査した。
既存の原prompt、acceptance、fixture、arXiv実装、manifest、6skill構成は変更していない。

静的preflightは供給されたrootと証拠のある時点の検査に留まる。
実runnerの隔離、認証、modelと両effort、予算強制、権限と実行承認、実resource read/executeは引き続き別途必要である。
LLM評価は0 runで、selection改善・task成功率・usage/costの実測はない。
今回fixtureの組版内容は変更しておらず、PDF再compile・新たな目視は実施していない。
実filesystem障害、他OS/FS、停電、非協調writer、悪意あるrace、active/private/cache/catalogは今回も検証していない。
C1の旧版/新版混在と一時残存の制限は残る。

**最終推奨: CR-001〜CR-004のsource修正は受入可能で、Git統合準備は完了。**
統合作業では独立レビューが挙げた未追跡Stage 3資源の意図的な取込みと、primary側の同path歴史資料の保全・衝突を別途確認する。
primary側の資料cleanupを本修正の一部として行わない。
active deploymentや独立LLM評価の開始可否は本判定に含めない。
ここで実装・検証を終了し、Git統合の前で停止する。
