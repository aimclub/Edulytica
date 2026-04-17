from httpx import AsyncClient, HTTPStatusError


class RagClient:
    def __init__(self, http_client: AsyncClient, base_url: str) -> None:
        self._http_client = http_client
        self._base_url = base_url

    async def enrich_prompt(
            self,
            original_prompt: str,
            document_text: str,
            event_name: str
    ) -> str:
        enrich_url = f"{self._base_url}/api/rag/v1/get_result"

        payload = {
            "prompt": original_prompt,
            "text": document_text,
            "event_name": event_name,
        }

        try:
            response = await self._http_client.post(
                url=enrich_url,
                json=payload,
                timeout=120.0
            )

            response.raise_for_status()

            data = response.json()
            enriched_prompt = data.get("result")

            if not enriched_prompt:
                print("RAG service response did not contain 'result' field.")
                return original_prompt
            return enriched_prompt

        except HTTPStatusError as _hse:
            print(
                f"RAG service returned an HTTP error: {_hse.response.status_code} - {_hse.response.text}")
            return original_prompt
        except Exception as _e:
            print(f"An unexpected error occurred during RAG call: {_e}")
            return original_prompt
