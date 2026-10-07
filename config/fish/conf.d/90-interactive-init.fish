# Make NVM-installed Codex available in interactive and non-interactive shells.
# Preserve an existing executable; otherwise use the newest complete installation.
if not command -sq codex
    set -l codex_node_bins "$HOME"/.nvm/versions/node/v*/bin
    if test (count $codex_node_bins) -gt 0
        for codex_node_bin in (printf '%s\n' $codex_node_bins | sort -Vr)
            if test -x "$codex_node_bin/node"; and test -x "$codex_node_bin/codex"
                set -gx PATH "$codex_node_bin" $PATH
                break
            end
        end
    end
end

if status --is-interactive
    # Set up Cargo PATH before looking for Starship.
    if test -f "$HOME/.cargo/env.fish"
        source "$HOME/.cargo/env.fish"
    end

    # prompt setting (using starship)
    if command -v starship >/dev/null
        starship init fish | source
    end

    # Greeting setting
    set fish_greeting "Where there is a will, there is a way."
end
