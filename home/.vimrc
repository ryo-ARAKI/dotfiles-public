" Daily-use Vim config for code editing on plain Vim
" このファイルは、素の Vim をコード編集向けに実用寄りで整える設定。
" 互換性よりも、普段の編集・検索・移動のしやすさを優先している。
scriptencoding utf-8

" Vi 互換モードを無効にして、Vim 本来の機能を使う。
set nocompatible
" 内部エンコーディングを UTF-8 にする。
set encoding=utf-8

" 構文ハイライトが使える環境なら有効化する。
if has('syntax')
  syntax on
endif

" ファイルタイプ検出・関連プラグイン・インデント設定を有効化する。
filetype plugin indent on

" Safety and file handling
" 外部でファイルが更新されたら再読込できるようにする。
set autoread
" 未保存バッファがあっても別ファイルへ移動できるようにする。
set hidden
" undo 履歴をファイルを閉じた後も保持する。
set undofile
" undo の履歴件数を十分に確保する。
set undolevels=1000
" コマンドライン履歴の保存件数を増やす。
set history=1000

" Editing
" 挿入モードで Backspace を自然に使えるようにする。
set backspace=indent,eol,start
" 行末の 1 文字先までカーソル移動を許可する。
set virtualedit=onemore
" Tab 入力をスペースに展開する。
set expandtab
" 画面上での Tab 幅を 2 桁にする。
set tabstop=2
" 自動インデントや >> << の幅を 2 にする。
set shiftwidth=2
" 挿入モードで Tab/Backspace を 2 スペース単位に揃える。
set softtabstop=2
" 前の行のインデントを引き継ぐ基本的な自動インデント。
set autoindent

" UI
" 単純なファイル行番号を表示する。
set number
" カーソル行を強調して視線を追いやすくする。
set cursorline
" 入力途中のコマンドをステータスに表示する。
set showcmd
" 対応する括弧へ一時的にジャンプ表示する。
set showmatch
" ステータスラインを常に表示する。
set laststatus=2
" コマンドライン補完候補をメニュー表示する。
set wildmenu
" 補完時は最長一致まで進めつつ候補一覧も見せる。
set wildmode=list:longest
" タブや行末スペースなどの不可視文字を表示する。
set list
" 不可視文字の見た目を定義する。
set listchars=tab:>-,trail:-,extends:>,precedes:<,nbsp:+
" ベル音の代わりに画面側で通知する。
set visualbell

" Search
" 検索語が小文字だけなら大文字小文字を区別しない。
set ignorecase
" 検索語に大文字が含まれるときだけ大文字小文字を区別する。
set smartcase
" 検索語入力中から逐次ヒット箇所を表示する。
set incsearch
" 検索結果をハイライト表示する。
set hlsearch
" ファイル末尾まで行ったら先頭から検索を続ける。
set wrapscan

" Movement
" 折り返し行では表示行単位で下へ移動する。
" ただし 10j のように件数指定があるときは本来の行移動を優先する。
nnoremap <expr> j v:count ? 'j' : 'gj'
" 上方向も同様に、通常は表示行単位・件数指定時は実行単位で移動する。
nnoremap <expr> k v:count ? 'k' : 'gk'

" Clear search highlight
" Esc を 2 回押したら検索ハイライトを消す。
nnoremap <silent> <Esc><Esc> :nohlsearch<CR><Esc>

" Colors
" 見た目は組み込みの industry カラースキームを使う。
colorscheme industry
