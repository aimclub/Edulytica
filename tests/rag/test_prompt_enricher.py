import unittest
import os
from unittest.mock import patch, MagicMock

from Edulytica.src.rag.core.prompt_enricher.prompt_enricher import PromptEnricher


class TestPromptEnricher(unittest.TestCase):
    """Tests for PromptEnricher class"""

    def setUp(self):
        """Set up the test environment"""
        # Create a mock for ConfigLoader
        self.config_loader_patcher = patch('Edulytica.src.rag.core.prompt_enricher.prompt_enricher.ConfigLoader')
        self.mock_config_loader = self.config_loader_patcher.start()

        # Configure mock to return a known prefix value
        mock_instance = MagicMock()
        mock_instance.get_additional_info_prefix.return_value = "Additional Information:"
        self.mock_config_loader.return_value = mock_instance

        # Create an instance of the tested class
        self.prompt_enricher = PromptEnricher()

    def tearDown(self):
        """Clean up after tests"""
        self.config_loader_patcher.stop()

    def test_enrich_prompt_with_specifics(self):
        """Test prompt enrichment with specific details"""
        base_prompt = "Analyze the scientific article"
        specifics = [
            "The conference accepts papers in Russian and English",
            "The paper must be at least 4 pages long",
            "File format - PDF"
        ]

        enriched = self.prompt_enricher.enrich_prompt(base_prompt, specifics)

        # Check that the base prompt is included
        self.assertIn(base_prompt, enriched)

        # Check that the prefix is included
        self.assertIn("Additional Information:", enriched)

        # Check that all specific details are included
        for specific in specifics:
            self.assertIn(specific, enriched)

    def test_enrich_prompt_without_specifics(self):
        """Test prompt enrichment without specific details"""
        base_prompt = "Analyze the scientific article"
        specifics = []

        enriched = self.prompt_enricher.enrich_prompt(base_prompt, specifics)

        # If no specific details, should return the base prompt
        self.assertEqual(enriched, base_prompt)

    def test_enrich_prompt_without_base_prompt(self):
        """Test enrichment with an empty base prompt"""
        base_prompt = ""
        specifics = ["Requirement 1", "Requirement 2"]

        enriched = self.prompt_enricher.enrich_prompt(base_prompt, specifics)

        # Check that the result contains only the information block
        self.assertIn("Additional Information:", enriched)
        self.assertIn("Requirement 1", enriched)
        self.assertIn("Requirement 2", enriched)
        # Check that there are no empty lines at the beginning (base prompt is absent)
        self.assertTrue(enriched.startswith("Additional Information:"))


if __name__ == '__main__':
    unittest.main()