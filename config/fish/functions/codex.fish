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

    set -l codex_args $argv
    if contains -- --oss $argv; and contains -- ollama $argv; and contains -- gpt-oss:120b $argv; and not contains -- --profile $argv; and test -f "$HOME/.codex/ollama-launch.config.toml"
        set -a codex_args --profile ollama-launch
    end

    $HOME/.config/fish/codex-pty-wrapper.py $codex_bin $codex_args
    return $status
end
