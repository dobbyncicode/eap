#!/bin/sh

set_shell_activation() {
    shell=$1
    core_py="${HOME}/.eap/core.py"

    sync_func="__eap_sync() {
    eval \$(python3 $core_py sync $shell \"\$EAP_LAST_MTIME\")
}
"

    case "$shell" in
        zsh)
            echo "$sync_func"
            echo "precmd_functions+=(__eap_sync)"
            echo "__eap_sync"
            ;;
        bash)
            echo "$sync_func"
            echo "PROMPT_COMMAND=\"\${PROMPT_COMMAND:+\$PROMPT_COMMAND; }__eap_sync\""
            echo "__eap_sync"
            ;;
        fish)
            echo "function __eap_sync"
            echo "    eval (python3 $core_py sync fish \"\$EAP_LAST_MTIME\")"
            echo "end"
            echo "function __eap_prompt_hook --on-event fish_prompt"
            echo "    __eap_sync"
            echo "end"
            echo "__eap_sync"
            ;;
        nu|nushell)
            echo "def __eap_sync { load-env (python3 $core_py sync nu \$EAP_LAST_MTIME | from json) }"
            echo "echo 'eap activated'"
            echo "__eap_sync"
            ;;
        *)
            echo "eap: unknown shell '$shell'" >&2
            return 1
            ;;
    esac
}

[ "$#" -gt 0 ] && set_shell_activation "$1"