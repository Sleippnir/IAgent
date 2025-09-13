import asyncio
import random
from typing import Dict, Any

from ..domain.models import ModelType
from ..application.use_cases import LLMProviderPort


class MockLLMProvider(LLMProviderPort):
    """Proveedor simulado de LLM para desarrollo y testing"""
    
    def __init__(self):
        self.model_configs = {
            ModelType.GPT_4: {
                "name": "GPT-4",
                "max_tokens": 4096,
                "context_window": 8192,
                "provider": "OpenAI"
            },
            ModelType.GPT_3_5: {
                "name": "GPT-3.5 Turbo",
                "max_tokens": 2048,
                "context_window": 4096,
                "provider": "OpenAI"
            },
            ModelType.CLAUDE: {
                "name": "Claude-3",
                "max_tokens": 4096,
                "context_window": 100000,
                "provider": "Anthropic"
            },
            ModelType.LLAMA: {
                "name": "Llama-2",
                "max_tokens": 2048,
                "context_window": 4096,
                "provider": "Meta"
            }
        }
    
    async def generate_text(
        self, 
        prompt: str, 
        model: ModelType, 
        max_tokens: int, 
        temperature: float
    ) -> str:
        """Simula la generación de texto"""
        # Simular tiempo de procesamiento
        processing_delay = random.uniform(0.5, 2.0)
        await asyncio.sleep(processing_delay)
        
        # Respuestas simuladas basadas en el contenido del prompt
        responses = self._get_mock_responses(prompt, model)
        
        # Seleccionar respuesta basada en temperatura
        if temperature < 0.3:
            # Respuesta más determinística
            response = responses[0]
        elif temperature > 0.8:
            # Respuesta más creativa
            response = random.choice(responses)
        else:
            # Respuesta balanceada
            response = random.choice(responses[:2])
        
        # Truncar si excede max_tokens (simulación simple)
        words = response.split()
        if len(words) > max_tokens // 4:  # Estimación: 4 caracteres por token
            response = " ".join(words[:max_tokens // 4])
        
        return response
    
    def get_model_info(self, model: ModelType) -> Dict[str, Any]:
        """Obtiene información del modelo"""
        return self.model_configs.get(model, {})
    
    def _get_mock_responses(self, prompt: str, model: ModelType) -> list:
        """Genera respuestas simuladas basadas en el prompt"""
        prompt_lower = prompt.lower()
        
        # Respuestas específicas por tipo de consulta
        if "hola" in prompt_lower or "hello" in prompt_lower:
            return [
                "¡Hola! Soy un asistente de IA. ¿En qué puedo ayudarte hoy?",
                "¡Saludos! Es un placer conocerte. ¿Qué te gustaría saber?",
                "¡Hola! Estoy aquí para ayudarte con cualquier pregunta que tengas."
            ]
        
        elif "código" in prompt_lower or "code" in prompt_lower:
            return [
                "Aquí tienes un ejemplo de código:\n\n```python\ndef ejemplo():\n    return 'Hola mundo'\n```",
                "Te puedo ayudar con programación. ¿Qué lenguaje te interesa?",
                "El código es mi especialidad. ¿Necesitas ayuda con algún proyecto específico?"
            ]
        
        elif "explicar" in prompt_lower or "explain" in prompt_lower:
            return [
                "Te explico paso a paso: Este concepto se basa en principios fundamentales que...",
                "Para entender esto mejor, primero debemos considerar los siguientes puntos...",
                "La explicación es la siguiente: Se trata de un proceso que involucra..."
            ]
        
        elif "ayuda" in prompt_lower or "help" in prompt_lower:
            return [
                "¡Por supuesto! Estoy aquí para ayudarte. ¿Podrías ser más específico sobre lo que necesitas?",
                "Claro, te ayudo con gusto. ¿Cuál es tu consulta específica?",
                "Estoy disponible para asistirte. ¿En qué área necesitas apoyo?"
            ]
        
        else:
            # Respuestas genéricas
            return [
                f"Entiendo tu consulta sobre '{prompt[:50]}...'. Basándome en mi conocimiento, puedo decirte que este es un tema interesante que requiere consideración cuidadosa.",
                f"Respecto a tu pregunta, hay varios aspectos importantes a considerar. El tema que mencionas es relevante en el contexto actual.",
                f"Tu consulta es muy pertinente. Permíteme proporcionarte una respuesta detallada basada en la información disponible."
            ]


class OpenAIProvider(LLMProviderPort):
    """Proveedor real de OpenAI (implementación futura)"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        # TODO: Inicializar cliente de OpenAI
    
    async def generate_text(
        self, 
        prompt: str, 
        model: ModelType, 
        max_tokens: int, 
        temperature: float
    ) -> str:
        """Implementación real con OpenAI API"""
        # TODO: Implementar llamada real a OpenAI
        raise NotImplementedError("OpenAI provider not implemented yet")
    
    def get_model_info(self, model: ModelType) -> Dict[str, Any]:
        """Información real de modelos OpenAI"""
        # TODO: Implementar información real
        return {}