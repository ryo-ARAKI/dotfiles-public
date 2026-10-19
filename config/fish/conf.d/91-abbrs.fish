if status --is-interactive
    # cd for parent directories
    abbr .. "cd .."
    abbr ... "cd ../.."
    abbr .... "cd ../../.."
    abbr pd "prevd"
    abbr nd "nextd"
    abbr dh "dirh"

    # git
    abbr g "git"
    abbr ga "git add"
    abbr gc "git commit"
    abbr gcm 'git commit -m'
    abbr gca "git commit --amend"
    abbr gpsh "git push --set-upstream origin HEAD"
    abbr gpl "git pull"
    abbr gf "git fetch"
    abbr gdif "git diff --no-binary --color-words"
    abbr gdh "git diff --no-binary --color-words HEAD^...HEAD"
    abbr gdc "git diff --no-binary --color-words --cached"
    abbr gchk "git checkout"
    abbr gust "git restore --staged"
    abbr gsav "git stash push -u"
    abbr gp "git stash pop"
    abbr gr "git rebase"
    abbr gm "git merge"
    abbr gls "git ls-files"
    abbr glst "git stash list"
    abbr gw "git switch"
    abbr --set-cursor gwa 'git worktree add .worktrees/%'
    abbr gb "git branch --sort=-committerdate"
    abbr gba "git branch --all --sort=-committerdate"
    ## https://techracho.bpsinc.jp/jhonda/2018_12_13/66486
    ## https://yuu.1000quu.com/git_alias_and_zsh_setting
    abbr gst "git status --short --branch"
    ### Show git log in compact form
    abbr gl "git log --oneline --decorate=short --date=format:'%Y-%m-%d %H:%M:%S' --pretty=format:'%Cgreen%h %C(yellow)%cd %Cred%d %Creset%s %Cblue<%cn>' -10"
    ### Show history of one file, including renames (glf -- path/to/file)
    abbr glf "git log --follow --oneline --decorate=short --date=format:'%Y-%m-%d %H:%M:%S' --pretty=format:'%Cgreen%h %C(yellow)%cd %Cred%d %Creset%s %Cblue<%cn>' -10"
    ### Show git log with number of modified lines
    abbr glli "git log --pretty=format:'%C(yellow)%h%Cred%d %Creset%s%Cblue [%cn]' --decorate --numstat -10"
    ### Show git log with visual graph of branch
    abbr glgr "git log --graph --oneline --decorate=short --date=format:'%Y-%m-%d %H:%M:%S' --pretty=format:'%Cgreen%h %C(yellow)%cd %Cred%d %Creset%s %Cblue<%cn>' -10"
    ## latexdiff with git
    abbr ldif "latexdiff-vc -e utf8 -t CFONT --flatten --git --force -r"

    # GitHub Actions
    abbr ghw "gh run watch --exit-status"

    # apt
    abbr aud "sudo apt-fast update"
    abbr aug "sudo apt-fast upgrade"
    abbr aui "sudo apt-fast install"
    abbr aar "sudo apt-fast autoremove"

    # Julia
    abbr jlp "julia --project=. --startup-file=no"
    abbr jlt "julia --project=. --startup-file=no -e 'using Pkg; Pkg.test()'"

    # File search by extension
    abbr fde "fdfind --type file --ignore-case --extension"

    # rsync option
    abbr rsync "rsync -artv"

    # PDF Viewer
    abbr ev "evince"  # Default PDF viewer
    abbr mp "mupdf"  # minimal PDF viewer

    # Other alias-like abbreviations
    abbr cfree "free -h && sync && sudo sysctl vm.drop_caches=3 && free -h"  # Cache clear
    abbr bb "extractbb -O"  # Output boundarybox information
    abbr --set-cursor gs 'gs -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/printer -sOutputFile="%"'
end
