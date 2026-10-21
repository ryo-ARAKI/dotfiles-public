# Stage 2: 設計の選択肢

## 1. 現状と設計目的

2026-10-21の設計案である。
**推奨はOption A: 既存6スキルと参照所有権を維持し、実行版の識別、ICS公開処理、discovery、完了条件、監査資料の配置を限定修正すること**である。
Stage 3の実装、配布、設定変更はいずれも未承認であり、本セッションでは行わない。

ここでの目的は正確性、保全、発見可能性、保守性、実行効率の改善である。
ファイル数・行数の削減は受入基準にしない。
以下のrepo相対パスは `/home/ryo/github/dotfiles-public` を基準とする。

| 項目 | Stage 1の記録 | Stage 2の新しい観測 |
| --- | --- | --- |
| HEAD / branch | `737ba2926d72ad51dccfc0cf6b26cd4d2994a44d` / `main` | 同一。tracked / staged差分なし |
| スキルの同一性 | 17 tracked resourceと既存ignored bytecode 1件 | [inventory §8](../stage1/01_inventory.md)の18 SHA-256すべて一致 |
| 未追跡資料 | 既存 `config/codex/docs/superpowers/` の6文書を保全 | 同じ6文書にStage 1の4文書が加わる。今回の入力・変更対象にはしない |
| 配置・cache | public resource 17件を比較 | 配置先14一致・3差異、cache 1一致・3差異・13欠落を再確認 |
| 現セッションのcatalog | public plugin名付きはarXiv / dotfilesのみ。旅行は単独版 | 同じ供給状態。新規セッションのcatalogや選択結果を意味しない |

現在のtracked sourceは監査版と同一である。
Stage 1文書は未追跡の追加物であり、HEADだけを比較するとD-006を見落とす。
既存 `docs/superpowers/` の内容は読み込まず、hashで保全対象を固定した。
初回のStage 2 identity記録は `2026-10-21T04:23:20.423595+00:00` に取得した。

## 2. Stage 1所見と証拠の再評価

[inventory](../stage1/01_inventory.md)、[diagnosis](../stage1/02_diagnosis.md)、[baseline](../stage1/03_baseline.md)、[handoff](../stage1/04_handoff.md)をすべて確認した。
Stage 1のE系列は過去の実測、P/N/B系列12件は設計済み・未実行である。
本書の「事実」はソースまたは記録から確定した事項、「観測」は実行結果、「静的リスク」は未実測の挙動上の懸念、「仮説」は原因・効果の未検証推論、「提案」は未承認の設計を指す。

| ID | 継承する重大度・分類 | 確認と解釈の更新 |
| --- | --- | --- |
| D-001 | High / Observed defect | 同じ不一致を再確認。古いcached verifierには現行のlog完了・ページ一致gateがない。原因が配布・登録・cache・session更新のどこにあるかは未確定 |
| D-002 | Medium / Observed defect | `generate()` の逐次final writeを確認。追加fault injectionで `overwrite=False` の新規作成でも先行ICSだけ残ることを観測。上書き専用の問題からbatch publication全般へ範囲を拡張 |
| D-003 | Medium / Static-analysis risk、越境挙動は観測済み | leaf symlinkの再現に加え、output directory自体のsymlinkでも外部sentinel変更を観測。悪用・OS権限突破の観測ではない |
| D-004 | Medium / Static-analysis risk | figure本文のreview契約とdescriptionの非対称を確認。B-02の偽陰性は未実測。正式capabilityの承認待ち |
| D-005 | Low / Static-analysis risk | `any unverified item` とhelperの保証範囲を確認。不要停止の実測はなく、必須gateの弱体化を支持しない |
| D-006 | Low / Observed defect | 使い捨てコピーでStage 1追加後にdistribution 3件中1件だけ失敗。資料とruntime集合の境界問題として維持 |

独立した新しい診断IDを要する欠陥は追加していない。
D-002/D-003の影響範囲を追加観測で広げた。
証拠・実行コマンド・限界は[検証計画 §6](03_validation_plan.md#6-実際のbaseline結果)にまとめた。

6責任は、dotfiles生成と許可された反映、公式arXiv全文diff PDF、科学図の実装とreview、可搬bundle、研究報告、予約MarkdownからICS、である。
Stage 1で成功したのはfrontmatter 6件とlink、関連22テスト、合成3ページTeXの実toolchainと目視、Typst断片compile、保全検査である。
公式arXivの2版からの全文作成、実研究図・bundle・reportのend-to-end、独立LLMのexplicit / implicit / disabled比較は実行していない。
Stage 2でもLLM成功率・usage・costは取得していない。

Stage 1には、一般scientific diagramへの表示方針、特殊なsource selector、arXivでcommand未指定の場合、旅行の一部必須日時不足時の独立event処理という仕様上の未確定事項もある。
これらは新しい欠陥として確定しておらず、今回の限定修正で一般仕様を追加しない。
user/publication要件優先と、定義不足は依存箇所だけ保留する既存規則を維持する。
該当workflowを評価する場合はfixtureの期待値を先に確定する。

## 3. 設計原則と保存契約

[Stage 1 handoff §3](../stage1/04_handoff.md)と詳細inventoryを保存契約とする。

| 契約 | 保持する実装・判断 |
| --- | --- |
| 権限 | read-only reviewはfindingsのみ。生成とdeployment、local生成とexternal writeを分離する |
| 保全 | 最新user edits、旧成功成果物、raw source、失敗candidateの記録を区別する。差分を最新baselineへ照合する |
| 科学値 | condition tupleとmultiplicity、series、点、interval endpoints、selection、aggregation、normalizationを保つ。hashと意味の検証を分離する |
| 科学的主張 | RMSE / SD / mean deviation、trend / interpretation / mechanismを区別し、結論を変える反例を保存する |
| 変換 | 表示変更、単位換算、storage変換、許可された科学data変更を区別する。換算は点・区間端・tick・referenceへ一度だけ適用する |
| Typst | report / figure / exportのownerを維持。CSV cell string・未描画値・順序を保存し再構築する。bundle-relative dependencies、必要なrelocationとrecipient inclusionを実検証する |
| arXiv | 公式2版の来歴、raw diff不変、別copyでの限定修復、全文coverage、log/PDF整合、構造、実目視を独立gateとして保持する |
| 旅行 | 原文・未確定表示、exact date/offset、checkout日を含む既定、Maps、stable UID、UTF-8/CRLF/folding/escape、既存CLI/JSONとimport非保証を保持する |
| 効率 | referenceは条件付き、検証はaffected scope。同一tree/input/環境の成功証拠は再利用する。参考資料の読込だけで別workflowを起動しない |

強い否定命令は役割ごとに評価する。
raw編集禁止、無断再推定禁止、review時の変更禁止、既存成果物の保全は維持する。
曖昧な完了範囲はtask内の判定規則へ直す。
一般的な説明をAGENTSへ機械的に移して、別repoでの自己完結性を失わせない。
filesystemの境界や複数ファイルの失敗回復はscriptと実行権限で扱う。

## 4. D-001からD-006の設計案

### D-001

責任の所在は `manifest/base.tsv`、installer、plugin metadata、登録元、cache、sessionである。
対象の [distribution test](../../../../../../tests/test_ryo_workflows_plugin.py) はfile到達性を検証し、LLMのruntime選択までは証明しない。

| 候補 | 利点 | 限界・判断 |
| --- | --- | --- |
| version文字列だけを更新 | 安価でreleaseを区別できる | 同じversionで内容が違う現観測を検出できない。単独では不採用 |
| active環境を直接更新し再起動して評価 | 実運用に近い | baselineを汚し、private overlayや単独版も動く。Stage 2では不可 |
| 全cacheを消す | 見かけの古さを消せる可能性 | 原因を隠し無関係なpluginも失う。vendor cacheの直接編集・削除は採用しない |
| 外部manifestでsource / deployed / cache / catalog / 実loadを照合 | 不一致の層を特定でき、読み取りのみで診断できる | catalogの取得方式はclientごとに確認が必要。推奨 |
| 専用runnerへ固定copyを供給 | active環境に触れずbefore/afterを比較できる | account・権限・catalogの独立性を事前検証する必要。推奨 |

提案するidentityは次の通りである。

1. managed sourceのfull commit、dirty差分、使用overlayのrevision/hashを記録する。
2. payloadのplugin-relative pathをソートし、各通常fileについて `SHA256`、2 spaces、path、LFのmanifestを生成する。
   symlinkや欠落・余分なresourceは別検出する。
   manifest自体はpayload外へ保存し、自己hash循環を作らない。
3. content identityにはREADMEとmetadataも含める。
   deploy mode `0644` は内容hashと別に照合する。
   public-onlyの現19fileのmanifest hashは `c151389fc6ffe21c12624ce7db6f2f024fe0b27912e0d1c76317528d0aaa162c`。
   Stage 1のbytecode込み18file manifestとは集合が異なる。
4. 同一手順で配置先とcacheを比較する。
   private compositeではpublic由来の非override resourceと、許可されたoverrideの集合・出所を別記録する。
   public19fileとprivate全体の単純完全一致を要求しない。
5. 新規セッションのcatalogで6スキルの名前、description、実pathを確認する。
   同名単独版、router、関連private版を列挙し、評価では重複を遮断する。
6. 実taskで読まれた `SKILL.md` / references / helperのpathとhashをtranscript・tool記録に結び付ける。
   catalogに見えることと選ばれたことを分離する。

OpenAI公式資料はdescriptionによるimplicit選択と同名スキルの併存を説明している。
それを根拠にmetadataと実loadを別検証する。[Build skills](https://learn.chatgpt.com/docs/build-skills)
pluginのlocal installはcache copyから読み込まれると説明され、source directory更新後の再起動確認が必要である。
既存 `.codex-plugin/plugin.json` は互換形式としてサポートされており、今回新manifest形式へ移行する理由にはならない。[Package your plugin](https://developers.openai.com/plugins/build/plugins)
`CODEX_HOME` はconfig・認証・cache等の状態を持つため、それだけの切替を完全隔離と見なさない。[Advanced Configuration](https://learn.chatgpt.com/docs/config-file/config-advanced)
これらは現在の公式説明であり、CLI 0.163.0とdesktopの全挙動一致を実証したものではない。

診断はread-onlyのidentity比較、source試験は専用runner、配布更新はmanaged installer、cache更新はサポートされたclient操作、新規sessionでの選択検証は最後、と分ける。
versionはStage 3でpublic `0.1.1` を候補とし、実装開始時のrelease状態で衝突を確認する。
private metadataがoverrideする場合、その同期変更も別targetへの承認が必要である。
sourceを試験するだけならactive plugin更新は不要である。
activeへのcopy、marketplace登録・更新、plugin再install、単独版の無効化・移動、active config変更、app再起動は今回許可されていない。

### D-002

根拠は [build_ics.py](../../../../plugins/ryo-workflows/skills/extrip-to-ics/scripts/build_ics.py) の `generate():85-104`、Stage 1 E-004、Stage 2の後続open failure注入である。
全payloadのvalidationは既に先行し、失敗の原因は公開中のI/Oである。

| 失敗契約 | 手法 | 利点 | 残る状態・互換性 |
| --- | --- | --- | --- |
| C0: 部分更新を許容して報告 | 逐次write＋失敗一覧 | 最小変更 | 旧成功保全を満たさない。不採用 |
| C1: 各fileは完全な旧版か新版 | 全body staging＋per-file atomic publish | truncateを防ぐ | batchは新旧混在し得る。単独では不足 |
| C2: 捕捉可能な公開失敗で旧集合へ戻す | C1＋backup＋reverse rollback＋回復記録 | stable filenames / CLIを維持し通常のI/O faultから回復 | rollback自体の失敗・process kill・停電は別。推奨 |
| C3: generation一式を一度に切替 | immutable generation directory＋single pointer | pointerを一度だけ読むreaderには一式の整合 | reader変更・新path・symlink policyとの調整が必要。固定名を別々に開くreaderのsnapshotは保証しない。今回は不採用 |

**推奨C2の保証は、trustedな専用directory、非協調writerなし、通常の捕捉可能例外という前提付きである。**

- validation、名前・全target種別・衝突・link検査、staging/backup失敗では、既存final bytesを一切変更しない。
- public fileは各々completeな旧版か新版とし、部分bodyを見せない。
- 公開途中の例外でrollbackが成功したら、既存targetのbytesとmodeを復旧し、このrunが新規公開したentryだけを撤去する。
- rollback失敗ではexit 2と `rollback=incomplete`、影響一覧、recovery directoryを明示し、backup・journalを残す。
  旧集合が無傷と報告しない。
- process kill / host loss後は次runがunfinished transactionを検出して停止する。
  自動復旧でuser editsを消さず、journalとbackupを人が確認して回復する。
- concurrent readerに対するbatch原子性、停電耐久性、非協調writerとのtransaction isolationは保証しない。
  `fsync`を追加する場合も、複数renameをtransactionにするとは説明しない。

同一filesystemのprivate staging directory、旧fileのbyte backup、協調lock、公開直前のbaseline再照合を用いる。
`overwrite=True` はstaged fileから `os.replace()`、`False` はexclusiveなno-clobber publicationを用いる。
後者は通常fileの `os.link()` による同一filesystem公開を候補とし、未対応FSでfinalへ直接streamするfallbackを入れない。
publishできないFSでは安全に失敗する。
全file公開・再照合後をcommit pointとし、以後のtemp cleanup失敗はcommitted状態とwarningとして報告する。
cleanup失敗を理由に成功一式をrollbackしない。
具体的なstate machine、exception interface、注入点は[更新計画 §6](02_update_plan.md#6-コンポーネント別の具体設計)に定める。

### D-003

| 候補 | 保護 | 残る問題・互換性 |
| --- | --- | --- |
| final filenameだけ `is_symlink()` で拒否 | danglingを含む普通のleaf linkを避ける | parent linkとcheck後raceには不足 |
| 許可directory内へrealpath解決 | 静的な境界照合 | userが渡したaliasを暗黙追跡し、TOCTOUも残る |
| final directory entryを安全に置換 | `os.replace()` はleaf linkの参照先へ書かない | parent linkは追跡する。linkを黙って壊す仕様にもなる |
| dedicated directory＋全関連componentのlink拒否＋entry公開 | 誤ったlink利用を早期拒否し、leaf dereferenceを防ぐ | trusted directoryの前提が必要。推奨default |
| dirfd / no-follow path walk＋OS confinement | parent差替えへの防御を強める | POSIX依存、ACL/同一UID脅威・全raceの解決とは別。強い脅威モデル向け選択肢 |

**承認対象のdefault提案は、leaf（danglingを含む）、output directory、既存parent componentのsymlinkを拒否すること**である。
`lstat`で検査し、既存targetは通常fileのみ許可する。
directory・FIFO・device等は書き込み開始前に拒否する。
字句上の `..` を含むoutput pathも拒否し、必要ならcallerが意図する実pathを指定する。
正当なsymlink運用でもこの変更後は失敗する。
例えばmacOSの `/tmp` aliasやsymlink化されたhomeは、実pathへの明示変更が必要となる。
無断でlinkを削除・追跡するflagは加えない。

Python 3.10+標準libraryと既存のportable CLIを保つため、defaultでPOSIX専用APIを必須化しない。
代わりに、新規の専用出力先またはowner管理で非協調writerのない場所を実行前提とする。
通常のlink検査とentry replacementは実装するが、これを悪意ある同時差替えに対する証明とはしない。
privileged processで共有directoryへ出す用途はdefault保証外であり、必要ならdirfd実装とOSによるwrite confinementを追加承認する。
既存hardlink targetへのentry replacementは共有inodeへ直接writeせず、inode/ACL/xattrの維持は既存 `open('wb')` と異なるため互換性として明記する。
scriptの検査、trusted directoryの運用、sandbox/ACLの強制は別責任である。

### D-004

figure reviewは入力値・表示点・区間端・legend等の同じ科学的contractを使う。
出力はfindingsであり、bundle移設やreportの論旨評価とは異なるが、新しいdata modelや独立toolchainを要しない。
したがって既存figure skillのmodeとして明示するのが妥当である。

| 候補 | 利点 | リスク・判定 |
| --- | --- | --- |
| 本文だけの現状維持 | 変更不要 | description非対称を残す。reviewを意図しないなら本文側の契約見直しが必要 |
| descriptionにread-only reviewを追加 | 最小変更で入口と既存本文が一致 | selection改善はB-02で要検証。推奨 |
| 新しいreview skill | 専用入口が増える | 共通contract・referenceの重複とrouting競合。独立利用の証拠が不足 |
| report skillへ一括移管 | report内図のreviewを集約 | standalone図reviewとreport論旨の境界を広げる。不採用 |

候補descriptionは次である。

> Use when creating, revising, or performing a read-only review of scientific Typst figures in reports, standalone sources, or existing editable bundles; portable packaging belongs to export-editable-typst-figures, and report prose or page composition belongs to writing-typst-research-reports.

名前は変えず、本文の `For a read-only review, report findings and leave sources and delivered outputs unchanged.` を保持する。
operation tableへ「scientific figure review → data対応と対象featureだけ、findingsのみ」を追加する。
report内でも点・legend等の実装reviewはfigure、caption・論旨・配置はreport、抽出・依存・移設はexportとする。
B-02はこのownershipの承認後にroutingの正誤を採点する。
read-only compileが必要なら使い捨てcopyへ出し、sourceとdelivered outputsのhash不変を検証する。

### D-005

原文は `State any unverified item; do not claim completion while one remains.` である。

| 候補 | 判断 |
| --- | --- |
| 現状維持 | 必須gateには強いがtask外の未確認との境界を読者に委ねる |
| 全checkをoptionalへ下げる | 不完全PDF防止を損なうため不採用 |
| 必須acceptanceとsupporting diagnosticsを区別 | 推奨。元のgateを列挙し、証明範囲を限定する |

提案ルールは「要求されたdiff PDFの必須acceptanceが未実施・不合格なら未完了。その他の未確認は、依頼への影響とともに限界として報告」である。
必須は公式2版のidentity、元版baseline（有効証拠の再利用可）、exact commandとraw checksum、不変性、必要な全section/bibliography/appendix coverage、最終log完了とPDFページ一致、fatal/reference/citation gate、構造check、first/middle/lastの実目視である。
必要な領域に疑義があれば追加pageの目視も必須となる。
補助のhang境界調査・chunk compile・全pageの追加samplingは、失敗原因やcoverage疑義がある時だけ必須へ昇格する。
未依頼のupstream数値計算の再現、著者への照会、別版の追加比較は完了条件にしない。
意図した旧新版の重複label等のreviewable warningは、既存referenceの条件と理由・件数記録を保持する。
helper合格をcoverageや目視の代用にしない。

### D-006

| 候補 | 利点 | 判定 |
| --- | --- | --- |
| Stage 1をruntime manifestへ追加 | 現testだけは通る | payload拡大・audit情報混入。不採用 |
| `stage1/` をtestから無期限に無視 | 現配置を維持 | 意図しないfile検出を弱める。不採用 |
| auditを外へ移し現在のstrict testを維持 | 概念と実配布が一致、最小変更 | 推奨。移動承認と参照更新が必要 |
| 新しいpayload allowlistを導入 | 将来複数artifact classへ拡張しやすい | 二重inventory・取りこぼしのrisk。今回のためだけには導入しない |

提案は `config/codex/docs/skill-audits/ryo-workflows/stage1/` へ既存4文書を移すことである。
Stage 2の4文書は既にruntime外の同系統directoryへ置く。
auditの本文にあるhistorical pathとSHAは歴史的記録として保持し、機能するMarkdown linkと現行案内だけを更新する。
まずcopyとbyte比較、移動後relative link更新、runtimeにauditを含まないことの検証を行い、承認された旧4pathだけを撤去する。
既存未追跡物なので `git mv` を前提とせず、移動前hashとbackupを持つ。
docsはversion管理対象にする案を推奨するが、Stage 2ではcommitしない。
raw transcriptや実予約情報はpayloadにもrepoにも入れず、匿名化したfixture・schema・要約を再現資料として管理する。
`tests/test_ryo_workflows_plugin.py` の「bytecode以外のplugin全fileがmanifestと一致」を保持し、未知file・resource欠落・壊れたlinkを引き続き失敗させる。

## 5. 6スキル構成の比較

| 観点 | Option A: 6つを限定修正 | Option B: 6つ＋support再編 | Option C: merge / split |
| --- | --- | --- | --- |
| 機能 | 既存workflowを保ち6所見へ直接対処 | 共通contract索引やownerを整理できる可能性 | report→figure連続作業の入口をまとめる、reviewを独立化等 |
| discovery | 既存名を保持、D-004だけ補強 | entrypoint不変ならほぼ同じ | 広いdescriptionまたは競合入口が増える |
| context | 条件付きreferenceを維持 | 不要loadの実測があれば改善余地 | 統合で不要workflowを読み込む、分割で同じcontractを再loadするrisk |
| 依存 | 現28 unique edgeを保持 | link移動・共通基盤へのcoupling増 | 複数skillに跨る前提が増えるか、大きい単一skillへ集中 |
| 保守 | 差分が小さくownerが明確 | duplicated ownershipが実在する場合に有効 | review/figure/exportの重複を新たに管理する必要 |
| 移行 | description・helper・運用の限定変更 | reference pathとmanifest、hash、全callerの更新 | name、catalog、prompt、router、参照、testsの移行 |
| 回帰 | 主にICS公開処理 | 科学値・provenanceの契約移動漏れ | font-only/caption-onlyが再抽出や全検証へ拡大するrisk |
| testability | 既存test＋fault / routing評価で測れる | before/afterのreference load実測が必要 | selection・機能双方の比較を全workflowで追加する必要 |

Typstの共有data contractはfigure側 `data-and-verification.md`、表示技術は `presentation-and-layout.md`、portability/CSVはexport側、論旨・caption・組版はreport側を維持する。
同じ科学値保存規則に依存することは、同じentrypointに統合すべき証拠ではない。
211行のreferenceや循環linkだけでは再編を正当化できず、不要loadや探索loopの実測はない。
Option Bは将来の測定でowner混乱が見つかった時、Option Cは独立した利用とrouting改善が実証された時の再検討案とする。

## 6. tradeoffとrisk

最大の残余riskは、C2を「batch atomic」と誤解すること、普通のsymlink検査をrace防御と誤解すること、source試験をactive配布成功と誤認することである。
各保証は上記の前提・限界を公開CLI説明と検証報告にも引き継ぐ。
backupには予約情報が含まれるためstaging/recovery directoryはprivateにし、既存成果物のmodeとrun-created artifactsのcleanup範囲を区別する。
inode差替えはACL/xattrやhardlinkの挙動を変え得る。
処理済みfileの同時user editを検出したら無条件rollbackせず、conflictとしてbackupと状態を保全する。

効率改善は仮説に留まる。
metadata修正やscope明確化が不要loadを減らす可能性はあるが、before LLM測定なしにtoken/cost改善を主張しない。

## 7. 推奨設計と所見の対応表

| 所見 | 推奨解 | Stage 3 task | 必須の受入 |
| --- | --- | --- | --- |
| D-001 | 外部content manifest、重複隔離、fresh catalogと実load照合、配布を別phase化 | T-001 / T-002 / T-008 / T-010 | source→試験runtimeのpath/hash一致。active解消は別のfresh運用証拠 |
| D-002 | C2: stage・backup・per-file公開・通常例外rollback・回復記録 | T-005 | prepublish無変更、catchable fault復旧、復旧失敗の正確な報告 |
| D-003 | 全関連symlink拒否、通常fileのみ、dedicated trusted output | T-004 / T-005 | leaf/parent/danglingで外部sentinel不変、保証外raceを明記 |
| D-004 | 既存figure skillのdescription / operation tableへreview追加 | T-006 | B-02のfindings品質とread-only保全、隣接境界維持 |
| D-005 | task内mandatory gateとtask外未確認の分離 | T-007 | 不完全PDF拒否を維持し、依頼外調査を要求しない |
| D-006 | auditをruntime外へ移動、strict配布検証を保持 | T-003 / T-009 | audit非配布、19file＋承認差分の完全配布、link有効 |

実装unitと依存は[更新計画](02_update_plan.md)、各受入の具体試験は[検証計画](03_validation_plan.md)にある。

## 8. 人のreviewが必要な決定

全項目の状態は **Pending human review** である。
推奨案を作ることへの許可と、その案の採用・実装許可を区別する。

| 決定 | 質問と選択肢 | 推奨default / 根拠 | 留保した場合 |
| --- | --- | --- | --- |
| R-001 | A / B / Cのどのarchitectureか | A。責任の分離と既存testsを保存 | source改修へ進めない |
| R-002 | figure read-only reviewを正式capabilityにするか、別ownerか | 既存figureのmode。本文に既存契約あり | T-006とB-02 routing採点を保留 |
| R-003 | ICSをC1 / C2 / C3のどの整合保証にするか | C2。fixed namesを維持し通常faultから回復 | T-005の実装契約が未確定 |
| R-004 | symlink拒否 / 追跡許可 / 強いPOSIX confinementか | 全関連link拒否＋trusted directory。race保証なし | T-004とsecurity受入を保留 |
| R-005 | arXivの必須完了scopeはどこまでか | 依頼された完全PDFの全gate、task外科学計算は限界報告 | T-007を保留。現行gateは維持 |
| R-006 | auditの配置・version管理・payload方針 | docs配下へ移動し管理、runtime外、raw機密は含めない | T-003を保留、D-006の既知test failureが残る |
| R-007 | 専用runner・model・予算・認証と追加権限 | 隔離runnerで同一条件比較。active変更なし | LLM比較未実行、改善率を主張できない |
| R-008 | deployment / cache / 単独版 / active設定をどこまで変えるか | source実装承認と別に、具体targetごとの承認を取得 | T-010を実行せずD-001の運用解消は未確認 |

選択肢の代償・承認チェックは[review用引き継ぎ §4](04_review_and_handoff.md#4-承認が必要な決定)に集約する。
