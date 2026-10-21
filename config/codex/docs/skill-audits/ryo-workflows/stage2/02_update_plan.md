# Stage 2: Stage 3更新計画

## 1. 範囲と提案architecture

本書は**未承認の実装計画**であり、Stage 2では下記taskを実行しない。
推奨は[Option A](01_design_options.md#5-6スキル構成の比較)である。
6つのskill名、Typstのreport / figure / exportのowner、既存referenceのpathと条件付き読込を維持する。
新しいrouter、共通runtime、mandatory provenance schemaは作らない。

対象repoは `/home/ryo/github/dotfiles-public`。
以下の略号を使う。

| 略号 | repo相対path |
| --- | --- |
| `PLUGIN` | `config/codex/plugins/ryo-workflows` |
| `SKILLS` | `config/codex/plugins/ryo-workflows/skills` |
| `AUDIT` | `config/codex/docs/skill-audits/ryo-workflows` |
| `EVAL` | `scripts/skill_audits/ryo_workflows`、新規提案。runtime payload外 |

Stage 3を開始する条件は、人が採用案・変更範囲を明示的に承認することである。
その後、現在のHEADとdirty状態を再確認し、approved multi-step implementationのgoalを設定し、primary root配下の `.worktrees/ryo-workflows-stage3` を使用する。
既存の適切なworktreeがあれば再利用する。
作成前にprimary checkoutの `.worktrees/` がignoredか確認し、必要なlocal exclude変更の範囲を守る。
元checkoutの未追跡Stage 1 / Stage 2文書は新worktreeへ自動継承されないため、hash付きの明示copyが必要である。
commit、push、active deployment、cache・global設定変更は実装承認に含めない。

## 2. 提案変更の要約

| 種別 | 変更 | 関連task |
| --- | --- | --- |
| metadata / prompt | figure reviewをdescriptionとoperation tableへ明記、arXivの完了scopeを具体化 | T-006 / T-007 |
| reference / architecture | 既存の所有権とlinkを維持。無根拠な移動・統合をしない | T-006 / T-009 |
| helper script | ICSのpath境界、stage、per-file公開、rollback、recovery記録 | T-004 / T-005 |
| test / evaluation | identity取得、隔離catalog、fixture、failure injection、before/after記録 | T-001 / T-002 / T-009 |
| packaging / deployment | versionとUI整合、payload検証、active更新は別承認 | T-008 / T-010 |
| 文書管理 | Stage 1をruntime外へ移動、linkと保全記録更新 | T-003 |

## 3. 影響file一覧

| file / component | 提案操作・task |
| --- | --- |
| `SKILLS/extrip-to-ics/scripts/build_ics.py` | T-004 / T-005でpathとpublicationを変更。stdlib / Python 3.10+を保持 |
| `tests/test_extrip_to_ics.py` | 既存7testを保ち、filesystem / fault / rollback / CLI回帰を追加 |
| `SKILLS/extrip-to-ics/SKILL.md` | T-005で保証・失敗時の扱い・専用directory条件を簡潔に追記 |
| `SKILLS/extrip-to-ics/references/events-schema.md` | 変更不要。JSON schemaを保持 |
| `SKILLS/extrip-to-ics/agents/openai.yaml` | 変更不要。implicit policyとUI既定を保持 |
| `SKILLS/creating-and-editing-typst-figures/SKILL.md` | T-006でdescription、review row、Return Verified Outputsのmode条件を限定更新 |
| `SKILLS/creating-arxiv-diff-pdfs/SKILL.md` | T-007でCompletionの必須scopeを明確化 |
| `SKILLS/creating-arxiv-diff-pdfs/scripts/verify_diff_pdf.py` | 変更不要。現行のlog summary / PDFページgateを保持 |
| `SKILLS/creating-arxiv-diff-pdfs/references/revtex-latexdiff-troubleshooting.md` | 原則変更不要。warning分類・全文/目視契約を保持 |
| `SKILLS/{dotfiles-deploy,export-editable-typst-figures,writing-typst-research-reports}/` とfigure references | 本体は変更不要。移行で無断に書き換えない |
| `PLUGIN/README.md` | T-006 / T-008でfigure review表記とidentity確認手順への簡潔な案内 |
| `PLUGIN/.codex-plugin/plugin.json` | T-008でrelease versionとfigure reviewのUI表現。互換manifest形式は維持 |
| `manifest/base.tsv` | 現19fileの配布mappingを原則維持。新規audit/eval resourceを加えない |
| `tests/test_ryo_workflows_plugin.py` | strict集合・copy・mode・全6入口・link検証を維持。必要なら試験用注入点のみ整理 |
| `EVAL/identity.py` | T-001で新規。read-onlyなsource / runtime比較CLI |
| `tests/test_ryo_workflows_identity.py` | T-001で新規。identityとoverlay差異のbehavior検証 |
| `EVAL/{run_eval.py,cases.json,fixtures/}` | T-002で新規。匿名fixture、catalog preflight、記録。Stage 1の原promptは保持 |
| `tests/test_ryo_workflows_evaluation.py` | T-002で新規。disabled汚染・path/hash mismatch時の拒否等を検証 |
| `SKILLS/stage1/{01_inventory,02_diagnosis,03_baseline,04_handoff}.md` | T-003の承認後だけ `AUDIT/stage1/` へ移動 |
| `AUDIT/stage1/*.md` と本Stage 2の4文書 | T-003で機能linkを更新。元identity・historical evidenceは保持 |
| private metadata / marketplace / active config / standalone copy | T-010で別targetとして承認された時だけ。public source変更へ混ぜない |

## 4. 順序付き実装task

各taskの承認状態は **Pending human review** である。
「rollback」はtask実装の取り消しと、helper自身のI/O回復を区別する。
Gitの破壊的操作で元のuser changesを戻す手順は用いない。

### T-001

- 関連: [D-001](01_design_options.md#d-001)。目的: 評価・運用で使った版を再現可能にする。
- 変更先: `EVAL/identity.py`、`tests/test_ryo_workflows_identity.py`。
- 内容: 既存manifestからpublic payloadを得てpath/hash/mode/typeを記録し、observed rootのequal / different / missing / unexpectedをJSON化する。private overlay期待値は明示mapで与える。
- 保持: source不変、activeへのwriteなし、version文字列を内容証明にしない。secret/config全体を収集しない。
- 依存・順序: R-001と本taskの実装承認後の最初。LLM runnerへのR-007承認とは独立し、T-003等のsource改修前baselineにも使える。
- 利益・risk: 誤った版の評価を排除する。expected集合が同じ欠落を含まないよう既存strict distribution testとも突合する。
- 検証・受入: 同version異bytes、欠落、未知file、symlink、mode違い、許可overlayと未許可overrideをfixtureで判別。sourceの17resourceとplugin19fileを混同しない。
- 取り消し: このunitの新規fileだけを取り除く承認済みcleanup、またはtask差分だけを反映しない。既存payloadは変化しない。

### T-002

- 関連: [D-001](01_design_options.md#d-001)、D-004 / D-005。目的: 独立したsource版のbeforeを、改修前に取れる状態にする。
- 変更先: `EVAL/run_eval.py`、`cases.json`、匿名fixture、`tests/test_ryo_workflows_evaluation.py`。
- 内容: [検証計画](03_validation_plan.md)の条件、prompt、mode、catalog・loaded path、usageを記録。identity / isolation preflight不合格ならmodelを起動しない。
- 保持: active config / caches / skillsは変更しない。原12promptはimmutableなcomparison groupとし、追補は別IDにする。
- 依存・順序: T-001、R-007のmodel・budget・runner承認。source変更前のbeforeを優先する。
- 利益・risk: selectionとexecutionと環境故障を区別できる。runner構築不能の場合は未実行を記録し、改善率を評価しない。
- 検証・受入: controlでtarget / standalone / routerの読込経路がないことをcatalogとread logで確認。model/effort/runtime/fixturesが条件間で一致する。
- 取り消し: disposable runnerを保持して停止できる。active環境を復元する必要を作らない。認証secretをfixtureへcopyしない。

### T-003

- 関連: [D-006](01_design_options.md#d-006)。目的: 監査資料とruntime payloadの分離。
- 変更先: Stage 1の旧4path、新 `AUDIT/stage1/`、両stageのMarkdown links。strict distribution検証は保持。
- 内容: 元hash記録→backup/copy→byte比較→新rootに合わせlinkだけ更新→全参照確認→承認された旧4pathを撤去する。Stage 2では実行しない。
  現在のStage 1内リンクは同じ4文書間なので原則そのまま有効。Stage 2の `../../../../plugins/ryo-workflows/skills/stage1/` を指す機能linkは `../stage1/` へ変更する。
- 保持: historical HEAD/hash/test結果を改変しない。`docs/superpowers/` 6文書、旧bytecode、他の未追跡物へ触れない。
- 依存・順序: R-006。T-001後、T-004〜T-007とは独立。
- 利益・risk: strict集合testを弱めず通常suiteを回復する。未追跡file移行漏れとrelative link切れに注意する。
- 検証・受入: 4入力のbackup一致、新4文書と既存Stage 2のlink有効、runtime manifestにauditなし、distribution 3test合格。未知file / missing resourceの負例は引き続き失敗。
- 取り消し: 保全した元bytesを旧位置へ復旧できる。新資料を消すのは移行unitの承認scope内だけ。旧位置へ戻すとD-006再発を明記する。

### T-004

- 関連: [D-003](01_design_options.md#d-003)、D-002。目的: ICS公開前にoutput境界を固定する。
- 変更先: `build_ics.py` のpath preflightとprivate helper、`tests/test_extrip_to_ics.py`。
- 内容: §6のdefault policyで全component / leaf / dangling linkを `lstat` 検査し、非通常targetを拒否する。既存filename validationを保持する。
- 保持: 入力JSON不変、invalid name/event時にoutput directoryを作らない、`--overwrite` は明示時のみ。環境導入なし。
- 依存・順序: R-003 / R-004、T-001。T-005の前提として同一script内で直列実装する。
- 利益・risk: 普通のsymlink越境とdirectory/FIFOへのwriteを防ぐ。symlink化homeやpath aliasは非互換となる。race完全防御は保証しない。
- 検証・受入: leaf / dangling / output-dir / 中間parent link、通常file、directory、FIFO、`..`、combined衝突のfixture。外部sentinel・既存一式・入力bytes不変。
- 取り消し: task差分だけを戻すと旧link挙動へ戻る。修正済みbatch処理との整合を再検証し、T-005後にこのunitだけを無検証で外さない。

### T-005

- 関連: [D-002](01_design_options.md#d-002)、D-003。目的: ICSをC2の失敗契約へ変更する。
- 変更先: `build_ics.py`、旅行 `SKILL.md`、`tests/test_extrip_to_ics.py`。
- 内容: §6のstate machineとexceptionを実装。stage / backup / per-file公開 / rollback / journal / lockを同じfilesystemへ置く。
- 保持: `generate(events, output_dir, combined='trips.ics', overwrite=False)` と成功時の `{filename: event_count}`、CLI引数、exit 2、JSON/ICS意味、旧成功bytesとmode。
- 依存・順序: T-004、R-003 / R-004。意味のあるfailure testを先に追加し既存実装で失敗することを確認する。
- 利益・risk: 後続I/O faultで新旧一式が黙って混在することを避ける。rollback failure、crash、非協調writer、FS機能差、backup中の秘密情報に注意。
- 検証・受入: 両overwrite modeでpreflight / stage / backup / 各publish / rollback / cleanupのfaultを注入。§6の各事後状態と[検証計画 §8](03_validation_plan.md#8-failure-injectionとfilesystem試験)を満たす。
- 取り消し・回復: 未完transactionはbackupとjournalを保持。コードunitの取り消し前にrecoveryを解決する。旧コードへ戻しただけで残骸を消したり旧一式復旧済みとしない。

### T-006

- 関連: [D-004](01_design_options.md#d-004)。目的: figure reviewのdiscoveryを本文契約に合わせる。
- 変更先: figure `SKILL.md` のdescription / operation row / Return Verified Outputsのmode条件、`PLUGIN/README.md` の該当entry。
- 内容: [候補文](01_design_options.md#d-004)を採用し、reviewはfindingsのみとする。output生成の指示はauthorized creation/edit時に適用し、report / exportの境界を保持する。
- 保持: 名前、references、scientific contract、implicit invocation既定。新review skillを作らない。
- 依存・順序: R-001 / R-002、可能ならT-002 before取得後。T-004 / T-005 / T-007と独立。
- 利益・risk: metadata非対称をなくす。一般の文章reviewやcaption-onlyへの誤発火はN/Bで確認する。
- 検証・受入: frontmatter、links、B-02、B-01、B-03、N-01/02。明示実行でreview保全、暗黙実行でroutingを別採点する。LLM未実行ならdiscovery改善を実測済みとしない。
- 取り消し: metadata / row差分だけを戻せる。runtime配布済みの場合はT-010の別rollbackが必要。

### T-007

- 関連: [D-005](01_design_options.md#d-005)。目的: 必須PDF acceptanceとtask外未確認を区別する。
- 変更先: arXiv `SKILL.md` のCompletion節。
- 内容: 下記候補文とmandatory一覧を記す。現行verifier / troubleshootingのgateは変更しない。
- 保持: raw diff不変、公式source、coverage、最終log/PDF一致、構造、first/middle/last目視、条件付きwarning review、有効baseline再利用。
- 依存・順序: R-005、可能ならT-002 before後。T-006やICSとは独立。
- 利益・risk: task外の無限追調査を避ける。任意check扱いで必要なcoverageや目視を落とさないよう条件を具体化する。
- 検証・受入: verifier既存12test、P-02、必須coverage/目視不足の追補負例、task外科学再現なしの完了case。合成helper testを公式arXiv end-to-endと扱わない。
- 取り消し: Completion差分のみを戻せる。旧表現への復帰は実PDFの検証証拠を変更しない。

### T-008

- 関連: [D-001](01_design_options.md#d-001)、D-004 / D-006。目的: source releaseと配布payloadをreview可能にする。
- 変更先: plugin `.codex-plugin/plugin.json`、`README.md`。`manifest/base.tsv` は必要がなければ変更しない。
- 内容: source release候補 `0.1.1` の衝突確認、figure reviewのlongDescription / prompt整合、copy→登録→cache→fresh catalog→実loadの案内。詳細手順はruntime外のauditを参照せず、README内に自己完結する短い説明にする。
- 保持: metadata互換形式、既存19fileのmode/context、private layerのoverride機構、payload外のeval/audit。
- 依存・順序: T-003 / T-005 / T-006 / T-007後、R-001 / R-006。READMEはT-006と同時編集せず直列で統合する。
- 利益・risk: release識別と操作境界を明確にする。versionだけではcontent証明にならず、private version overrideも別確認が必要。
- 検証・受入: T-001でsourceと一時配布先のcontent一致、distribution 3test、mode / reference全件。未知file負例でstrict testが失敗する。
- 取り消し: source metadata差分のみ取り消せる。active installationはこのtaskで更新しない。

### T-009

- 関連: D-001〜D-006。目的: 最終差分と受入を評価し、承認済み実装の完了判定を行う。
- 変更先: eval evidenceと `AUDIT` の検証結果記録。productionへの追加修正は実際のfailureに対応するものだけ。
- 内容: affected helper / distribution / identity / eval tests、before/afterの同条件比較、最終diffとpreservation照合を実施する。
- 保持: 同じtree/input/環境の有効証拠を再利用。skill wording一致だけのテストや無関係な全suite反復を増やさない。
- 依存・順序: T-001〜T-008。LLM部分はR-007とfixture依存。
- 利益・risk: 実装成功と未測定効果を分離できる。旧baseline欠如は後から埋めたことにしない。
- 検証・受入: [検証計画 §9](03_validation_plan.md#9-変更別の受入基準)のmandatoryを全て確認。source品質とruntime運用の完了状態は別報告する。
- 取り消し: 不合格unitだけcandidateとして保留し、成功出力を公開しない。追加変更がなければ成功検査の再実行は不要。

### T-010

- 関連: [D-001](01_design_options.md#d-001)。目的: 承認された運用targetだけで実更新を確認する。
- 変更先候補: `/home/ryo/plugins/ryo-workflows`、選択されたprivate metadata / marketplace、対応clientのplugin install、必要なら単独 `extrip-to-ics` のenablement。
- 内容: approved targetのsnapshot / backup、managed installerのscoped dry-run、承認済みapply、再dry-run、対応clientのsupported update/reinstall、fresh sessionの6入口と実load照合。
- 保持: private overlayと無関係なplugin / user設定。vendor cacheを手作業で編集・全消去しない。
- 依存・順序: T-009、**R-008の具体action / target承認**。source実装だけ承認された場合は実行しない。
- 利益・risk: source修正が実運用へ届く。private catalog / client差異はsource testだけでは解消を保証できない。
- 検証・受入: approved compositeのpath/hash/mode、fresh catalog、B-02等のloaded path、current verifierのpage gate確認。失敗時はsource修正完了とD-001運用未完を分ける。
- 取り消し: backupしたmanaged targetと登録状態を、同targetの許可範囲で復旧する。cacheはsupported client操作で戻し、別のfresh sessionで確認する。

## 5. 依存関係と並行可能性

```text
承認 → T-001 → T-002と旧版baseline
             ├→ T-003 ─────────────────────┐
             ├→ T-004 → T-005 ─────────────┤
             ├→ T-006 ─────────────────────┤→ T-008 → T-009
             └→ T-007 ─────────────────────┘             └→ 別承認 → T-010
```

T-003、T-006、T-007、ICSのT-004→T-005系列はfile責任が分離できる。
T-001/T-002もproduction改修から独立するがbeforeの取得順は守る。
README / Git index / manifest / 最終metadataへのwriteは直列にする。
**この独立性はsubagentの利用許可を意味しない。**
現在はdelegation未承認のためinlineで進める計画とする。
LLM runnerが使えない場合は未実行を固定してdeterministic修正を進める選択を人が承認できる。
その場合もT-006のselection改善率は主張しない。

## 6. コンポーネント別の具体設計

### identity / evaluation interface

`identity.py` のCLI候補を以下に固定する。

```text
python3 -B scripts/skill_audits/ryo_workflows/identity.py \
  --source-repo REPO --observed-root PLUGIN_COPY --output IDENTITY_JSON
```

public expected集合は既存manifestのplugin entriesから導出する。
overlayを評価する場合は `--expected-overlay OVERLAY_JSON` を追加し、各override/additionのpath、origin、hashを明示する。
source HEAD、dirty input hash、各fileのpath/type/hash/mode、canonical content ID、差異一覧、unexpected fileを出す。
出力先は呼出側が与え、sourceやactive rootを変更しない。
catalog取得・実loadは別のeval記録へ紐付け、file比較だけでruntime成功を返さない。
tool pathをbasenameだけで同一視せずrealpathも記録する。

### ICS publication state machine

```text
VALIDATED
  → OUTPUT_CHECKED
  → LOCKED
  → STAGED_AND_BACKED_UP
  → PUBLISHING
  → COMMITTED
  → CLEANED

PUBLISHINGの捕捉可能例外
  → ROLLING_BACK → ROLLED_BACK
                 → RECOVERY_REQUIRED（restore failure / concurrent conflict）
```

1. 既存 `validate()` と全filename validation・combined衝突検査を先に完了する。
   `calendar()` の意味を変えず、全payload bytesを先に構成する。
2. 絶対pathの既存componentを `lstat` で確認し、symlink、字句上の `..`、非directory parentを拒否する。
   outputの既存targetはregular fileのみ許可し、dangling linkも検出する。
   `overwrite=False` は既存entryを内容によらず衝突とする。
3. trusted outputの `.extrip-to-ics.lock` をexclusive directory creationで先に確保する。
   既存lockがあればtransactionを作らず停止する。
   lock下で既存unfinished transactionを確認し、存在すれば上書きせず回復確認を要求する。
   自分のtransactionはその後 `tempfile.mkdtemp()` でprivateに作る。
   setup失敗時は自分が確保したlockだけを解放し、既存lockをPIDの不在だけでstaleと判断して削除しない。
4. 同filesystemのtransaction内へ全新bodyを書き、close後に読戻し照合する。
   元finalは動かさずbackup copyを取る。
   元bytes/modeとbaseline signature（device/inode、size、mtime_ns、hash）を記録する。
   new published modeは従来同様callerのumaskに従い、overwrite時は元modeを保持する。
   backupとjournalはprivate directoryに閉じ込める。
5. journalをtemp→replaceで更新する。
   schemaは `transaction_id`, `state`, `overwrite`, `entries[]` とし、entryはsafe basename、元存在、old/new hash、mode、relative backup/stage名、publish状態を持つ。
   任意のabsolute restore targetは受け付けない。
   publish前にintentを記録し、publish後にdoneを記録する。
   interruptionが2記録間に起きてもold/new signatureで現状態を照合できるようにする。
6. 全baselineを再照合し、各publish直前も対象を検査する。
   `overwrite=True` は `os.replace(stage, final)`。
   `False` は同filesystemのexclusive `os.link(stage, final)` を使い、既存entryを潰さない。
   FS未対応は例外として扱い、finalへのstream writeへfallbackしない。
7. 例外では公開済みentryを逆順に回復する。
   現entryがこのrunのnew signatureと一致する時だけbackupをreplaceするか、新規entryをunlinkする。
   外部変更を検出したentryは保持し、残りも安全に回復できる範囲だけ処理して `RECOVERY_REQUIRED` とする。
8. 全公開後のfinal bytesと件数を照合して `COMMITTED` とする。
   以後のtemp cleanup failureはwarningとcommitted記録を残す。
   success一式をcleanup errorで旧版へ戻さない。
   cleanupはこのrunが作ったstage/backup/lockだけに限定する。

`generate()` の成功returnと呼出順は維持する。
公開失敗は `BatchPublicationError(OSError)` を候補とし、`phase`, `published_names`, `rollback_complete`, `recovery_dir` を属性に持つ。
既存callerの `except OSError` とCLIのexit 2に収まる。
CLIは `Error: ...; rollback=complete|incomplete; recovery_dir=...` と対象名をstderrへ出すが、予約本文を出さない。
prepublish failureは「既存final変更なし」、rollback成功は「旧対象集合復旧」、rollback失敗は「復旧必要」と区別する。
新規作成失敗後に空のoutput directoryが残ることは許容するが、このrunが公開したICSはrollback成功時に残さない。
既存の無関係なICSや他のfileは削除しない。

`_stage_payloads`, `_backup_targets`, `_publish_one`, `_restore_one`, `_cleanup_transaction` のような境界へfaultを注入可能にする。
public APIへtest用flagは追加しない。
`fsync`やSIGKILL試験を行っても停電耐久・batch原子性を保証する表現を加えない。
自動recovery CLIは今回の必須変更に含めず、journalとbackupの人による確認・回復手順を提供する。
通常の `Exception` に対する回復と、`KeyboardInterrupt` / signal / process loss後のunfinished検出を区別し、後者まで自動rollback成功を約束しない。
非POSIX環境やatomic hardlink非対応FSでは安全なfailureを互換性制限として明示する。

### figure discovery

description候補は[設計案D-004](01_design_options.md#d-004)を使う。
review rowはdata・対象appearanceの参照を選び、missing definitionは依存claimだけ保留する。
既存 `Return Verified Outputs` はreview時に出力再生成を強制しないよう、findings / authorized editsの条件を明示する。
既存plot codeとscientific inputを読まず、画像だけで正しい値対応を断定する動作は受け入れない。

### arXiv completion

Completion末尾の候補は次である。

> State every unverified item and its effect on the requested PDF. Do not claim completion while a mandatory acceptance check for that PDF is unverified or fails. Work outside the request, such as reproducing upstream scientific calculations, is a reported limitation unless it is necessary to establish a required check.

この前にmandatory gateを[設計案D-005](01_design_options.md#d-005)の一覧で対応付ける。
全page目視を無条件に増やさず、first/middle/lastと問題箇所の追加目視を区別する。
helperは現source版を使い、sample PNG生成だけを目視済みと数えない。

## 7. 移行と互換性

Stage 1移行前の4入力hashは以下である。
Stage 3開始時に再照合し、違えば新しいuser editsとして取り込む。

| file | Stage 2開始時SHA-256 |
| --- | --- |
| `01_inventory.md` | `0533998aa7eaabf44dbc5d87b9ad5a6019cd0573e61377045c6632ead061d1f0` |
| `02_diagnosis.md` | `b571e6df45b3939cf373cdcc426eaa66560361d19d24670270104473bb8a5631` |
| `03_baseline.md` | `f5f2945b0e573e7270c433717ff484446a1beb76003dd4aae8e709a47a84f3fa` |
| `04_handoff.md` | `d6022c477fcfcecf09b1162b907ff187d0be5140abdc802c4d8710ed77c921cf` |

原文prompt・過去結果・旧pathを記した本文はhistorical evidenceとして維持する。
動作するrelative linkと現在の入力案内だけを変更し、変更前copyと更新差分を保存する。
sourceの新規runtime fileは予定しないため、audit移動でmanifestを増やす必要はない。
private composite、単独 `extrip-to-ics`、active catalogは別物として扱い、sourceのmergeやversion更新だけでD-001解消とはしない。

ICSではfilename・JSON・default combined・UID/時刻/Maps等を維持する。
新しい非互換性は、symlink / 非通常target / `..` の拒否、協調lockとrecovery残骸時の停止、atomic no-clobber非対応FSでのfailure、entry差替えによるinode/ACL/xattrの意味である。
成功return、標準出力の件数とpath、`--overwrite` の明示性を保つ。
`DTSTAMP` は現在時刻由来であり、別runのICS全bytes一致を要求せず、UIDとevent意味を比較する。
rollbackでは過去bytesをそのまま復旧するため、`DTSTAMP` も元通りである。

## 8. 保存要件

[設計案 §3](01_design_options.md#3-設計原則と保存契約)を全taskの共通受入とする。
特にTypstのcondition tuple/multiplicity、点・interval、normalization、CSV再構築、extraction/current/verificationの分離は、今回のmetadata修正を理由に簡略化しない。
font-onlyやcaption-onlyを抽出・移設・再推定へ拡大しない。
arXivのraw checksum・coverage・log/PDF・構造・実目視は独立gateのままにする。
旅行は原文を編集せず、Calendar APIや認証を導入しない。
同一条件の既存成功証拠は再利用し、未実行項目を合格へ昇格させない。

## 9. rollbackとrecovery

実装unitはfile差分と検証結果を一緒にreviewし、未承認のunitを混ぜて取り消さない。
作業開始前snapshotとtask別差分を使い、`git reset --hard` やworktreeの強制撤去は用いない。

ICSの手動recoveryは、同じoutput directoryで新しい生成を停止した状態で行う。
journalを読んでsafe basenameとold/new hashを検証し、各finalをold / new / missing / conflictへ分類する。
oldは保持、newはbackupからentry置換、新規のnewはrun-owned一致確認後に撤去、conflictはuserへ判断を戻す。
復旧対象の全bytes/modeと無関係fileの不変を確認してから、承認されたtransaction/lockだけをcleanupする。
壊れたjournalやbackup欠落では復旧成功とせず、残るdataを保全する。
process crash後もjournalとbackupが必ず永続化する保証はなく、host loss後の検証不能な内容はunknownとする。

sourceを旧版へ戻すことと、active plugin・cache・catalogを旧版へ戻すことは別手順である。
T-010のbackupとsupported client操作を使う場合も、fresh catalogとloaded hashを再確認する。

## 10. 承認依存

| 決定 | 依存task | 未承認時の扱い |
| --- | --- | --- |
| R-001: Option A | T-001〜T-009のsource実装 | 全実装を開始しない |
| R-002: figure review owner | T-006、B-02採点 | 現行metadataを保持 |
| R-003: ICS C2保証 | T-004 / T-005 | 失敗契約を実装決定しない |
| R-004: link / trust / FS互換性 | T-004 / T-005 | security policy変更を行わない |
| R-005: arXiv acceptance scope | T-007 | 現行gate維持 |
| R-006: audit migration / version管理 | T-003 / T-008 | 旧4pathを保持しD-006を既知failureとして記録 |
| R-007: runner / model / budget / credentials | T-002のLLM部分、T-009比較 | deterministic検証とafter-only評価の限界を分離 |
| R-008: active対象と具体操作 | T-010のみ | 配布・設定・cache・単独版へ触れない |

全状態は **Pending human review**。
Stage 2の作成許可は、どのtaskについてもStage 3実装・deploymentの承認を意味しない。
