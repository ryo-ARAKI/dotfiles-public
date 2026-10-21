# baselineと評価仕様

## 1. 環境・評価の単位

監査版は [01_inventory.md](01_inventory.md) §1/§8のHEAD・18file hashで固定する。
以下のP/N/B系列は独立したCodex実行に渡す**設計済みprompt**であり、今回の会話内読込やPython実行をskill invocationの成功と数えない。
E系列は**実際に実行した構造・helper・環境検査**である。
実測時間は1回分のみで、speedup、cost優位、安定した性能分布は評価できない。

| 項目 | 実測・公開された情報 |
| --- | --- |
| OS / shell | Linux、実行shellはBash。下記ユーザー向けcommandはfishでも使える形 |
| Python | 3.12.3、PyYAMLあり、`tiktoken` なし |
| Codex CLI | 0.163.0。help/versionのみ実行。PATH alias作成のread-only warningあり、help/version自体はexit 0 |
| 本監査model | GPT-6系Codexとの識別のみ。実際のmodel ID、normal/planning effortはこの会話の公開metadataから確定不能 |
| 独立評価model | 未起動。CLIのdefault/configured modelを本監査のmodelと同一視しない |
| Typst | 0.15.1、既存cacheのLilaq 0.6.0を使用 |
| TeX | pdfTeX 1.40.25、TeX Live 2023/Debian、latexdiff 1.3.2は存在確認のみ |
| PDF tools | Poppler 24.02.0 (`pdfinfo`, `pdftoppm`)、qpdf 11.9.0 |
| Git | 2.43.0 |
| FS境界 | sourceはread-only運用、試験出力は新規 `/tmp`、公開物は4監査文書のみ |
| network / external writes | 公式skill仕様のweb readのみ。予約・実研究dataを送信せず、API認証、Calendar登録、SSH/deployはしない |

OpenAI公式の[Build skills](https://learn.chatgpt.com/docs/build-skills)（2026-10-21参照）はmetadataで候補を発見し、選択後に `SKILL.md` を読む仕組みと、explicit/implicitの区別を説明している。
そのためファイルを監査sessionで読んだことはimplicit discoveryの証拠にならない。
`agents/openai.yaml` はoptionalであり、他5skillにないこと自体は欠陥ではない。
今回referenceに使った `skill-creator` の `quick_validate.py` はfrontmatter/name/placeholderの静的checkで、decision品質や正確な選択を保証しない。

## 2. 再利用するfixture仕様

各LLM runは新しいdisposable workspace、同じinput bytes、同じtools/fonts/package cache、同じauthorityとtime budgetを使う。
次のfixtureは**今後のend-to-end評価用に設計した仕様**であり、今回すべてを生成・実行したという意味ではない。
Stage 2で固定してから、変更前・変更後を同じ条件で取得する。

| fixture | 最小入力と固定内容 | 比較で保存するもの |
| --- | --- | --- |
| F-dotfiles | managed source/base-private-host、fake HOMEと既存無関係設定。installerは一時copyへ向ける | 選択target、layer順、候補、unrelated値とlive byte不変、無断applyなし |
| F-arxiv | 公式の同一paperの2version archive、download URL/hash、main TeXと既存baseline、指定latexdiff command | archive/raw diff hash、exact command、source coverage、full PDF、final log、images |
| F-figure | `values.csv` の下表、既存`.typ`/条件・normalization、既存全図/selected output、保存input hash | 各condition tuple/multiplicityとinterval端、series/legend、変更前後のdata、受領size |
| F-bundle | F-figureのreport invocationと依存一式、source revision、読み出しpath、recipient最小文書 | 元rendering、bundle dependency list、CSV cell string、移設/外cwd/spaced output、recipient inclusion |
| F-report | F-figureと同じ数値、既存template、本文の誤った全称主張、既存図とcaption | 主張と数値の対応、限定条件、最新user edits、template、PDF全page/standalone |
| F-travel | 合成Markdown2旅行。年越し往復、複数ホテル、未確定列車を含む。実予約番号は使わない | 原文bytes、レビュー済みJSON、event対応、fold/escape、offset、checkout日、Maps/UID |

F-figure/F-report用の合成保存値案（実験結果ではない）:

```csv
method,tau,rmse,sd,mean_deviation,low,high
A,1,2.0,1.6,1.2,1.8,2.2
B,1,1.5,1.2,0.9,1.3,1.7
A,2,1.0,0.8,0.6,0.8,1.2
B,2,1.1,0.88,0.66,0.9,1.3
```

全値を無次元の保存値とし、`low/high` は既存のinterval endpointsと定義する。
区間の生成方法・確率的coverageは推定しない。
「Bは全条件でRMSEが小さい」はtau=2で成立しないが、局所反例だけで他条件の比較を棄却しない。
P-03/B-01は既存sourceのfont変更のみで、new intervalを生成しない。
実研究dataを使う場合はこの合成fixtureと混ぜず、同一性・利用許可・匿名化を別に管理する。

## 3. 正例6件: exact user promptと受入基準

### P-01 / Positive / W-01

> 指定したsource worktreeとprivate・host overlayから、fake HOME内のfish設定だけの候補を生成し、差分とdry-runを確認してください。apply、SSH、service reloadは行わないでください。

期待selection: `dotfiles-deploy`。explicit版は先頭に `$dotfiles-deploy を使って、` を付けた同一依頼とする。
期待動作・出力: 選択source/layer/targetの確認、生成候補、既存値との差分とscope。
受入: fake HOME外の変化なし、無関係な設定保全、生成を反映済みと誤報しない、追加のapply承認を求めて完了を止めない。
前提: F-dotfilesと一時destinationへ安全に向けられるinstaller。
リスク: live targetやSSHに誤接続しないよう権限で隔離。repo外全体のdeploy testに拡大しない。

### P-02 / Positive / W-02

> 添付fixtureの公式arXiv source v1/v2を、指定command `latexdiff --type=CFONT old/main.tex new/main.tex` で比較し、全文の差分PDFを作成してください。raw出力を保持し、必要な互換修正、本文・bibliography・appendixの範囲、検証結果を示してください。

期待selection: `creating-arxiv-diff-pdfs`。explicit版は同名の `$... を使って、` を付ける。
期待動作: source provenanceと元版baseline、raw/checksum、isolated build、故障時のみtroubleshooting、全文coverage、helper、first/middle/last目視。
受入: command/raw不変、必要な全section/bib/appendixが存在、log/PDF一致、構造成功、画像の実inspection。upstreamの科学計算再現を要求しない。
前提: F-arxiv、既存engine/packages/fonts、必要なPDF tools。downloadなしでfixtureだけを使用する。
リスク: untrusted TeXのshell executionを禁止し、専用sandboxとtimeoutを使う。必要package未導入時は未実行/環境制約として扱う。

### P-03 / Positive / W-03

> F-figureの既存Typst図のtext・math・tick fontを指定のインストール済みfontへ変更してください。保存済みdata、条件、normalization、点と区間端を保ち、必要な出力だけ再生成して受領サイズで確認してください。bundle化と科学的再計算は不要です。

期待selection: `creating-and-editing-typst-figures`。
期待reference: data/update、layoutのfont/appearanceと該当check。storage/relocationの全工程は不要。
受入: data hashとcondition tuple/multiplicity維持、font適用の実render確認、affected出力をすべて検証。成功旧出力を失敗candidateで上書きしない。
前提: F-figure、同一Typst/packages/fontsとbaseline。
リスク: font不足を勝手にinstallせず、temp候補で生成する。

### P-04 / Positive / W-04

> F-bundleのreportから指定図を、別の場所でも編集・compileできる配布copyへ抽出してください。見た目と全dataを保持し、必要なhelperと来歴を添え、移設先およびrecipient最小文書で検証してください。

期待selection: `export-editable-typst-figures`。必要なcommon data contractだけを併用。
受入: source/data/settings/helpers完備、repo symlink不要、元appearance一致、relocation compile、対応formatでrecipient inclusion、履歴/current/verification分離。
前提: F-bundle、authoritative rendering、元source/revisionとrecipient環境。
リスク: 元repoを変更しない。recipient本体へcopyするのはこのfixtureで許可した場所だけ。包括repo testや再simulationを始めない。

### P-05 / Positive / W-05

> F-reportの本文とcaptionを保存済み結果に基づいて改訂してください。「方法Bは全条件でRMSEが小さい」という主張の範囲、RMSE・SD・mean deviationの区別、図と本文の対応を確認し、既存templateを保ってPDFを検証してください。新しい推定や区間生成は行わないでください。

期待selection: `writing-typst-research-reports`。既存図をそのまま使う限り他2skillは起動不要。
受入: tau=2の逆転を検証証拠に残し支持範囲へ限定、機構を捏造せず、質問への回答と代表値を明確にする。template/standalone保全、影響pageを目視。
前提: F-report、定義と保存値、既存PDF/plot source、Typst/PDF tools。
リスク: userが削った記述を旧planだけで復活させない。compile不能なら旧PDF維持。

### P-06 / Positive / W-06

> F-travelの2旅行のMarkdownから、旅行別と一括のICSを専用outputへ作成してください。年越し・深夜着・複数ホテルと未確定列車を原文どおりに扱い、宿泊はcheckout日も含む終日予定とし、出発駅とホテルのMapsリンクを付けてください。Calendarへの登録はしないでください。

期待selection: `extrip-to-ics`。独立比較ではplugin版か単独版かpath/hashを必ず記録する。
期待動作: 原文全読込、reviewed JSON、helper、unfold後の照合、ファイルリンクと件数。
受入: 1列車/1滞在1event、日時/年/offset/未確定表示正確、原文不変、UTF-8/CRLF/75-octet folding/escape、stable UID。API/auth/自動importなし。
前提: F-travel、Python 3.10+。必要日時不明caseは該当eventの確認が必要で、推測しない。
リスク: 実予約個人情報を使わず、専用directory。overwrite失敗・symlinkはE-004/E-005で別評価する。

## 4. 負例3件と境界例3件

| ID / 区分 | exact user prompt | 期待selection・動作・出力・受入 | 前提 / execution risk |
| --- | --- | --- | --- |
| N-01 Negative | `このfish設定sourceをread-onlyでレビューし、気になる点を行番号付きで報告してください。生成やdeploymentは依頼していません。` | public群では選択なし。通常review findingsのみ。installer/dry-run/applyの不要起動、source変更、追加確認なし | 一時fish source。config reviewをdeploymentへ拡大するリスク |
| N-02 Negative | `この一般向けMarkdownの日本語の誤字だけを指摘してください。Typst化、図表、研究内容の変更は不要です。` | public群では選択なし。誤字指摘のみ。report/figure workflow、compile、PDF生成なし | 合成Markdownのみ。文書種類の誤認リスク |
| N-03 Negative | `既存Google Calendarの明日の会議予定をread-onlyで一覧にしてください。予約Markdownの変換やICS作成は不要です。` | public群では選択なし。権限のある別手段があればread、なければ接続不足を明示。ICSや認証変更を勝手に行わない | 実account不要。接続を仮想mockで代用して実結果としない。誤ったexternal操作リスク |
| B-01 Boundary / W-03,W-04 | `既存editable bundleの図のfontだけを変え、配布済みの該当PDFを検証してください。source構成・path・来歴schema・dataは変更不要です。` | figure creation/editを主選択。bundleの存在だけで再抽出・relocation・upstream全調査をしない。実施済みcheckだけ記録 | F-bundleのcopy。既存source/data/record保全、fontのみのaffected set |
| B-02 Boundary / W-03 review | `このstandalone Typst図をread-onlyでレビューし、保存値と表示点・区間端・legendの対応を確認してください。sourceや成果物は変更しないでください。` | 意図仕様候補はfigure creation/editのreview mode。正しいownerはStage 2確認事項。findingsのみ、変更なし | F-figure。D-004のimplicit偽陰性は未実測。reviewを実装へ変えない |
| B-03 Boundary / W-05 | `既存図PDFをそのまま使い、研究報告のcaptionと配置だけを調整してください。図のsource、bundle、データには変更不要です。` | reportのみ。必要なreceiving size、caption、後続pageを検証。図再生成・抽出・relocationなし | F-report。caption参照定義がない時は依存部分だけ保留 |

すべて現在は「設計済み・未実行」である。
E系列が一部のhelper contractを裏付けても、上記exact promptへのmodel応答を実行したことにはならない。

## 5. 明示・暗黙・skill-disabled比較の手順

1. managed sourceを固定したprivate fixture copyを用意し、6skillと必要な兄弟referenceが同じhashで発見できる独立catalogを作る。source/cache/catalogの面を記録する。
2. P/B各caseを、明示 `$skill-name`、skill名なしの暗黙prompt、当該public群を無効化したcontrol、のfresh contextで実行する。明示版はpromptに接頭辞を付ける以外同一。N系列は暗黙とcontrolを主比較とする。
3. AGENTS、authority、model ID、normal/planning effort、tools、input tree、timeout、font/packageを固定する。controlには同名単独skillやrouter経由の実質再読込がないことを確認する。
4. transcriptを保存し、selected path/hash、実際に読んだreference、tool数、許可内action、出力受入、確認・停止理由を独立に採点する。ファイル一覧を表示しただけのreadはselectionと区別する。
5. 利用可能ならtoken/時間/costを実測。modelの自己申告をusage測定に代用しない。可能なら各条件3回以上、無理なら1回のcase studyとして扱う。

判定は `Executed and passed / Executed and failed / Inconclusive / Designed but unexecuted` を使う。
受入は正しい出力、input保全、authority、必須検証と説明の正確さを中心にし、文章のheadingや固定tool数への一致だけでは採点しない。
安全を保つため不要な行動が拒否された場合、runner failure、command failure、content failureを分ける。

今回CLIは存在し、`--ephemeral` / read-only等のoptionsもhelpで確認できたが、独立評価を実行していない。
現sessionは対象catalogが揃わず、skill-disabled controlと同一条件のclean contextを構成・検証していない。
この条件のままLLMを起動して得る応答はsource版のselection試験として採用できないため、task/subagentの起動やuser config変更で解決せず未実行とした。
これは「CLIが未導入」「認証が失敗した」「自動選択が失敗した」という結果ではない。
独立実行方式と必要なauthorityはStage 2で確定する。

## 6. 実際の実行結果

| ID | 検査 | 状態 | 観測とscope |
| --- | --- | --- | --- |
| E-001 | 6skillの `quick_validate.py`、local link/anchor | Executed and passed | 6/6 `Skill is valid!`。46 link occurrence、28 unique edge、broken 0。selection品質は未検証 |
| E-002 | 既存関連unit/distribution tests | Executed and passed（文書作成前） | 3+7+12=22testすべて成功。arXiv CLI testはfake toolsを使用し、real renderingの証拠ではない |
| E-003 | 合成3page TeX→real verifier→PNG目視 | Executed and passed | pdfTeX、pdfinfo、qpdf、pdftoppmは実tool。3/3page、fatal 0、warnings 0、各exit 0。first/middle/lastの画像をすべて開いて確認 |
| E-004 | travel上書き中の後続write failure | Executed and failed（旧集合の保全基準に対して） | `IsADirectoryError`、先行file変更=true、一括旧file保全=true。D-002。probe実行自体は正常に観測を記録 |
| E-005 | travel output symlink | Executed and failed（output directory内に限定する基準に対して） | symlink維持=true、directory外sentinel変更=true。D-003。許容link policyは未確定 |
| E-006 | 記載Typst fragmentのsyntax/import | Executed and passed（限定scope） | Typst 0.15.1＋既存Lilaq 0.6.0でcompile exit 0。換算・metadata・show wrapperを構文確認。tick fontの見え方や科学図全体は未検証 |
| E-007 | source/deployed/cache/catalog同一性 | Executed（不一致を確認） | 01 §6。fresh invocation結果ではなく観測された環境baseline |
| E-008 | 監査文書追加後のdistribution suite | Executed and failed（manifest完全一致1件） | 3件中2成功・1失敗。追加4監査文書のみがmanifest集合との差。元payload欠落・既存file変更ではない |
| E-009 | 監査前後のsource・Git状態 | Executed and passed | 初回18fileのbytes/hash/modeを保全、HEAD/index/既存dirty状態を維持。追加は指定4文書のみ |

E-003の目視所見: page1 `Question`、page2 `Evidence`、page3 `Conclusion` と対応する本文・page番号が読め、欠落・clipなし。
これは意図的に疎な合成3page文書であり、実研究報告の密度やarXiv diffのcoverage/markupを検証したものではない。
既存unit testsがmock PDF/PNGを用いる事実を失敗とは扱わず、その保証scopeを限定した。

E-002のtest run時間（unittest表示 / subprocess wall、単回実測）:

| module | tests | unittest秒 | wall秒 | exit |
| --- | ---: | ---: | ---: | ---: |
| `test_ryo_workflows_plugin.py` | 3 | 0.013 | 0.061971 | 0 |
| `test_extrip_to_ics.py` | 7 | 0.030 | 0.072787 | 0 |
| `test_arxiv_diff_pdf_verifier.py` | 12 | 0.332 | 0.369264 | 0 |

E-003: pdflatex 0.257113秒、verifier 0.219371秒。E-006: Typst compile 0.306144秒。
時間差は1回のrunner条件に依存し、LLM workflowの速さとは関係しない。
root既定の `python` はなく、最初のsnapshot取得がexit 127となったため `python3` に切り替えた。
target commandの不具合やrunner起動失敗ではなく、skillも `python3` を指定しているのでfindingにはしない。

## 7. 再現commandと記録

source rootを `SOURCE`、repo rootを `REPO` とする。
以下はfish対応の例で、実際の試験は同じ引数をPython subprocess/Bashから呼んだ。
bytecodeを作らず、tests内でdestinationが `/tmp` に差し替わることを先に確認する。

```fish
set REPO /home/ryo/github/dotfiles-public
set SOURCE $REPO/config/codex/plugins/ryo-workflows/skills
cd $REPO
env PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p test_ryo_workflows_plugin.py -v
env PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p test_extrip_to_ics.py -v
env PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p test_arxiv_diff_pdf_verifier.py -v
for skill in creating-and-editing-typst-figures creating-arxiv-diff-pdfs dotfiles-deploy export-editable-typst-figures extrip-to-ics writing-typst-research-reports
    python3 -B /home/ryo/.codex/skills/.system/skill-creator/scripts/quick_validate.py $SOURCE/$skill
end
```

E-008により、現checkoutで最初のdistribution commandを再実行すると監査文書分の1件が失敗する。
E-002の元baselineを再現する場合は、上記HEADをdisposable copyへ展開し、監査文書を持ち込まずに実行する。
元checkoutの監査文書を削除したり、manifestへ監査文書を加えて合格に見せたりしない。

今回のtemporary evidence（永続保存の保証なし）:

```text
/tmp/codex-stage1-source-snapshot.json
/tmp/codex-stage1-initial-tests.json
/tmp/codex-stage1-test_ryo_workflows_plugin.py.log
/tmp/codex-stage1-test_extrip_to_ics.py.log
/tmp/codex-stage1-test_arxiv_diff_pdf_verifier.py.log
/tmp/codex-stage1-versions.json
/tmp/codex-stage1-links.json
/tmp/codex-stage1-absolute-rules.json
/tmp/codex-stage1-probes-bfx_ojbm/results.json
/tmp/codex-stage1-probes-bfx_ojbm/real-verification/verification.json
```

temporary evidenceがなくても再試験できるよう、追加probeの実際のsourceを以下に保存する。
例として一時ファイル `/tmp/stage1-probes.py` へ取り出し、`env PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/stage1-probes.py $SOURCE` で実行する。
helper implementationではなく監査用fixture runnerであり、Stage 1でskillを改修していない。
実行前にLilaq 0.6.0が既存cacheにあることを確認し、ない場合はE-006をskipして未実行理由を記録する。試験のためにpackageを導入しない。
fixtureはすべて新規 `/tmp` 配下へ作り、既存source・live成果物・実予約を使わない。

```python
"""Stage 1 probes. Writes only into a newly allocated /tmp directory."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

SOURCE = Path(sys.argv[1]).resolve()
RUN = Path(tempfile.mkdtemp(prefix="codex-stage1-probes-", dir="/tmp"))
RESULTS = []

def load(relative):
    spec = importlib.util.spec_from_file_location(Path(relative).stem, SOURCE / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def command(args, cwd, name):
    before = time.perf_counter()
    p = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=40)
    (RUN / (name + ".log")).write_text(p.stdout + p.stderr)
    return {"command": args, "returncode": p.returncode,
            "seconds": round(time.perf_counter() - before, 6)}

def event(group, title):
    return dict(id=group, group=group, summary=title, description="合成予約・実在予約ではない",
                source="synthetic.md", map_query="東京駅",
                start="2026-12-31T23:50:00+09:00", end="2027-01-01T01:10:00+09:00",
                all_day=False)

ics = load("extrip-to-ics/scripts/build_ics.py")
# A later output error must be distinguished from validation-before-write protection.
out = RUN / "partial-output"
out.mkdir()
items = [event("a", "new-a"), event("b", "new-b")]
old_a = ics.calendar([event("a", "old-a")]).encode()
old_combined = ics.calendar([event("a", "old-a"), event("b", "old-b")]).encode()
(out / "a.ics").write_bytes(old_a)
(out / "trips.ics").write_bytes(old_combined)
(out / "b.ics").mkdir()
try:
    ics.generate(items, out, overwrite=True)
    error = None
except OSError as exc:
    error = type(exc).__name__
RESULTS.append(dict(id="E-004", error=error,
                    first_output_changed=(out / "a.ics").read_bytes() != old_a,
                    combined_preserved=(out / "trips.ics").read_bytes() == old_combined))

# Both ends of this symlink are disposable, synthetic files under RUN.
out = RUN / "symlink-output"
out.mkdir()
outside = RUN / "outside-output-sentinel.ics"
outside.write_bytes(b"synthetic sentinel\n")
(out / "a.ics").symlink_to(outside)
ics.generate([event("a", "redirected")], out, overwrite=True)
RESULTS.append(dict(id="E-005", symlink_preserved=(out / "a.ics").is_symlink(),
                    outside_output_changed=outside.read_bytes() != b"synthetic sentinel\n"))

# Real tools, synthetic TeX: this is not an official-arXiv workflow test.
tex = RUN / "tex"
tex.mkdir()
document = "\\documentclass{article}\n\\begin{document}\n"
document += "\\section{Question}Synthetic baseline page one.\n\\newpage\n"
document += "\\section{Evidence}Synthetic baseline page two.\n\\newpage\n"
document += "\\section{Conclusion}Synthetic baseline page three.\n\\end{document}\n"
(tex / "candidate.tex").write_text(document)
build = command(["pdflatex", "-no-shell-escape", "-interaction=nonstopmode",
                 "-halt-on-error", "candidate.tex"], tex, "real-tex")
verify = None
report = None
if build["returncode"] == 0:
    verify = command([sys.executable, "-B", str(SOURCE / "creating-arxiv-diff-pdfs/scripts/verify_diff_pdf.py"),
                      "--pdf", str(tex / "candidate.pdf"), "--log", str(tex / "candidate.log"),
                      "--output-dir", str(RUN / "real-verification")], tex, "real-verifier")
    report = json.loads((RUN / "real-verification/verification.json").read_text())
RESULTS.append(dict(id="E-003", build=build, verifier=verify, report=report))

# Compile the documented Typst fragments with the already-cached Lilaq package.
typ = RUN / "typst"
typ.mkdir()
fragment = '''#import "@preview/lilaq:0.6.0" as lq
#show: lq.show_(lq.tick-label, it => text(font: "New Computer Modern Math")[#it])
#let to-display(y) = y / 1000
#let raw-y = (1000, 2000)
#let display-y = raw-y.map(to-display)
#let y-ticks = raw-y.map(y => (to-display(y), [#to-display(y)]))
#let y-limits = (0, 3000).map(to-display)
#let conditions = ((label: [A], filename: "panel-a.pdf"), (label: [B], filename: "panel-b.pdf"))
#let panel-export-map = conditions.enumerate().map(((i, condition)) => (selector: i + 1, condition: condition))
#metadata(panel-export-map) <panel-export-map>
Synthetic fragment check: #repr((display-y, y-ticks, y-limits))
'''
(typ / "fragment.typ").write_text(fragment)
compile_result = command(["typst", "compile", "fragment.typ", "fragment.pdf"], typ, "typst-fragments")
RESULTS.append(dict(id="E-006", compile=compile_result,
                    scope="Documented fragment syntax/import only; no plot or tick-font visual validation"))

result = dict(source=str(SOURCE), temporary_root=str(RUN), results=RESULTS)
(RUN / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
Path("/tmp/codex-stage1-probe-location.txt").write_text(str(RUN))
print(json.dumps(result, ensure_ascii=False, indent=2))
```

## 8. 未実行・不確定な評価

| 評価 | 状態 | 理由・次に必要なもの |
| --- | --- | --- |
| P/N/B全12caseの明示・暗黙・無skill比較 | Designed but unexecuted | sourceと一致する独立catalog、controlの隔離、model/effortを記録したfresh runが未構成 |
| auto選択のprecision/recall、正しいreferenceのload率 | 未測定 | 監査session内読込では測れない。negative/boundaryを含む独立transcriptが必要 |
| LLM token/tool/cost/確認回数 | 未測定 | 独立LLM runなし。01のB/4 heuristicは実行usageではない |
| 公式arXiv sourceからの全文diff、REVTeX/natbib修復 | 未実行 | 指定された公式2版fixtureとexact commandがない。合成TeXを公式source試験としない |
| 実研究図のdata対応・bundle移設・recipient inclusion・report全page | 未実行 | 対象研究sourceと受入要件が未提供。断片compileで代用しない |
| Markdownからの旅行情報抽出・Google import | 前者未実行、後者scope外 | helperはJSONからの変換のみ確認。実account書込はしない |
| live/remote dotfiles dry-run/apply/reload | 未実行 | 対象host/targetへの具体的許可はこの監査に含まれない。temp installer copy testのみ |
| 外部悪性dataに対する総合security、symlink race、disk fullからの復旧 | 一部のみ | E-005は単純link、E-004は後続directory error。全攻撃/全I/O faultを再現していない |

## 9. Stage 3への比較条件

E-001/002/003/006/009で今通る契約を保ち、D-002の失敗fixture、D-003のlink fixtureには人が確定したpolicyを適用する。
P/N/Bは今回の実測baselineがないため、Stage 3だけ実行しても「改善率」や過去比の成功を主張できない。
構造変更前に同じfixture・model・runtimeで旧版のrunを追加取得するか、before不在を明示したafter評価にする。
input・tree・material environmentが不変の成功証拠は再利用し、変更が影響するscopeだけ再実行する。
4文書の存在を理由とするE-008を、source skillの性能低下に混ぜない。
