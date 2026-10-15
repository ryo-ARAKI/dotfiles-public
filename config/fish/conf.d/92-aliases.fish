if status --is-interactive
    # Confirm before overwriting or removing files
    alias cp "cp -i"
    alias mv "mv -i"
    alias rm "rm -i"

    # Correct a common cd typo
    alias dc "cd"

    # Suppress GUI application stderr
    alias eog "eog 2>/dev/null"
    alias vlc "vlc 2>/dev/null"
    alias evince "evince 2>/dev/null"

    # Clear the terminal
    alias c "clear"

    # Julia MPI launcher (quote the path for home directories containing spaces)
    alias mpiexecjl '"$HOME/.julia/bin/mpiexecjl"'
end
