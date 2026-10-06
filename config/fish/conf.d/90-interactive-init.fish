if status --is-interactive
    # Set up Cargo PATH before looking for Starship.
    if test -f "$HOME/.cargo/env.fish"
        source "$HOME/.cargo/env.fish"
    end

    # Node and Codex installed through NVM.
    if test -d "$HOME/.nvm/versions/node/v20.19.3/bin"
        set -gx PATH "$HOME/.nvm/versions/node/v20.19.3/bin" $PATH
    end

    # prompt setting (using starship)
    if command -v starship >/dev/null
        starship init fish | source
    end

    # Greeting setting
    set fish_greeting "Where there is a will, there is a way."
end
