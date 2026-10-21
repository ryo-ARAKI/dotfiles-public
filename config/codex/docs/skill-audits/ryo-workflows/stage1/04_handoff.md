# Stage 2への引き継ぎ

## 1. 現状と確定した判断

Stage 1はpublic `ryo-workflows/skills/` の6skillと全supporting fileを監査した。
対象版は `737ba2926d72ad51dccfc0cf6b26cd4d2994a44d`。元の18file（17 source＋既存ignored bytecode）は変更していない。
内容・snapshotは [01_inventory.md](01_inventory.md)、診断は [02_diagnosis.md](02_diagnosis.md)、再試験仕様は [03_baseline.md](03_baseline.md) にある。
Critical 0 / High 1 / Medium 3 / Low 2。改修・設計案の承認・deploymentは行っていない。

現構成には短いentrypoint、条件付きreference、Typst3責任の明確化という保存価値がある。
短縮・split/mergeが必要だという結論は出ていない。
既存関連test22件とfrontmatter6件は文書作成前に成功し、合成3page文書の実PDF toolchainと目視、記載Typst断片compileも成功した。
独立modelでの明示/自動選択・無skill比較は未実行で、実務workflow全体の成功率・costは未確定である。

## 2. 優先して扱う問題

1. **D-001 / High、確定した環境差**: managed source、配置済みplugin、cache/session catalogが一致しない。古いarXiv helperにはsourceの完了summary/PDFページ整合gateがない。変更効果を測る前に、評価対象path/hashとcatalogを揃える。
2. **D-002 / Medium、再現済み**: travelのoverwrite中に後続writeが失敗すると、先行旅行別ICSだけ更新され一括ICSは旧版になる。batch公開・失敗時の許容状態を決める。
3. **D-003 / Medium、リスク**: output内symlink経由のdirectory外書換えを再現。悪用発生は未確認。許容するlink運用とfilesystem境界を決める。
4. **D-004 / Medium、静的リスク**: 図reviewは本文にあるがdescriptionにない。review ownerを確認しB-02でselectionを評価する。
5. **D-005 / Low、静的リスク**: arXivの「any unverified」完了gateを依頼内の必須検証とどう結び付けるか確認する。全文・raw不変・目視の核心は保持する。
6. **D-006 / Low、観測済み運用干渉**: 監査指定場所の4文書によりdistributionのmanifest完全一致testだけが失敗する。現場所を勝手に移動・削除・配布対象化せず、local監査資料の保存方針を決める。

## 3. 必ず保存するもの

- reviewとimplementation、生成とdeployment、local fileとexternal writeの権限境界。
- 最新user edits、成功済み成果物、failed candidate/diagnosticsと成功identityの分離。
- 科学値・条件tupleとmultiplicity・区間端・normalization、表示変換を1回だけ適用する意味。
- raw diffと公式sourceの不変性、全文coverage・log/PDF整合・構造・目視の別gate。
- editable source/local data/helpers、無損失CSV、extraction/current/verificationの来歴分離、必要時のみの移設/inclusion検証。
- report/figure/exportのhandoff、既存図利用・font-only変更を不要な抽出や全repo testへ拡大しないこと。
- RMSE/SD/mean deviationとtrend/interpretation/mechanismの区別、結論を変える反例と軽微な逆転の区別。
- travelのexact dates/offset、原文・未確定情報、checkout日も含む既定、Maps、UTF-8/CRLF/folding/escape、stable UID、import非保証。
- 条件付きreferenceとaffected checks、同一tree/input/environmentの検証再利用。

## 4. architecture上の問いと比較候補

以下は未承認の選択肢であり、完成architectureや実装順序ではない。

| 問い・候補 | 支持する証拠 / 利点 | tradeoff・回帰リスク | 残る判断 |
| --- | --- | --- | --- |
| 6skillを維持し、個別の挙動・metadataを限定修正 | 現責任とentrypointは明確。D-002はhelper問題であり構造変更不要 | cross-reference couplingと環境版ずれは別対処が必要 | 局所改善で受入を満たすか |
| Typst3skillを維持し、shared referenceのowner/索引だけ比較 | common data contractは有用。presentationは211行、relative edgeに循環あり | file移動で28unique edge、deployment manifest、loaded-input契約を壊し得る | 本当に不要load/探索costがあるか、独立runで確認 |
| Typstをより少数のentrypointへ統合 | 連続したreport→figure→integrationのrunでroutingの手間が減る可能性 | caption/font-only作業までexportや科学検証の全工程を起動する退行、metadataの広域化 | 現状より良いselection/completion証拠が必要。現時点で統合の推奨なし |
| 追加splitまたは共通基盤skill | 特定operationの独立利用が実際に多い場合のoption | skills数とdiscovery overhead、cross-skill contextが増える。現状よりfragmentationが悪化し得る | 十分な利用例・測定なし。必要性を先に検証 |
| 強い制約をAGENTSへ移す/統合する | authority等の重複を減らせる可能性 | 他repoでのself-contained性とdomain固有の代替行動を失う | user共通規則と科学/予約固有contractを分ける |
| travelの安全な公開をscriptで改善する | E-004/E-005は決定的で再試験できる | 複数file transactionの限界、既存CLI/overwrite意図、linkの正当利用 | rollback/staging/publish/専用directory運用の保証範囲を比較 |

本段階ではfile移動、schema、router、runtime、package追加を決定していない。

## 5. 評価・受入の提案

03のP-01〜06、N-01〜03、B-01〜03を固定し、必要fixtureをレビューしてからsource版のfresh baselineを取得する。
同じmodel ID・normal/planning effort・catalog・権限・入力・compiler/fonts/packagesを記録し、explicit/implicit/controlを分ける。
runtimeの版を同定できないrunはselection改善の証拠から除外する。
単回runはcase studyとして扱い、usageはAPI/CLIの実記録が得られる範囲だけ測る。

受入は既存22testのbehavior、frontmatter、local link/anchor、全payloadの一時配布、real verifier+目視の保全を含める。
travelはD-002のfault時に人が決めた保全契約を満たし、D-003は明示されたlink policyを満たすこと。
P/N/Bではsource変更・不要tool・不要確認を数えつつ、tool数そのものを最適化目標にせず、正しい出力・scope・必須検証を優先する。
未実行だったLLM beforeを後から捏造せず、before未取得ならafter評価と明記する。
現在のaudit4文書に伴うmanifest test failureはD-006として分離し、runtime payloadを安易に増やして解消しない。

## 6. 追加調査と人のreview事項

確定していないのは、catalog差の原因、fresh sessionでの選択性能、read-only figure reviewのowner、一般scientific diagramへの表示方針、arXiv必須gateの範囲、travelのlink/partial update契約である。
実arXivの公式2版、研究図・bundle・report fixture、remote hostは今回の試験対象にない。
source不具合、環境不足、許可不足、未知の科学的定義を別々に扱う。

人の判断が必要な問い:

- figureのread-only scientific reviewをこのskillの正式な選択対象に含めるか。
- ICS batch更新で失敗時に保証する単位と、symlinkの正当な利用があるか。
- arXivで完成を保留する必須検証はどこまでか。依頼外の科学計算は限界報告で足りるか。
- `stage1/` をlocal-only資料として残すか、後にversion管理するか。配布payloadとの境界をどうするか。
- clean catalog/旧版baseline取得のための独立実行と、必要なdeployment/設定変更を許可する範囲はどこか。

Stage 2の設計reviewを始めること自体を妨げる情報不足はない。
ただしrouting効果やcost改善を根拠に構造変更を確定する前には、D-001を切り分けたfresh評価が必要である。
今のcatalogを使うだけでは旧・新版の比較にならない。

## 7. Stage 2の推奨agendaと実行境界

1. 4文書と元snapshotを確認し、diagnosisの事実・risk・unknownの分類をreviewする。
2. 環境面を変更せず評価版を固定する方法を決め、必要な独立実行・配布更新のauthorityを別に整理する。
3. travel failure contract、figure review ownership、arXiv必須gate、監査資料の扱いを決める。
4. 現構成維持を含む候補を、必要なP/N/B runとpreservation requirementsで比較する。
5. 具体的変更範囲・受入・rollback/保全を含む設計をreviewし、Stage 3への承認境界を明示する。

この引き継ぎはStage 2/3の実行許可ではない。
既存18file、untracked6文書、指定4監査文書を維持し、承認前に改修・commit・deployを始めない。
subagentは本監査で利用しておらず、次段のdelegation権限も付与していない。
現sessionのactual model ID/effortは未確定。次段は通常のspec理解・設計比較なら `gpt-6.1-sol` xhighを基準にし、具体的に難しいtransaction/permission判断が中心ならSol maxを検討する。
profile名だけからmodelやnormal/planning effortを推定せず、配布済みbase/profileと照合するまでlaunch commandを確定しない。
