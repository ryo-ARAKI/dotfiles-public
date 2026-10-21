# Stage 2: 検証計画

## 1. 評価環境

検証の状態は `Designed but unexecuted`、`Executed and passed`、`Executed and failed`、`Inconclusive` で記録する。
設計済みcaseや環境確認を、LLM invocationの合格へ数えない。
安全性・scope・出力品質を優先し、文言一致・行数・固定tool数を成功条件にしない。

| 項目 | Stage 2で確認したこと | 今後の固定条件 |
| --- | --- | --- |
| source | HEAD `737ba2926d72ad51dccfc0cf6b26cd4d2994a44d`、tracked差分なし、Stage 1の18hash一致 | before / afterのfull revisionとdirty input hash |
| OS / shell | Linux、実行Bash | 同じrunner image / OS、tool shell |
| Python / Git | Python 3.12.3、Git 2.43.0 | helperの最低互換Python 3.10+と、主比較の同じPython |
| CLI | `codex-cli 0.163.0`、help/versionのみ。PATH alias作成のread-only warningあり、commandはexit 0 | 同じbinary/version、resolved config、client種別 |
| 今回のmodel | 正確なmodel ID / normal / planning effortを公開metadataから確定できない | 独立runではrequestとruntimeのeffective identityを記録 |
| 独立LLM | **未起動、0 run** | 推奨候補 `gpt-6.1-sol`、normal `xhigh`、planning `max`。可用性と予算を承認後固定 |
| TeX / Typst / PDF tools | Stage 1のversionと成功証拠を参照。Stage 2で再compile・目視はしていない | TeX engine/packages、Typst、Lilaq、fonts、Poppler/qpdfのversionとcacheを固定 |
| 実行範囲 | disposable fixtureは `/tmp/ryo-workflows-stage2-8tu8suhp/`、全入力は合成またはtracked source copy | 1 case / mode / repeatにつき別workspace。出力・backup・cacheはrunner所有 |
| 外部操作 | 公式文書readのみ。model API、実予約送信、Calendar、SSH、deployment、installなし | 外部write禁止。model通信は承認されたfixtureとbudgetのみ |

CLIの `exec --help` で `--ephemeral`、`--json`、`--ignore-user-config`、`--model`、`--sandbox`、`--cd` を確認した。
`--ignore-user-config` の説明はuser configを読まないことであり、authは `CODEX_HOME` を使うと明記されている。
これはuser/admin/system skills、router、plugin、親directoryのinstructionsまで除外できた証拠ではない。
`/home/ryo/.agents/skills` と `/home/ryo/.codex/skills` が存在する。
`bwrap` はPATHにあるが、今回専用namespace runnerの構築・動作確認はしていない。
隔離不能や認証失敗を実測した、とも報告しない。

**結論: 現在のactive設定を変えずに、target版とdisabled controlの独立性を証明したLLM実行環境は確立していない。**
R-007で専用runner、認証の供給方法、model/effort、予算を確定する。
既存の安全な別user/containerが使える場合はそれを優先し、その通常homeで実行する。
hostの `HOME` / `CODEX_HOME` を書き換えたり、active authをfixtureへ複製したりしない。
runnerを新設するための環境導入・mount・認証・network権限は必要に応じて別承認とする。

## 2. sourceとruntime identityの検証

T-001の外部manifestはplugin-relative path順の `SHA256  path\n` をUTF-8で連結してhash化する。
内容とmode/typeは別項目にする。
public payloadは17 skill resource＋README＋metadataの19fileであり、現content manifest IDは `c151389fc6ffe21c12624ce7db6f2f024fe0b27912e0d1c76317528d0aaa162c`。
監査資料とbytecodeは含めず、未知fileは無視せず別検出する。
metadata versionは現 `0.1.0+codex.20260912054231` だが、同じ文字列で異なるbytesがある。

| 層 | 採る証拠 | 成功判定 |
| --- | --- | --- |
| managed source | HEAD、status、実bytes、manifest entry、overlay origin | 期待copyを再構成できる |
| isolated deployed copy | 全payload hash/mode/type、reference解決 | sourceと一致。許可overlayだけを明示差分として許す |
| installed cache | observed実pathと同じmanifest | cache内resourceがexpected copyと一致 |
| session catalog | 新規contextの全name/description/path、対象・同名・routerの可視性 | treatmentでは6入口が正しいpathから可視、controlでは同等の入口なし |
| actual load | `SKILL.md` / reference read、helper実行path、対応するimmutable hash | 対象runtimeで実際に使った版がsourceと一致 |

catalogは対応clientのskill selector、またはinstalled app-server schemaで確認できた `skills/list` 相当のAPIから採る。
存在未確認のCLI flagやJSON fieldを仮定してrunnerを書かない。
CLI JSONLが必要なreadやcatalogを露出しない場合は、独立したtool監査記録を用意するかroutingを `Inconclusive` とする。
modelの自己申告したskill名/pathだけをselectionの証拠にしない。
before / afterでsource pathが変わる時はrunner内の同じ論理pathへ供給し、path名から処置条件が漏れないようにする。

手順は診断、固定sourceの試験、managed配布、supported cache更新、fresh sessionの実load確認を別phaseとして記録する。
Stage 2のread-only比較でD-001が再確認できても、active環境への修復完了とはしない。
公式根拠とsource/runtimeの責任分離は[設計案D-001](01_design_options.md#d-001)を参照する。

## 3. Stage 1の12 LLM caseのreview

exact promptは[Stage 1 baseline §3–4](../stage1/03_baseline.md)に保持する。
以下はtest仕様のreviewであり、観測済みの応答ではない。

| case | 代表性と期待routing | 観測するacceptance / fixture不足 |
| --- | --- | --- |
| P-01 | layer選択＋生成だけ。`dotfiles-deploy` が妥当 | fake HOME外writeゼロ、base/private/hostの実targetと差分、dry-runのみ。fake layer / installer引数を固定する必要 |
| P-02 | 公式2版の全文diff。arXiv skillが妥当 | exact CFONT command、raw hash、公式来歴、coverage、log/PDF、構造、実目視。paper ID / 版 / archive hash / engineが未確定 |
| P-03 | font-only科学図。figureが妥当 | input bytes、tuple/multiplicity、点/区間端維持、fontのrender、affected outputsのみ。実際のinstalled fontと独立baselineが必要 |
| P-04 | 可搬抽出。exportが主owner、必要な共通知識のみ | 元appearance、editable dependencies、lossless cells、移設とrecipient inclusion。recipient format / compilerを固定 |
| P-05 | 保存値による報告改訂。reportが妥当 | tau=2の反例を残し主張を限定。RMSE/SD/mean deviation区別、template・user edit保全、必要page目視。baseline本文と定義を用意 |
| P-06 | Markdown抽出→ICS。旅行skillが妥当 | 原文→JSON→各eventの対応、年越し、UTC、checkout日、Maps、UID/encoding。未確定列車の必須日時を明確化する必要 |
| N-01 | fish source review。public6つは対象外 | findingsのみ、installer/dry-run/applyなし。合成sourceに既知の観点を用意 |
| N-02 | 一般Markdownの誤字指摘。public対象外 | 指摘の正確性、Typst/PDF/科学workflow不要。plain text fixtureを固定 |
| N-03 | Calendar既存予定read。旅行変換は対象外 | 接続なしなら不足を正確に報告、ICS/auth変更なし。日付とconnector利用不可を全runで固定し実accountを使わない |
| B-01 | editable bundle内のfont-only。figureが主owner | bundle再抽出・relocation・全upstream調査なし。既存schema/来歴/dataの保全、affected PDF確認 |
| B-02 | standalone科学図のread-only review | figure ownershipはR-002待ち。点/区間/legendを保存値へ照合し、source/delivered hash不変。compileするならtempだけ |
| B-03 | 既存PDF利用、caption/配置のみ。reportが主owner | caption根拠、receiving size/後続pageを確認。図再生成・抽出・移設なし |

全caseはfresh input copyから独立して走らせる。
実行順をランダム化する場合もseedと順を記録し、前caseの成果物や評価者の正解をmodelへ渡さない。
fixtureと正解oracleは別管理し、正解oracleを同じ生成codeから導出して自己確認にしない。
primary owner以外のreferenceを必要範囲で読むことは、直ちにmisroutingとはしない。
全workflowの不要起動と、共通知識の参照を区別する。

提案する修正はStage 1の原文を上書きせず、case manifestの `acceptance_revision` と追補IDへ保存する。

| 変更ID | 提案内容 | 理由と比較への影響 |
| --- | --- | --- |
| M-001 | P-01/P-03/B-01/B-03のwrite対象はfixture copyだけと明示 | live成果物へ触れる誤解を除く。全条件で同じauthorityを与える |
| M-002 | P-02は実fixtureに存在するsection / bibliography / appendix inventoryを事前固定 | 存在しないappendixを要求しない。必要構成を持つpaperを選ぶ |
| M-003 | B-02のownerをR-002承認で固定し、interval/legend欠陥を持つfixture variantを用意 | wordingではなく既知欠陥と保全で採点する。originalとvariantを別記録 |
| M-004 | N-03はconnectorなし、評価基準日を `2026-10-21 Asia/Tokyo` と固定 | live accountや明日の日付変化を除く |
| M-005 | LLMの「確認しました」でなくread/compile/画像inspection記録とartifactで判定 | 自己申告を実施証拠にしない |
| M-006 | P-06基本fixtureは日時確定、列車番号/座席等のみ未確定にする | mandatory日時不足で正しく確認したrunを誤ってfailureにしない。日時不足は別追補へ |
| M-007 | B-01/B-03は必要reference読込を禁止せず、不要な実作業を判定 | conditional reference契約を守る |
| M-008 | disabled controlでは期待skill名を採点せず同じ出力契約を採点 | skillを与えないcontrolでrouting失敗を数えない |

M-006は追加の評価仕様リスクであり、既存helperの新しい欠陥とは判定しない。
追補caseは `X-01`（arXiv必須coverage/目視不足）、`X-02`（全必須合格・upstream科学再現なし）、`X-03`（旅行必須日時不足）、`X-04`（一般Markdown reviewと科学図reviewの隣接境界）を提案する。
原12caseとは別系列でbefore / after両方へ同じ条件を供給する。

## 4. fixtureと準備

各fixture manifestへinput全hash、権限、compiler/font/package version、期待I/O、oracle revision、timeoutを記録する。
新規dependency導入はStage 2ではせず、Stage 3でも別承認とする。

| fixture | 必須内容 | 独立oracle / リスク制御 |
| --- | --- | --- |
| F-dotfiles | 一時sourceとbase/private/host manifest、fake HOME、無関係sentinel、既存target | installerをこのtreeとdestinationだけへ向ける。SSH/service/external applyを権限で遮断 |
| F-arxiv | 公式archive 2版、URL/hash、main TeX、元版build証拠、exact command、bibliography/appendix inventory | paper ID・versionはR-007準備時に確定。shell escape無効、networkなし、timeout。公式source取得未完なら実行しない |
| F-figure | Stage 1の4行CSV、quantity/normalization定義、既存plot、baseline PDF、全図/selected outputs | tuple `(method,tau)` が各1、保存値とintervalを別oracle表へ固定。font以外を変えない |
| F-bundle | report invocation、source revisionまたはcaptured tree、依存一式、recipient最小文書 | 別directory、別cwd、空白入りpathでcompile。PDF非対応recipientではSVG等を実検証 |
| F-report | 既存template・誤った全称主張・latest user edit sentinel・figure/caption | tau=1のB優位とtau=2の逆転、統計定義を固定。figure再生成不要variantを分ける |
| F-travel | 合成2旅行Markdown、年越し、深夜着、複数ホテル、未確定列車番号/座席、確定日時 | 原文と期待eventを人が照合したoracle。実予約番号・個人情報・Calendar accountを使わない |
| F-review-mutant | F-figureのsourceに既知のinterval端・legend対応の誤りを限定導入 | data CSVは無変更。評価者だけがmutant箇所と期待指摘を知る |
| F-fault / F-path | old/new ICS、無関係file、outside sentinel、各種link、stage/backup注入点 | すべてrun内に置く。「outside」は指定output外であって、実user fileではない |

F-figureの元CSVはStage 1のものをそのまま保持する。
F-dotfilesのfake HOMEはinstallerの既存destination指定で扱う一時directoryであり、hostの `HOME` を書き換える意味ではない。
`low/high` は保存済みinterval端であり、coverageや推定法を新たに仮定しない。
mean deviation等の意味はfixtureの定義に明記し、一般的な統計等式から勝手に推定しない。

## 5. explicit / implicit / disabledの評価

専用runnerはtarget input以外の研究repo、audit、解答、active plugin、単独skill、private routerを読めない構成とする。
各条件の全catalogを保存する。
host全体のglobal設定を無効化して済ませず、runner側で必要なtools / system skills / instructionsを同一にする。
必要なgeneric PDF等のskillを使う場合も全条件で同じ版を供給し、target内容へのlinkがないことを確認する。
controlにはtarget6スキルの実体も検索可能なsource treeも供給しない。
targetのsource hash表や正解をpromptへ注入しない。

| mode | 入力の差 | routingの判定 |
| --- | --- | --- |
| Explicit | P/B原promptへ `$skill-name` のprefixだけを付与 | 選択path/hashと実読込を確認。file存在だけでは合格にしない |
| Implicit | 元prompt、target6入口はcatalogに可視 | 正しいownerを選んだか、不要workflowを起動したかを観測 |
| Disabled | 同一prompt/fixture/authority、targetと同等copy・routerを遮断 | target読込なしを必須とし、taskの出力品質とscopeを比較 |

N系列はimplicit / disabledを主比較とし、意図的なexplicit強制は主集計に入れない。
全12caseは1 revisionあたり `9 × 3 + 3 × 2 = 33 run`、3反復なら99 runとなる。
before / after両方で3反復するなら198 runなので、budgetを先に承認する。
まずB-02の3条件、N-01/B-01/B-03のimplicit / disabledの2条件ずつ、合計9 run/revisionのfocused比較を推奨する。
P-02は公式fixtureとtoolchainが揃う時だけ追加する。
deterministicなD-002/D-003をLLMで再発見させることは必須としない。

実行記録の最小schemaは以下である。

```json
{
  "case_id": "B-02", "prompt_revision": "stage1", "acceptance_revision": "proposed-m003",
  "mode": "implicit", "repeat": 1,
  "source_commit": "...", "payload_manifest_sha256": "...", "fixture_manifest_sha256": "...",
  "runtime_version": "...", "client_binary_sha256": "...",
  "requested_model": "...", "effective_model": "unknown-if-not-exposed",
  "normal_effort": "...", "planning_effort": "...", "effective_config_evidence": "...",
  "catalog_evidence": "...", "loaded_resources": [{"path": "...", "sha256": "...", "evidence": "..."}],
  "permissions_and_instructions": "...", "compiler_fonts_packages": "...",
  "usage": {"source": "runtime-events-or-unavailable", "input_tokens": null, "output_tokens": null, "cost": null},
  "timing": {"preflight_seconds": null, "task_wall_seconds": null},
  "selection": "inconclusive", "execution": "designed-but-unexecuted", "failure_class": null,
  "artifact_hashes": {}, "observations": [], "unverified": []
}
```

model・effortが条件間で確認できない場合、定性的case studyは残せるが同条件の性能比較から除外する。
CLI JSONLやAPIのusageイベントを保存し、model自己申告のtoken/tool/costを採用しない。
tool数とreference bytesは実transcriptから別途数え、正しいscopeと品質の副指標にする。
単回runはcase study、3回でも小標本と明示する。

## 6. 実際のbaseline結果

### Stage 1から継承する証拠

| ID | 既存状態 | Stage 2での扱い |
| --- | --- | --- |
| E-001 | frontmatter 6/6、link/anchor破損0 | source同一性を再確認。静的成功証拠として再利用 |
| E-002 | 文書追加前の3+7+12=22test合格 | disposable tracked copyで新たに22test合格を取得 |
| E-003 | 合成3page TeX→real verifier→first/middle/last目視合格 | Stage 1の限定証拠。今回の新しいrender / 公式arXiv試験ではない |
| E-004/E-005 | 後続write部分更新 / leaf symlink越境を観測 | 新しい合成probeで再確認・範囲拡張 |
| E-006 | Typst fragment syntax/import合格 | 再利用。科学図・tick fontの実目視を示さない |
| E-007/E-008 | runtime mismatch / audit追加後distribution失敗 | Stage 2で再確認 |
| E-009 | 元18file / Git保全 | Stage 2でも18hash一致。既存のsource・入力文書・観測runtime等62fileのhash/modeと、HEAD / tracked / stagedの不変を保存時に照合 |
| P/N/B12case | Designed but unexecuted | **全件引き続き未実行。explicit / implicit / disabled各0 run** |

### Stage 2の実行

全helper runはPython 3.12.3、上記sourceのbytesを使った。
LLM model、selected skill、LLM usageは適用外であり、0 runである。
実入力・出力は合成で、実予約や実研究結果ではない。

| ID | 状態 | 入力・観測・品質scope |
| --- | --- | --- |
| S2-ID | Executed and passed（同一性観測） | source18hash一致。配置先14/3/0、cache1/3/13、単独旅行はSKILLのみ差異。D-001は未解消 |
| S2-REG-PLUGIN | Executed and passed | HEADから必要tracked treeを一時展開。distribution 3/3、wall 0.0513 s |
| S2-REG-ICS | Executed and passed | 同copyの既存7/7、wall 0.0742 s。Markdown抽出やfailure recoveryの成功ではない |
| S2-REG-ARXIV | Executed and passed | 同copyの既存12/12、wall 0.3796 s。fake PDF toolsのcontrol-flow試験を含み、公式全文PDFではない |
| S2-PAYLOAD | Executed and failed（既知D-006） | disposable copyに元Stage 1の4文書を追加。distribution 3中2合格、manifest集合1失敗 |
| S2-FAULT-CREATE | Executed and failed（提案C2に対して） | `b.ics` のopenでOSError注入。`overwrite=False` でも `a.ics` が新版で残る |
| S2-FAULT-OVERWRITE | Executed and failed（旧集合保全に対して） | 旧a/b/combined、bのopenでOSError。aは新版、combinedは旧bytes |
| S2-LINK-leaf | Executed and failed（提案境界に対して） | output内aのlinkを外部sentinelへ向ける。sentinel変更、link維持 |
| S2-LINK-parent | Executed and failed（提案境界に対して） | output directory自体を別dirへのlinkにする。外側a変更、directory link維持 |
| S2-REPLAY | Executed and passed（再現手順の検証） | 本書のPython probeを実行し、22test成功、audit時の1test failure、両faultと両linkの既知挙動を再確認。追加のLLM runではない |
| S2-GUIDANCE | Executed and passed（探索のみ） | rootからtargetまで実在する祖先AGENTS.mdなし。会話のWorking Agreementsを適用 |
| S2-LLM | Designed but unexecuted | 隔離catalog / control / 認証・権限・budgetの条件未確立。CLI不在・認証failure・selection failureという結果ではない |

失敗probeは観測の採取には成功したが、保存・境界の受入に失敗した、という意味である。
単回wall時間からspeedupやcostを推定しない。
raw evidenceは `/tmp/ryo-workflows-stage2-8tu8suhp/identity-before.json`、`public-payload.sha256`、`baseline-results.json`、各testの `.log`、`distribution-with-stage1.log` にある。
`/tmp` の永続性は保証されないので、上表の結果と以下の再現方法を本書に残す。
再現手順の実行記録は `/tmp/stage2-replay-xtfefspy/` のtest logsにも残る。
input/outputそのものをuser repoへ追加しない。

### 実行の再現

対象のtracked snapshotを展開するPython codeは次である。
保存先を `/tmp/replay_stage2_baseline.py` として、後述のfish-compatible commandで実行できる。
Stage 1文書のcopyだけは現checkoutから取り、[更新計画 §7](02_update_plan.md#7-移行と互換性)の4入力hashと同じか確認する。

```python
import hashlib, importlib.util, io, os, shutil, subprocess, sys, tarfile, tempfile
from pathlib import Path
from unittest.mock import patch

repo = Path(sys.argv[1]).resolve()
run = Path(tempfile.mkdtemp(prefix="stage2-replay-", dir="/tmp"))
tree = run / "source"
tree.mkdir()
paths = ["tests/test_ryo_workflows_plugin.py", "tests/test_extrip_to_ics.py",
         "tests/test_arxiv_diff_pdf_verifier.py", "dotfiles_installer",
         "manifest/base.tsv", "config/codex/plugins/ryo-workflows"]
blob = subprocess.check_output(["git", "archive",
    "737ba2926d72ad51dccfc0cf6b26cd4d2994a44d", *paths], cwd=repo)
with tarfile.open(fileobj=io.BytesIO(blob)) as archive:
    archive.extractall(tree, filter="data")  # replay環境はPython 3.12+
env = os.environ | {"PYTHONDONTWRITEBYTECODE": "1"}
def tests(name, label):
    result = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover",
        "-s", "tests", "-p", name, "-v"], cwd=tree, env=env,
        capture_output=True, text=True, timeout=45)
    (run / (label + ".log")).write_text(result.stdout + result.stderr)
    print(label, result.returncode)
for name in ["test_ryo_workflows_plugin.py", "test_extrip_to_ics.py",
             "test_arxiv_diff_pdf_verifier.py"]:
    tests(name, name)
relative = Path("config/codex/plugins/ryo-workflows/skills")
stage1_hashes = {
    "01_inventory.md": "0533998aa7eaabf44dbc5d87b9ad5a6019cd0573e61377045c6632ead061d1f0",
    "02_diagnosis.md": "b571e6df45b3939cf373cdcc426eaa66560361d19d24670270104473bb8a5631",
    "03_baseline.md": "f5f2945b0e573e7270c433717ff484446a1beb76003dd4aae8e709a47a84f3fa",
    "04_handoff.md": "d6022c477fcfcecf09b1162b907ff187d0be5140abdc802c4d8710ed77c921cf",
}
for name, digest in stage1_hashes.items():
    assert hashlib.sha256((repo / relative / "stage1" / name).read_bytes()).hexdigest() == digest
(tree / relative / "stage1").mkdir()
for name in stage1_hashes:
    shutil.copyfile(repo / relative / "stage1" / name, tree / relative / "stage1" / name)
tests("test_ryo_workflows_plugin.py", "with-audit")
spec = importlib.util.spec_from_file_location("ics", tree / relative /
    "extrip-to-ics/scripts/build_ics.py")
ics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ics)
def event(group, title):
    return dict(id=group, group=group, summary=title, description="synthetic",
        source="synthetic.md", map_query="Tokyo station", all_day=False,
        start="2026-12-31T23:50:00+09:00", end="2027-01-01T01:10:00+09:00")
items = [event("a", "new-a"), event("b", "new-b")]
for overwrite in [False, True]:
    out = run / ("overwrite" if overwrite else "create")
    out.mkdir()
    if overwrite:
        ics.generate([event("a", "old-a"), event("b", "old-b")], out)
    old_combined = (out / "trips.ics").read_bytes() if overwrite else None
    original_open = Path.open
    def injected(path, *args, **kwargs):
        mode = args[0] if args else kwargs.get("mode", "r")
        if path == out / "b.ics" and mode in ("wb", "xb"):
            raise OSError("injected later output failure")
        return original_open(path, *args, **kwargs)
    try:
        with patch.object(Path, "open", injected):
            ics.generate(items, out, overwrite=overwrite)
    except OSError as exc:
        print("fault", overwrite, str(exc), sorted(p.name for p in out.iterdir()),
              b"new-a" in (out / "a.ics").read_bytes(),
              overwrite and (out / "trips.ics").read_bytes() == old_combined)
for kind in ["leaf", "parent"]:
    out, outside = run / ("link-" + kind), run / ("outside-" + kind)
    outside.mkdir()
    target = outside / "a.ics"
    target.write_bytes(b"sentinel")
    if kind == "leaf":
        out.mkdir()
        (out / "a.ics").symlink_to(target)
    else:
        out.symlink_to(outside, target_is_directory=True)
    ics.generate([event("a", "redirected")], out, overwrite=True)
    print("link", kind, "outside_changed", target.read_bytes() != b"sentinel")
print("evidence", run)
```

```fish
env PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/replay_stage2_baseline.py /home/ryo/github/dotfiles-public
```

これは未改修の監査版を再現するprobeであり、新実装へのfailure testにはT-005の専用注入点を使う。
Stage 1移行後は旧4文書の入力pathを新しい `AUDIT/stage1` に明示変更し、その他のfixtureは同じにする。

## 7. 構造・helperの回帰検査

以下はStage 3のmandatoryである。

| 検査 | 範囲・成功条件 |
| --- | --- |
| source保全とdiff | unrelated dirty/staged/untrackedと原入力をsnapshot比較。`git diff --check`、最終diff self-review |
| frontmatter | 全6skillを既存 `quick_validate.py` で検査。selection品質とは区別 |
| links | 全entrypoint/referenceのpath・anchorと配布先内への包含、audit移行後の全functioning link |
| distribution | 既存3test、mode `0644`、local context、全6入口、実bytes。未知file追加と必要resource除去の負例で失敗すること |
| 旅行既存契約 | 既存7testを保存。UTC、all-day exclusive end、escape、75-octet UTF-8 fold、stable UID、Maps、validation、CLI出力とsource不変 |
| arXiv既存契約 | 既存12testを保存。fatal、summary欠落、log/PDFページ不一致、PDF構造、sample選択、JSON/exit分類 |
| identity / eval harness | 同version異bytes、missing/extra、mode、overlay、catalog汚染、disabled再読込、失敗分類のbehavior test |

実行例はStage 3の隔離worktreeで次の通りである。

```fish
env PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p test_extrip_to_ics.py -v
env PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p test_arxiv_diff_pdf_verifier.py -v
env PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p test_ryo_workflows_plugin.py -v
env PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p test_ryo_workflows_identity.py -v
env PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p test_ryo_workflows_evaluation.py -v
git diff --check
```

manifest / installer本体を変えた場合は該当manifest/context/apply testを追加し、repo要件があればfull suiteを行う。
無関係なsuiteを成功回数のために反復しない。
実PDF/図の出力が評価対象となる時はcompileと画像の実inspectionを必須とする。
現行helper source/tool環境が同じならStage 1合成real-tool証拠は再利用できるが、公式arXiv fixtureや変更後の図の目視を代用しない。

## 8. failure injectionとfilesystem試験

両overwrite modeでF-faultを実行する。
例外を注入するだけでなく、全target / unrelated file / backup / journalのbytesとmodeを事後照合する。

| ID | 注入・入力 | 提案C2の受入 |
| --- | --- | --- |
| F-01 | invalid event / combined衝突 / 後続targetがdirectory | final無変更。invalid inputでoutput dirを作らない |
| F-02 | 2番目のstage write / close / readbackでOSError、ENOSPC相当 | final無変更。run-created tempだけcleanup、失敗phase明示 |
| F-03 | old targetのbackup途中で失敗 | final無変更。元bytes/mode保持 |
| F-04 | 最初のpublish前に失敗 | final無変更、旧成功一式を保持 |
| F-05 | 1番目・中間・最後のpublish後、または最終照合で失敗 | rollback成功なら全旧bytes/mode復旧、新規target撤去、exit 2 |
| F-06 | `overwrite=False` の後続publish失敗、または競合entry出現 | exclusive publishで既存entryを潰さず、自分の公開entryだけrollback |
| F-07 | publish失敗＋rollbackの1targetでも失敗 | `rollback=incomplete`、影響一覧、private backup/journal保持。再runを止め、成功と報告しない |
| F-08 | commit後cleanup失敗 | new一式は完全なまま、成功returnとwarning、committed記録。旧版へ戻さない |
| F-09 | prepublish baseline変更、rollback前の外部user edit | conflictを検出しuser editを保全。勝手にsnapshotへ戻さない |
| F-10 | subprocessをpublish barrier直後にSIGKILL | group原子性は要求しない。unfinished journal/lockを検出して次run停止、残るold/newとbackupを分類可能 |
| F-11 | 壊れたjournal / backup欠落 / 既存lock | fail closed。PID不在だけで削除せず、人の回復判断へ返す |
| F-12 | no-clobber hardlink未対応FSの例外 | final stream writeへのfallbackなし。公開済み分はC2回復、明確なFS制約 |

F-10は使い捨てchild processの明示終了記録で判定する。
host processの不在を `/proc` や `ps` の一回の結果だけで断定する試験ではない。
OS全体をdisk fullにせずOSErrorを注入し、未注入の実power-loss耐性は未検証とする。

| ID | filesystem入力 | default policyの受入 |
| --- | --- | --- |
| S-01 | final leaf symlink / dangling link | 両modeで拒否、linkと外部sentinel不変、他final無変更 |
| S-02 | output directory symlink / 中間parent symlink | prepublish拒否、参照先にwriteしない |
| S-03 | regular directory / FIFO / device相当、`..` path | 非通常target・曖昧pathを拒否。FIFOでhangしない |
| S-04 | 既存通常fileが外部sentinelのhardlink | overwriteはentryを差し替え、外部inodeのbytes不変。link関係の変更を仕様通り確認 |
| S-05 | 通常path、空白含むparent、custom combined、無関係file | 従来の正常利用が成功し、無関係file保全 |
| S-06 | final衝突がcheck後に出現 | no-clobberは既存entryを保持。overwriteで非協調writerがある場合は保証外と記録 |

悪意あるparent置換や同一UIDの共有directory raceを完全に防ぐ受入はdefaultに含めない。
R-004で強いrace防御を選ぶ場合に限り、dirfd / no-follow pathwalk、parent rename、link swapの同期barrier試験、OS write confinementを追加する。
portableな `lstat` 成功だけでsecurity race合格としない。

## 9. 変更別の受入基準

| AC | 関連 | mandatory | conditional / optional |
| --- | --- | --- | --- |
| AC-001 | D-001 / T-001,002,008 | expected source / isolated file copyの全hashとmodeを照合。LLMを実行する場合はcatalogとactual loadの照合も必須で、不一致runを比較から除外 | LLM部分はR-007依存。active D-001解消はT-010承認後のfresh運用試験 |
| AC-002 | D-002 / T-005 | F-01〜09,11,12、成功path、既存7test、error/rollback報告 | F-10はprocess interruption契約を提供する場合必須。本推奨C2では提供するので実施 |
| AC-003 | D-003 / T-004 | S-01〜06、ordinary link境界と互換性説明、outside sentinel保全 | malicious raceは強いpolicy採用時のみ |
| AC-004 | D-004 / T-006 | metadataと本文整合、read-only契約、frontmatter/link | selection効果を主張するならB-02 before/after必須。B-01/B-03/N-01/02で境界確認 |
| AC-005 | D-005 / T-007 | mandatory gateが現行以下にならないことのself-review、既存12test | wordingが実行判断を改善すると主張するならP-02/X-01/X-02。公式fixture未準備は未実行 |
| AC-006 | D-006 / T-003 | 旧4文書保全、移動後link、audit非配布、strict distribution成功と未知/欠落の負例 | raw evidenceの長期保管は匿名化と保存先承認後 |
| AC-007 | Typst保存 | referencesとowner不変、scopeのself-review | 実workflow効果はP-03〜05/B-01〜03とtuple・interval・relocation・inclusionのartifact確認 |
| AC-008 | 効率 | 正確性・scopeを先に採点、measurement不足を明記 | measured token、reference bytes、tool数、wall、確認回数。少数例で一般的改善率を主張しない |
| AC-009 | 全task | 最終diffとunrelated保全、承認scope、未実行の明示 | package/install/deployは承認された時のみ |

deterministic source改修の完了とLLM上の改善実証は別判定にする。
R-007未承認でも人がdeterministic実装のみを許可できるが、その場合AC-004/005の効果は未検証である。
source修正を終えてもactive catalogが古ければD-001の運用解消は未完である。

## 10. 測定上の限界と未解決前提

pre-refactoring LLM baselineはない。
今回のsessionはStage 1 findingsと推奨案を知っており、独立したselection/controlの評価者には使えない。
既存22testは有用だが全domain workflowやLLMの判断を証明しない。
raw logsとunit testのmock範囲を区別する。

未確定なのはclean runnerでのcatalog、認証・network・budget、modelのeffective identity、公式arXiv fixture、recipient環境、科学図の固定renderである。
これらは全source taskを妨げるものではないが、該当するLLM比較とend-to-endの信頼性を妨げる。
R-002〜R-006が未承認なら、そのspecに依存する実装も保留する。
通常のsymlink検査の限界、rollbackの限界、既存full suite未実行を報告から落とさない。

## 11. Stage 3でのbefore / after比較

1. 承認済みspec、case manifest、fixture、runnerを先に固定する。
2. 改修前HEADまたはcaptured working treeを同じ論理pathへ供給し、identity preflightを通す。
3. focused 9 runをbudget内で取得し、必要なら全33 runと追補へ広げる。
   取得できなければ理由を残し、after-onlyにする選択を人が確認する。
4. sourceをtask単位で実装し、意味のあるhelper regression / fault testを通す。
5. 同じmodel/effort/permissions/tools/fixtureでafterを取得する。
   code/runtimeを同時更新したrunは別群にし、source単独効果を主張しない。
6. selection、task品質、preservation、環境faultを別列で比較する。
   workflow成功を満たした範囲でのみcontext / tool / wall / usageを副比較する。
7. 同条件の有効証拠は再利用し、最終差分が影響したscopeだけ再検査する。
8. source受入、LLM効果、active配布の3状態を別々にhandoffする。
   before欠如のafter合格を「改善率」や「旧版より高速」と記さない。
