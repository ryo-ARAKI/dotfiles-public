def detect_context(explicit: str | None, environ: dict[str, str]) -> str:
    if explicit in {"local", "remote"}:
        return explicit
    if environ.get("SSH_CONNECTION") or environ.get("SSH_TTY"):
        return "remote"
    return "local"
