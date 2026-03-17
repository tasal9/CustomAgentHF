import json
import subprocess
import sys
import unittest


class ZeerakCliTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "customagenthf", "zeerak", *args],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_search_features_json_output_is_machine_readable(self) -> None:
        completed = self.run_cli("--search-features", "curriculum", "--output", "json")

        self.assertEqual(completed.returncode, 0, msg=completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload[0]["name"], "education")
        self.assertEqual(payload[0]["capabilities"], ["search", "tool-calling"])

    def test_list_features_respects_max_width(self) -> None:
        completed = self.run_cli("--list-features", "--max-width", "60")

        self.assertEqual(completed.returncode, 0, msg=completed.stderr)
        lines = completed.stdout.strip().splitlines()
        self.assertTrue(lines)
        self.assertTrue(all(len(line) <= 60 for line in lines))
        self.assertIn("...", completed.stdout)

    def test_max_width_rejected_for_json_output(self) -> None:
        completed = self.run_cli("--search-features", "curriculum", "--output", "json", "--max-width", "80")

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("--max-width can only be used with --output table", completed.stderr)


if __name__ == "__main__":
    unittest.main()
