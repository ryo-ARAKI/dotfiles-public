if status --is-interactive
    # prompt setting (using starship)
    if command -v starship >/dev/null
        starship init fish | source
    end

    # Greeting setting
    set fish_greeting "Where there is a will, there is a way."
end
