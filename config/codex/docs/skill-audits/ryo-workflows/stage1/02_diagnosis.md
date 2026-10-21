# 診断報告

## 1. 要旨

現在の6skillは責任、科学・予約dataの保存、操作別検証の境界をかなり明確に持つ。
全体を短縮・統合・再分割すべきという証拠は得ていない。
重要な現状問題は、実行時に見える版とsourceのずれ、およびtravel helperの上書き失敗時の部分更新である。
symlink越境は実測できたが、不正利用・機密漏えいの発生を確認したものではない。
auto-selection、過剰停止、実行効率については独立LLM試験がなく、静的懸念と観測結果を混同しない。

findingは6件: Critical 0、High 1、Medium 3、Low 2。
種類はObserved defect 3、Static-analysis risk 3、Unverified hypothesis 0。
未検証の仮説は後述のunknownsに残し、件数を増やすためにfindingへ昇格していない。

## 2. 診断軸別の総合評価

| 軸 | 評価と証拠 | 制限・該当ID |
| --- | --- | --- |
| A 目的・責任 | public6skillの目的は分離。Typst3責任のhandoffとownerを明記。README:44-57 | 複数skillを含むpluginという単位と単一skillを区別。split/mergeの優劣は未測定 |
| B discovery | name一致、frontmatter6件合格、operationと除外を記述 | D-001のruntime版ずれ、D-004のreview表現。実selection未試験 |
| C instruction | raw不変・科学値保全等は実リスクへの具体的代替あり。追加権限を与えない | D-005の完了語の範囲。強い表現を一律に欠陥としない |
| D context | entrypoint 29〜50行、referenceは操作別。local path/anchor欠落0 | presentationは211行、cross-linkには循環あり。不要loadやloopの観測なし |
| E execution | helper化、feature別checks、証拠再利用、独立作業の継続は有効 | 22既存testと合成実tool検証は良好。LLM cost/不要tool数は不明 |
| F 正しさ・安全 | dates/encoding/validation、TeX完了summaryとPDFページ一致をtest | D-002/D-003。実際のsource coverageはhelper外という限定が適切 |
| G 保守 | 通常repo suiteにbehavior・配布・reference testがある | D-001の面ごとの版識別、D-006のaudit文書とpayload集合の干渉 |
| H 運用・評価 | source / deployed / catalogを別証拠として扱える | D-001/D-006。test nameの「discovers」はfilesystem到達性でありLLM選択性能ではない |

## 3. finding一覧

| ID | タイトル | 重大度 | 確信度 | 種類 | 主な証拠 |
| --- | --- | --- | --- | --- | --- |
| D-001 | source・deployed・cache/catalogの版が揃っていない | High | High | Observed defect（環境・配布状態） | 01 §6のhash比較、03 E-007、cached verifierとの差分 |
| D-002 | ICS上書き途中の失敗で旧成果物集合が部分更新される | Medium | High | Observed defect | `extrip-to-ics/scripts/build_ics.py:97-104`、03 E-004 |
| D-003 | `--overwrite` がoutput内symlinkの参照先へ書き込む | Medium | High | Static-analysis risk（越境挙動は実測） | 同helper:96-104、03 E-005 |
| D-004 | 図のread-only reviewがdescriptionに現れない | Medium | Medium | Static-analysis risk | figure `SKILL.md:3,17`、03 B-02 |
| D-005 | arXivの「unverifiedが1つでも残れば未完了」の範囲が曖昧 | Low | Medium | Static-analysis risk | arXiv `SKILL.md:24,29`、reference:46 |
| D-006 | 指定audit出力が「全file＝配布payload」の検証と干渉する | Low | High | Observed defect（監査配置に伴うtest failure） | `tests/test_ryo_workflows_plugin.py:35-50`、03 E-008 |

## 4. 詳細

### D-001 source・deployed・cache/catalogの版が揃っていない

- 対象: pluginの配布・登録・session catalog。source instruction自体の欠陥とは区別する。
- 事実: source6skillに対し、この会話のplugin catalogにはpublic arXiv/dotfilesの2skillだけがある。cached resource17件の比較は1一致、3不一致、13不存在。配置済みpluginには6skillあるが3referenceがsourceと異なる（01 §6）。
- 補足: travelは別の単独配置からbare名で見える。従って「travelが全く利用できない」とは判定しない。figure creation/export/reportの3skillはこの会話の一覧にない。
- 技術的影響: cached arXiv helperにはsourceの `parse_log_page_count` とPDF/logページ一致gateがなく、fatal patternも旧版。source:57-66,156-173とcached同fileのdiffで確認した。
- 期待される結果: sourceの修正・test成功を、そのままこのsessionで使われるworkflowの改善と誤認し得る。重要な不完全PDF検知修正もruntimeへ届いた証拠がないためHigh。
- 原因仮説: 配布・cache更新・登録・session更新のいずれかに版の差がある。どの機構が原因かは未検証。同version文字列だけでは判別できない。
- 次の方向: source/deployed/cache/catalog各面のidentityを固定してから比較評価する。必要な更新方法と権限をStage 2で整理する。今回deploymentやcache書換えは行わない。
- 限界: fresh sessionの選択を実測しておらず、catalog欠落がauto-selectionの偽陰性を発生させた実行例はない。

### D-002 ICS上書き途中の失敗で旧成果物集合が部分更新される

- 対象: W-06、helper `generate`。
- 根拠: validateと名前・衝突の事前確認はあるが、final pathへ順次 `open('wb')` する（helper:85-104）。CLIはOSErrorをexit 2へ変換するだけ（:120-121）。plugin README:9は失敗candidateから以前の成功出力を保全する目的を掲げる。
- 再現 E-004: `/tmp` 内に旧 `a.ics` と `trips.ics` を置き、`b.ics` をdirectoryにして2groupを `overwrite=True` で更新した。`IsADirectoryError` が出た後、`a.ics` は変更済み、`trips.ics` は旧bytesのままだった。
- 影響: 旅行別と一括ファイルの内容が食い違う。exit failureを見て旧一式が残ると考えると、誤ったimportや再実行の判断につながる。
- 重大度の理由: 明示overwrite時の後続I/O失敗という条件付きであり、通常生成やvalidation errorでの既存保護はtest済み。普遍的なデータ破損やCriticalとはしない。
- 原因推定: batch validationとbatch publicationを同じ安全保証として扱い、書込時失敗を含む公開手順がない。
- 次の方向: batchの失敗契約、temporary stagingとpublish、復旧可能性を比較する。複数fileの完全transactionを安易に保証しない。Stage 2で許容状態と受入試験を決める。

### D-003 `--overwrite` がoutput内symlinkの参照先へ書き込む

- 対象: W-06の出力境界、helper:96-104。
- 観測 E-005: disposable output内の `a.ics` を、同じ `/tmp` fixture内だがoutput directory外のsentinelへsymlinkにした。overwrite生成後もlinkは残り、sentinelがICSに変わった。
- リスク: output directoryだけの更新を許可した運用で、第三者や以前の処理が置いたlinkを信頼すると、別pathの書換えに到達する。
- 分類: 越境挙動は再現済みだが、linkの存在が悪意・権限逸脱を意味するかは運用依存なのでStatic-analysis riskとする。実データの漏えい・攻撃は確認していない。
- 重大度の理由: 明示overwriteと既存linkが必要。通常の専用出力先では起きず、OS権限を越えるものでもないためMedium。
- 原因推定: filename validationはあるが、最終pathのlink/realpath境界や親directoryのtrustが仕様化されていない。
- 次の方向: symlinkを認める条件、専用directory運用、script側の防御とsandbox側の制御を比較する。instructionだけではTOCTOU等まで防げず、実filesystem権限の制御が必要な範囲を分ける。

### D-004 図のread-only reviewがdescriptionに現れない

- 対象: W-03のdiscovery。
- 事実: descriptionは “creating, adding, or revising scientific Typst figures” とpackaging境界を記述する（`SKILL.md:3`）。本文:17は “For a read-only review, report findings and leave sources and delivered outputs unchanged.” と明示する。
- リスク: 図だけの数値対応・legend reviewがentrypointの意図に含まれていても、metadata段階で選ばれにくい可能性がある。report skillのdescriptionはfigure implementationを除外している。
- 確信度: 文字上の非対称は確実だが、LLMは意味からreviewを選べる可能性がある。偽陰性を実測していないのでMedium。
- 原因仮説: 作成・改訂と配布の分離で、review modeの入口条件が取り残された可能性。historyから著者意図までは断定しない。
- 次の方向: 03 B-02をfresh contextで明示/暗黙/無skill比較する。reviewが意図したcapabilityか人が確認し、その後にdescriptionの変更要否を判断する。

### D-005 arXivの完了gateの範囲が曖昧

- 対象: W-02のcompletion。
- 根拠: “State any unverified item; do not claim completion while one remains.”（`SKILL.md:29`）。一方、helperの証明範囲は明示的に限定され（:24）、reviewable warningは条件付きで許容される（reference:46）。
- 解釈: 全文範囲・build整合・必要な目視の未実施を完了にしないのは重要である。ただし、依頼外のupstream科学計算等まで「any」に含むかは明確でない。
- 予想影響: 過度に広く読むと、許可されたPDF作成が終わっても不要な調査・確認を続ける可能性がある。
- 確信度と重大度: task内の必須事項だけを指す自然な解釈もできる。停止・不要質問の観測はないためLow / Medium confidence。
- 原因仮説: 過去の部分PDF完了誤認を防ぐ強い表現の適用範囲が、task contractへ明示的に結び付いていない。
- 次の方向: 必須gateと参考限界を区別する表現の必要性をStage 2で確認する。raw不変・全文PDF・画像目視という元の禁止を削らない。

### D-006 audit出力と配布payload検証の干渉

- 対象: repoのdistribution testと今回の指定output location。
- 根拠: `tests/test_ryo_workflows_plugin.py:35-50` はplugin配下の全fileをexpected manifestへ加え、除外は `__pycache__` だけである。untrackedの `stage1/*.md` も含まれる。
- 観測 E-008: 4文書作成前は関連test22/22成功。文書作成後、distributionの3test中manifest完全一致だけが失敗し、他2件は成功。差は新しい4監査文書のみだった。
- 影響: 指定どおりの監査資料を置くだけで通常suiteの1testが失敗する。audit文書を配布payloadに追加して直すと、意図しないruntime contextや配布範囲の拡張になる。
- 分類・重大度: 監査配置に起因する再現済みtest failureであり、既存skill実行の欠陥とはしない。local-only reportの取扱いという限定条件なのでLow。
- 原因: 「plugin配下のfile」と「runtime payload」の集合がtest内で同一視されている。保全漏れ検知という元の利点はある。
- 次の方向: Stage 2で監査文書の保存・version管理・配布境界を決める。今回はユーザー指定場所を守り、manifest/test/ignoreは変更しない。

## 5. 強い制約・否定命令の評価

全14 Markdownを通読し、英語の `do not / never / avoid / always / must / cannot / only / required / requires` と日本語の禁止・必須表現を照合した。
機械検索は125行に一致したが、`notation-only` や引用内の “always” も含み、125個の独立した禁止を意味しない。
以下は同じ目的・適用条件を持つ命令をまとめた評価である。
「代替」は禁止時に行う具体的な手段、「整合」は上位のuser scopeとの関係を示す。

パス略号: F=`creating-and-editing-typst-figures`、E=`export-editable-typst-figures`、R=`writing-typst-research-reports`、A=`creating-arxiv-diff-pdfs`、T=`extrip-to-ics`。
`data`=Fの`references/data-and-verification.md`、`layout`=Fの`references/presentation-and-layout.md`、`provenance`=Eの`references/data-and-provenance.md`、`examples`=Eの`references/provenance-examples.md`、`composition`/`writing`=Rの各reference。

| 命令群と位置 | 目的・実リスク | 適用条件 | actionableな代替 | 整合と比例性の判断 |
| --- | --- | --- | --- | --- |
| reviewは変更しない: F/SKILL:17、R/SKILL:15-16 | reviewを無断実装にしない | read-only依頼時 | location/evidence付きfindingsを返す | 上位境界と一致。必須維持。discoveryはD-004 |
| 科学値の再推定・勝手なschema変更をしない: F/SKILL:19-21,34、data:16-31、E/SKILL:21-22、provenance:38-45、R/SKILL:20-22、writing:42 | 数値意味・user scopeの破壊 | 表示変更、storage変更、通常執筆。別途許可されたdata deltaは別扱い | 保存値・定義を使い、許可deltaだけ照合 | 普遍的な再推定禁止ではない。条件と代替が明確で比例的 |
| raw diff/公式source不変、失敗を反復しない: A/SKILL:10,14,16、A/reference:3,7,34,38,42 | 再現性・由来の破壊 | diff作成と互換修復 | 別名copy、最小再現、公式bblから復元 | 必須維持。過去modelへの過剰適合とは判断しない |
| partial PDF・markup全抑制を完成扱いしない: A/SKILL:22-29、A/reference:46,50 | 全文欠落の誤納品 | 完成PDFを要求された時 | full build、範囲・構造・目視を別確認 | 核心契約は比例的。「any unverified」のみD-005 |
| 成功成果物と履歴を失敗candidateで置換しない: data:35-50,54-65、provenance:61-82、examples:46,52,79-103、composition:63-78、R/SKILL:39 | 旧成功・user editsの喪失 | affected set更新、concurrent edit、部分失敗 | temp候補、記録append、再照合、依存setだけ保留 | 必須維持。意味の重複はあるがowner/callerの目的がある。travelの保証差はD-002 |
| hashを数値正しさやupstream証明にしない、自己hashを入れない: data:14,18,46、provenance:29-31,61-65、examples:5 | 循環identity・誤った科学的保証 | baseline/来歴/loaded metadata | 数値対応と観測scopeを別記録、final hashは外部 | 実リスクへの具体的対処。普遍的に維持 |
| missing definition時は依存箇所だけ保留: data:56、layout:21,48,66-70,207、composition:32,48,66-67、writing:29 | 推測による結果変更と全作業停止 | 未確定quantity/unit/条件 | 根拠を探し、gapを明示し独立作業継続 | 不要確認を一律要求していない。維持 |
| affected featureだけ検証し、読込を全workflow起動にしない: F/SKILL:32-33、data:49-50、layout:3,56,129,155,187-192、E/SKILL:11,37、provenance:65,84、composition:23-36,68 | 無関係なtool/調査の増加 | font-only、maintenance、既存図利用等 | operation tableとfeature rowsを選ぶ | context節約と権限維持。実効性は未測定だが比例的 |
| drawingに長文説明・内部ID・完成captionを入れない: layout:12-20,117,150-151,199、writing:84-85 | reader向け情報と来歴の混線 | figure。layout:5でuser/publication要件優先 | sourceのcaption ingredients、本文caption、既存記録 | 意図的編集方針。必須user選択を上書きする普遍規則ではない。科学diagramへの適用境界は要確認 |
| 点を勝手に接続・補間・contour化しない、条件を落とさない: layout:42-62,140,190,198,202、composition:17-19、writing:99-103 | 未計算条件や欠落を隠す | provenanceとaxis意味に依存。時系列/model曲線は別扱い | point表示、原定義照合、条件tuple/multiplicityチェック | domain判断が具体的で維持。全line plot禁止ではない |
| conversionの二重適用・labelだけ変更をしない: layout:66-97,200、composition:71、writing:78-80 | unit/interval位置の誤り | notationかquantity変換かを区別 | 式/単位確認、座標・区間端・tick・理論を1回変換 | 比例的。sample-count式は例であり固定手順ではない |
| hollow透明、legend一致、inset境界一致: layout:27-39,123-148,197,203 | data遮蔽・記号意味の誤認 | 当該表現が存在・変更時 | receiving sizeでstyleとintervalを照合 | 条件限定で妥当。色/形/配置の固定なし |
| 本文page設定を図が変えない、縮小/余白変更を安易にしない: layout:111-127、R/SKILL:17-19、composition:49,53-59 | caller contractと可読性の破壊 | inherited templateとfigure inclusion | grouping、panel分割、flow/placementを調整 | user要件優先。新稿A4も未指定時だけで比例的 |
| selectorの第2active list・source text parseを作らない: layout:156-183,205、provenance:21-25 | full/selected/exportの条件ずれ | selector/batchを追加・変更時 | 同じ条件source/metadata、既存interfaceのvalidation | source形式が特殊な時の例外は未実測。現workflowでは一貫性維持の根拠あり |
| bundle-relative path、元repo symlinkに依存しない: E/SKILL:15-24、provenance:11-25、composition:65 | 移設でcompile不能 | portable bundleとrecipient inclusion | 同梱依存、移設compile、対応formatへexport | 認める外部依存（Typst/fonts/packages）も明記。完全offline要求ではない |
| CSV cellを丸め・平均・再推定しない: provenance:36-45 | storage-onlyで科学値を変える | storage変換時だけ | identifierで分割して原table再構築 | 許可scientific deltaとは区別済み。維持 |
| general trendをminor reversalだけで棄却せず、統計量を混同しない: writing:16-48 | 科学的主張の過剰化/過小化 | 保存値・研究質問とconditionの範囲 | counterexample保存、必要限定、代表値と意味を記述 | 普遍閾値を要求しない点が有効。機構の推論には根拠を要求 |
| 本文に表・図・条件・作業履歴を機械的追加しない: composition:8-12,40-48、writing:38-40,53-56,60-75,83-105 | 重複・読みにくさ・撤回user editsの復活 | 役割のない情報、既存参照で足りる時 | 質問への寄与で選ぶ、必要な意味/値は残す | 説明削除を一律要求していない。1文1行はtouchした自然文だけで比例的 |
| deployment/環境導入/削除等の権限を拡大しない: dotfiles/SKILL:14-25、F/SKILL:42、data:59,65、E/SKILL:23-24、R/SKILL:40 | live変更・既存data喪失 | mutationの直前、対象別 | managed source、dry-run、既存許可を確認 | 上位規約と重複するがoperation境界の説明として有用。毎段階の再承認を要求しない |
| 旅行情報を推測しない・API不要・登録しない: T/SKILL:9-16,28-29,37-50、T/schema:5,36-46 | 誤予定・漏えい・無断external write | ローカルICS生成、必須日時不足 | 原文照合、unknown明記、該当予定の必要情報だけ確認 | 予約workflowに比例。Python stdlibとCLI interface、再import限界を維持。書込境界はD-002/D-003 |

コード・example内の “required” や “always” の引用は独立命令と扱わず、元の条件を付けて評価した。
一般能力の説明を長く繰り返す箇所や、単なるfile名・page数・図数を無条件固定する規則は見つからなかった。
`./install` の例はselected checkout基準という周辺説明があるが、実cwdの設定は省略される（dotfiles:25-29）。
これは今回の欠陥再現とはせず、remote実行例の可搬性を今後確認する点とする。

## 6. 横断問題と保存要件

環境上の版ずれ（D-001）をinstructionのrouting品質や新しいsourceの欠陥と混同しないことが最重要である。
同様に、validation-before-write、検証済みcandidateの公開、directoryへの書込許可は異なる保証である（D-002/D-003）。
instructionを短くしてもこれらの実装・実行環境問題は解消しない。
逆に、強い禁止を増やすだけではmulti-file I/O失敗やlink raceに実効的な保護を与えない。

| 保存すべき価値 | 根拠 | Stage 2で守る性質 |
| --- | --- | --- |
| 条件付きprogressive disclosure | 全entrypointのoperation tables、F:32-34 | 関連referenceを使うだけで抽出・移設・全testを起動しない |
| 条件tuple/multiplicity・intervalまでの照合 | data:16-21、layout:50-61 | 総件数とhashだけで欠落・duplicateを見逃さない |
| 保全を伴うstaging | data:33-65、composition:63-78 | 部分失敗とconcurrent editsで旧成功成果物・user editsを守る |
| 科学的主張の質 | writing:14-48 | RMSE/SD/bias、傾向/解釈/機構、反例の重要度を区別 |
| portabilityの実検証 | provenance:8-25,36-44 | editable source、無損失table、移設とrecipient inclusionを別検証 |
| 完全PDFへの複数のgate | A/SKILL:22-25、helper:138-225 | `.log`整合とsource coverageと目視を代替関係にしない |
| travelのformat/予約契約 | helper:12-81、7既存tests | UTC、CRLF/UTF-8 folding、escape、stable UID、checkout日含有、Maps |
| testの通常suite統合 | 3関連test modules | mocked control-flowとreal toolchainを区別しつつ両方保存 |

## 7. 定型分類外の所見とunknowns

payload集合とlocal監査資料の干渉はinstruction品質以外の運用問題としてD-006に独立させた。
プラグインのversion文字列とfilesystem copyだけでは、現在の会話にどの版が供給されたかを証明できない点も追加所見である。
READMEの歴史的監査は日付と旧inventoryを明示しており、現inventoryとの見かけの差を欠陥とはしない。

未確定なのは、fresh catalogでの正負・境界promptのselection、不要referenceの実load量、実行cost、確認回数、workflow completion rateである。
図の説明文排除やpaper継承は明確な編集方針であり、user/publication優先もあるため、一般論で削除対象にしない。
一般的なscientific diagram、特殊なsource selector、必須日時の一部不足に対する独立eventの扱いは、実例と期待仕様の追加確認余地がある。
安全な検証で重大な機密送信・live mutationは見つけていないが、全外部dataのprompt injection耐性を試験したわけではない。
予約MarkdownやarXiv source内のcommandを信頼して実行しない境界は上位規約・sandboxにも依存し、instructionだけで保証できない。

## 8. 診断と設計の境界

D-002の失敗契約、D-001の評価版固定は改善の必要性を直接支持する。
D-003のlink policy、D-004のreview ownership、D-005の完了表現、Typst3skillの構造変更は比較・reviewが必要な選択である。
具体的な置換architecture、file移動、統合・分割、実装手順は承認済み決定として提示していない。
候補とtradeoffは [04_handoff.md](04_handoff.md) に限定して引き継ぐ。
