if status --is-interactive
    function __fish_should_delete_failed_history --argument-names commandline
        if string match -qr '^\s*$' -- $commandline
            return 1
        end

        set -l noisy_patterns \
            '^\s*(?:builtin\s+)?(?:ls|pwd|cd|clear|history|dirh|prevd|nextd|cdh)\b' \
            '^\s*(?:builtin\s+)?(?:z|zo)\b' \
            '^\s*(?:command\s+)?eza\b' \
            '^\s*(?:command\s+)?(?:evince|eog|vlc|mupdf)\b'

        for pattern in $noisy_patterns
            if string match -qr -- $pattern $commandline
                return 0
            end
        end

        return 1
    end

    function __fish_history_cleanup_postexec --on-event fish_postexec --argument-names commandline
        if test $status -eq 0
            return
        end

        if __fish_should_delete_failed_history $commandline
            builtin history delete --exact --case-sensitive -- $commandline >/dev/null 2>/dev/null
        end
    end

    function __fish_history_cleanup_posterror --on-event fish_posterror --argument-names commandline
        if __fish_should_delete_failed_history $commandline
            builtin history delete --exact --case-sensitive -- $commandline >/dev/null 2>/dev/null
        end
    end
end
