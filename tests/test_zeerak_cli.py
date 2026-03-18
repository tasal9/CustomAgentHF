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
        completed = self.run_cli("--list-features", "--max-width", "80")

        self.assertEqual(completed.returncode, 0, msg=completed.stderr)
        lines = completed.stdout.strip().splitlines()
        self.assertTrue(lines)
        self.assertTrue(all(len(line) <= 80 for line in lines))
        self.assertIn("...", completed.stdout)

    def test_list_features_no_truncate_prints_full_width(self) -> None:
        completed = self.run_cli("--list-features", "--no-truncate")

        self.assertEqual(completed.returncode, 0, msg=completed.stderr)
        self.assertIn("Public services, documents, and everyday guidance for Afghan users.", completed.stdout)
        self.assertNotIn("...", completed.stdout)

    def test_max_width_rejected_for_json_output(self) -> None:
        completed = self.run_cli("--search-features", "curriculum", "--output", "json", "--max-width", "80")

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("--max-width can only be used with --output table", completed.stderr)

    def test_no_truncate_rejected_for_json_output(self) -> None:
        completed = self.run_cli("--search-features", "curriculum", "--output", "json", "--no-truncate")

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("--no-truncate can only be used with --output table", completed.stderr)

    def test_help_output_mentions_discovery_options(self) -> None:
        completed = self.run_cli("--help")

        self.assertEqual(completed.returncode, 0, msg=completed.stderr)
        self.assertIn("--search-features", completed.stdout)
        self.assertIn("--output", completed.stdout)
        self.assertIn("--max-width", completed.stdout)
        self.assertIn("--no-truncate", completed.stdout)

    def test_feature_run_output_does_not_preprint_model_line(self) -> None:
        completed = self.run_cli("--feature", "chat", "--task", "hello")

        if completed.returncode != 0:
            self.skipTest(completed.stderr.strip() or "chat runtime requires configured model access")

        self.assertIn("[answer]", completed.stdout)
        answer_index = completed.stdout.index("[answer]")
        self.assertNotIn("[model]", completed.stdout[:answer_index])

    def test_list_and_search_features_are_mutually_exclusive(self) -> None:
        completed = self.run_cli("--list-features", "--search-features", "curriculum")

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("cannot be used together", completed.stderr)


if __name__ == "__main__":
    unittest.main()
