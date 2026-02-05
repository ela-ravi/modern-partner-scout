# EPIC-1: Project Foundation

## Overview

**Goal:** Set up the complete backend project infrastructure with TDD methodology, including project structure, configuration management, database schema, and core utilities.

**Duration:** 2-3 days  
**Dependencies:** None (Starting point)  
**Deliverables:** Working backend skeleton with tests passing

---

## Environment Variables Required

```bash
# Core Configuration
ENVIRONMENT=development          # development | staging | production
DEBUG=true                       # Enable debug mode

# Supabase Configuration
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_JWT_SECRET=your-jwt-secret-here

# SQLite Fallback (for local development without Supabase)
USE_SQLITE_FALLBACK=false
SQLITE_DATABASE_PATH=./data/partner_scout.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_PREFIX=/api
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

---

## FEATURE-1.1: Project Structure Setup

### STORY-1.1.1: Initialize Backend Project

**As a** developer  
**I want** a properly structured Python backend project  
**So that** I can build features in an organized manner

#### TASK-1.1.1.1: Create Project Directory Structure

**Priority:** P0 (Critical)  
**Estimated Time:** 30 minutes

##### SUB-TASK-1.1.1.1.1: Create Backend Folder Structure

```bash
partner-scout/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application entry
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py           # Settings management
│   │   │   ├── constants.py        # Application constants
│   │   │   ├── exceptions.py       # Custom exceptions
│   │   │   └── logging.py          # Logging configuration
│   │   ├── guards/
│   │   │   ├── __init__.py
│   │   │   ├── auth_guard.py       # Authentication guard
│   │   │   └── rate_limit_guard.py # Rate limiting
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py             # Dependency injection
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       ├── health.py       # Health check endpoints
│   │   │       ├── auth.py         # Auth endpoints
│   │   │       ├── discovery.py    # Discovery job endpoints
│   │   │       ├── profiles.py     # Profile endpoints
│   │   │       └── agent.py        # AI agent endpoints
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # Base Pydantic models
│   │   │   ├── user.py             # User models
│   │   │   ├── discovery.py        # Discovery job models
│   │   │   ├── profile.py          # Profile models
│   │   │   └── agent.py            # Agent request/response models
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── llm_service.py      # LLM provider abstraction
│   │   │   ├── apify_service.py    # Apify Instagram scraping
│   │   │   ├── discovery_service.py # Discovery orchestration
│   │   │   └── profile_service.py  # Profile operations
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # Base repository pattern
│   │   │   ├── user_repository.py  # User data access
│   │   │   ├── discovery_repository.py # Discovery job data access
│   │   │   └── profile_repository.py # Profile data access
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── base_agent.py       # Base agent class
│   │   │   ├── brand_analyzer.py   # Brand DNA extraction
│   │   │   ├── discovery_agent.py  # Similar profile discovery
│   │   │   ├── scorer_agent.py     # Profile scoring
│   │   │   └── prompts/
│   │   │       ├── __init__.py
│   │   │       ├── brand_analyzer.py  # Brand analyzer prompts
│   │   │       ├── discovery.py       # Discovery prompts
│   │   │       └── scorer.py          # Scorer prompts
│   │   └── db/
│   │       ├── __init__.py
│   │       ├── supabase_client.py  # Supabase client wrapper
│   │       └── sqlite_client.py    # SQLite fallback client
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py             # Pytest fixtures
│   │   ├── unit/
│   │   │   ├── __init__.py
│   │   │   ├── test_config.py
│   │   │   ├── test_models.py
│   │   │   └── ...
│   │   ├── integration/
│   │   │   ├── __init__.py
│   │   │   ├── test_database.py
│   │   │   └── ...
│   │   └── e2e/
│   │       ├── __init__.py
│   │       └── test_api_flows.py
│   ├── scripts/
│   │   ├── seed_database.py        # Database seeding
│   │   ├── validate_env.py         # Environment validation
│   │   └── run_discovery.py        # CLI discovery runner
│   ├── config/
│   │   ├── logging.yaml            # Logging configuration
│   │   └── settings.yaml           # Default settings
│   ├── requirements.txt            # Production dependencies
│   ├── requirements-dev.txt        # Development dependencies
│   ├── pyproject.toml              # Project metadata
│   ├── pytest.ini                  # Pytest configuration
│   ├── .env.example                # Environment template
│   └── README.md                   # Backend documentation
```

**Commands:**

```bash
# Create all directories
mkdir -p backend/app/{core,guards,api/routes,models,services,repositories,agents/prompts,db}
mkdir -p backend/tests/{unit,integration,e2e}
mkdir -p backend/scripts backend/config

# Create __init__.py files
find backend -type d -exec touch {}/__init__.py \;
```

##### SUB-TASK-1.1.1.1.2: Create requirements.txt

```txt
# requirements.txt - Production Dependencies

# Web Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0

# Database
supabase==2.3.4
python-dotenv==1.0.0

# AI/LLM
langchain==0.1.4
langchain-openai==0.0.5
langchain-google-genai==0.0.6
openai==1.10.0
google-generativeai==0.3.2

# HTTP Client
httpx==0.26.0
aiohttp==3.9.1

# Utilities
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
pyyaml==6.0.1
tenacity==8.2.3

# Logging
structlog==24.1.0
```

##### SUB-TASK-1.1.1.1.3: Create requirements-dev.txt

```txt
# requirements-dev.txt - Development Dependencies

-r requirements.txt

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
pytest-mock==3.12.0
httpx==0.26.0
faker==22.2.0
factory-boy==3.3.0

# Code Quality
black==24.1.0
isort==5.13.2
flake8==7.0.0
mypy==1.8.0
pre-commit==3.6.0

# Documentation
mkdocs==1.5.3
mkdocs-material==9.5.4

# Debugging
ipython==8.20.0
rich==13.7.0
```

##### SUB-TASK-1.1.1.1.4: Create pyproject.toml

```toml
[project]
name = "partner-scout-backend"
version = "0.1.0"
description = "PartnerScout AI Backend - Instagram Partner Discovery Platform"
requires-python = ">=3.10"

[tool.black]
line-length = 88
target-version = ['py310', 'py311']
include = '\.pyi?$'
exclude = '''
/(
    \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
line_length = 88
skip = [".venv", "venv"]

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true
exclude = ["tests", "venv"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
asyncio_mode = "auto"
addopts = "-v --tb=short"
filterwarnings = [
    "ignore::DeprecationWarning",
]
```

##### SUB-TASK-1.1.1.1.5: Create .env.example

```bash
# .env.example - Environment Variables Template

# ===========================================
# CORE CONFIGURATION
# ===========================================
ENVIRONMENT=development
DEBUG=true

# ===========================================
# SUPABASE CONFIGURATION
# ===========================================
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret

# ===========================================
# DATABASE FALLBACK
# ===========================================
USE_SQLITE_FALLBACK=false
SQLITE_DATABASE_PATH=./data/partner_scout.db

# ===========================================
# API CONFIGURATION
# ===========================================
API_HOST=0.0.0.0
API_PORT=8000
API_PREFIX=/api
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]

# ===========================================
# LLM CONFIGURATION
# ===========================================
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...
OLLAMA_BASE_URL=http://localhost:11434

# ===========================================
# APIFY CONFIGURATION
# ===========================================
APIFY_API_KEY=apify_api_...
APIFY_INSTAGRAM_SCRAPER_ID=apify/instagram-scraper

# ===========================================
# RATE LIMITING
# ===========================================
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60
```

---

#### TASK-1.1.1.2: Implement Configuration Management

**Priority:** P0 (Critical)  
**Estimated Time:** 2 hours

**ENV VARIABLES NEEDED:**
- All variables from `.env.example`

##### SUB-TASK-1.1.1.2.1: Write Configuration Tests First (TDD)
**File:** `backend/tests/fixtures/config.py`

```python
"""
Test fixtures for configuration tests.
Layered format: Input → Test → Output
"""

# === ENVIRONMENT INPUT DATA ===
VALID_ENV_INPUT = {
    "ENVIRONMENT": "testing",
    "DEBUG": "true",
    "SUPABASE_URL": "https://test.supabase.co",
    "SUPABASE_KEY": "test-key",
}

MINIMAL_ENV_INPUT = {
    "SUPABASE_URL": "https://test.supabase.co",
    "SUPABASE_KEY": "test-key",
}

CORS_ENV_INPUT = {
    **MINIMAL_ENV_INPUT,
    "CORS_ORIGINS": '["http://localhost:3000","http://localhost:5173"]',
}

INVALID_LLM_ENV_INPUT = {
    **MINIMAL_ENV_INPUT,
    "LLM_PROVIDER": "invalid_provider",
}

PRODUCTION_MISSING_SECRETS_INPUT = {
    "ENVIRONMENT": "production",
    "SUPABASE_URL": "https://test.supabase.co",
    "SUPABASE_KEY": "test-key",
    # Missing SUPABASE_SERVICE_ROLE_KEY
}

SQLITE_FALLBACK_INPUT = {
    "ENVIRONMENT": "development",
    "USE_SQLITE_FALLBACK": "true",
    "SQLITE_DATABASE_PATH": "./test.db",
}

# === EXPECTED OUTPUT ===
VALID_ENV_OUTPUT = {
    "environment": "testing",
    "debug": True,
    "supabase_url": "https://test.supabase.co",
    "supabase_key": "test-key",
}

DEFAULT_VALUES_OUTPUT = {
    "environment": "development",
    "api_host": "0.0.0.0",
    "api_port": 8000,
}

CORS_OUTPUT = {
    "cors_count": 2,
    "expected_origin": "http://localhost:3000",
}
```

**File:** `backend/tests/unit/test_config.py`

```python
"""
Unit tests for configuration management.
TDD: Write these tests FIRST, then implement config.py
"""
import os
import pytest
from unittest.mock import patch

from tests.fixtures.config import (
    VALID_ENV_INPUT,
    VALID_ENV_OUTPUT,
    MINIMAL_ENV_INPUT,
    DEFAULT_VALUES_OUTPUT,
    CORS_ENV_INPUT,
    CORS_OUTPUT,
    INVALID_LLM_ENV_INPUT,
    PRODUCTION_MISSING_SECRETS_INPUT,
    SQLITE_FALLBACK_INPUT,
)


class TestSettings:
    """Test suite for Settings configuration class."""

    def test_settings_loads_from_environment(self):
        """Settings should load values from environment variables."""
        with patch.dict(os.environ, VALID_ENV_INPUT):
            from app.core.config import Settings
            settings = Settings()
            
            assert settings.environment == VALID_ENV_OUTPUT["environment"]
            assert settings.debug is VALID_ENV_OUTPUT["debug"]
            assert settings.supabase_url == VALID_ENV_OUTPUT["supabase_url"]
            assert settings.supabase_key == VALID_ENV_OUTPUT["supabase_key"]

    def test_settings_has_default_values(self):
        """Settings should have sensible defaults."""
        with patch.dict(os.environ, MINIMAL_ENV_INPUT, clear=True):
            from app.core.config import Settings
            settings = Settings()
            
            assert settings.environment == DEFAULT_VALUES_OUTPUT["environment"]
            assert settings.api_host == DEFAULT_VALUES_OUTPUT["api_host"]
            assert settings.api_port == DEFAULT_VALUES_OUTPUT["api_port"]

    def test_settings_validates_required_fields(self):
        """Settings should raise error if required fields missing."""
        with patch.dict(os.environ, {}, clear=True):
            from app.core.config import Settings
            with pytest.raises(ValueError):
                Settings()

    def test_settings_cors_origins_parses_json(self):
        """CORS origins should parse from JSON string."""
        with patch.dict(os.environ, CORS_ENV_INPUT):
            from app.core.config import Settings
            settings = Settings()
            
            assert len(settings.cors_origins) == CORS_OUTPUT["cors_count"]
            assert CORS_OUTPUT["expected_origin"] in settings.cors_origins

    def test_settings_llm_provider_validation(self):
        """LLM provider should only accept valid values."""
        with patch.dict(os.environ, INVALID_LLM_ENV_INPUT):
            from app.core.config import Settings
            with pytest.raises(ValueError):
                Settings()

    def test_get_settings_singleton(self):
        """get_settings should return cached instance."""
        from app.core.config import get_settings
        
        settings1 = get_settings()
        settings2 = get_settings()
        
        assert settings1 is settings2


class TestEnvironmentValidation:
    """Test environment-specific validation."""

    def test_production_requires_all_secrets(self):
        """Production environment should require all secrets."""
        with patch.dict(os.environ, PRODUCTION_MISSING_SECRETS_INPUT):
            from app.core.config import Settings
            with pytest.raises(ValueError, match="SUPABASE_SERVICE_ROLE_KEY"):
                Settings()

    def test_development_allows_sqlite_fallback(self):
        """Development can use SQLite fallback."""
        with patch.dict(os.environ, SQLITE_FALLBACK_INPUT):
            from app.core.config import Settings
            settings = Settings()
            
            assert settings.use_sqlite_fallback is True
```

##### SUB-TASK-1.1.1.2.2: Implement config.py

**File:** `backend/app/core/config.py`

```python
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
    
    Attributes:
        environment: Current environment (development/staging/production)
        debug: Enable debug mode
        supabase_url: Supabase project URL
        supabase_key: Supabase anon key
        ...
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Core Configuration
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    
    # Supabase Configuration
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    supabase_service_role_key: Optional[str] = None
    supabase_jwt_secret: Optional[str] = None
    
    # SQLite Fallback
    use_sqlite_fallback: bool = False
    sqlite_database_path: str = "./data/partner_scout.db"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api"
    cors_origins: List[str] = Field(default_factory=lambda: [
        "http://localhost:5173",
        "http://localhost:3000"
    ])
    
    # LLM Configuration
    llm_provider: Literal["openai", "gemini", "ollama"] = "openai"
    openai_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    ollama_base_url: str = "http://localhost:11434"
    
    # Apify Configuration
    apify_api_key: Optional[str] = None
    apify_instagram_scraper_id: str = "apify/instagram-scraper"
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_period: int = 60
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from JSON string or list."""
        if isinstance(v, str):
            import json
            return json.loads(v)
        return v
    
    @model_validator(mode="after")
    def validate_database_config(self):
        """Ensure database configuration is valid."""
        if not self.use_sqlite_fallback:
            if not self.supabase_url or not self.supabase_key:
                raise ValueError(
                    "SUPABASE_URL and SUPABASE_KEY required when not using SQLite fallback"
                )
        return self
    
    @model_validator(mode="after")
    def validate_production_secrets(self):
        """Ensure all secrets are set in production."""
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
        """Ensure API key is set for selected LLM provider."""
        if self.llm_provider == "openai" and not self.openai_api_key:
            if self.environment != "development":
                raise ValueError("OPENAI_API_KEY required for OpenAI provider")
        elif self.llm_provider == "gemini" and not self.google_api_key:
            if self.environment != "development":
                raise ValueError("GOOGLE_API_KEY required for Gemini provider")
        return self
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Uses lru_cache to ensure only one Settings instance exists.
    
    Returns:
        Settings: Application settings
    """
    return Settings()
```

---

#### TASK-1.1.1.3: Implement Core Utilities

**Priority:** P1 (High)  
**Estimated Time:** 2 hours

##### SUB-TASK-1.1.1.3.1: Write Exception Tests First (TDD)

**File:** `backend/tests/fixtures/exceptions.py`

```python
"""
Test fixtures for exception tests.
Layered format: Input → Test → Output
"""

# === EXCEPTION INPUT DATA ===
BASE_EXCEPTION_INPUT = {
    "message": "Test error",
    "code": "TEST_ERROR",
}

VALIDATION_ERROR_INPUT = {
    "message": "Invalid input",
}

NOT_FOUND_ERROR_INPUT = {
    "message": "Resource not found",
}

AUTH_ERROR_INPUT = {
    "message": "Invalid token",
}

AUTHZ_ERROR_INPUT = {
    "message": "Permission denied",
}

LLM_ERROR_INPUT = {
    "message": "OpenAI rate limited",
    "provider": "openai",
}

APIFY_ERROR_INPUT = {
    "message": "Actor failed",
    "actor_id": "test-actor",
}

VALIDATION_WITH_DETAILS_INPUT = {
    "message": "Invalid email",
    "details": {"field": "email"},
}

# === EXPECTED OUTPUT ===
BASE_EXCEPTION_OUTPUT = {
    "message": "Test error",
    "code": "TEST_ERROR",
    "status_code": 500,
}

VALIDATION_ERROR_OUTPUT = {
    "status_code": 400,
    "code": "VALIDATION_ERROR",
}

NOT_FOUND_ERROR_OUTPUT = {
    "status_code": 404,
    "code": "NOT_FOUND",
}

AUTH_ERROR_OUTPUT = {
    "status_code": 401,
    "code": "AUTHENTICATION_ERROR",
}

AUTHZ_ERROR_OUTPUT = {
    "status_code": 403,
    "code": "AUTHORIZATION_ERROR",
}

LLM_ERROR_OUTPUT = {
    "status_code": 503,
    "provider": "openai",
}

APIFY_ERROR_OUTPUT = {
    "status_code": 503,
    "actor_id": "test-actor",
}

TO_DICT_OUTPUT = {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email",
    "field": "email",
}
```

**File:** `backend/tests/unit/test_exceptions.py`

```python
"""
Unit tests for custom exceptions.
TDD: Write these tests FIRST, then implement exceptions.py
"""
import pytest

from tests.fixtures.exceptions import (
    BASE_EXCEPTION_INPUT,
    BASE_EXCEPTION_OUTPUT,
    VALIDATION_ERROR_INPUT,
    VALIDATION_ERROR_OUTPUT,
    NOT_FOUND_ERROR_INPUT,
    NOT_FOUND_ERROR_OUTPUT,
    AUTH_ERROR_INPUT,
    AUTH_ERROR_OUTPUT,
    AUTHZ_ERROR_INPUT,
    AUTHZ_ERROR_OUTPUT,
    LLM_ERROR_INPUT,
    LLM_ERROR_OUTPUT,
    APIFY_ERROR_INPUT,
    APIFY_ERROR_OUTPUT,
    VALIDATION_WITH_DETAILS_INPUT,
    TO_DICT_OUTPUT,
)


class TestCustomExceptions:
    """Test suite for custom exception classes."""

    def test_partner_scout_exception_base(self):
        """PartnerScoutException should be base for all custom exceptions."""
        from app.core.exceptions import PartnerScoutException
        
        exc = PartnerScoutException(**BASE_EXCEPTION_INPUT)
        assert str(exc) == BASE_EXCEPTION_OUTPUT["message"]
        assert exc.code == BASE_EXCEPTION_OUTPUT["code"]
        assert exc.status_code == BASE_EXCEPTION_OUTPUT["status_code"]

    def test_validation_error(self):
        """ValidationError should have 400 status code."""
        from app.core.exceptions import ValidationError
        
        exc = ValidationError(**VALIDATION_ERROR_INPUT)
        assert exc.status_code == VALIDATION_ERROR_OUTPUT["status_code"]
        assert exc.code == VALIDATION_ERROR_OUTPUT["code"]

    def test_not_found_error(self):
        """NotFoundError should have 404 status code."""
        from app.core.exceptions import NotFoundError
        
        exc = NotFoundError(**NOT_FOUND_ERROR_INPUT)
        assert exc.status_code == NOT_FOUND_ERROR_OUTPUT["status_code"]
        assert exc.code == NOT_FOUND_ERROR_OUTPUT["code"]

    def test_authentication_error(self):
        """AuthenticationError should have 401 status code."""
        from app.core.exceptions import AuthenticationError
        
        exc = AuthenticationError(**AUTH_ERROR_INPUT)
        assert exc.status_code == AUTH_ERROR_OUTPUT["status_code"]
        assert exc.code == AUTH_ERROR_OUTPUT["code"]

    def test_authorization_error(self):
        """AuthorizationError should have 403 status code."""
        from app.core.exceptions import AuthorizationError
        
        exc = AuthorizationError(**AUTHZ_ERROR_INPUT)
        assert exc.status_code == AUTHZ_ERROR_OUTPUT["status_code"]
        assert exc.code == AUTHZ_ERROR_OUTPUT["code"]

    def test_llm_error(self):
        """LLMError should handle AI/LLM failures."""
        from app.core.exceptions import LLMError
        
        exc = LLMError(**LLM_ERROR_INPUT)
        assert exc.status_code == LLM_ERROR_OUTPUT["status_code"]
        assert exc.provider == LLM_ERROR_OUTPUT["provider"]

    def test_apify_error(self):
        """ApifyError should handle scraping failures."""
        from app.core.exceptions import ApifyError
        
        exc = ApifyError(**APIFY_ERROR_INPUT)
        assert exc.status_code == APIFY_ERROR_OUTPUT["status_code"]
        assert exc.actor_id == APIFY_ERROR_OUTPUT["actor_id"]

    def test_exception_to_dict(self):
        """Exceptions should serialize to dict for API responses."""
        from app.core.exceptions import ValidationError
        
        exc = ValidationError(**VALIDATION_WITH_DETAILS_INPUT)
        result = exc.to_dict()
        
        assert result["error"]["code"] == TO_DICT_OUTPUT["code"]
        assert result["error"]["message"] == TO_DICT_OUTPUT["message"]
        assert result["error"]["details"]["field"] == TO_DICT_OUTPUT["field"]
```

##### SUB-TASK-1.1.1.3.2: Implement exceptions.py

**File:** `backend/app/core/exceptions.py`

```python
"""
Custom exception classes for PartnerScout AI.
All exceptions inherit from PartnerScoutException base class.
"""
from typing import Any, Dict, Optional


class PartnerScoutException(Exception):
    """
    Base exception for all PartnerScout errors.
    
    Attributes:
        message: Human-readable error message
        code: Machine-readable error code
        status_code: HTTP status code
        details: Additional error details
    """
    
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to API response format."""
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details
            }
        }


class ValidationError(PartnerScoutException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=400,
            details=details
        )


class NotFoundError(PartnerScoutException):
    """Raised when a requested resource is not found."""
    
    def __init__(self, message: str, resource_type: Optional[str] = None):
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=404,
            details={"resource_type": resource_type} if resource_type else {}
        )


class AuthenticationError(PartnerScoutException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            status_code=401
        )


class AuthorizationError(PartnerScoutException):
    """Raised when user lacks permission for an action."""
    
    def __init__(self, message: str = "Permission denied"):
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR",
            status_code=403
        )


class LLMError(PartnerScoutException):
    """Raised when LLM provider encounters an error."""
    
    def __init__(
        self,
        message: str,
        provider: str = "unknown",
        details: Optional[Dict[str, Any]] = None
    ):
        self.provider = provider
        super().__init__(
            message=message,
            code="LLM_ERROR",
            status_code=503,
            details={"provider": provider, **(details or {})}
        )


class ApifyError(PartnerScoutException):
    """Raised when Apify scraping encounters an error."""
    
    def __init__(
        self,
        message: str,
        actor_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.actor_id = actor_id
        super().__init__(
            message=message,
            code="APIFY_ERROR",
            status_code=503,
            details={"actor_id": actor_id, **(details or {})}
        )


class DatabaseError(PartnerScoutException):
    """Raised when database operations fail."""
    
    def __init__(self, message: str, operation: Optional[str] = None):
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            status_code=500,
            details={"operation": operation} if operation else {}
        )


class RateLimitError(PartnerScoutException):
    """Raised when rate limit is exceeded."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None
    ):
        super().__init__(
            message=message,
            code="RATE_LIMIT_ERROR",
            status_code=429,
            details={"retry_after": retry_after} if retry_after else {}
        )
```

##### SUB-TASK-1.1.1.3.3: Write Constants Module

**File:** `backend/app/core/constants.py`

```python
"""
Application constants and enums.
"""
from enum import Enum


class DiscoveryStatus(str, Enum):
    """Status values for discovery jobs."""
    PENDING = "pending"
    ANALYZING = "analyzing"
    DISCOVERING = "discovering"
    SCORING = "scoring"
    COMPLETED = "completed"
    FAILED = "failed"


class ProfileStatus(str, Enum):
    """Status values for discovered profiles."""
    NEW = "new"
    PROCESSING = "processing"
    SCORED = "scored"
    SKIPPED = "skipped"
    ERROR = "error"


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    GEMINI = "gemini"
    OLLAMA = "ollama"


class ScoreCategory(str, Enum):
    """Categories for profile scoring."""
    BRAND_ALIGNMENT = "brand_alignment"
    AUDIENCE_FIT = "audience_fit"
    ENGAGEMENT_QUALITY = "engagement_quality"
    CONTENT_QUALITY = "content_quality"
    PARTNERSHIP_POTENTIAL = "partnership_potential"


# API Constants
API_VERSION = "v1"
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Discovery Constants
MAX_REFERENCE_PROFILES = 5
DEFAULT_DISCOVERY_LIMIT = 50
MAX_DISCOVERY_LIMIT = 200
MIN_FOLLOWER_COUNT = 1000
MAX_FOLLOWER_COUNT = 1000000

# Scoring Constants
MIN_SCORE = 0
MAX_SCORE = 100
DEFAULT_SCORE_THRESHOLD = 70

# Rate Limiting Constants
DEFAULT_RATE_LIMIT = 100
DEFAULT_RATE_PERIOD = 60  # seconds
```

##### SUB-TASK-1.1.1.3.4: Write Logging Configuration

**File:** `backend/app/core/logging.py`

```python
"""
Logging configuration using structlog.
"""
import logging
import sys
from typing import Any, Dict

import structlog


def setup_logging(
    log_level: str = "INFO",
    json_logs: bool = False
) -> None:
    """
    Configure structured logging for the application.
    
    Args:
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR)
        json_logs: If True, output JSON formatted logs (for production)
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )
    
    # Shared processors
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]
    
    if json_logs:
        # Production: JSON output
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Development: Pretty console output
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True),
        ]
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a logger instance with the given name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


def log_request_context(
    request_id: str,
    user_id: str = None,
    **extra: Dict[str, Any]
) -> None:
    """
    Bind request context to all subsequent log calls.
    
    Args:
        request_id: Unique request identifier
        user_id: Optional authenticated user ID
        **extra: Additional context to bind
    """
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        user_id=user_id,
        **extra
    )
```

---

## FEATURE-1.2: FastAPI Application Setup

### STORY-1.2.1: Create FastAPI Application Entry Point

#### TASK-1.2.1.1: Write Main Application Tests

**File:** `backend/tests/unit/test_main.py`

```python
"""
Unit tests for FastAPI application setup.
TDD: Write these tests FIRST, then implement main.py
"""
import pytest
from fastapi.testclient import TestClient


class TestApplication:
    """Test suite for main FastAPI application."""

    def test_app_creates_successfully(self):
        """Application should create without errors."""
        from app.main import app
        assert app is not None
        assert app.title == "PartnerScout AI"

    def test_app_has_cors_middleware(self):
        """Application should have CORS middleware configured."""
        from app.main import app
        
        middleware_classes = [m.cls.__name__ for m in app.user_middleware]
        assert "CORSMiddleware" in middleware_classes

    def test_app_includes_api_router(self):
        """Application should include API routes."""
        from app.main import app
        
        routes = [route.path for route in app.routes]
        assert "/api/health" in routes or any("/api" in r for r in routes)


class TestHealthEndpoint:
    """Test health check endpoint."""

    @pytest.fixture
    def client(self):
        from app.main import app
        return TestClient(app)

    def test_health_returns_200(self, client):
        """Health endpoint should return 200 OK."""
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_returns_status(self, client):
        """Health endpoint should return status information."""
        response = client.get("/api/health")
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "healthy"
        assert "version" in data
        assert "environment" in data
```

#### TASK-1.2.1.2: Implement main.py

**File:** `backend/app/main.py`

```python
"""
FastAPI application entry point.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health
from app.core.config import get_settings
from app.core.logging import setup_logging, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan handler.
    
    Sets up resources on startup and cleans up on shutdown.
    """
    settings = get_settings()
    
    # Setup logging
    setup_logging(
        log_level="DEBUG" if settings.debug else "INFO",
        json_logs=settings.is_production
    )
    
    logger.info(
        "Starting PartnerScout AI",
        environment=settings.environment,
        debug=settings.debug
    )
    
    yield
    
    # Cleanup on shutdown
    logger.info("Shutting down PartnerScout AI")


def create_application() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Returns:
        Configured FastAPI application instance
    """
    settings = get_settings()
    
    app = FastAPI(
        title="PartnerScout AI",
        description="Instagram Partner Discovery Platform for D2C Brands",
        version="0.1.0",
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        lifespan=lifespan,
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(health.router, prefix="/api")
    
    return app


app = create_application()
```

---

## VALIDATION PLAN: EPIC-1

### Validation Script

**File:** `backend/scripts/validate_epic1.py`

```python
#!/usr/bin/env python3
"""
Validation script for EPIC-1: Project Foundation.
Runs all checks to verify the foundation is correctly set up.
"""
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    print(f"VALIDATION: {description}")
    print(f"Command: {' '.join(cmd)}")
    print("="*60)
    
    result = subprocess.run(cmd, capture_output=False)
    success = result.returncode == 0
    
    print(f"Result: {'PASS' if success else 'FAIL'}")
    return success


def validate_structure() -> bool:
    """Validate project structure exists."""
    required_files = [
        "app/__init__.py",
        "app/main.py",
        "app/core/config.py",
        "app/core/exceptions.py",
        "app/core/constants.py",
        "app/core/logging.py",
        "tests/conftest.py",
        "requirements.txt",
        "pyproject.toml",
        ".env.example",
    ]
    
    backend_dir = Path(__file__).parent.parent
    
    print("\n" + "="*60)
    print("VALIDATION: Project Structure")
    print("="*60)
    
    all_exist = True
    for file in required_files:
        path = backend_dir / file
        exists = path.exists()
        status = "✓" if exists else "✗"
        print(f"  {status} {file}")
        if not exists:
            all_exist = False
    
    print(f"\nResult: {'PASS' if all_exist else 'FAIL'}")
    return all_exist


def main():
    """Run all validations."""
    print("\n" + "#"*60)
    print("# EPIC-1 VALIDATION: Project Foundation")
    print("#"*60)
    
    results = []
    
    # 1. Structure validation
    results.append(validate_structure())
    
    # 2. Python syntax check
    results.append(run_command(
        ["python", "-m", "py_compile", "app/main.py"],
        "Python Syntax Check"
    ))
    
    # 3. Import validation
    results.append(run_command(
        ["python", "-c", "from app.core.config import get_settings; print(get_settings())"],
        "Config Import Check"
    ))
    
    # 4. Run unit tests
    results.append(run_command(
        ["pytest", "tests/unit/", "-v", "--tb=short"],
        "Unit Tests"
    ))
    
    # 5. Type checking
    results.append(run_command(
        ["mypy", "app/core/", "--ignore-missing-imports"],
        "Type Checking (mypy)"
    ))
    
    # 6. Code formatting check
    results.append(run_command(
        ["black", "--check", "app/"],
        "Code Formatting (black)"
    ))
    
    # Summary
    print("\n" + "#"*60)
    print("# VALIDATION SUMMARY")
    print("#"*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total}")
    
    if all(results):
        print("\n✓ EPIC-1 VALIDATION PASSED")
        return 0
    else:
        print("\n✗ EPIC-1 VALIDATION FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

### Manual Validation Checklist

| Check | Command | Expected Result |
|-------|---------|-----------------|
| Virtual env works | `source venv/bin/activate` | No errors |
| Dependencies install | `pip install -r requirements.txt` | All packages install |
| Tests pass | `pytest tests/unit/ -v` | All tests green |
| App starts | `uvicorn app.main:app --reload` | Server runs on :8000 |
| Health check | `curl http://localhost:8000/api/health` | `{"status":"healthy"}` |
| Docs accessible | Open `http://localhost:8000/docs` | Swagger UI loads |

---

## Files Created in EPIC-1

| File | Description |
|------|-------------|
| `app/__init__.py` | Package init |
| `app/main.py` | FastAPI application |
| `app/core/__init__.py` | Core package init |
| `app/core/config.py` | Settings management |
| `app/core/exceptions.py` | Custom exceptions |
| `app/core/constants.py` | Application constants |
| `app/core/logging.py` | Logging configuration |
| `app/api/__init__.py` | API package init |
| `app/api/routes/__init__.py` | Routes package init |
| `app/api/routes/health.py` | Health check endpoint |
| `tests/__init__.py` | Tests package init |
| `tests/conftest.py` | Pytest fixtures |
| `tests/unit/__init__.py` | Unit tests init |
| `tests/unit/test_config.py` | Config tests |
| `tests/unit/test_exceptions.py` | Exception tests |
| `tests/unit/test_main.py` | Application tests |
| `scripts/validate_epic1.py` | Validation script |
| `requirements.txt` | Production deps |
| `requirements-dev.txt` | Dev deps |
| `pyproject.toml` | Project config |
| `.env.example` | Env template |

---

## Definition of Done

- [ ] All directories created as per structure
- [ ] All `__init__.py` files in place
- [ ] `requirements.txt` and `requirements-dev.txt` created
- [ ] `pyproject.toml` configured
- [ ] `.env.example` created with all required variables
- [ ] `config.py` implemented and tested
- [ ] `exceptions.py` implemented and tested
- [ ] `constants.py` implemented
- [ ] `logging.py` implemented
- [ ] `main.py` creates FastAPI app
- [ ] Health endpoint returns `{"status": "healthy"}`
- [ ] All unit tests pass
- [ ] `validate_epic1.py` runs successfully
- [ ] Code formatted with black
- [ ] No mypy errors

---

## Next EPIC

After completing EPIC-1, proceed to:
- **[02-EPIC-DATABASE.md](./02-EPIC-DATABASE.md)** - Database Layer Implementation
