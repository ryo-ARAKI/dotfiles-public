import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class FishConfigTests(unittest.TestCase):
    def test_interactive_init_guards_starship_initialization(self) -> None:
        config = (ROOT / "config" / "fish" / "conf.d" / "90-interactive-init.fish").read_text(encoding="utf-8")

        self.assertIn("if command -v starship >/dev/null", config)
        self.assertLess(config.index("if command -v starship >/dev/null"), config.index("starship init fish | source"))


if __name__ == "__main__":
    unittest.main()
