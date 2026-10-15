#!/usr/bin/env python3
"""Verify a complete latexdiff PDF and prepare pages for visual inspection."""

from __future__ import annotations

import re
import argparse
import json
import os
import shutil
import subprocess
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


class VerificationError(RuntimeError):
    """Raised when a diff-PDF verification gate fails."""


FATAL_LOG_PATTERNS = (
    r"^! LaTeX Error:",
    r"^! Package .+ Error:",
    r"Fatal error occurred",
    r"Emergency stop",
    r"There were undefined references",
    r"There were undefined citations",
)

WARNING_LOG_PATTERNS = (
    r"multiply defined",
    r"There were multiply defined citations",
)


def classify_log(text: str) -> tuple[list[str], list[str]]:
    lines = text.splitlines()
    errors = [
        line
        for line in lines
        if any(re.search(pattern, line) for pattern in FATAL_LOG_PATTERNS)
    ]
    warnings = [
        line
        for line in lines
        if any(re.search(pattern, line) for pattern in WARNING_LOG_PATTERNS)
    ]
    return errors, warnings


def parse_pdfinfo(text: str) -> int:
    match = re.search(r"^Pages:\s+(\d+)\s*$", text, re.MULTILINE)
    if not match or int(match.group(1)) < 1:
        raise VerificationError("pdfinfo did not report a positive page count")
    return int(match.group(1))


def inspection_pages(page_count: int) -> list[int]:
    if page_count < 1:
        raise VerificationError("page count must be positive")
    return sorted({1, (page_count + 1) // 2, page_count})


def run_command(
    args: Sequence[str], *, env: Mapping[str, str]
) -> subprocess.CompletedProcess[str]:
    executable = shutil.which(args[0], path=env.get("PATH"))
    if executable is None:
        raise VerificationError(f"required command not found: {args[0]}")
    try:
        return subprocess.run(
            [executable, *args[1:]],
            text=True,
            capture_output=True,
            check=False,
            timeout=120,
            env=dict(env),
        )
    except subprocess.TimeoutExpired as error:
        raise VerificationError(f"command timed out: {args[0]}") from error
    except OSError as error:
        raise VerificationError(f"could not run {args[0]}: {error}") from error


def command_output(result: subprocess.CompletedProcess[str]) -> str:
    return "\n".join(part.strip() for part in (result.stdout, result.stderr) if part.strip())


def write_report(output_dir: Path, report: dict[str, Any]) -> Path:
    report_path = output_dir / "verification.json"
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report_path


def main(
    argv: Sequence[str] | None = None,
    *,
    env: Mapping[str, str] | None = None,
) -> int:
    parser = argparse.ArgumentParser(
        description="Verify a complete latexdiff PDF and render first/middle/last pages."
    )
    parser.add_argument("--pdf", required=True, help="complete diff PDF")
    parser.add_argument("--log", required=True, help="LaTeX build log")
    parser.add_argument("--output-dir", required=True, help="verification output directory")
    args = parser.parse_args(argv)

    pdf = Path(args.pdf).expanduser().resolve()
    log = Path(args.log).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    process_env = dict(os.environ if env is None else env)
    report: dict[str, Any] = {
        "pdf": str(pdf),
        "log": str(log),
        "page_count": None,
        "inspection_pages": [],
        "rendered_images": [],
        "checks": {},
        "warnings": [],
        "errors": [],
    }

    try:
        if not pdf.is_file():
            raise VerificationError(f"PDF file not found: {pdf}")
        if not log.is_file():
            raise VerificationError(f"log file not found: {log}")

        log_text = log.read_text(encoding="utf-8", errors="replace")
        log_errors, log_warnings = classify_log(log_text)
        report["errors"].extend(log_errors)
        report["warnings"].extend(log_warnings)
        report["checks"]["log"] = {
            "fatal_count": len(log_errors),
            "warning_count": len(log_warnings),
        }
        if log_errors:
            report_path = write_report(output_dir, report)
            print(report_path)
            return 1

        pdfinfo_result = run_command(["pdfinfo", str(pdf)], env=process_env)
        report["checks"]["pdfinfo"] = {
            "exit_code": pdfinfo_result.returncode,
            "output": command_output(pdfinfo_result),
        }
        if pdfinfo_result.returncode != 0:
            raise VerificationError(
                f"pdfinfo failed with exit code {pdfinfo_result.returncode}"
            )
        page_count = parse_pdfinfo(pdfinfo_result.stdout)
        pages = inspection_pages(page_count)
        report["page_count"] = page_count
        report["inspection_pages"] = pages

        qpdf_result = run_command(["qpdf", "--check", str(pdf)], env=process_env)
        report["checks"]["qpdf"] = {
            "exit_code": qpdf_result.returncode,
            "output": command_output(qpdf_result),
        }
        if qpdf_result.returncode == 3:
            report["warnings"].append("qpdf completed with warnings (exit code 3)")
        elif qpdf_result.returncode != 0:
            raise VerificationError(
                f"qpdf structural check failed with exit code {qpdf_result.returncode}"
            )

        render_checks: list[dict[str, Any]] = []
        for page in pages:
            prefix = output_dir / f"page-{page:03d}"
            image = Path(f"{prefix}.png")
            if image.exists():
                image.unlink()
            render_result = run_command(
                [
                    "pdftoppm",
                    "-png",
                    "-r",
                    "144",
                    "-f",
                    str(page),
                    "-l",
                    str(page),
                    "-singlefile",
                    str(pdf),
                    str(prefix),
                ],
                env=process_env,
            )
            render_checks.append(
                {
                    "page": page,
                    "exit_code": render_result.returncode,
                    "output": command_output(render_result),
                }
            )
            if render_result.returncode != 0:
                raise VerificationError(
                    f"pdftoppm failed for page {page} with exit code {render_result.returncode}"
                )
            if not image.is_file():
                raise VerificationError(f"rendered image missing for page {page}: {image}")
            report["rendered_images"].append(str(image))
        report["checks"]["renders"] = render_checks
    except VerificationError as error:
        report["errors"].append(str(error))

    report_path = write_report(output_dir, report)
    print(report_path)
    return 0 if not report["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
