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

    set -l has_oss 0
    set -l has_ollama_provider 0
    set -l has_gpt_oss_120b_model 0
    set -l has_model_catalog_json 0

    for index in (seq (count $argv))
        set -l arg $argv[$index]
        set -l next_index (math $index + 1)

        switch $arg
            case --oss
                set has_oss 1
            case --local-provider=ollama
                set has_ollama_provider 1
            case --local-provider
                if test $next_index -le (count $argv); and test "$argv[$next_index]" = ollama
                    set has_ollama_provider 1
                end
            case -m --model
                if test $next_index -le (count $argv); and test "$argv[$next_index]" = gpt-oss:120b
                    set has_gpt_oss_120b_model 1
                end
            case --model=gpt-oss:120b
                set has_gpt_oss_120b_model 1
            case -c --config
                if test $next_index -le (count $argv); and string match -q "*model_catalog_json=*" -- $argv[$next_index]
                    set has_model_catalog_json 1
                end
            case --config="*model_catalog_json=*"
                set has_model_catalog_json 1
        end
    end

    set -l codex_args $argv
    if test $has_oss -eq 1; and test $has_ollama_provider -eq 1; and test $has_gpt_oss_120b_model -eq 1; and test $has_model_catalog_json -eq 0
        set -a codex_args -c "model_catalog_json=\"/home/ryo/.codex/model-catalogs/gpt-oss.json\""
    end

    $HOME/.config/fish/codex-pty-wrapper.py $codex_bin $codex_args
    return $status
end
