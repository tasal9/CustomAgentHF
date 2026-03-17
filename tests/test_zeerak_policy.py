import unittest

from customagenthf.zeerak import apply_tabib_policy


class TabibPolicyTests(unittest.TestCase):
    def test_emergency_keywords_trigger_emergency_response(self) -> None:
        emergency, message = apply_tabib_policy("My father has chest pain and cannot breathe")

        self.assertTrue(emergency)
        self.assertIn("Call local emergency services", message)

    def test_non_emergency_requests_return_safe_prompt(self) -> None:
        emergency, message = apply_tabib_policy("I have a mild cough for two days")

        self.assertFalse(emergency)
        self.assertIn("structured triage style", message)


if __name__ == "__main__":
    unittest.main()
