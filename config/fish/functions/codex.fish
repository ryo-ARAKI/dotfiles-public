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

    set -l has_profile 0
    set -l has_oss 0
    set -l has_local_provider 0
    set -l has_ollama_provider 0
    set -l has_model 0
    set -l has_gpt_oss_120b_model 0
    set -l has_model_catalog_json 0
    set -l effective_cwd $PWD

    for index in (seq (count $argv))
        set -l arg $argv[$index]
        set -l next_index (math $index + 1)

        switch $arg
            case -p --profile
                set has_profile 1
            case --profile="*"
                set has_profile 1
            case --oss
                set has_oss 1
            case --local-provider=ollama
                set has_local_provider 1
                set has_ollama_provider 1
            case --local-provider="*"
                set has_local_provider 1
            case --local-provider
                set has_local_provider 1
                if test $next_index -le (count $argv); and test "$argv[$next_index]" = ollama
                    set has_ollama_provider 1
                end
            case -C --cd
                if test $next_index -le (count $argv)
                    set -l resolved_cwd (command realpath "$argv[$next_index]" 2>/dev/null)
                    if test -n "$resolved_cwd"
                        set effective_cwd $resolved_cwd
                    else
                        set effective_cwd $argv[$next_index]
                    end
                end
            case --cd="*"
                set -l cd_arg (string replace -- "--cd=" "" $arg)
                set -l resolved_cwd (command realpath "$cd_arg" 2>/dev/null)
                if test -n "$resolved_cwd"
                    set effective_cwd $resolved_cwd
                else
                    set effective_cwd $cd_arg
                end
            case -m --model
                set has_model 1
                if test $next_index -le (count $argv); and test "$argv[$next_index]" = gpt-oss:120b
                    set has_gpt_oss_120b_model 1
                end
            case --model=gpt-oss:120b
                set has_model 1
                set has_gpt_oss_120b_model 1
            case --model="*"
                set has_model 1
            case -c --config
                if test $next_index -le (count $argv); and string match -q "*model_catalog_json=*" -- $argv[$next_index]
                    set has_model_catalog_json 1
                end
            case --config="*model_catalog_json=*"
                set has_model_catalog_json 1
        end
    end

    set -l resume_session_id ""
    set -l resume_uses_last 0
    set -l resume_all_sessions 0
    set -l resume_include_non_interactive 0
    set -l parsing_resume_args 0
    set -l skip_next_resume_arg 0
    for index in (seq (count $argv))
        set -l arg $argv[$index]

        if test $skip_next_resume_arg -eq 1
            set skip_next_resume_arg 0
            continue
        end

        if test $parsing_resume_args -eq 0
            switch $arg
                case -c --config -i --image -m --model -p --profile -s --sandbox -C --cd --add-dir -a --ask-for-approval --local-provider --enable --disable --remote --remote-auth-token-env
                    set skip_next_resume_arg 1
                case --config="*" --image="*" --model="*" --profile="*" --sandbox="*" --cd="*" --add-dir="*" --ask-for-approval="*" --local-provider="*" --enable="*" --disable="*" --remote="*" --remote-auth-token-env="*" --all --include-non-interactive --strict-config --oss --search --no-alt-screen --dangerously-bypass-approvals-and-sandbox --dangerously-bypass-hook-trust
                    continue
                case resume
                    set parsing_resume_args 1
                case "*"
                    break
            end
            continue
        end

        switch $arg
            case -c --config -i --image -m --model -p --profile -s --sandbox -C --cd --add-dir -a --ask-for-approval --local-provider --enable --disable --remote --remote-auth-token-env
                set skip_next_resume_arg 1
            case --last
                set resume_uses_last 1
            case --all
                set resume_all_sessions 1
            case --include-non-interactive
                set resume_include_non_interactive 1
            case --config="*" --image="*" --model="*" --profile="*" --sandbox="*" --cd="*" --add-dir="*" --ask-for-approval="*" --local-provider="*" --enable="*" --disable="*" --remote="*" --remote-auth-token-env="*" --strict-config --oss --search --no-alt-screen --dangerously-bypass-approvals-and-sandbox --dangerously-bypass-hook-trust
                continue
            case "-*"
                continue
            case "*"
                if test $resume_uses_last -eq 1; or test $resume_all_sessions -eq 1
                    break
                end
                set resume_session_id $arg
                break
        end
    end

    set -l should_restore_gpt_oss_resume 0
    if test -d "$HOME/.codex/sessions"
        set -l session_file ""
        if test -n "$resume_session_id"
            if string match -qr '^[0-9A-Fa-f-]+$' -- "$resume_session_id"; and test (string length -- "$resume_session_id") -ge 8
                set session_file (find "$HOME/.codex/sessions" -type f -name "*.jsonl" -print 2>/dev/null | python3 -c 'import os, re, sys
needle = sys.argv[1].lower()
uuid_re = re.compile(r"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})\.jsonl$")
for line in sys.stdin:
    path = line.rstrip("\n")
    match = uuid_re.search(os.path.basename(path))
    if match and match.group(1).lower().startswith(needle):
        print(path)
        break
' "$resume_session_id" 2>/dev/null)
            end
            if test -z "$session_file"; and test -f "$HOME/.codex/session_index.jsonl"
                set -l lookup_session_id (python3 -c 'import json, sys
needle = sys.argv[2]
for line in open(sys.argv[1], encoding="utf-8"):
    try:
        row = json.loads(line)
    except json.JSONDecodeError:
        continue
    if row.get("thread_name") == needle:
        print(row.get("id", ""))
        break
' "$HOME/.codex/session_index.jsonl" "$resume_session_id" 2>/dev/null)
                if test -n "$lookup_session_id"
                    set session_file (find "$HOME/.codex/sessions" -type f -name "*$lookup_session_id*.jsonl" -print -quit 2>/dev/null)
                end
            end
        else if test $resume_uses_last -eq 1
            for candidate in (find "$HOME/.codex/sessions" -type f -name "*.jsonl" -printf "%T@ %p\n" 2>/dev/null | sort -nr | string replace -r '^[^ ]+ ' '')
                set -l candidate_probe (head -n 5 "$candidate" 2>/dev/null | string collect)
                if test $resume_include_non_interactive -eq 0
                    if string match -q '*"source":"exec"*' -- $candidate_probe; or string match -q '*"originator":"codex_exec"*' -- $candidate_probe
                        continue
                    end
                end

                if test $resume_all_sessions -eq 1
                    set session_file $candidate
                    break
                end

                if string match -q "*\"cwd\":\"$effective_cwd\"*" -- $candidate_probe
                    set session_file $candidate
                    break
                end
            end
        end

        if test -n "$session_file"
            set -l session_probe (head -n 20 "$session_file" 2>/dev/null | string collect)
            if string match -q '*"model_provider":"ollama"*' -- $session_probe; and string match -q '*"model":"gpt-oss:120b"*' -- $session_probe
                set should_restore_gpt_oss_resume 1
            end
        end
    end

    set -l has_conflicting_resume_override 0
    if test $has_model -eq 1; and test $has_gpt_oss_120b_model -eq 0
        set has_conflicting_resume_override 1
    end
    if test $has_local_provider -eq 1; and test $has_ollama_provider -eq 0
        set has_conflicting_resume_override 1
    end

    set -l codex_args $argv
    if test $should_restore_gpt_oss_resume -eq 1; and test $has_conflicting_resume_override -eq 0
        set -l resume_prefix_args
        if test $has_profile -eq 0
            set -a resume_prefix_args --profile dgx
        end
        if test $has_oss -eq 0
            set -a resume_prefix_args --oss
            set has_oss 1
        end
        if test $has_local_provider -eq 0
            set -a resume_prefix_args --local-provider ollama
            set has_local_provider 1
            set has_ollama_provider 1
        end
        if test $has_model -eq 0
            set -a resume_prefix_args -m gpt-oss:120b
            set has_model 1
            set has_gpt_oss_120b_model 1
        end

        if test (count $resume_prefix_args) -gt 0
            set codex_args $resume_prefix_args $codex_args
        end
    end
    if test $has_oss -eq 1; and test $has_ollama_provider -eq 1; and test $has_gpt_oss_120b_model -eq 1; and test $has_model_catalog_json -eq 0
        set -a codex_args -c "model_catalog_json=\"/home/ryo/.codex/model-catalogs/gpt-oss.json\""
    end

    $HOME/.config/fish/codex-pty-wrapper.py $codex_bin $codex_args
    return $status
end
