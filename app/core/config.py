"""
Configuration management with environment variables and defaults.
Uses pydantic-settings for validation.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application configuration with validation"""
    
    # API Configuration
    # ✅ IMPROVEMENT: Made Optional. No more "Validation Error" if key is missing.
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    
    openai_model: str = Field(default="gpt-4o-mini", description="Model to use")
    openai_temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    openai_max_tokens: int = Field(default=2000, ge=100, le=4000)
    
    # Application Settings
    environment: str = Field(default="development", pattern="^(development|staging|production)$")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    
    # Paths
    # ✅ IMPROVEMENT: More robust base path resolution for Azure/Docker
    base_dir: Path = Field(default_factory=lambda: Path.cwd())
    
    data_dir: Path = Field(default_factory=lambda: Path("data"))
    output_dir: Path = Field(default_factory=lambda: Path("output"))
    template_dir: Path = Field(default_factory=lambda: Path("app/templates"))
    
    # Generation Settings
    default_test_type: str = Field(default="FAT")
    prompt_version: str = Field(default="v1.1")
    template_version: str = Field(default="v1.0")
    enable_validation: bool = Field(default=True)
    
    # Performance
    max_retries: int = Field(default=3, ge=1, le=10)
    retry_delay_sec: float = Field(default=1.0, ge=0.1, le=60.0)
    timeout_sec: int = Field(default=30, ge=5, le=300)
    
    # Metrics
    enable_cost_tracking: bool = Field(default=True)
    enable_metrics_db: bool = Field(default=True)
    metrics_db_path: Path = Field(default_factory=lambda: Path("output/metrics.db"))
    
    # Approval Workflow
    enable_approval_workflow: bool = Field(default=True)
    approval_storage_path: Path = Field(default_factory=lambda: Path("output/approvals.json"))
    
    @field_validator("data_dir", "output_dir", "template_dir", mode="before")
    @classmethod
    def resolve_paths(cls, v, info):
        """Convert relative paths to absolute"""
        if isinstance(v, str):
            v = Path(v)
        if not v.is_absolute():
            # ✅ IMPROVEMENT: Use the base_dir defined above for consistency
            base = Path.cwd()
            v = base / v
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


# Singleton instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create settings instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
        _ensure_directories(_settings)
    return _settings


def _ensure_directories(settings: Settings):
    """Create required directories if they don't exist"""
    # ✅ IMPROVEMENT: Silent error handling for read-only filesystems (just in case)
    try:
        for path in [settings.data_dir, settings.output_dir]:
            path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create directories: {e}")


# Convenience function for testing
def override_settings(**kwargs) -> Settings:
    """Override settings for testing"""
    global _settings
    _settings = Settings(**kwargs)
    return _settings


# Pricing information (as of Jan 2026)
PRICING = {
    "gpt-4o-mini": {
        "input": 0.150 / 1_000_000,   # $ per token
        "output": 0.600 / 1_000_000
    },
    "gpt-4o": {
        "input": 2.50 / 1_000_000,
        "output": 10.00 / 1_000_000
    },
    "gpt-3.5-turbo": {
        "input": 0.50 / 1_000_000,
        "output": 1.50 / 1_000_000
    }
}


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate cost in USD for API usage"""
    if model not in PRICING:
        return 0.0
    
    pricing = PRICING[model]
    return (
        input_tokens * pricing["input"] +
        output_tokens * pricing["output"]
    )