if status --is-interactive
    # Rust re-implementation
    set rust_tools batcat fdfind dust eza procs rg sd
    for tool in $rust_tools
        if command -v $tool >/dev/null
            switch $tool
                case batcat
                    abbr cat "batcat"
                case fdfind
                    abbr find "fdfind"
                    abbr findempty "fdfind --type empty | xargs -r rmdir"
                case dust
                    abbr du "dust"
                case eza
                    abbr ls "eza"
                    abbr ltr "eza -l --sort new"
                    abbr lt "eza -l --sort old"
                    abbr lhs "eza -l --sort size"
                    abbr lhn "eza -l --sort name"
                    abbr ll "eza -ahl --git"
                    abbr lst "eza -T --git-ignore"
                    abbr lsd "eza -D"
                    abbr sl "eza"
                    abbr s "eza"
                    abbr l "eza"
                    abbr ks "eza"
                case procs
                    abbr ps "procs"
                case rg
                    abbr grep "rg"
                case sd
                    abbr sed "sd"
            end
        end
    end
end
