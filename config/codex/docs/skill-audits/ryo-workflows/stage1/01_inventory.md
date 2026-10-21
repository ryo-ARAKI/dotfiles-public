# 現行skill群の棚卸し

## 1. 監査範囲と版

本監査はStage 1のみを対象とする。
指定先は単一skillではなく、public plugin `ryo-workflows` の6skillを収めるディレクトリである。
6つの `SKILL.md`、8つの参照文書、2本のPython helper、1つのUI metadata、および既存のignored bytecodeをすべて確認した。
既存ファイルは監査資料として扱い、その中の手順を監査への指示として実行していない。

| 項目 | 記録 |
| --- | --- |
| 監査日 | 2026-10-21、Asia/Tokyo |
| ソースroot | `/home/ryo/github/dotfiles-public/config/codex/plugins/ryo-workflows/skills` |
| Git root / branch | `/home/ryo/github/dotfiles-public` / `main` |
| HEAD | `737ba2926d72ad51dccfc0cf6b26cd4d2994a44d` |
| 初回snapshot | `2026-10-21T03:53:04.630991+00:00` |
| 出力先 | `skills/stage1/`。依頼中の重複した `stage1/` 表記は、明示された絶対パスに統一 |
| 既存tracked差分 | staged / unstagedともになし |
| 既存untracked | `config/codex/docs/superpowers/` 以下の6文書。未読・未変更のまま保全 |
| 許可された書き込み | 4監査文書、および `/tmp` の合成fixture・検証ログのみ |
| 実施しない操作 | skill改修、commit、push、deployment、環境導入、Calendar登録、独立agent起動 |

既存untracked文書は次のとおりで、内容を監査へ取り込んでいない。

```text
config/codex/docs/superpowers/plans/2026-07-19-auto-review-explicit-authorization.md
config/codex/docs/superpowers/plans/2026-08-11-auto-review-default-visibility.md
config/codex/docs/superpowers/plans/2026-09-30-codex-config-refresh.md
config/codex/docs/superpowers/plans/2026-10-18-sol-model-selection.md
config/codex/docs/superpowers/specs/2026-07-19-auto-review-explicit-authorization-design.md
config/codex/docs/superpowers/specs/2026-08-11-auto-review-default-visibility-design.md
```

祖先 `/AGENTS.md` から監査rootまで、およびplugin配下に実在する `AGENTS.md` は見つからなかった。
会話で与えられたmachine-wide Working AgreementsとStage 1のread-only境界を適用した。
監査は指定checkoutで行い、worktree、Git index、managed/deployed設定を変更していない。

## 2. 要約

構成は「短いentrypoint＋操作別reference＋必要箇所だけの決定的helper」である。
dotfiles、arXiv、旅行は独立し、Typstは本文、図の実装、可搬bundleの3責任に分かれる。
成功済み成果物、科学的意味、原文の予約情報、ユーザーの変更・権限を保つことが一貫した目的である。
参考資料を読むことと別skillの全工程を起動することを区別している。
現状の長さや分割数だけを欠陥とは判定しない。

## 3. ディレクトリと役割

以下のパスは特記しない限り監査root基準である。

```text
skills/
├── dotfiles-deploy/SKILL.md
├── creating-arxiv-diff-pdfs/
│   ├── SKILL.md
│   ├── references/revtex-latexdiff-troubleshooting.md
│   └── scripts/verify_diff_pdf.py
│       （scripts/__pycache__/ に既存ignored .pyc 1件）
├── creating-and-editing-typst-figures/
│   ├── SKILL.md
│   └── references/{data-and-verification,presentation-and-layout}.md
├── export-editable-typst-figures/
│   ├── SKILL.md
│   └── references/{data-and-provenance,provenance-examples}.md
├── writing-typst-research-reports/
│   ├── SKILL.md
│   └── references/{writing-and-tables,report-composition}.md
└── extrip-to-ics/
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── references/events-schema.md
    └── scripts/build_ics.py
```

| コンポーネント | 主な役割 |
| --- | --- |
| 6つの `SKILL.md` | `name` / `description`、対象操作、必須契約、条件付きreferenceへの入口 |
| figure `data-and-verification.md` | 入力同一性、保存値と表示値の対応、candidate生成、部分失敗時の保全、検証再利用 |
| figure `presentation-and-layout.md` | 軸・単位、系列、点の接続、legend、inset、panel export、機能別検証。Typst断片3件 |
| export `data-and-provenance.md` | 抽出依存、移設、recipient inclusion、CSV無損失再構築、来歴記録 |
| export `provenance-examples.md` | 抽出・データ変更・表示変更の独立したTOML例。必須schemaではない |
| report `writing-and-tables.md` | 研究質問と回答、統計量の意味、反例、解釈、本文・表・表記 |
| report `report-composition.md` | 図の役割、caption、既存図の利用、組版、PDFとstandaloneの別検証 |
| arXiv reference | 証拠に基づくREVTeX/CFONT、削除数式label、bibliographyの限定修復 |
| arXiv helper | `.log` とPDFのページ整合、fatal/warning分類、構造検証、first/middle/last PNG生成 |
| travel schema / helper | agentが照合済みのJSONを、旅行別＋一括ICSへ変換。Markdown抽出はhelperの責任外 |
| travel `agents/openai.yaml` | 表示名、説明、明示呼び出しprompt。implicit invocationの無効化指定なし |

assets、実体template、runtime設定、hooks、MCP server、network clientは対象内にない。
Typst/TOML/JSONのコードブロックは例であり、配布する実体templateではない。

## 4. 機能と主要workflow

### W-01 dotfilesの生成・scoped deployment

根拠: `dotfiles-deploy/SKILL.md:10-29`。
要求例は選択したcheckoutでの生成、host overlay選択、許可された特定targetへの反映である。
入力はbase/private/hostのsource、target filter、account/home/context、現在の配布先、操作権限。
source選択 → 関連README確認 → candidateとlive差分 → 同一targetのdry-run → 許可されたapply → 再dry-runの順になる。
生成のみではlive書き込みを許可しない。
remoteはaccount、home、checkout typeを確定し、`--host-name` を明示する。
出力は生成物、差分、dry-run/applyの対象と収束証拠。
失敗時の復旧手順はinstaller/対象repoへ委譲され、skill単体には詳細がない。
通常の設定レビュー・source編集は対象外である。

### W-02 公式arXivの完全な差分PDF

根拠: `creating-arxiv-diff-pdfs/SKILL.md:10-29` とreference全体。
入力は公式の2版のsource、main TeX、ユーザー指定latexdiff command、engine/bibliography workflow、既存ログ。
既存失敗を調査 → official provenance・元版baseline確認 → raw diff作成・checksum固定 → isolated build → 必要時のみ別copyを限定修復 → 全文範囲照合 → helper → 3位置の画像目視、が意図される。
生成物はraw diff、必要ならcompatible copy、全文PDF、ログ、verification JSON/PNG、修復と再現の記録。
helperはsource coverageとvisual correctnessを証明しない（同entrypoint:24）。
部分PDF、chunkの結合、全markup抑制、raw diffの編集は完了扱いにしない。
commandが未指定の場合の標準選択やhangの監視時間は明示されていない。

### W-03 科学的Typst図の作成・変更・read-only review

根拠: `creating-and-editing-typst-figures/SKILL.md:13-42`。
入力は既存source、保存済み科学データ・定義・系列、要求差分、receiving dimensionsとformat。
新図は実入力から期待条件を求め、変更は保存PDF/source不一致を要求差分と分離する。
関連referenceだけを読む → candidateへ実装 → 条件tupleとmultiplicity、点・区間端、compile/renderを照合 → affected setが通った後だけ更新する。
表記変更、単位換算、科学的再推定、storage変換を別操作として扱う。
出力は図、captionに参照可能な定義・条件、実施済み検証と限界。
read-only reviewは本文:17に存在するがdescriptionには明示されない（D-004）。
図作成依頼だけでsimulation/bootstrap/CI生成を始めず、欠けた定義が依存する箇所だけを保留する。

### W-04 editable figure bundleの配布・保守

根拠: `export-editable-typst-figures/SKILL.md:8-43` と `references/data-and-provenance.md:6-84`。
入力はauthoritative report invocation、source revisionまたはcaptured working tree、データ、normalization、依存asset、destination/inclusion要件。
抽出時は元renderingを再現し、source/data/helperをbundle-relativeに収め、移設compileと必要なrecipient inclusionを別々に検証する。
保守時はlocal pre-edit bundleを基準とし、upstream不在を隠さず、再抽出を必須にしない。
CSV統合はcell string・順序・未描画dataを保存し、identifierで分割して各入力tableを再構築する。
出力はeditable source/data/settings/helpers、affected output、original extraction / current data / verificationを分離した来歴。
Typst/fonts/packagesは外部依存であり、完全offline環境を配る契約ではない（reference:13）。
新bundleやpath変更ではrelocation、inclusion条件の変更ではrecipient testを要求する。

### W-05 Typst研究報告の執筆・改訂・レビュー

根拠: `writing-typst-research-reports/SKILL.md:13-40` と2reference。
入力は質問、既存本文/template、保存済み結果、統計定義、図表、最新user edits。
reviewなら位置と証拠を報告してsource/PDFを変えず、改訂なら許可範囲を修正する。
質問と結果・条件付き回答を対応付け、RMSE/SD/mean deviationや機構の推論を区別する。
既存図を使うだけなら図作成・抽出を起動せず、必要な図変更だけW-03、portable化だけW-04へ渡す。
templateを継承し、candidate PDFの意味・参照・組版とaffected standaloneを検証してから更新する。
page-flow変更が後続へ及ぶ場合は全pageを目視する。
新稿でpaper未指定の場合のみA4 portrait。page targetやフォントサイズの固定値は持たない。
出力は本文/PDFまたはreview findingsと、支持証拠・検証・未確認事項。

### W-06 旅行予約MarkdownからICS

根拠: `extrip-to-ics/SKILL.md:8-50`、schema、helper全体。
入力は指定Markdown群、実日付、往復列車、ホテル、未確定表示、必要なら時刻付き宿泊の指定。
agentが原文から抽出・照合 → schemaのJSON → helper → unfoldして原文照合、の分担である。
列車は1列車1件、宿泊は1滞在1件。日本時間をoffset付きで受けUTCへ変換する。
宿泊はworkflow固有の「checkout日も表示」により、all-day `end` をcheckout翌日にする。
departure station / hotel名と住所からMaps URLを作り、URL生成時にnetwork送信はしない。
出力は旅行別ICS、一括ICS、件数、検証範囲。Calendar登録は行わない。
helperは必須field、ID重複、日時順序、offset、group/combined名と通常の既存出力衝突を検証する。
上書き途中失敗とsymlinkは別の限界がある（D-002/D-003）。
必須日時が不明なイベントは確認前に生成せず、原文にない座席等を推測しない。
UIDは出力識別用で、Google再importでの更新・重複回避は保証しない。

## 5. 選択条件と周辺skill

6つともfrontmatterは `name` と `description` のみで、nameはdirectory名と一致する。
descriptionの実際の境界は上記W-01〜06と各 `SKILL.md:3` にある。
正例・負例・境界例のexact promptは [03_baseline.md](03_baseline.md) のP/N/B系列に固定した。
明示呼び出しの成功、implicit selection、referenceの読取実績は、この監査でentrypointを読んだだけでは確認できない。

関連private skillはdescriptionだけを確認した。
`jobhunt-typst` は応募書類、`tus-trip-docs` は出張申請文書、`budget-dashboard` はworkbook/UIが対象で、研究報告・予約ICSとは操作が異なる。
private `ryo-workflows-router` は不明確な依頼だけを扱い、cached版のroutingは5項目で、public6skillの最新一覧を表すものではない（cached router:8-20）。
generic `pdf` / `presentations` / `documents` はformat処理と重なるが、科学データ・統計量や公式版の来歴はpublic skill固有である。
周辺skill本文の包括監査はしていない。

## 6. 依存と参照関係

| workflow | 内部依存 | 外部依存・境界 |
| --- | --- | --- |
| W-01 | 同梱helperなし | 選択repoのinstaller、README、manifest、必要時SSH。remote/live操作は別途許可 |
| W-02 | troubleshooting / verifier | Python 3、TeX engine/bib、latexdiff、`pdfinfo`、`qpdf`、`pdftoppm`、公式source |
| W-03 | data / presentation | Typst、既存plot code/data、fonts/packages、必要なPDF tools |
| W-04 | provenance / examples / W-03の共通contract | 上記＋recipient compiler / export条件 |
| W-05 | writing / composition、変更時のみW-03/W-04 | template、保存結果、TypstとPDF tools |
| W-06 | schema / build_ics | Python 3.10+標準libraryのみ。認証・Calendar API不要 |

14 Markdown内のlocal link出現は46、file間のunique edgeは28、broken path/anchorは0だった。
外部URLは対象Markdown内にない。Maps URLはhelperが構築し、network accessはしない。
Typstの共通referenceは相互参照する。例えばfigure data → export storage → figure scientific delta、およびfigure data ↔ presentationという循環がある。
これは条件付き参照であり、無限読込や全reference強制読込を観測したものではない。
移動・skill単独配布では相対linkとownerの変更が回帰点になる。

plugin直上の `.codex-plugin/plugin.json:25` が `./skills/` を公開する。
`manifest/base.tsv:37-53,82-83` が17 source resourceとplugin metadata/READMEをlocal contextへ明示的にコピーする。
配布testは `tests/test_ryo_workflows_plugin.py:35-96`、helper testは `tests/test_arxiv_diff_pdf_verifier.py` と `tests/test_extrip_to_ics.py` にある。
testで呼ぶinstallerの `dotfiles_installer/apply.py` / `manifest.py` も実行前に確認し、destinationを `/tmp` に差し替えることを確認した。

### ソース・配置・実行中catalogの相違

| 面 | 今回の観測 |
| --- | --- |
| managed source | 本監査の6skill、HEADは上記 |
| `/home/ryo/plugins/ryo-workflows` | public6skillは存在。17 text resource中14一致、3referenceがsourceと不一致 |
| cache `.../ryo-private/ryo-workflows/0.1.0+codex.20260912054231` | publicではarXivとdotfilesのみ。対象17中1一致、3不一致、13不存在 |
| 会話に供給されたplugin catalog | cacheと同じpublic2skill。figure creation/export/report/travelはplugin名付きでは列挙なし |
| 単独 `/home/ryo/.codex/skills/extrip-to-ics` | bare名でcatalogに存在。helper/schema/UIは一致、entrypointは旧test commandを含み不一致 |

従って、public6skillのうちfigure creation/export/reportの3つはこの会話の一覧に現れず、travelは別copyから利用可能である。
sourceからcatalogまでの原因箇所やfresh sessionでの挙動は未確定（D-001）。
同じplugin version文字列が内容同一性を保証していない。
vendor cacheや配布先を変更してこの差を解消する操作は行っていない。

## 7. 保存すべき契約

- reviewと変更の権限境界、source・user edits・成功済み成果物の保全。
- 保存値・条件・統計量・normalizationを表示変更から分離すること、およびhashと数値正しさを区別すること。
- affected setだけの検証、入力・tree・環境が同じ場合の証拠再利用、依存箇所だけの保留。
- raw latexdiff不変、全文範囲とbuild整合・目視を別々に検証すること。
- editable bundleのlocal dependencies、無損失CSV、抽出履歴と現在値・新検証の分離。
- 本文・図・配布の責任分担と、参考資料の読込をworkflow起動と同一視しないこと。
- 予約原文・未確定情報の維持、checkout日を含む既定、stable UID、無断importしないこと。
- deployment/install/Git/external writesの追加権限をskillが与えないこと。

## 8. 定量指標

値は初回snapshotでの実測であり、`stage1/` を含めない。

| 対象 | text files | bytes | lines | 概算tokens相当 |
| --- | ---: | ---: | ---: | ---: |
| figure creation/edit | 3 | 30,018 | 318 | 7,505 |
| arXiv | 3 | 14,567 | 314 | 3,642 |
| dotfiles | 1 | 1,970 | 30 | 493 |
| figure export | 3 | 16,471 | 230 | 4,118 |
| travel | 4 | 11,676 | 227 | 2,919 |
| research report | 3 | 23,295 | 223 | 5,824 |
| 合計 | 17 | 97,997 | 1,342 | 24,500 |

概算は `ceil(UTF-8 bytes / 4)` という比較用heuristicで、encoderによる測定ではない。
日本語・codeの実tokensには大きな誤差があり、実行costや毎回のcontext投入量を示さない。
全6 entrypointは234行 / 17,734 bytes、8 referenceは742行 / 66,319 bytes、Pythonは362行 / 13,632 bytes、YAMLは4行 / 312 bytes。
descriptionは計1,324 bytes。最長entrypointは50行で、最長referenceはpresentationの211行 / 20,277 bytes。
`tiktoken` は未導入で、正確なtokens・tool cost・LLM latencyは測っていない。
既存bytecode 1件10,097 bytesを含む物理file数は18、総量108,094 bytes。
bytecodeのheaderはCPython 3.12 timestamp式、元source size 7,223で、現source 7,907 bytesとは異なる。
このcacheはignoredであり、削除・更新していない。実行時は `-B` / `PYTHONDONTWRITEBYTECODE=1` を用いた。

### file別snapshot

下表のSHA-256は後日の同一性確認用であり、内容の意味を証明するものではない。

| 相対パス | bytes | lines | SHA-256 |
| --- | ---: | ---: | --- |
| `creating-and-editing-typst-figures/SKILL.md` | 3182 | 42 | `cf0f3a744426303469a4ac807925c3ce2e9db856564c0f9fba4134bae6137435` |
| `creating-and-editing-typst-figures/references/data-and-verification.md` | 6559 | 65 | `c589db9978315f5f48f895168e135aa89c4ec2df92c4606354a4d87891877fdb` |
| `creating-and-editing-typst-figures/references/presentation-and-layout.md` | 20277 | 211 | `40f798cb7f273d19a74da791683af50baba6a9d26f3b0a80aa3e56eb7aa70b04` |
| `creating-arxiv-diff-pdfs/SKILL.md` | 2396 | 29 | `9d5ce09c2028c9698b1ddb9c2d7c949c61b5c7be4d2b9fef2d171177d585740c` |
| `creating-arxiv-diff-pdfs/references/revtex-latexdiff-troubleshooting.md` | 4264 | 50 | `9b21ea50446588432054af1b002d25b94e3346a1804056baaed43bcc66b1aefd` |
| `creating-arxiv-diff-pdfs/scripts/__pycache__/verify_diff_pdf.cpython-312.pyc` | 10097 | binary | `bb91c96748f7e97456507849e234623ec5af58cf7e6da1a3eb8ab751e96f69db` |
| `creating-arxiv-diff-pdfs/scripts/verify_diff_pdf.py` | 7907 | 235 | `630dced7984395e93f831eb01258cf9b482f8f290da9c958a95b8ddff14b32e1` |
| `dotfiles-deploy/SKILL.md` | 1970 | 30 | `b842c242776534e188700961a900cf985720b8e3fbd796c37ad0ae377a67ce3d` |
| `export-editable-typst-figures/SKILL.md` | 3541 | 43 | `8150bcb2c461098d0334225c603e145ecb882fafa52e348e3262852222c5c19e` |
| `export-editable-typst-figures/references/data-and-provenance.md` | 7801 | 84 | `08f73002ab04e1195630e4334f0dfd188346decd90d5af85124c91496ad80145` |
| `export-editable-typst-figures/references/provenance-examples.md` | 5129 | 103 | `310c3c3712319e70f22874cca8c2eae09e789bc79c32e574299e22694ab9dab1` |
| `extrip-to-ics/SKILL.md` | 3452 | 50 | `39ebd739ca47b0ec945e40ea2d513a56fa1026e24270f894aa6457a8cf54f450` |
| `extrip-to-ics/agents/openai.yaml` | 312 | 4 | `db202ca67d2456d5ac2ca77fe198dc55ba599d01af60fb58c1aa8934b193cc2b` |
| `extrip-to-ics/references/events-schema.md` | 2187 | 46 | `eb113e1983e5f469ce4065d52a7c3e04a6cabc1df78a53a2539a406a0098301b` |
| `extrip-to-ics/scripts/build_ics.py` | 5725 | 127 | `11a1fe2048cef61610cb419faa87431d468cc0c20deba6eca021c7ab4533d0a5` |
| `writing-typst-research-reports/SKILL.md` | 3193 | 40 | `9ee906754251beea61dd868cb48661cb561b1e512c053a010047481f7835d061` |
| `writing-typst-research-reports/references/report-composition.md` | 9063 | 78 | `6914b1410ae843c5abb3dec8f41f87198a2d439bd377419a29642eaa04510cd9` |
| `writing-typst-research-reports/references/writing-and-tables.md` | 11039 | 105 | `a288d096f485815addaa4813621c8a5e02bdefa84b94f5da660a52868290abb0` |

SHA-256と2 spacesとpathとLFを上表順に連結したmanifestのSHA-256は `294c4350ee01364370d126647f9b2dffd92aed48201eca5109de90366b078bf4`。
全18fileは通常file、初回modeは `0664`。symlinkはなかった。
Git上のtracked sourceは17fileで、内容はHEADと一致していた。

## 9. 曖昧さと証拠の限界

直近historyでは `a3f1c6d` がTypstの責任を分割し、`3766008` がarXivの不完全build拒否、`4a83fa9` がtravel配布と通常testを修正している。
plugin README:75-99の2026-10-18監査は自らhistorical baselineと明記しており、現在の5skill inventoryとは扱わない。
過去のfigure-export reviewは「実bundle実行未検証」として調査観点にのみ利用し、今回の合格証拠に流用していない。

現行選択性能、workflow全体の完了率、実際の過剰確認・停止・tool数は未測定である。
display方針の適用範囲（一般的なscientific diagramを含むか）、arXivの未指定commandと必須完了範囲、output symlinkの許容運用は仕様が十分に確定していない。
実研究data・公式arXivの2版・実予約・remote hostを使うend-to-end試験はしていない。
Stage 2への判断事項は [04_handoff.md](04_handoff.md) に分離した。
