---
name: extrip-to-ics
description: Use when converting EXダイナミックパック or similar Japanese train and hotel reservation Markdown files into Google Calendar importable .ics files, including departure-station and hotel Google Maps links.
---

# 旅行予約 Markdown から ICS を作成

予約文面を読み取り、旅行別と一括取り込み用の `.ics` をローカルで作成する。
Computer Use、Google Calendar API、アカウント認証は不要。
入力ファイルを残し、カレンダーへの登録は行わない。

## 抽出と生成

1. 対象の `.md` をすべて読み、旅行期間・往復列車・宿泊予約を抽出する。
   年は旅行期間から判断する。年越し、深夜着、複数ホテルは実際の日付で扱う。
   原文にない座席・列車・時刻を補完しない。必須日時が不明なら、その予定を生成する前に確認する。
2. [正規化JSONの形式](references/events-schema.md) に沿ってイベントをまとめる。
   新幹線は1列車につき1件、宿泊は1滞在につき1件。
   新幹線の地図検索語は**出発駅**、ホテルは**施設名と住所**。
   列車番号・発着時刻・座席が未確定という原文は説明に残し、タイトルにも未確定の内容を明記する。
   列車番号も未確定なら「列車・時刻・座席未確定」とする。
3. このスキルの実際の配置先を `SKILL_DIR` として、同梱スクリプトを実行する。

   ```text
   python3 <SKILL_DIR>/scripts/build_ics.py <events.json> --output-dir <出力先> --combined trips.ics
   ```

   Python 3.10以上の標準ライブラリのみを使う。
   既存ファイルがある場合は別の出力先を使うか、更新対象を確認して `--overwrite` を指定する。

## File publication

Use an owner-controlled, trusted output directory without noncooperating writers.
The helper rejects output-path symlinks (including dangling leaves and parent aliases), nonregular targets, and lexical `..` components; legitimate aliases must be replaced by an explicit real directory path.
Ordinary path checks do not eliminate malicious filesystem races.

The helper validates and prepares all payloads, then stages and closes every file before publishing any final file.
Preparation or staging failure leaves existing finals unchanged.
Each final entry is published atomically on the same filesystem: replacement with `--overwrite`, or no-clobber hard-link creation without it.
Unsupported no-clobber filesystems fail safely; there is no direct-streaming fallback.
Existing permission bits are preserved for replacements where supported; new files follow the caller's umask. Inode identity, hard-link relationships, ACLs, and extended attributes may change.

This is C1 per-file publication. A later publication failure stops the batch and may leave complete new individual files alongside old or absent outputs, including an old combined file.
The CLI fails with a nonzero status and reports successful operation records, the failing output, whether its publication was attempted, unattempted subsequent names, post-failure observations, and cleanup uncertainty without exposing event bodies.
In `PublicationError.report` and CLI diagnostics, `phase=pre-publication` and `failed_publication_attempted=false` mean a path/target recheck stopped the failing file before the publication helper was invoked; that file is not an uncertain publication.
`phase=publication` and `failed_publication_attempted=true` mean the helper was invoked but did not return success; keep that file in `uncertain_names` even if inspection observes new content.
`published_names` records successful returns, `failed_name` identifies the stopped file, and `unattempted_names` lists subsequent files for either publication phase. Failed staging still leaves every final unattempted. Observations remain separate and can flag uncertainty about the current contents of an already published file.
Do not report the full batch as successful after partial publication.
No batch rollback, cross-file snapshot consistency, crash recovery, power-loss durability, or isolation from noncooperating writers is provided.
Cleanup removes only this run's named staging files; incomplete cleanup is reported with its private directory path.
If all files were published but cleanup failed, the helper returns its normal counts with a `PublicationCleanupWarning` reporting `batch_completed=true`; it does not undo publication.


## 日時と記載内容

- 列車の時刻は日本時間の `+09:00` で入力し、ICSにはUTCで出力する。
- 宿泊は到着日からチェックアウト日を含む終日予定が既定。
  ICSの終了日は排他的なので、`end` にはチェックアウト日の翌日を入れる。
  ユーザーが時刻付きの宿泊予定を指定した場合は、その指示に従う。
- 説明には予約番号、座席・車両・禁煙区分、人数、食事、ホテル住所・電話、チェックイン／アウト時刻、予定到着時刻、交通案内、未確定の注意事項を原文にある範囲で残す。
  支払条件など、予定の利用に関係しない契約文の転記は不要。
- `LOCATION` と `URL` にGoogle Mapsリンクを入れる。出典ファイル名も説明に付く。

## 確認と受け渡し

生成したICSを読み直し、折り返しを展開して原文と照合する。
イベント件数、列車の日本時間、宿泊の終了日、出発駅、ホテル、未確定表示を確認する。
UTF-8・CRLF、75バイト以内の行折り返し、TEXTのエスケープはスクリプトが処理する。

最終回答では一括ファイルと旅行別ファイルへのリンク、件数、検証範囲を示す。
Google側に取り込んでいない場合は、その事実を明記する。
すでに同じ予定が登録されている場合は、別カレンダーでの試用を案内する。
安定したUIDは出力の識別用であり、Googleへの再インポートによる重複防止・更新は保証しない。
