# ~/.bashrc: keep Bash minimal, then hand off to Fish for interactive use.

case $- in
    *i*) ;;
      *) return ;;
esac

if [ -f "$HOME/.shell_env" ]; then
    . "$HOME/.shell_env"
fi

if command -v fish >/dev/null 2>&1; then
    exec fish
fi
