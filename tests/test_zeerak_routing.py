import unittest

from customagenthf.zeerak import (
    FEATURE_OVERVIEW,
    get_feature_spec,
    list_features,
    load_feature_prompt,
    render_feature_table,
    route_feature,
    search_features,
)


class RouteFeatureTests(unittest.TestCase):
    def test_defaults_to_chat_when_no_keywords_match(self) -> None:
        feature, reason = route_feature("Tell me something interesting")

        self.assertEqual(feature, "chat")
        self.assertIn("defaulted to chat", reason)

    def test_prefers_feature_with_highest_keyword_score(self) -> None:
        feature, reason = route_feature("I need Python debugging help for my HTML and CSS homework")

        self.assertEqual(feature, "codekhana")
        self.assertIn("Matched", reason)

    def test_feature_metadata_is_typed_and_exposed(self) -> None:
        spec = get_feature_spec("education")

        self.assertEqual(spec.name, "education")
        self.assertTrue(spec.search_enabled)
        self.assertTrue(spec.tool_calling_enabled)
        self.assertEqual(FEATURE_OVERVIEW["education"], spec.overview)

    def test_prompt_is_loaded_from_package_data(self) -> None:
        prompt = load_feature_prompt("chat")

        self.assertIn("Zeerak Chat", prompt)

    def test_list_features_returns_typed_specs(self) -> None:
        features = list_features(include_auto=False)

        self.assertTrue(all(feature.name != "auto" for feature in features))
        self.assertEqual(features[0].name, "chat")

    def test_search_features_matches_name_and_overview(self) -> None:
        by_name = search_features("tab")
        by_overview = search_features("curriculum")

        self.assertEqual([feature.name for feature in by_name], ["tabib"])
        self.assertEqual([feature.name for feature in by_overview], ["education"])

    def test_render_feature_table_matches_expected_snapshot(self) -> None:
        features = search_features("curriculum")

        expected = (
            "feature   | capabilities         | default-model             | overview                                            \n"
            "----------+----------------------+---------------------------+-----------------------------------------------------\n"
            "education | search, tool-calling | Qwen/Qwen2.5-72B-Instruct | Curriculum-aligned tutoring for Afghan classes 6-12."
        )
        self.assertEqual(render_feature_table(features), expected)


if __name__ == "__main__":
    unittest.main()
