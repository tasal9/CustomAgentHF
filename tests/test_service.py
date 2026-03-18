import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from customagenthf.service import app
from customagenthf.zeerak.agents import FeatureRunResult


class ServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_health_endpoint_reports_service_status(self) -> None:
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["service"], "customagenthf")
        self.assertGreater(payload["feature_count"], 0)

    def test_features_endpoint_filters_by_query(self) -> None:
        response = self.client.get("/features", params={"query": "curriculum"})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["features"][0]["name"], "education")

    def test_route_endpoint_returns_feature_and_reason(self) -> None:
        response = self.client.post("/feature/route", json={"task": "Help me with my homework"})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn(payload["feature"], {"education", "chat"})
        self.assertTrue(payload["reason"])

    def test_feature_run_endpoint_returns_structured_payload(self) -> None:
        fake_result = FeatureRunResult(
            requested_feature="hunar",
            feature="hunar",
            model="demo-model",
            raw_answer="raw summary",
            formatted_answer="## Summary\nStrong junior developer profile.",
            structured={"summary": "Strong junior developer profile."},
            fallback_note=None,
            route_reason=None,
        )

        with patch("customagenthf.service.run_feature_result", return_value=fake_result):
            response = self.client.post(
                "/feature/run",
                json={"feature": "hunar", "task": "Build me a CV summary", "output_mode": "markdown"},
            )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["feature"], "hunar")
        self.assertEqual(payload["model"], "demo-model")
        self.assertEqual(payload["structured"], {"summary": "Strong junior developer profile."})

    def test_feature_run_rejects_unknown_feature(self) -> None:
        response = self.client.post("/feature/run", json={"feature": "unknown", "task": "test"})

        self.assertEqual(response.status_code, 400)
        self.assertIn("Unsupported feature", response.json()["detail"])


if __name__ == "__main__":
    unittest.main()