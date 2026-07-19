import json
import shutil
import subprocess
import unittest
from pathlib import Path


@unittest.skipUnless(shutil.which("codex"), "Codex CLI is required for execpolicy tests")
class CodexRulesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rules_path = Path(__file__).resolve().parents[1] / "config" / "codex" / "rules" / "default.rules"

    def decision_for(self, *command: str) -> str | None:
        result = subprocess.run(
            ["codex", "execpolicy", "check", "--rules", str(self.rules_path), "--", *command],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        return json.loads(result.stdout).get("decision")

    def test_allows_bounded_reads_with_variable_arguments(self) -> None:
        allowed = [
            ("rg", "-n", "different-pattern", "different-file"),
            ("git", "branch", "--show-current"),
            ("git", "branch", "--list", "topic-*"),
            ("git", "worktree", "list", "--porcelain"),
            ("git", "ls-remote", "origin", "refs/heads/main"),
            ("gh", "pr", "view", "123", "--json", "title"),
            ("gh", "issue", "list", "--limit", "20"),
            ("gh", "api", "--method", "GET", "repos/openai/codex"),
            ("codex", "execpolicy", "check", "--pretty", "--", "git", "status"),
        ]
        for command in allowed:
            with self.subTest(command=command):
                self.assertEqual(self.decision_for(*command), "allow")

    def test_does_not_durably_allow_mutation_or_arbitrary_execution(self) -> None:
        not_allowed = [
            ("find", ".", "-delete"),
            ("sed", "-n", "-i", "1p", "file"),
            ("sort", "-o", "/tmp/output", "input"),
            ("pdftotext", "-layout", "input.pdf", "/tmp/output.txt"),
            ("git", "branch", "-D", "topic"),
            ("git", "worktree", "remove", "/tmp/topic"),
            ("git", "push", "origin", "main"),
            ("gh", "api", "--method", "POST", "repos/openai/codex/issues"),
            ("gh", "pr", "create", "--title", "topic"),
            ("bash", "-lc", "git status"),
            ("python3", "-c", "print('arbitrary')"),
            ("julia", "-e", "println(1)"),
            ("timeout", "180s", "git", "status"),
            ("rm", "file"),
        ]
        for command in not_allowed:
            with self.subTest(command=command):
                self.assertNotEqual(self.decision_for(*command), "allow")


if __name__ == "__main__":
    unittest.main()
