"""
PartnerScout AI - Configuration Management

Centralized configuration using pydantic-settings for environment-specific settings.
All configuration is loaded from environment variables with type validation.
"""

from functools import lru_cache
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class SupabaseSettings(BaseSettings):
    """Supabase database and authentication settings."""
    
    model_config = SettingsConfigDict(
        env_prefix="SUPABASE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    url: str = Field(..., description="Supabase project URL")
    anon_key: str = Field(..., description="Supabase anonymous/public key")
    service_role_key: str = Field(..., description="Supabase service role key (admin)")
    jwt_secret: str = Field(..., description="JWT secret for token validation")


class OpenAISettings(BaseSettings):
    """OpenAI LLM provider settings."""
    
    model_config = SettingsConfigDict(
        env_prefix="OPENAI_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    api_key: str = Field(default="", description="OpenAI API key")
    model: str = Field(default="gpt-4-turbo-preview", description="OpenAI model to use")


class GeminiSettings(BaseSettings):
    """Google Gemini LLM provider settings."""
    
    model_config = SettingsConfigDict(
        env_prefix="GEMINI_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    api_key: str = Field(default="", description="Gemini API key")
    model: str = Field(default="gemini-pro", description="Gemini model to use")


class OllamaSettings(BaseSettings):
    """Ollama local LLM provider settings."""
    
    model_config = SettingsConfigDict(
        env_prefix="OLLAMA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    base_url: str = Field(default="http://localhost:11434", description="Ollama server URL")
    model: str = Field(default="llama2", description="Ollama model to use")


class OpenRouterSettings(BaseSettings):
    """OpenRouter LLM provider settings (access to multiple models via single API)."""
    
    model_config = SettingsConfigDict(
        env_prefix="OPENROUTER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    api_key: str = Field(default="", description="OpenRouter API key")
    model: str = Field(default="anthropic/claude-3.5-sonnet", description="OpenRouter model to use")
    base_url: str = Field(default="https://openrouter.ai/api/v1", description="OpenRouter API base URL")


class HuggingFaceSettings(BaseSettings):
    """Hugging Face LLM provider settings."""
    
    model_config = SettingsConfigDict(
        env_prefix="HUGGINGFACE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    api_key: str = Field(default="", description="Hugging Face API key")
    model: str = Field(default="mistralai/Mistral-7B-Instruct-v0.2", description="Hugging Face model to use")



class ApifySettings(BaseSettings):
    """Apify web scraping service settings."""
    
    model_config = SettingsConfigDict(
        env_prefix="APIFY_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    api_key: str = Field(default="", description="Apify API key")
    instagram_scraper_id: str = Field(
        default="apify/instagram-profile-scraper",
        description="Actor ID for Instagram profile scraping"
    )
    hashtag_scraper_id: str = Field(
        default="apify/instagram-hashtag-scraper",
        description="Actor ID for Instagram hashtag scraping"
    )
    search_scraper_id: str = Field(
        default="apify/instagram-search-scraper",
        description="Actor ID for Instagram user/keyword search"
    )
    tagged_scraper_id: str = Field(
        default="apify/instagram-tagged-scraper",
        description="Actor ID for Instagram tagged posts (find who tags a brand)"
    )


class Settings(BaseSettings):
    """
    Main application settings.
    
    Aggregates all configuration sections and provides
    application-wide settings.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    # Environment
    environment: str = Field(default="development", description="Runtime environment")
    debug: bool = Field(default=False, description="Debug mode flag")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API host address")
    api_port: int = Field(default=8000, description="API port")
    api_prefix: str = Field(default="/api", description="API route prefix")
    
    # CORS Configuration
    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        description="Comma-separated list of allowed CORS origins"
    )
    
    # LLM Provider Selection
    llm_provider: str = Field(
        default="openai",
        description="LLM provider to use (openai, gemini, ollama)"
    )
    
    # Embedding Provider Selection
    embedding_provider: str = Field(
        default="openai",
        description="Embedding provider to use (openai, gemini, huggingface)"
    )
    
    # Rate Limits and Quotas
    daily_job_limit: int = Field(default=10, description="Maximum jobs per user per day")
    max_profiles_per_job: int = Field(default=100, description="Maximum profiles per discovery job")
    scoring_batch_size: int = Field(default=5, description="Number of profiles to score in parallel")
    request_timeout_seconds: int = Field(default=30, description="HTTP request timeout")
    
    # Scoring Thresholds
    min_score_threshold: int = Field(default=50, description="Minimum score for recommendations")
    high_score_threshold: int = Field(default=80, description="Threshold for high-quality matches")
    
    # Nested settings (loaded separately)
    supabase: SupabaseSettings = Field(default_factory=SupabaseSettings)
    openai: OpenAISettings = Field(default_factory=OpenAISettings)
    gemini: GeminiSettings = Field(default_factory=GeminiSettings)
    ollama: OllamaSettings = Field(default_factory=OllamaSettings)
    openrouter: OpenRouterSettings = Field(default_factory=OpenRouterSettings)
    huggingface: HuggingFaceSettings = Field(default_factory=HuggingFaceSettings)
    apify: ApifySettings = Field(default_factory=ApifySettings)
    
    @field_validator("llm_provider")
    @classmethod
    def validate_llm_provider(cls, v: str) -> str:
        """Validate that LLM provider is one of the supported options."""
        valid_providers = {"openai", "gemini", "ollama", "openrouter", "huggingface"}
        if v.lower() not in valid_providers:
            raise ValueError(f"LLM provider must be one of: {valid_providers}")
        return v.lower()
    
    @field_validator("embedding_provider")
    @classmethod
    def validate_embedding_provider(cls, v: str) -> str:
        """Validate that embedding provider is one of the supported options."""
        valid_providers = {"openai", "gemini", "huggingface"}
        if v.lower() not in valid_providers:
            raise ValueError(f"Embedding provider must be one of: {valid_providers}")
        return v.lower()
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate that log level is valid."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() == "production"
    
    # Convenience properties for backward compatibility
    @property
    def SUPABASE_URL(self) -> str:
        return self.supabase.url
    
    @property
    def SUPABASE_ANON_KEY(self) -> str:
        return self.supabase.anon_key
    
    @property
    def SUPABASE_SERVICE_ROLE_KEY(self) -> str:
        return self.supabase.service_role_key
    
    @property
    def SUPABASE_JWT_SECRET(self) -> str:
        return self.supabase.jwt_secret


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Uses LRU cache to ensure settings are only loaded once
    and reused across the application.
    
    Returns:
        Settings: Application settings instance
    """
    return Settings()


# Convenience alias for easy importing
settings = get_settings()
