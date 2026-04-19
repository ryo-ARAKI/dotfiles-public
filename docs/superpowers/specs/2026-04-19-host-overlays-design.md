# Host Overlay Loading Design

**Goal:** `install` が `dotfiles-hosts` のホスト別 manifest を読み込み、`base < private < host` の順で overlay を解決できるようにする。

## Scope

この変更は `dotfiles-public` 側の installer CLI に限定する。`dotfiles-hosts` リポジトリ側の中身は空のままでよく、将来差分が入ったときにそのまま読める入口だけを追加する。

対象に含めるもの:

- `install` への `--hosts /path/to/dotfiles-hosts` 追加
- `install` への `--host-name <name>` 追加
- `dotfiles-hosts/manifest/<host-name>.tsv` の読込
- host layer の source root 解決
- CLI と apply 動作のテスト追加
- `README.md` の運用手順とオプション説明の更新

対象に含めないもの:

- `dotfiles-hosts` の自動 discover
- host 名の正規化や alias 解決
- host overlay の remote 自動配備

## CLI Design

### New Options

- `--hosts /path/to/dotfiles-hosts`
  host-specific repository root を明示的に渡す。指定が無い場合は host overlay を読まない。
- `--host-name <name>`
  読み込む host manifest 名を明示的に上書きする。主用途は dry-run とテスト。

### Resolution Order

host 名は次の順序で決める:

1. `--host-name` があればそれを使う
2. 無ければ `socket.gethostname()` の返り値を使う

`--hosts` が指定された場合だけ、`<hosts-root>/manifest/<resolved-host>.tsv` を探す。

### Missing Manifest Behavior

`--hosts` が指定されているのに対象 manifest が存在しない場合はエラーで終了する。これは「host overlay を使うつもりでコマンドを打ったのに、その host 定義が存在しない」状態を設定ミスとして扱うため。

`--host-name` 単独指定は無効とし、`--hosts` なしで使われた場合も argparse error とする。

## Loading Model

layer 順序は既存どおり `base < private < host` を維持する。`planner.py` の優先順位はそのまま使えるので、必要なのは entry list へ host layer を追加することだけ。

読込順:

1. `manifest/base.tsv`
2. `dotfiles-private/manifest/private.tsv` if `--private`
3. `dotfiles-hosts/manifest/<resolved-host>.tsv` if `--hosts`

host layer の manifest 行は layer 名 `host` で `load_manifest()` に渡す。

## Source Root Resolution

適用時と preview 時には layer ごとに source root を切り替える必要がある。

- `base` -> repository root
- `private` -> `--private` で渡された root
- `host` -> `--hosts` で渡された root

この切替は `install` 内で一元化し、preview と apply の両方で同じ関数を使う。これにより host layer の source が `dotfiles-public` 側で誤って解決されることを防ぐ。

## Error Handling

- `--host-name` without `--hosts`: argparse error
- `--hosts` points to a path without `manifest/<resolved-host>.tsv`: `FileNotFoundError` を捕まえて利用者向けメッセージで終了
- `manifest` 内容自体が不正: 既存の manifest parser の `ValueError` をそのまま出す

dry-run でも本適用でも、host manifest の存在チェックは同じように行う。

## Testing

追加するテストは次の 3 系統。

1. CLI option behavior
   - `--hosts` と `--host-name` を含む dry-run が host layer を表示する
   - `--host-name` 単独が失敗する
   - `--hosts` 指定時に host manifest が無いと失敗する

2. Apply behavior
   - `host` layer の file source が `--hosts` root から解決される

3. Planner integration
   - 既存の `host overrides private and base` テストは維持し、実際に CLI から host layer が入る経路を追加で担保する

## Documentation

`README.md` は次の内容を更新する。

- Current implementation status に host overlay loading が CLI に接続されたことを反映
- Command Reference に `--hosts` / `--host-name` を使う dry-run と apply 例を追加
- Remote workflow に `dotfiles-hosts` の clone/update と実行例を追加
- Current limitations から「host overlay loading is not yet connected」を削除し、代わりに host manifest が未定義なら `--hosts` 実行は失敗することを明記

README のコマンド例は省略せず、`dotfiles-public` / `dotfiles-private` / `dotfiles-hosts` を全部使う実例を載せる。
