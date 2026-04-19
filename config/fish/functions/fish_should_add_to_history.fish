function fish_should_add_to_history
    set -l commandline $argv[1]

    if string match -qr '^\s*$' -- $commandline
        return 1
    end

    # Preserve fish's default convention: commands prefixed with a space stay out of history.
    if string match -qr '^\s' -- $commandline
        return 1
    end

    set -l sensitive_patterns \
        '^\s*(?:sudo\s+)?(?:vault|mysql|psql|redis-cli|aws|gcloud|openssl|sshpass)\b' \
        '^\s*(?:sudo\s+)?gh\s+auth\b' \
        '^\s*(?:sudo\s+)?docker\s+login\b'

    for pattern in $sensitive_patterns
        if string match -qr -- $pattern $commandline
            return 1
        end
    end

    return 0
end
