# Stage 3 決定記録

2026-10-21。production codeの変更前に作成した。
Stage 1/2の8報告書を読み、現在のHEAD `737ba2926d72ad51dccfc0cf6b26cd4d2994a44d` が監査版と一致することを確認した。
原本8文書のSHA-256とcopy一致は [input_hashes.json](input_hashes.json) に記録する。

## 採用範囲

- R-001: Option A。既存6スキル、名前、参照所有権を維持する。
- R-002: 科学図のread-only reviewは既存figure skillのmodeとする。根拠付きfindingsのみを返し、sourceと配布済み成果物を変更しない。
- R-003: **ユーザーはC2ではなくC1を選択した。** Stage 2のC2推奨、T-005仕様、F系列のrollback要求を本決定と今回のC1-F01〜F10で置き換える。
- R-004: leaf（danglingを含む）、output directory、指定pathの既存componentのsymlink、非通常target、字句上の `..` を拒否する。owner管理のtrusted output directoryを前提とする。正当なaliasも拒否する互換性変更であり、通常の `lstat` 検査は悪意あるraceの完全防御ではない。
- R-005: 要求された完全arXiv diff PDFのmandatory acceptanceを維持し、依頼外の科学再現と区別する。verifierは実欠陥が見つからなければ変更しない。
- R-006: auditをruntime外のdocsへcopyし、機能するrelative linkだけを更新する。原本の歴史的観測・hash・revisionを維持する。primary checkoutのStage 1原本は削除しない。
- R-007: identityとfocused評価準備・安全なpreflightを実装する。runnerのcatalog隔離、effective model/normal/planning effort、認証境界、予算、workspace権限が未確立なので独立LLM実行は行わない。原P/N/B promptをimmutable groupとして保存する。
- R-008: source-only。active deploymentとT-010は対象外。

## C1の保証

1. 対応filesystem semanticsを前提に、公開された各final pathでは完全な旧版または完全な新版が観測される。
2. 全event、output名、衝突、生成payloadを公開前に検証する。
3. 全bodyを生成し、全fileをstageしてcloseしてから最初のfinalを公開する。
4. preparation/staging失敗では既存finalを変更しない。
5. finalと同じfilesystemで各fileをatomicに公開する。
6. batch途中の公開失敗では公開済みfileは新版のまま、他は旧版または未作成になり得る。
7. 公開済み、失敗箇所、未試行、batch完了、cleanupの不確実性を区別して報告する。
8. 一部だけの公開をbatch全体の成功としない。
9. `overwrite=False` はatomic no-clobberを使い、既存destinationを置換しない。
10. 承認されたsymlink/trusted-directory policyに違反するpathを拒否する。

## 保証しないこと

batch全体の原子的公開、全旧fileの自動復元、transaction-wide rollback、concurrent readerのcross-file snapshot整合、crash-recovery journal、停電耐久性、非協調writerからのisolation、悪意あるfilesystem raceの完全防御は提供しない。
旧file backup、rollback state machine、recovery journal、persistent lock、手動transaction recovery interface、`RECOVERY_REQUIRED`、C2用SIGKILL回復試験は追加しない。
private stagingとper-file replace/linkだけを基本とし、追加mechanismが必要なら単純な代替案との比較理由を記録する。

## 作業環境と権限

専用worktree: `/home/ryo/github/dotfiles-public/.worktrees/ryo-workflows-stage3-c1`。
branch: `codex/ryo-workflows-stage3-c1`。`.worktrees/` は既存Git ignoreで除外済み。
primary checkoutの追跡済み差分はなく、未追跡audit8文書、無関係なlocal文書6件、既存ignored bytecodeを含む136fileのhash/mode/typeとindexを作業前に保存した。
既存worktreeの内容は変更しない。
commit、push、deployment、active plugin/vendor cache/standalone/global config変更、依存導入、認証copy、Calendar/remote write、subagentは実行しない。
決定的テストはworktreeと新規 `/tmp` fixtureだけで行う。

## 実装制約による差分

Stage 2のprimary側4文書撤去を行わず、隔離worktreeだけをruntime外配置にする。primary側cleanupは別途残る。
LLM比較は未実行とし、source検証・selection評価・active runtime検証を別判定する。
追加の実装判断は次のとおりである。

- replacementは `os.replace`、no-clobberは `os.link` とし、stageは同一output directory内のrun専用0700 directoryに置く。旧file backup、journal、lockは不要で追加しない。
- staged bodyをclose後に再読して一致を確認し、その後に既存permission bitsを適用する。write-only targetの権限継承でreadbackを妨げないためである。inode、hard-link関係、ACL/xattrの継承は保証しない。
- publication失敗は `OSError` subclassのreportとCLI非zeroで通知する。全file公開後のcleanupだけが失敗した場合は通常の成功returnを保持し、`PublicationCleanupWarning` に `batch_completed=true` とcleanup残存を記録する。公開済みをrollbackしたとは扱わない。
- failure時は成功operation recordとpost-failure観測を分け、成功returnのないoperationを観測だけで成功分類しない。
- versionは現metadataとGit履歴・manifest方式を確認してsource上の `0.1.1` とする。active cacheの更新やrelease公開を意味しない。
- evaluationはofflineのfixture/catalog/evidence検査までとし、LLMを起動するadapterを追加しない。安全な外部runnerの実効隔離と予算・認証・実行権限は別途確立が必要である。
