# Stage 3 独立コードレビュー

レビュー日: 2026-10-21（Asia/Tokyo）。変更の実装者とは別セッションで、実ファイルと追加プローブを根拠に評価した。

## 1. Executive summary

**総合結論: Ready after specified corrections。現状のままのGit統合は推奨しない。**

確定指摘は **P0: 0、P1: 0、P2: 3、P3: 1、計4件**。
C1の全payload準備、全stageのclose、per-file atomic replace、atomic no-clobber、準備失敗時の旧出力保全について、重大な破損・越境・上書き違反は見つからなかった。
C2のrollback、journal、永続lockを追加する必要はない。
ただし、公開syscallを呼ぶ前の検査失敗まで公開結果不明として報告する問題がある（CR-003）。
評価preflightには、controlの可読領域にある旧版skill・router・評価者oracleを見逃す問題（CR-001）と、生成後のprompt改変を見逃す問題（CR-002）がある。
不正な結果JSONでvalidatorがtracebackを出す軽微な問題も再現した（CR-004）。

既存の関連65テストは独立再実行で全件成功したが、上記の経路は防げていない。
9件のfixture PDFを再生成し、代表3件を画像化して目視確認した。
LLM実行、skill自動選択の改善、active pluginの更新・実loadは今回も検証していない。
source統合の受入とactive deploymentの受入は別であり、後者は保留する。

## 2. Reviewed scope

### 対象版と変更一覧

- Repository: `/home/ryo/github/dotfiles-public`
- Review worktree: `/home/ryo/github/dotfiles-public/.worktrees/ryo-workflows-stage3-c1`
- Branch: `codex/ryo-workflows-stage3-c1`
- HEAD / original audited commit: `737ba2926d72ad51dccfc0cf6b26cd4d2994a44d`
- レビュー開始時: **追跡済み変更7件、未追跡41件**。staged差分、削除、移動はない。以下の全変更・追加を対象とした。
- `git status --porcelain=v1 -uall`、`git diff --stat`、`--name-status`、全`git diff`、`--cached`、`git ls-files --others --exclude-standard`、`git diff --check`を確認した。
- 追跡済み差分は256行追加・23行削除。指定範囲外の実装変更はなかった。

以下では `PLUGIN=config/codex/plugins/ryo-workflows`、`EVAL=scripts/skill_audits/ryo_workflows`、`AUDIT=config/codex/docs/skill-audits/ryo-workflows` と略記する。参照行番号はレビュー時のworktree実ファイルを指す。

| 種別 | レビュー対象 |
| --- | --- |
| 変更済み7件 | `PLUGIN/.codex-plugin/plugin.json`、`PLUGIN/README.md`、`PLUGIN/skills/creating-and-editing-typst-figures/SKILL.md`、`PLUGIN/skills/creating-arxiv-diff-pdfs/SKILL.md`、`PLUGIN/skills/extrip-to-ics/SKILL.md`、`PLUGIN/skills/extrip-to-ics/scripts/build_ics.py`、`tests/test_ryo_workflows_plugin.py` |
| 新規tool・manifest等6件 | `EVAL/README.md`、`identity.py`、`run_eval.py`、`cases.json`、`oracles.json`、`original_prompts.json` |
| 新規figure-review fixture 4件 | `EVAL/fixtures/figure-review/{TASK.md,definitions.md,figure.typ,values.csv}` |
| 新規bundle-font fixture 6件 | `EVAL/fixtures/bundle-font/{TASK.md,definitions.md,figure.typ,normalization.toml,provenance.toml,values.csv}` |
| 新規report-caption fixture 5件 | `EVAL/fixtures/report-caption/{TASK.md,definitions.md,figure.typ,report.typ,values.csv}` |
| 新規fish-review fixture 2件 | `EVAL/fixtures/fish-review/{TASK.md,config.fish}` |
| 新規test 3件 | `tests/test_extrip_publication.py`、`tests/test_ryo_workflows_identity.py`、`tests/test_ryo_workflows_evaluation.py` |
| 移行copy 8件 | `AUDIT/stage1/{01_inventory.md,02_diagnosis.md,03_baseline.md,04_handoff.md}`、`AUDIT/stage2/{01_design_options.md,02_update_plan.md,03_validation_plan.md,04_review_and_handoff.md}` |
| 新規Stage 3証拠7件 | `AUDIT/stage3/{00_decisions.md,01_implementation_log.md,02_test_results.md,03_final_handoff.md,input_hashes.json,source_identity.json,validation_evidence.json}` |

Stage 1/2は背景の診断・保存契約・比較仕様として扱い、C2提案よりStage 3のC1決定を優先した。
copy8件すべてをprimaryの原本と照合した。
Stage 1はbyte一致、Stage 2は2文書のStage 1向けrelative linkだけが変更され、残る2文書はbyte一致だった。
原本8件のSHA-256は`input_hashes.json`と一致した。

primaryだけに存在する未追跡fileは次の10件である。

- `config/codex/plugins/ryo-workflows/skills/stage1/{01_inventory.md,02_diagnosis.md,03_baseline.md,04_handoff.md}`
- `config/codex/docs/superpowers/plans/{2026-07-19-auto-review-explicit-authorization.md,2026-08-11-auto-review-default-visibility.md,2026-09-30-codex-config-refresh.md,2026-10-18-sol-model-selection.md}`
- `config/codex/docs/superpowers/specs/{2026-07-19-auto-review-explicit-authorization-design.md,2026-08-11-auto-review-default-visibility-design.md}`

primaryのStage 2原本4件はworktreeと同じrelative pathにあるが未追跡であり、2件は上記link差を持つ。
単純copyやcheckoutによる統合時に衝突する可能性がある。
これらとprimaryのStage 1原本は本レビューで変更・削除していない。

### 実行した検証

Python 3.12.3、Typst 0.15.1、既存Popplerを使用した。
`PYTHONDONTWRITEBYTECODE=1`と`python3 -B`を使い、追加出力は `/tmp/ryo-workflows-independent-review-rpjfqxaw/` に限定した。
Typstのcache先も同directory配下へ向けた。

| 検証 | 独立実測 |
| --- | --- |
| `test_extrip_to_ics.py` | 7/7成功 |
| `test_arxiv_diff_pdf_verifier.py` | 12/12成功。mock外部toolを含む |
| `test_ryo_workflows_plugin.py` | 5/5成功。実installer関数の書込先は`/tmp` |
| `test_extrip_publication.py` | 19/19成功 |
| `test_ryo_workflows_identity.py` | 11/11成功 |
| `test_ryo_workflows_evaluation.py` | 11/11成功 |
| 合計 | **65/65成功**。既存22、新規43という件数とも整合 |
| 6 skill frontmatter | 既存`quick_validate.py`で6/6成功 |
| public payload | disposable copy19件のhash/type/配布mode一致。stored source identityとも一致 |
| audit/tool local links | file存在66件、欠落0。runtime link/anchorは配布suiteが確認 |
| 新規41件 | 全件textとして読取可能。末尾空白なし。追加binaryや認証情報は見つからなかった |
| ICS semantics | `escape/fold/required/validate/calendar`のASTが監査HEADと一致 |
| fixture | `prepare --compile-fixtures`で9条件・9 PDF生成。B-02図、B-01図、B-03報告の代表3件をPNGで目視 |
| 追加障害注入 | mkdtemp、stage write、短いwrite、stream close、readback、chmod、unlink、公開前検査、link成功後の例外 |

65件は`unittest.TestLoader.discover`で上記6patternを選び、一つのsuiteとして実行した。全repository suiteは実行していない。
追加プローブのsource・結果・logは同`/tmp`に置いた。この一時証拠の長期保存は保証しないため、主要な再現条件と結果は以下にも記載する。

### 制限と保全

外部LLM、実認証、Calendar、公式arXivからの新規全文生成、他OS/他filesystem、停電・SIGKILL、悪意あるrace、active/private/standalone/cache/catalogの状態は未検証である。
既存arXiv verifier/test、manifest、未変更referenceは差分と関連試験の対象に含めたが、今回新しい公式全文PDFを検証したわけではない。
本レポート以外のrepository file、index、HEAD、branchは変更していない。commit、merge、push、deploy、依存導入、subagentは実施していない。

## 3. Findings

| ID | 重大度 | 内容 | 主なsource |
| --- | --- | --- | --- |
| CR-001 | P2 — Medium | 可読領域内の旧版skill・router・oracleがpreflightを通過する | `scripts/skill_audits/ryo_workflows/run_eval.py:109–140,180–199` |
| CR-002 | P2 — Medium | 生成後のpromptを変更しても同一性検査が通過する | `scripts/skill_audits/ryo_workflows/run_eval.py:96–104,150–161` |
| CR-003 | P2 — Medium | 公開前検査の失敗まで公開結果不明と報告する | `config/codex/plugins/ryo-workflows/skills/extrip-to-ics/scripts/build_ics.py:231–238,247–259` |
| CR-004 | P3 — Low | 不正な結果JSONの型でCLIがtraceback終了する | `scripts/skill_audits/ryo_workflows/run_eval.py:205–222,247–249` |

### CR-001 — 可読領域に残る旧版skill・router・oracleを見逃す

**新規導入。確信度: High。**

`catalog_problems()`の`known`は現在のpublic skill resourceのhashだけである（109–112行）。
名前の禁止検査はcatalog entryだけに適用され（113–115行）、filesystem上の可読fileは現在版hashとの一致しか確認しない（131–139行）。
古いskillやrouterの入口が可読領域に残っていてもcatalog未掲載なら通り、評価者oracleはこの禁止集合に含まれない。
これは、README 42行のcontrol全可読領域からの六skill・旧router除外、48行のoracle隔離という条件を、供給された領域の中ですら十分検査できていない。

**再現:** `prepare --compile-fixtures`で作った実PDF付き9条件planを使用した。
既存positive test（`tests/test_ryo_workflows_evaluation.py:80–116`）と同じ形で、manifest modeのtarget copy、空control directory、syntheticな証拠参照を作り、まず空blockerで通ることを確認した。
その後、controlの宣言済み`readable_roots`内へ以下を一つずつ置き、同じ`preflight(plan, evidence)`を実行した。

1. `git show 737ba2926d72ad51dccfc0cf6b26cd4d2994a44d:config/codex/plugins/ryo-workflows/skills/creating-and-editing-typst-figures/SKILL.md`のbytesを、別名`old-skill.txt`で配置。
2. `skills/ryo-workflows-router/SKILL.md`に、同名frontmatterを持つsynthetic routerを配置（source-only planによる追加probe）。
3. 実際の`EVAL/oracles.json`を`oracles.json`として配置。

いずれも**実測は`prerequisites_satisfied=true, blockers=[]`**だった。
期待値は、既知の入口・監査版resource・評価者oracleへの可読経路をblockerにすることである。
oracleは`input/`にcopyされないという現実装の性質だけでは、他の可読rootからの到達を防げない。

**影響:** controlがskillの旧版から知識を得たり、正解を読んだりする評価を許容し、選択・task結果の比較を無効にする。
LLMを実行した・漏えいが起きたという主張ではなく、offline validatorの偽陰性を確認した指摘である。
外部runnerの強制隔離を証明できないという文書上の限定は妥当だが、宣言済みroot内に直接見える違反の見逃しは別問題である。

**推奨修正:** current/audited版の禁止resource集合を明示し、既知のskill/router名を持つ入口もfilesystem側で検査する。
評価者oracleを両modeの可読領域から排除する検査を追加する。
任意の改変・言い換えまで識別できるとは説明せず、残る隔離要件はrunnerと人の証拠確認に委ねる。

**修正後検証:** current版の別名copy、監査版の別名copy、catalog未掲載の旧router、両modeのoracle混入をそれぞれ拒否し、無関係な匿名fixtureと正常targetは通ること。
実runnerのcatalog・filesystem・instruction面の隔離は別途検証する。

### CR-002 — `prompt.txt`の改変が検査対象外

**新規導入。確信度: High。**

96行で`prompt.txt`を`input/`の兄弟に書くが、98行と158–160行でhash化・照合するのは`workspace=input/`だけである。
planの`original_prompts_sha256`はpreflightで参照されず、実際にrunnerへ渡すpromptのbytesも再確認されない。

**再現:** CR-001と同じ実PDF付きplan・正常synthetic evidenceで、`B-02-implicit/prompt.txt`だけを`Altered task\n`へ変更した。
fixtureとsourceを一切変更しなくても、**実測は`prerequisites_satisfied=true, blockers=[]`**だった。
期待値はprompt同一性のblockerである。

**影響:** prepare後の編集・取り違えでimplicit/disabledの同文性や元promptが失われても検出できず、比較の前提を壊す。
`original_prompts.json`自体の保存と既存unit testの成功は、配布された各promptの不変性を証明しない。

**推奨修正:** 各runのprompt path/hashをplanに記録し、preflightで実bytesを検証する。
保存したoriginal group hashも再照合し、case/modeに対応する期待promptと一致させる。
source/fixtureと同様に、prompt変更を明示的な新評価revisionへ結び付ける。

**修正後検証:** 一文字変更、欠落、implicit/explicitの取り違え、disabledだけの変更を拒否するnegative testを追加し、正常9条件を通すこと。

### CR-003 — syscall前の失敗と、公開結果の曖昧さを区別しない

**新規導入。確信度: High。ファイル内容の破損はない。**

233–234行のpath/target検査と235行の公開処理を同じ`phase='publication'`で捕捉し、250–253行は失敗箇所を無条件で`uncertain_names`へ追加する。
公開操作が未呼出でも、成功returnのない公開操作と同じ分類になる。

**再現A（非協調writer不要）:** 旧`a.ics/b.ics/trips.ics`を用意してoverwrite生成した。
`a.ics`の公開成功後、`b.ics`の再検査で`OSError(EIO)`を注入し、`_publish_one`の呼出も記録した。

```text
_publish_one calls = ['a.ics']
published_names = ('a.ics',)
failed_name = 'b.ics'
unattempted_names = ('trips.ics',)
uncertain_names = ('b.ics',)
batch_completed = false
```

`b.ics`の公開syscallは一度も呼ばれず、旧bytesは保持された。
それでも公開結果不明に分類された。
**再現B:** no-clobberで、a公開後・b再検査前に完成済みの競合bを置いた場合も同じ分類となり、競合file自体は正しく保全された。

**期待値:** 検査失敗による未公開と、公開操作を呼んだが成功returnを得られない状態を区別すること。
`failed_name`は保持してよいが、syscall未呼出のbを「この生成処理が公開したか不明な出力」に含める根拠はない。
後者の曖昧な操作は、既存のreplace後例外testと追加のlink後例外probeどおり、引き続きuncertainにする。

**影響:** C1が約束する失敗状態の正確な報告が損なわれ、確定した検査失敗にも不要な公開確認を要求する。
この問題でbatch成功やrollback成功が誤報されるわけではないためP1とはしない。

**推奨修正:** 検査と公開操作の境界を小さく区別し、公開操作に入ったかを記録する。
既存のpublished/observed分離は維持する。journalやC2回復状態は不要である。
skillの「成功returnなしならuncertain」という説明も、実際に開始した公開操作に限定する。

**修正後検証:** 公開前lstat/path検査失敗・no-clobber事前競合では操作未呼出が分かること。
replace/link呼出後の曖昧な例外はuncertainとなり、旧/新内容、unattempted、CLI exitも正しいこと。

### CR-004 — 不正な結果recordの型を検証せずtracebackになる

**新規導入。確信度: High。**

`validate_result()`は外側dictを確認するが、222行で各`loaded_resources`要素をdictと仮定して`.get()`する。
248行のCLI例外処理は`AttributeError`を捕捉しない。

**再現:** 必要なruntime欄と有効なsynthetic catalog/config evidence参照を持つresultで、`loaded_resources=[1]`とし、`run_eval.py check-result RESULT.json`を実行した。
**実測はexit 1、`AttributeError: 'int' object has no attribute 'get'`のtraceback**。
期待値はinvalid recordとしてexit 2で拒否することである。

**影響:** 手編集・異版runnerのrecordが正常な不合格と区別しにくいCLI障害になる。成功への誤昇格はない。

**推奨修正:** `loaded_resources`のlist/要素dict、usageやevidence path等の入力shapeを境界で検証する。
無差別な例外握り潰しで内部不具合を隠す必要はない。

**修正後検証:** non-dict要素、`null`、誤ったusage型等を、tracebackなしのinvalid-record結果として拒否すること。

## 4. Component assessments

| 評価軸 | 判定 | 根拠・留保 |
| --- | --- | --- |
| 1. C1 correctness | **Needs correction** | 内容保全とper-file公開は良好。失敗分類CR-003を修正する必要がある |
| 2. Filesystem safety | **Pass with reservations** | 指定したsymlink/非通常file/字句`..`の拒否、同filesystem stage、外部sentinel保全を確認。trusted-directory前提とrace除外の範囲内 |
| 3. Backward compatibility | **Pass with reservations** | 成功counts、CLI/JSON、日時・UID・Maps・UTF-8/CRLF/foldingは保持。下記の意図的非互換は残る |
| 4. Skill instruction quality | **Pass** | read-onlyと編集を区別し、figure/report/exportの責任とarXiv必須gateを維持。LLM選択効果はNot evaluated |
| 5. Evaluation tooling quality | **Needs correction** | CR-001/002、軽微なCR-004。identity単体は試験した範囲でPass |
| 6. Test adequacy | **Needs correction** | 65件成功は確認したが、CR-001〜003に対応するnegative testが欠ける |
| 7. Documentation accuracy | **Pass with reservations** | C1許容混在、cleanup warning、race除外、source/runtime区別は正確。control検査とuncertain説明は上記修正に合わせる必要がある |
| 8. Git integration readiness | **Needs correction** | 必須P2修正、未追跡41件の選別、primaryの移行原本との衝突整理が必要 |
| 9. Deployment readiness | **Not evaluated** | active/private/standalone、登録、fresh catalog、actual loadを検証していない。配布・cache更新も未実施 |

### C1とpath処理

201–212行で全event/name/collisionとUTF-8 payloadを構築し、215行で全targetを事前検査する。
222行の`mkdtemp(dir=output_dir)`、223–229行の全stage・close・readback・chmod後に、初めて公開loopへ入る。
`_write_stage`の`with`はclose時例外も捕捉可能な外側try内にある。
`os.replace`と`os.link`を使い、finalへ直接streamingするfallbackはない。
no-clobberの競合はatomicな`link`で拒否され、後続失敗後も先行の完全新版を保持する。
close/短いwrite/readback/chmod/mkdtempの追加障害でも既存finalの不変を確認した。

cleanupはrun専用0700 directoryのpayload名だけをunlinkし、未知fileを再帰削除しない。
unlink失敗の追加probeでも、全公開後は通常counts、`batch_completed=true`のwarning、残存名とdirectoryを得た。
preflight/mkdirのtry外エラーは従来型の例外として直接返り、この段階で公開はない。
reservation本文をreportへ埋め込む処理もない。

leaf/dangling/output-directory/既存parentのsymlinkを通常の`lstat`で検査する方針は実装・文書で一致する。
lexical `..`を正規化で消さず拒否し、空白pathと通常のrelative pathは追加probeでも成功した。
hard-linkを持つ旧targetをreplaceしても外部inodeを変更しない既存testは意味がある。
owner-controlled directoryを強制隔離する実装ではなく、path componentの並行差替えを防ぐdirfd等もない。
これは明記されたtrusted-directory前提で評価し、TOCTOU完全防御とは扱わない。

### 互換性

監査版の5つのcalendar関数と既存7 testは不変であり、成功API・CLI出力も確認した。
symlink/非通常target/字句`..`の拒否、hard-link非対応FSでのfailure、inode/hard-link/ACL/xattrの差は意図的な制限として説明されている。
mode bit保持はowner/groupやACLの同一性までは意味しない。
公開途中の例外は`PublicationError(OSError)`に包まれるので、競合時に`FileExistsError`だけを捕捉するconsumerには差があるが、Stage 3の決定記録が採用したreport付き例外の範囲である。
事前の既存file衝突は`FileExistsError`、成功returnは従来のname→件数dictを維持する。

### Skill instructions

figureのdescriptionにread-only科学reviewを明記し、保存値・点・区間端・legendの根拠付きfindings、source/配布物不変、必要compileのdisposable出力を具体化した。
編集時だけStage/Verify/Updateへ進むよう条件付けされ、reportの論旨・caption・配置、exportの抽出・可搬性とは区別される。
reference内の編集手順をreviewで自動実行する必要はない構成である。

arXivでは公式版identity/baseline、raw command/checksum、不変raw、本文・bibliography・appendix、log/PDF、fatal/関連warning、構造、実first/middle/last目視を必須とした。
必須検査に必要な追加page確認も残り、無関係な上流科学再現は完了条件から分離されている。
不完全PDFを許す緩和は見つからなかった。

ICSの21行追加は、C1の混在状態、no-clobber、alias拒否、cleanupの解釈をagentへ伝えるため大部分が必要である。
既存の予約日付・未確定情報・Maps・UID/import非保証も維持される。
具体的なsyscall名やwarning classの詳細は将来referenceへ移せるが、単に長いことを欠陥とはしない。

### Identityとpackaging

`identity.py`はmanifestを期待集合とし、unknown内容をhashせずにfile type/追加pathを検出し、既知symlinkを辿らない。
private overlayは明示path/hash/mode/originに限り、approval origin文字列自体を権限の証明とはしていない。
source mode `0664`と配布mode `0644`、mtimeと内容ID、metadata versionとactual loadを分離した点は適切である。
確認したpayload IDは `9fb05b6cec98d4e57624706ebe11fcffafeb21017665386fad4d2d212385feeb`、source release labelは`0.1.1`で、保存JSONと一致した。

19 runtime file・6 entrypointとmanifest mappingは維持され、監査tool/test/docs/fixtureはpayload外である。
version・README・figure review metadataに明白な不整合はない。
ファイルcopyの一致はcatalog可視性やactual loadの証明ではなく、identity toolもこれらを`unverified`とする。

## 5. Test coverage gaps

| 未充足/不足 | 実用上の意味と今回の扱い |
| --- | --- |
| 旧版・catalog未掲載router・oracleの可読root混入 | CR-001。既存testは現在版の完全copyを別名にするだけで、履歴版やoracleを保護しない |
| prompt fileの改変/欠落/取り違え | CR-002。既存fixture mutation testは`input/TASK.md`のみを変更する |
| 公開前検査失敗と公開呼出後失敗の区別 | CR-003。現在のtestはpublish helper内部の例外を中心にし、未呼出を検査しない |
| 不正JSON shape | CR-004。現在のresult testは正常shapeの不足欄・証拠不足を中心にする |
| 直接のshort write、stream close、readback I/O、chmod、mkdtemp、実cleanup unlink失敗 | 既存suiteの不足を今回の追加fault injectionで補った。保全・warningは期待どおり。既存testへの追加は次の修正sessionで検討 |
| 「全stageをclose」の直接証拠 | 現F03のstage再読だけではopen handle残存を検出できない。実装の`with`を静的確認し、今回はclose例外も注入した |
| font fixtureのmath | B-01にmath要素がなく、将来のLLM runでmath font変更を十分試せない。font適用の網羅性を主張する前にfixtureを拡充する |
| LLMのread/execute・画面確認・read-only遵守 | 0 run。template・frontmatter・fixture compileを実task成功やselection改善に数えない |
| 実filesystemのENOSPC/EIO/EOPNOTSUPP、他OS、並行reader | 今回もfault injection中心。atomic性は対応OS/FSの意味論を前提とし、stressの実測成功とはしない |
| 公式arXiv全文、P-02/P-06完全fixture、X系列 | 未実行。sourceの今回変更や65件成功をend-to-end証拠へ拡張しない |

fixtureの四condition tupleと保存端点、B-02の意図的な上端加算/逆legend、B-01/B-03の正しい基準図はdata/sourceと目視が整合した。
B-03の`TASK.md`はcaptionに必要な比較結果も指定するため、将来そのcaseが示すのは主にscopeと組版であり、自力で科学的関係を発見する能力の証明にはならない。
各modeのPDFは個別compileされるため、比較時には生成metadata等による差の扱いも固定することが望ましい。

## 6. Maintainability and complexity

ICS helperの増加は、選択されたC1の必要なphaseと失敗報告に概ね対応する。
独立したwrite/publish/cleanup/observation関数は障害注入と保全確認に役立ち、不要なbackup/journal/永続stateはない。
全payloadをmemoryに持ち、同filesystemのprivate stageから一件ずつ公開する構造は、少量の旅行calendarという用途に比例している。
CR-003は検査とsyscallの境界を小さく明示することで直せる問題であり、transaction frameworkへの置換を勧めない。

identity/evaluation toolもstdlibのみでruntimeとは分離され、LLM runnerや認証copyを抱えていない。
一方、評価の「不変入力」「隔離」「証拠record」は別契約なので、現在の簡易検査が証明する範囲を正確にする必要がある。
CR-001/002の修正も、既知の入口/資源/実promptを検査する範囲に留め、万能なLLM監視基盤を作る必要はない。

skill本文の科学・予約data保護、限定的reference loading、read-only境界は保存価値がある。
否定命令の多さや行数だけを理由に削除する根拠はない。
ICSの内部実装詳細のprogressive disclosureは任意の小改善であり、今回の必須修正ではない。

## 7. Integration and deployment risks

1. **未追跡41件は`git diff`だけに現れない。** source/tool/test/fixtureに加え、評価testが参照するStage 1 baselineと履歴JSONも意図的に取り込む必要がある。`git commit -am`だけでは不足する。
2. **primaryの同path Stage 2原本が衝突し得る。** 内容比較と保全先を決めて統合し、link変更以外の歴史的証拠を失わないこと。
3. **primaryの`PLUGIN/skills/stage1/`4文書が残る。** worktree側のstrict配布testが通っても、primaryのruntime-tree完全一致にはこの既存の干渉が残る。配布対象追加・広いignoreで隠さず、対象限定の別承認cleanupとして扱う。
4. **無関係なprimary-only6文書を混ぜない。** これらはレビュー対象の実装差分ではない。
5. **version更新はactive更新ではない。** private metadata override、単独travel、既存cache、登録・enablement、fresh catalogは今回確認していない。`0.1.1`だけでD-001解消を宣言しない。
6. **LLM比較はまだ開始可能と判断できない。** CR-001/002修正後も、runnerの実効隔離、model/両effort、認証、予算、権限と実行承認が別途必要である。offline synthetic evidenceの合格を実行許可にしない。
7. **配布は別の承認済みtargetで検証する。** public/private revisionと許可overlayを固定し、生成/dry-run、許可後のfile identity、fresh catalog、actual read/execute identityを別証拠にする。

## 8. Required corrections

### Git統合前の必須修正

- **CR-001:** 既知旧版/非掲載router/評価者oracleの混入を検出し、文書の除外契約とnegative testを一致させる。
- **CR-002:** 実promptのidentityをplan/preflightの対象にし、元promptとmode対応を保護する。
- **CR-003:** 公開前検査の失敗を、公開呼出の結果不明と区別する。report、CLI/skill説明、negative testを合わせる。
- 修正後は該当moduleと影響する既存regressionを再実行し、今回保全を確認したC1保証を維持する。未変更の無関係suiteを機械的に増やす必要はない。
- 未追跡fileとprimary原本の統合方法をレビューする。既存fileの削除は、このレビューの権限には含めない。

### 任意の改善・次の評価前の準備

- CR-004のJSON shape validationとCLIのinvalid-record処理を整える。
- close/短いwrite/個別cleanup操作等の小さい回帰testを保存する。
- mathを含むfont fixture、条件間で固定した基準PDF、同じ論理pathでのrunner入力供給を用意する。
- helper内部詳細を必要に応じreferenceへ移す。ただしC1の部分公開と失敗時の読み方はagentに見える場所へ残す。

本レビューでは修正を実装していない。

## 9. Final recommendation

**Ready after specified corrections。**

per-file C1の内容保全とno-clobber、path policy、calendar互換、skill責任分担、runtime外tool配置には相応の実装・試験証拠がある。
P0/P1の欠陥は確認していない。
しかし、65件が通っても評価前提の崩れを検出できず、公開前失敗の分類にも誤りが残るため、CR-001〜003を直すまでは統合を進めないことを推奨する。

修正されたsourceの統合可否と、active deploymentの可否は分ける。
active deploymentは未検証・未実施であり、今回のレビューから開始してよいとは判定しない。
LLM選択の改善や現在のruntimeでの使用を主張できる証拠もない。
ここでレビューを終了し、修正・Git操作・配布へは進まない。
