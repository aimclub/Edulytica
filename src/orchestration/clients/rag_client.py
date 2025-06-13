from httpx import AsyncClient


class RagClient:
    def __init__(self, http_client: AsyncClient, base_url: str):
        self._http_client = http_client
        self._base_url = base_url

    async def enrich_prompt(self, prompt: str) -> str:
        """
        Обогащаем промт...
        """
        pass
