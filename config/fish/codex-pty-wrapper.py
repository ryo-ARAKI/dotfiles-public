#!/usr/bin/env python3

import fcntl
import os
import pty
import select
import signal
import sys
import termios
import tty


CTRL_C = b"\x03"
CTRL_RIGHT_BRACKET = b"\x1d"


def transform_input(data: bytes) -> bytes:
    return data.replace(CTRL_C, b"").replace(CTRL_RIGHT_BRACKET, b"")


def wants_sigint(data: bytes) -> bool:
    return CTRL_RIGHT_BRACKET in data


def sync_winsize(source_fd: int, target_fd: int) -> None:
    packed = fcntl.ioctl(source_fd, termios.TIOCGWINSZ, b"\0" * 8)
    fcntl.ioctl(target_fd, termios.TIOCSWINSZ, packed)


def main() -> int:
    argv = sys.argv[1:] or ["codex"]
    stdin_fd = sys.stdin.fileno()
    stdout_fd = sys.stdout.fileno()
    pid, master_fd = pty.fork()
    if pid == 0:
        os.execvp(argv[0], argv)

    old_tty = termios.tcgetattr(stdin_fd)
    previous_sigint = signal.signal(signal.SIGINT, signal.SIG_IGN)
    previous_sigwinch = signal.getsignal(signal.SIGWINCH)

    def handle_sigwinch(_signum, _frame):
        sync_winsize(stdin_fd, master_fd)

    try:
        signal.signal(signal.SIGWINCH, handle_sigwinch)
        sync_winsize(stdin_fd, master_fd)
        tty.setraw(stdin_fd)

        while True:
            readable, _, _ = select.select([stdin_fd, master_fd], [], [])
            if stdin_fd in readable:
                data = os.read(stdin_fd, 1024)
                if not data:
                    break

                if wants_sigint(data):
                    try:
                        os.kill(pid, signal.SIGINT)
                    except ProcessLookupError:
                        pass

                forwarded = transform_input(data)
                if forwarded:
                    os.write(master_fd, forwarded)

            if master_fd in readable:
                try:
                    data = os.read(master_fd, 1024)
                except OSError:
                    break

                if not data:
                    break
                os.write(stdout_fd, data)
    finally:
        termios.tcsetattr(stdin_fd, termios.TCSADRAIN, old_tty)
        signal.signal(signal.SIGINT, previous_sigint)
        signal.signal(signal.SIGWINCH, previous_sigwinch)
        try:
            os.close(master_fd)
        except OSError:
            pass

    _, status = os.waitpid(pid, 0)
    return os.waitstatus_to_exitcode(status)


if __name__ == "__main__":
    raise SystemExit(main())
