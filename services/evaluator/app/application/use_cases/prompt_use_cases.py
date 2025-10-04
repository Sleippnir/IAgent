from datetime import datetime
from typing import List, Optional, Dict, Any
from ...domain.entities.prompt import Prompt
from ...domain.repositories.prompt_repository import PromptRepository

class PromptUseCases:
    def __init__(self, repository: PromptRepository):
        self.repository = repository
    
    async def create_prompt(self, template: str, parameters: Dict[str, Any], model: str, max_tokens: int, temperature: float) -> Prompt:
        prompt = Prompt(
            id=str(datetime.now().timestamp()),
            template=template,
            parameters=parameters,
            created_at=datetime.now(),
            model=model,
            max_tokens=max_tokens,
            temperature=temperature
        )
        return await self.repository.create(prompt)
    
    async def get_prompt(self, prompt_id: str) -> Optional[Prompt]:
        return await self.repository.get(prompt_id)
    
    async def list_prompts(self) -> List[Prompt]:
        return await self.repository.list()
    
    async def update_prompt_response(self, prompt_id: str, response: str) -> Optional[Prompt]:
        prompt = await self.repository.get(prompt_id)
        if prompt:
            prompt.response = response
            prompt.processed_at = datetime.now()
            return await self.repository.update(prompt_id, prompt)
        return None
    
    async def update_prompt_error(self, prompt_id: str, error: str) -> Optional[Prompt]:
        prompt = await self.repository.get(prompt_id)
        if prompt:
            prompt.error = error
            prompt.processed_at = datetime.now()
            return await self.repository.update(prompt_id, prompt)
        return None