# Stage 2: ReviewとStage 3への引き継ぎ案

## 1. 推奨の要点

**既存6スキルを維持するOption Aを推奨する。**
実行版の識別、ICSの失敗回復とpath境界、figure reviewのdiscovery、arXivの完了scope、監査資料の配置を限定修正する。
統合・分割、共通runtime、新routerは、現在の証拠からは必要性を認めない。

本書は人のreview用の提案であり、**Stage 3の開始許可ではない**。
Stage 2では4文書の作成と使い捨てfixture評価だけを行い、既存skills・scripts・manifest・deployed copy・runtime設定を変更していない。
詳細は[設計案](01_design_options.md)、[更新計画](02_update_plan.md)、[検証計画](03_validation_plan.md)を参照する。

## 2. 影響の大きい提案

| 所見 | 推奨変更 | 守る契約・限界 |
| --- | --- | --- |
| D-001 / High | source、deploy、cache、catalog、実loadのpath/hashを外部manifestで照合。隔離評価とactive更新を分離 | version文字列を内容証明にしない。fresh sessionの実load確認まで運用解消とはしない |
| D-002 / Medium | C2: 全bodyのstage、backup、per-file atomic publish、捕捉可能失敗でrollback、回復記録 | fixed filenamesとCLIを維持。batch全体の原子性、停電耐久性、非協調writerとのisolationは保証しない |
| D-003 / Medium | leaf・output directory・既存parentのsymlinkを拒否し、trusted directoryへ通常fileだけ公開 | 正規のpath aliasも拒否する互換性変更。通常のlink検査をrace完全防御とは説明しない |
| D-004 / Medium | 既存figure skillのdescriptionとoperation tableにread-only reviewを明示 | reportの論証・構成review、exportのbundle検証と分離。B-02の選択改善は未実測 |
| D-005 / Low | 完全PDFのmandatory gateと、依頼外の未確認事項を区別 | raw diff、全文coverage、log/PDF整合、構造、必要な実目視をすべて維持 |
| D-006 / Low | Stage 1を将来docs配下へ移動しlink更新。strict distribution testを維持 | 今回は移動しない。auditをpayloadへ追加したり広い除外規則でtestを通さない |

新しい独立診断IDは追加しなかった。
追加観測によりD-002は新規作成時にも部分batchが残る問題、D-003はoutput directoryのlinkでも越境する問題へ範囲を広げた。
評価仕様ではP-06の「便が未確定」とrequired timestampの関係を明確化する追補M-006を提案した。
既存helperの新欠陥とは区別する。[所見再評価](01_design_options.md#2-stage-1所見と証拠の再評価)、[case追補](03_validation_plan.md#3-stage-1の12-llm-caseのreview)

## 3. Architectureと根拠

6つのentry pointは `dotfiles-deploy`、`creating-arxiv-diff-pdfs`、`creating-and-editing-typst-figures`、`export-editable-typst-figures`、`writing-typst-research-reports`、`extrip-to-ics` を維持する。
figure reviewはfigureのmodeとし、独立skillにはしない。
reportは問い・根拠・文章と構成、figureは科学dataから図への実装とreview、exportはlosslessな可搬成果物に責任を持つ。
condition tuple、multiplicity、normalization、interval endpoints等の契約とreferenceの条件付き読込を保つ。

Option Bの参照再配置は現状のbroken linkや読込過多から支持されず、Option Cの統合・分割はownerとtriggerの移行riskを増やす。
重複知識の削減だけでは再配置せず、実測上の保守・context問題が出た時に再検討する。[architecture比較](01_design_options.md#5-6スキル構成の比較)

## 4. 承認が必要な決定

**すべてPending human review。Approvedの項目はない。**
採用する選択肢と、実装を許可するtask範囲の両方を確認する。

| 決定・質問 | 選択肢と推奨default | 証拠・tradeoff | 留保の結果 |
| --- | --- | --- | --- |
| R-001: architectureをどうするか | A: 6つ維持＋限定修正を推奨。B: 参照再配置。C: 統合・分割 | 既存ownerが独立し、構造欠陥の実証なし。Aは共通知識の重複を残す | Stage 3 source実装を開始しない |
| R-002: figure reviewを正式capabilityにするか | 既存figureのread-only modeを推奨。reportへ限定、または独立review entryも選択肢 | 本文に既存review契約。B-02は未実行。metadata明示は適用候補を広げる | T-006とB-02の期待routingを保留 |
| R-003: ICSにどの整合保証を求めるか | C2を推奨。C1: per-fileのみ。C3: generation切替とreader変更 | 後続I/O faultの部分更新を観測。C2はCLI互換を保つがjournalと回復処理が増える | T-004/005の失敗契約が未確定 |
| R-004: symlinkとraceのpolicyは何か | 全関連link拒否＋trusted directoryを推奨。追跡許可、強いPOSIX confinementも候補 | leaf/parent越境を再現。拒否はalias利用と非互換。強いrace対策は実装・OS要件が増える | path変更とsecurity受入を保留 |
| R-005: arXivの必須完了範囲はどこか | 依頼PDFの全gateを推奨。依頼外の科学再現まで要求する案も比較 | 曖昧なのはscope。PDF検証の緩和を支持する証拠なし | T-007を保留し現行gate維持 |
| R-006: auditをどこで管理・配布するか | docs配下でversion管理、runtime外を推奨。外部保管も候補 | 現配置でstrict distribution failure。移動にはlink更新と旧4fileの限定撤去が必要 | T-003を保留、D-006が残る |
| R-007: 独立評価のrunner・model・予算を許可するか | clean runnerで条件を固定したbefore/afterを推奨。deterministicのみ、after-onlyも選択可 | CLIはあるがclean catalog・認証・権限・budgetは未確立。全33 run/revision、focused 9 run/revision | LLM効果と効率改善の比較を主張しない |
| R-008: active環境の何を更新するか | source実装と切り離し、targetと具体操作ごとの別承認を推奨。source受入だけで止めてもよい | D-001はsource修正だけでは運用解消しない。private overlay・単独版に波及し得る | T-010と運用解消確認を実行しない |

R-008の候補にはmanaged deploy、plugin version更新、supported cache refresh、単独版の無効化、active設定変更、新規session確認がある。
source実装への承認だけでこれらを実行しない。
認証情報のcopyやglobal設定変更を評価の近道として行わない。

## 5. 主要な代替案と代償

C3はreaderがgeneration pointerを一度だけ取得する時の一式整合に適するが、現在の固定名を別々に開く契約から移行する必要がある。
その要求があるならC2を実装する前にR-003を変更する。
また、悪意ある共有directory raceまで防御する要件があるなら、R-004でdirfd / no-followとOS側write confinementを含む設計を選び直す。
`lstat` の追加だけでその保証へ昇格させない。

descriptionへのreview追加は小さい変更だが、routing改善を証明するには独立LLM比較が必要である。
全6スキルを統合して共通scientific contractを常時読む案は、境界とcontext負担を悪化させるriskがある。[finding別代替案](01_design_options.md#4-d-001からd-006の設計案)

## 6. 実装risk

最も判断を要するunitはICS transactionである。
rollback失敗、外部user edit、process interruption、cleanup failureを別状態として扱い、復旧不能時に旧成功一式を復旧済みと報告しない。
backupは予約情報を含むためprivate directoryへ置き、run-ownedであると照合できるものだけcleanupする。
atomic entry置換によりmodeは保持するが、inode、hardlink、ACL/xattrの意味は変わり得る。

Stage 1と既存docsは未追跡であり、new worktreeへ自動継承されない。
T-003では元bytesのsnapshot、限定copy、hash照合、link更新を済ませてから、承認された旧4fileだけを撤去する。
Stage 3の開始時にHEAD、dirty、private overlay、release versionを再確認する。[migrationとrecovery](02_update_plan.md#7-移行と互換性)、[rollback](02_update_plan.md#9-rollbackとrecovery)

## 7. 試験と受入の要点

Stage 2の使い捨てコピーではdistribution **3/3**、ICS **7/7**、arXiv verifier **12/12**、合計 **22/22** が成功した。
続いてStage 1を配置したコピーではdistribution **2 pass / 1 fail**となりD-006を再現した。
late write faultとleaf / output-dir linkの負例も再現した。
arXivの12testはmock toolを含み、今回の実PDF生成成功を意味しない。
Stage 1の実toolchain・目視結果と、今回の新しい実測を分けて記録した。

**独立LLM baselineは0 run。P-01〜06、N-01〜03、B-01〜03は未実行のままである。**
0.163.0 CLIの存在とhelpだけでは、実load版、disabled control、別installation経由の遮断を証明できない。
clean runnerのpreflightが通ってからexplicit / implicit / disabledを実施する。
beforeを取得できない場合、afterの適合は示せても改善率やtoken/cost削減は主張しない。

Stage 3では既存22test、strict payloadの未知/欠落負例、link/frontmatter、ICSのF-01〜12とS-01〜06、最終diffと保全を必須範囲にする。
LLM・実compiler・active配布は各変更の影響と承認に応じた条件付き試験である。[実測](03_validation_plan.md#6-実際のbaseline結果)、[受入表](03_validation_plan.md#9-変更別の受入基準)

## 8. 残る不確実性

実装仕様の確定を妨げるのはR-001〜R-006の未承認である。
特にC2保証とlink非互換性を未決のままhelper実装へ進めない。
LLM比較の信頼性を妨げるのはrunnerのcatalog/実load同一性、model effective identity、認証・network・budgetの未確立である。
公式arXiv fixtureとrecipient環境も必要なend-to-end評価の前提となる。
これらの不足と、sourceのdeterministic修正が可能かどうかは別判断である。
一般scientific diagramの表示方針、特殊selector、arXiv command未指定、旅行の一部日時不足時の扱いも未確定であり、今回の限定修正で新しい一般仕様へ広げない。

D-001の不一致を生んだ正確な層は未確定であり、cache直接修正で原因を隠さない。
本セッションのactual model ID、profile、normal/planning effort、Stage 3用のdeployed profile設定は検証していない。
launch commandは未提示とし、開始時に実設定と適切なeffortを確認する。
subagentは未使用で、Stage 3にもdelegation許可を引き継がない。

## 9. 提案するStage 3順序

1. R-001〜R-007の採用範囲を記録し、repo状態を再確認してgoalとisolated worktreeを準備する。
2. T-001でidentity tool、T-002でcase/runner preflightを作り、改修前のfocused baselineを確保する。
3. T-003でauditを移行。T-004→T-005でICS境界と回復を実装し、T-006でfigure metadata、T-007でarXiv scopeを修正する。
4. T-008でversion・packagingを整え、T-009でaffected tests、before/after、self-reviewを行う。
5. source受入後、R-008で別途許可された場合だけT-010でactive更新とfresh session確認を行う。

T-003、T-006、T-007はT-001/002後に独立review可能である。
T-004/005は同一helperのため直列にする。
taskの独立性は並列agent実行の許可ではない。[task仕様と依存](02_update_plan.md#4-順序付き実装task)

## 10. 承認checklistと現在の状態

- [ ] R-001: Option A、または変更するarchitectureを選ぶ。
- [ ] R-002: figure skillのread-only reviewを正式に扱うか決める。
- [ ] R-003: C2の保証と保証外の状態を承認する、または別案を指定する。
- [ ] R-004: 全関連symlink拒否とFS互換性の代償を承認する、または脅威modelを変更する。
- [ ] R-005: 完全PDFのmandatory gateとtask外事項のscopeを決める。
- [ ] R-006: auditのdocs移行・管理方針と旧4fileの限定撤去を承認する。
- [ ] R-007: runner・model/effort・予算・必要権限、before未取得時の扱いを決める。
- [ ] R-008: active更新が必要ならtargetと具体操作を別途承認する。
- [ ] Stage 3を開始してよいtask範囲を明示する。commit / pushの許可とは分ける。

Stage 2の設計・代替比較・実装task・検証条件の準備は完了した。
採用と実装は**Pending human review**であり、ここで作業を終了する。
