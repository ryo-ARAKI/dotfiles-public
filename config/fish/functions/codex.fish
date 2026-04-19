function codex
    if not status --is-interactive
        command codex $argv
        return $status
    end

    set -l codex_bin (command -s codex)
    if test -z "$codex_bin"
        echo "codex executable not found" >&2
        return 127
    end

    ~/.config/fish/codex-pty-wrapper.py $codex_bin $argv
    return $status
end
