import httpx
import os

class CoreServiceClient:
    def __init__(self):
        self.base_url = os.getenv("CORE_SERVICE_URL", "http://localhost:8001/api/v1")

    async def get_role_for_session(self, session_id: str) -> str | None:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/interviews/{session_id}/role")
                response.raise_for_status()
                return response.text
            except httpx.HTTPStatusError as e:
                # Handle 404 Not Found specifically
                if e.response.status_code == 404:
                    return None
                raise
