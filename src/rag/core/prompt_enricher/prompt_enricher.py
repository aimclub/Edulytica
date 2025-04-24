from typing import List
from core.utils.config_loader import ConfigLoader

class PromptEnricher:
    """
    Class for enriching prompts based on specific details
    """
    def enrich_prompt(self, base_prompt: str, specifics: List[str]) -> str:
        """
        Combines the base prompt and a list of specific details
        :param base_prompt: Original prompt
        :param specifics: List of strings with specific information

        :return: Enriched prompt as a string
        """
        if not specifics:
            return base_prompt
        # Get prefix from configuration
        prefix = ConfigLoader().get_additional_info_prefix()
        specifics_text = "\n\n".join(specifics)
        info_block = f"{prefix}\n{specifics_text}"
        if base_prompt:
            return f"{base_prompt}\n\n{info_block}"
        return info_block
