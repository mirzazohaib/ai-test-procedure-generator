"""
Enhanced AI generator with retry logic, cost tracking, and error handling.
Delegates actual generation to pluggable AIProvider implementations.
"""

import time
from typing import Dict, Any, Optional

from app.core.models import Project, TestType
from app.core.config import get_settings, calculate_cost
from app.ai.prompts import get_prompt
from app.utils.logging import create_logger

# Import the providers from the new providers.py file
from app.ai.providers import OpenAIProvider, MockAIProvider, AIProvider

logger = create_logger(__name__, component='ai_generator')


class TestGenerator:
    """High-level test procedure generator"""
    
    def __init__(self, provider: AIProvider):
        self.settings = get_settings()
        self.provider = provider
        logger.info(f"TestGenerator initialized with provider: {provider.__class__.__name__}")
    
    def generate(
        self,
        project: Project,
        test_type: TestType,
        prompt_version: str = None
    ) -> Dict[str, Any]:
        """
        Generate test procedure for project.
        
        Args:
            project: The project data model
            test_type: The type of test (FAT, SAT, etc.)
            prompt_version: Optional version string for the prompt template
            
        Returns:
            dict: {
                'content': str,
                'metadata': {
                    'tokens': dict,
                    'cost_usd': float,
                    'model': str,
                    'prompt_version': str,
                    'generation_time_sec': float
                }
            }
        """
        prompt_version = prompt_version or self.settings.prompt_version
        
        logger.info("Starting test generation", extra_data={
            'project_id': project.project_id,
            'test_type': test_type.name,
            'signal_count': len(project.signals)
        })
        
        start_time = time.time()
        
        # Build prompt
        prompt = get_prompt(
            test_type=test_type,
            project=project,
            version=prompt_version
        )
        
        logger.debug("Prompt prepared", extra_data={
            'prompt_length': len(prompt),
            'version': prompt_version
        })
        
        # Delegate generation to the provider (Mock or Real)
        try:
            result = self.provider.generate(prompt)
        except Exception as e:
            logger.error("Generation failed in provider", exc_info=True)
            raise
        
        generation_time = time.time() - start_time
        
        # Calculate cost
        cost = calculate_cost(
            model=result['model'],
            input_tokens=result['tokens']['input'],
            output_tokens=result['tokens']['output']
        )
        
        metadata = {
            'tokens': result['tokens'],
            'cost_usd': cost,
            'model': result['model'],
            'prompt_version': prompt_version,
            'generation_time_sec': round(generation_time, 3),
            'finish_reason': result['finish_reason']
        }
        
        logger.info("Generation completed", extra_data=metadata)
        
        return {
            'content': result['content'],
            'metadata': metadata
        }


def create_generator(provider_name: str = None) -> TestGenerator:
    """
    Factory to create generator with specific provider.
    
    Args:
        provider_name: 'openai', 'mock', or None (auto-detect)
    
    Returns:
        TestGenerator configured with the requested provider.
    """
    settings = get_settings()
    
    # Auto-detection logic:
    # 1. If provider_name is explicit, use it.
    # 2. If no OpenAI API key is found in settings, default to 'mock'.
    # 3. Otherwise default to 'openai'.
    
    if not provider_name:
        if not settings.openai_api_key:
            logger.warning("No OpenAI API key found. Defaulting to MOCK provider.")
            provider_name = "mock"
        else:
            provider_name = "openai"
            
    logger.info(f"Factory creating generator with provider: {provider_name}")

    if provider_name.lower() == "mock":
        return TestGenerator(MockAIProvider())
    
    elif provider_name.lower() == "openai":
        return TestGenerator(OpenAIProvider())
    
    else:
        raise ValueError(f"Unknown provider: {provider_name}")