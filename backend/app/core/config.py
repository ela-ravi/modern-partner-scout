"""
Application configuration management.
Uses pydantic-settings for environment variable loading and validation.
"""
from functools import lru_cache
from typing import List, Literal, Optional

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    This class uses pydantic-settings to automatically load configuration
    from environment variables and .env files, with full type validation.
    
    Attributes:
        environment: Current environment (development/staging/production)
        debug: Enable debug mode for detailed logging
        supabase_url: Supabase project URL
        supabase_key: Supabase anon key for public operations
        supabase_service_role_key: Supabase service role key for admin operations
        supabase_jwt_secret: JWT secret for token verification
        use_sqlite_fallback: Use local SQLite instead of Supabase
        sqlite_database_path: Path to SQLite database file
        api_host: Host to bind the API server
        api_port: Port for the API server
        api_prefix: URL prefix for all API routes
        cors_origins: Allowed CORS origins
        llm_provider: Which LLM provider to use (openai/gemini/ollama)
        openai_api_key: OpenAI API key
        google_api_key: Google/Gemini API key
        ollama_base_url: Base URL for Ollama server
        apify_api_key: Apify API key for Instagram scraping
        apify_instagram_scraper_id: Apify actor ID for Instagram scraper
        rate_limit_requests: Maximum requests per rate limit period
        rate_limit_period: Rate limit time window in seconds
    """
    
    # Configure pydantic-settings to load from .env file
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Core Configuration
    # Defines the runtime environment - affects logging, docs visibility, etc.
    environment: Literal["development", "staging", "production", "testing"] = "development"
    # Enable debug mode for verbose logging and development features
    debug: bool = True
    
    # Supabase Configuration
    # Primary database connection settings
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    supabase_service_role_key: Optional[str] = None
    supabase_jwt_secret: Optional[str] = None
    
    # SQLite Fallback Configuration
    # Allows local development without Supabase credentials
    use_sqlite_fallback: bool = False
    sqlite_database_path: str = "./data/partner_scout.db"
    
    # API Configuration
    # Server binding and routing settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api"
    # CORS origins - defaults to common local development ports
    cors_origins: List[str] = Field(default_factory=lambda: [
        "http://localhost:5173",
        "http://localhost:3000"
    ])
    
    # LLM Configuration
    # AI provider selection and credentials
    llm_provider: Literal["openai", "gemini", "ollama"] = "openai"
    openai_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    ollama_base_url: str = "http://localhost:11434"
    
    # Apify Configuration
    # Instagram scraping service credentials
    apify_api_key: Optional[str] = None
    apify_instagram_scraper_id: str = "apify/instagram-scraper"
    
    # Rate Limiting Configuration
    # Protects the API from abuse
    rate_limit_requests: int = 100
    rate_limit_period: int = 60

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """
        Parse CORS origins from JSON string or list.
        
        Handles both JSON string format (from env) and list format (direct).
        
        Args:
            v: The input value, either a JSON string or a list
            
        Returns:
            List of CORS origin strings
        """
        if isinstance(v, str):
            import json
            return json.loads(v)
        return v
    
    @model_validator(mode="after")
    def validate_database_config(self):
        """
        Ensure database configuration is valid.
        
        Either Supabase credentials must be provided, or SQLite fallback
        must be enabled. Cannot have neither configured.
        
        Raises:
            ValueError: If no database is configured
        """
        if not self.use_sqlite_fallback:
            if not self.supabase_url or not self.supabase_key:
                raise ValueError(
                    "SUPABASE_URL and SUPABASE_KEY required when not using SQLite fallback"
                )
        return self
    
    @model_validator(mode="after")
    def validate_production_secrets(self):
        """
        Ensure all secrets are set in production environment.
        
        Production deployments require service role key and JWT secret
        for secure operations.
        
        Raises:
            ValueError: If required production secrets are missing
        """
        if self.environment == "production":
            required = [
                ("supabase_service_role_key", "SUPABASE_SERVICE_ROLE_KEY"),
                ("supabase_jwt_secret", "SUPABASE_JWT_SECRET"),
            ]
            for attr, env_name in required:
                if not getattr(self, attr):
                    raise ValueError(f"{env_name} required in production")
        return self
    
    @model_validator(mode="after")
    def validate_llm_provider_keys(self):
        """
        Ensure API key is set for selected LLM provider.
        
        In non-development environments, the selected LLM provider
        must have its API key configured.
        
        Raises:
            ValueError: If LLM API key is missing in non-development mode
        """
        if self.llm_provider == "openai" and not self.openai_api_key:
            if self.environment not in ("development", "testing"):
                raise ValueError("OPENAI_API_KEY required for OpenAI provider")
        elif self.llm_provider == "gemini" and not self.google_api_key:
            if self.environment not in ("development", "testing"):
                raise ValueError("GOOGLE_API_KEY required for Gemini provider")
        return self
    
    @property
    def is_development(self) -> bool:
        """
        Check if running in development mode.
        
        Returns:
            True if environment is 'development', False otherwise
        """
        return self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        """
        Check if running in production mode.
        
        Returns:
            True if environment is 'production', False otherwise
        """
        return self.environment == "production"
    
    @property
    def is_testing(self) -> bool:
        """
        Check if running in testing mode.
        
        Returns:
            True if environment is 'testing', False otherwise
        """
        return self.environment == "testing"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Uses lru_cache to ensure only one Settings instance exists
    throughout the application lifecycle. This prevents multiple
    reads of environment variables and .env file.
    
    Returns:
        Settings: Cached application settings instance
    """
    return Settings()
