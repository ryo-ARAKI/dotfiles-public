if status --is-interactive
    function __fish_history_cleanup_queue_path
        set -l state_home ~/.local/state
        if set -q XDG_STATE_HOME
            set state_home $XDG_STATE_HOME
        end

        echo $state_home/fish/failed-history-delete-queue
    end

    function __fish_history_cleanup_history_path
        set -l data_home ~/.local/share
        if set -q XDG_DATA_HOME
            set data_home $XDG_DATA_HOME
        end

        echo $data_home/fish/fish_history
    end

    function __fish_history_cleanup_ensure_queue_dir
        set -l queue_path (__fish_history_cleanup_queue_path)
        set -l queue_dir (path dirname $queue_path)
        command mkdir -p -- $queue_dir >/dev/null 2>/dev/null
    end

    function __fish_should_queue_failed_history --argument-names commandline
        if string match -qr '^\s*$' -- $commandline
            return 1
        end

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

    function __fish_history_cleanup_queue_failed_entry --argument-names block_index when commandline
        if not __fish_should_queue_failed_history "$commandline"
            return
        end

        if string match -qr '^\s*$' -- $block_index
            return
        end

        if string match -qr '^\s*$' -- $when
            return
        end

        __fish_history_cleanup_ensure_queue_dir

        set -l queue_path (__fish_history_cleanup_queue_path)
        printf '%s\t%s\t%s\n' "$block_index" "$when" "$commandline" >>$queue_path 2>/dev/null
    end

    function __fish_history_cleanup_extract_entry_key
        set -l commandline
        set -l when

        for line in $argv
            if string match -qr '^- cmd: ' -- $line
                set commandline (string replace -r '^- cmd: ' '' -- $line)
            else if string match -qr '^  when: ' -- $line
                set when (string replace -r '^  when: ' '' -- $line)
            end
        end

        if test -n "$commandline"; and test -n "$when"
            printf '%s\t%s\n' "$when" "$commandline"
            return 0
        end

        return 1
    end

    function __fish_history_cleanup_block_matches_queue --argument-names block_index
        set -l block_key (__fish_history_cleanup_extract_entry_key $argv)
        if test (count $block_key) -eq 0
            return 1
        end

        set -l block_queue_key (printf '%s\t%s' "$block_index" "$block_key")
        for queued_key in $__fish_history_cleanup_queue_keys
            if test "$queued_key" = "$block_queue_key"
                return 0
            end
        end

        return 1
    end

    function __fish_history_cleanup_rewrite_history_from_queue
        set -l queue_path (__fish_history_cleanup_queue_path)
        if not test -f $queue_path
            return
        end

        set -e __fish_history_cleanup_queue_keys
        for queued_line in (string split \n -- (string collect < $queue_path))
            if test -n "$queued_line"
                set -ga __fish_history_cleanup_queue_keys $queued_line
            end
        end

        if not set -q __fish_history_cleanup_queue_keys[1]
            return
        end

        set -l history_path (__fish_history_cleanup_history_path)
        if not test -f $history_path
            printf '' >$queue_path 2>/dev/null
            set -e __fish_history_cleanup_queue_keys
            return
        end

        set -l tmp_path $history_path.tmp.$fish_pid
        if not printf '' >$tmp_path 2>/dev/null
            set -e __fish_history_cleanup_queue_keys
            return
        end

        set -l current_block
        set -l block_index 0

        for line in (string split \n -- (string collect < $history_path))
            if string match -q -- '- cmd:*' $line
                if test (count $current_block) -gt 0
                    set block_index (math $block_index + 1)
                    if not __fish_history_cleanup_block_matches_queue $block_index $current_block
                        printf '%s\n' $current_block >>$tmp_path
                    end
                end

                set current_block $line
            else if test (count $current_block) -gt 0
                set -a current_block $line
            else
                printf '%s\n' "$line" >>$tmp_path
            end
        end

        if test (count $current_block) -gt 0
            set block_index (math $block_index + 1)
            if not __fish_history_cleanup_block_matches_queue $block_index $current_block
                printf '%s\n' $current_block >>$tmp_path
            end
        end

        if command mv -- $tmp_path $history_path
            printf '' >$queue_path 2>/dev/null
        else
            command rm -f -- $tmp_path
        end

        set -e __fish_history_cleanup_queue_keys
    end

    function __fish_history_cleanup_find_latest_history_entry --argument-names commandline
        set -l history_path (__fish_history_cleanup_history_path)
        if not test -f $history_path
            return 1
        end

        set -l current_block
        set -l block_index 0
        set -l latest_entry

        for line in (string split \n -- (string collect < $history_path))
            if string match -q -- '- cmd:*' $line
                if test (count $current_block) -gt 0
                    set block_index (math $block_index + 1)

                    set -l block_key (__fish_history_cleanup_extract_entry_key $current_block)
                    if test (count $block_key) -gt 0
                        set -l block_fields (string split -m 1 \t -- $block_key)
                        if test (count $block_fields) -eq 2
                            if test "$block_fields[2]" = "$commandline"
                                set latest_entry (printf '%s\t%s\t%s' "$block_index" "$block_fields[1]" "$block_fields[2]")
                            end
                        end
                    end
                end

                set current_block $line
            else if test (count $current_block) -gt 0
                set -a current_block $line
            end
        end

        if test (count $current_block) -gt 0
            set block_index (math $block_index + 1)

            set -l block_key (__fish_history_cleanup_extract_entry_key $current_block)
            if test (count $block_key) -gt 0
                set -l block_fields (string split -m 1 \t -- $block_key)
                if test (count $block_fields) -eq 2
                    if test "$block_fields[2]" = "$commandline"
                        set latest_entry (printf '%s\t%s\t%s' "$block_index" "$block_fields[1]" "$block_fields[2]")
                    end
                end
            end
        end

        if test (count $latest_entry) -eq 0
            return 1
        end

        printf '%s\n' "$latest_entry"
    end

    function __fish_history_cleanup_queue_latest_exact_history_entry --argument-names commandline
        if not __fish_should_queue_failed_history "$commandline"
            return
        end

        set -l latest_entry (__fish_history_cleanup_find_latest_history_entry "$commandline")
        if test (count $latest_entry) -eq 0
            return
        end

        set -l latest_fields (string split -m 2 \t -- $latest_entry[1])
        if test (count $latest_fields) -ne 3
            return
        end

        set -l block_index $latest_fields[1]
        set -l when $latest_fields[2]
        set -l latest_commandline $latest_fields[3]
        if test "$latest_commandline" != "$commandline"
            return
        end

        __fish_history_cleanup_queue_failed_entry $block_index $when "$latest_commandline"
    end

    function __fish_history_cleanup_preexec --on-event fish_preexec --argument-names commandline
        set -g __fish_history_cleanup_last_commandline $commandline
    end

    function __fish_history_cleanup_on_prompt --on-event fish_prompt
        set -l last_status $status

        if not set -q __fish_history_cleanup_queue_processed
            set -g __fish_history_cleanup_queue_processed 1
            __fish_history_cleanup_rewrite_history_from_queue
        end

        if not set -q __fish_history_cleanup_last_commandline
            return
        end

        set -l commandline $__fish_history_cleanup_last_commandline
        set -e __fish_history_cleanup_last_commandline

        if test $last_status -eq 0
            return
        end

        __fish_history_cleanup_queue_latest_exact_history_entry "$commandline"
    end

    function __fish_history_cleanup_posterror --on-event fish_posterror --argument-names commandline
        set -e __fish_history_cleanup_last_commandline
        __fish_history_cleanup_queue_latest_exact_history_entry "$commandline"
    end
end
