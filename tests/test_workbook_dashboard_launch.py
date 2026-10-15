import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "bin/workbook-dashboard-launch"


class WorkbookDashboardLaunchTests(unittest.TestCase):
    def run_launcher(self, import_status=0, dev_status=0, arguments=None):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        directory = Path(temporary.name)
        npm = directory / "npm"
        npm.write_text('''#!/usr/bin/env python3
import json, os, sys
with open(os.environ["CALLS"], "a") as output:
    output.write(json.dumps(sys.argv[1:]) + "\\n")
sys.exit(int(os.environ["IMPORT_STATUS" if sys.argv[2] == "simple:import" else "DEV_STATUS"]))
''')
        npm.chmod(0o755)
        calls = directory / "calls.jsonl"
        log = directory / "launch.log"
        if arguments is None:
            arguments = ["--workbook", "inputs/example workbook.xlsx", "--log", str(log)]
        result = subprocess.run(
            ["bash", str(SCRIPT), *arguments], cwd=directory,
            env={**os.environ, "PATH": str(directory) + os.pathsep + os.environ["PATH"],
                 "CALLS": str(calls), "IMPORT_STATUS": str(import_status), "DEV_STATUS": str(dev_status)},
            stdin=subprocess.DEVNULL, capture_output=True, text=True,
        )
        commands = [json.loads(line) for line in calls.read_text().splitlines()] if calls.exists() else []
        return result, commands, log

    def test_workbook_argument_is_preserved_and_server_exit_status_is_returned(self):
        result, calls, log = self.run_launcher(dev_status=5)
        self.assertEqual(result.returncode, 5, result.stderr)
        self.assertEqual(calls, [
            ["run", "simple:import", "--", "inputs/example workbook.xlsx", "--replace"],
            ["run", "dev"],
        ])
        self.assertIn("import_exit_status=0", log.read_text())
        self.assertIn("dev_exit_status=5", log.read_text())

    def test_failed_import_does_not_start_server(self):
        result, calls, _ = self.run_launcher(import_status=9)
        self.assertEqual(result.returncode, 9, result.stderr)
        self.assertEqual(calls, [["run", "simple:import", "--", "inputs/example workbook.xlsx", "--replace"]])

    def test_missing_workbook_has_no_side_effects(self):
        result, calls, log = self.run_launcher(arguments=[])
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(calls, [])
        self.assertFalse(log.exists())
