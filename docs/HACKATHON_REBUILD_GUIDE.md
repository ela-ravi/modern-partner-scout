# COMPLETE REBUILD GUIDE — PartnerScout AI (v2)

*Everything verified against the actual codebase. Nothing is guessed.*

---

## PHASE 0: Create New Project

**Step 0.1** — Create a brand new project folder:
```bash
mkdir C:\Users\DELL\Desktop\partner-scout-v2
cd C:\Users\DELL\Desktop\partner-scout-v2
git init
```

**Step 0.2** — Create a new GitHub repo:
- Go to GitHub, create a new empty repo (e.g., `partner-scout-v2`)
- Connect it:
```bash
git remote add origin https://github.com/YOUR_USERNAME/partner-scout-v2.git
```

**Step 0.3** — Open the new folder in Cursor IDE and connect Claude Code:
```bash
claude
```

---

## PHASE 1: Create Complete Folder Structure

**Step 1.1** — Create all directories:
```bash
# Root
mkdir -p docs
mkdir -p scripts

# Frontend
mkdir -p frontend/public
mkdir -p frontend/src/components/ui
mkdir -p frontend/src/components/composite
mkdir -p frontend/src/components/features
mkdir -p frontend/src/components/layouts
mkdir -p frontend/src/pages
mkdir -p frontend/src/hooks
mkdir -p frontend/src/services
mkdir -p frontend/src/types/api
mkdir -p frontend/src/contexts
mkdir -p frontend/src/mockups/_data
mkdir -p frontend/src/test/mocks
mkdir -p frontend/src/lib/api
mkdir -p frontend/src/lib/query
mkdir -p frontend/src/lib/supabase
mkdir -p frontend/src/lib/tokens
mkdir -p frontend/src/lib/utils
mkdir -p frontend/e2e

# Backend
mkdir -p backend/app/api/routes
mkdir -p backend/app/agents
mkdir -p backend/app/models
mkdir -p backend/app/services
mkdir -p backend/app/db
mkdir -p backend/app/middleware
mkdir -p backend/app/core/settings
mkdir -p backend/app/prompts/brand_analyzer
mkdir -p backend/app/prompts/discovery
mkdir -p backend/app/prompts/scorer
mkdir -p backend/app/prompts/email_composer
mkdir -p backend/app/prompts/contact_enricher
mkdir -p backend/tests
mkdir -p backend/scripts

# Claude Code
mkdir -p .claude/agents
```

**Step 1.2** — Verify:
```bash
find . -type d -not -path './.git/*' | sort
```

---

## PHASE 2: Create All Configuration Files

### 2A — Root Files

**Step 2.1** — Create `.gitignore`:
```gitignore
# ============================================
# Partner-Scout .gitignore
# ============================================

# ============================================
# Environment & Secrets
# ============================================
.env
.env.local
.env.*.local
*.env
!.env.example

# ============================================
# Python
# ============================================
venv/
.venv/
env/
ENV/
backend/venv/
__pycache__/
*.py[cod]
*$py.class
*.pyc
*.pyo
build/
dist/
*.egg
*.egg-info/
.eggs/
*.whl
.pytest_cache/
.coverage
.coverage.*
htmlcov/
.tox/
.nox/
coverage.xml
*.cover
*.py,cover
.mypy_cache/
.dmypy.json
dmypy.json
.ruff_cache/
.ipynb_checkpoints/

# ============================================
# Node.js / Frontend
# ============================================
node_modules/
dist/
dist-ssr/
*.local
logs/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*
.cache/
.parcel-cache/
.next/
.nuxt/
.turbo/
out/
build/

# ============================================
# IDE & Editors
# ============================================
.vscode/*
!.vscode/settings.json
!.vscode/tasks.json
!.vscode/launch.json
!.vscode/extensions.json
.idea/
*.iml
*.ipr
*.iws
*.swp
*.swo
*.sw?
*~
.cursor/
.claude/
*.sublime-workspace
*.sublime-project

# ============================================
# OS Generated Files
# ============================================
.DS_Store
.AppleDouble
.LSOverride
._*
.Spotlight-V100
.Trashes
Thumbs.db
Thumbs.db:encryptable
ehthumbs.db
ehthumbs_vista.db
[Dd]esktop.ini
$RECYCLE.BIN/
*.cab
*.msi
*.msix
*.msm
*.msp
*.lnk

# ============================================
# Supabase
# ============================================
.supabase/
supabase/.branches/
supabase/.temp/

# ============================================
# n8n
# ============================================
.n8n/

# ============================================
# Miscellaneous
# ============================================
*.tmp
*.temp
*.bak
*.backup
*.zip
*.tar.gz
*.rar
*.7z
*.local
local/
*.pem
*.key
*.crt
credentials.json
secrets.json
service-account*.json
*.db
*.sqlite
*.sqlite3
debug/
*.debug
```

**Step 2.2** — Create `.cursorrules` (copy exact same content as your `CLAUDE.md` — Cursor reads this file for project context). You will create `CLAUDE.md` in Phase 5.

---

### 2B — Frontend Configuration

**Step 2.3** — Create `frontend/package.json`:
```json
{
  "name": "frontend",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "lint": "eslint .",
    "preview": "vite preview",
    "test": "vitest",
    "test:watch": "vitest --watch",
    "test:coverage": "vitest --coverage",
    "format": "prettier --write \"src/**/*.{ts,tsx,css}\"",
    "format:check": "prettier --check \"src/**/*.{ts,tsx,css}\""
  },
  "dependencies": {
    "@emotion/react": "^11.14.0",
    "@emotion/styled": "^11.14.1",
    "@hookform/resolvers": "^5.2.2",
    "@mui/icons-material": "^7.3.7",
    "@mui/material": "^7.3.7",
    "@radix-ui/react-dialog": "^1.1.15",
    "@radix-ui/react-dropdown-menu": "^2.1.16",
    "@radix-ui/react-select": "^2.2.6",
    "@radix-ui/react-slider": "^1.3.6",
    "@radix-ui/react-slot": "^1.2.4",
    "@radix-ui/react-tabs": "^1.1.13",
    "@radix-ui/react-tooltip": "^1.2.8",
    "@supabase/supabase-js": "^2.95.3",
    "@tanstack/react-query": "^5.90.20",
    "clsx": "^2.1.1",
    "date-fns": "^4.1.0",
    "react": "^19.2.0",
    "react-dom": "^19.2.0",
    "react-hook-form": "^7.71.1",
    "react-router-dom": "^7.13.0",
    "tailwind-merge": "^3.4.0",
    "zod": "^4.3.6"
  },
  "devDependencies": {
    "@eslint/js": "^9.39.1",
    "@playwright/test": "^1.58.2",
    "@tailwindcss/postcss": "^4.1.18",
    "@tailwindcss/vite": "^4.1.18",
    "@testing-library/jest-dom": "^6.9.1",
    "@testing-library/react": "^16.3.2",
    "@testing-library/user-event": "^14.6.1",
    "@types/node": "^24.10.1",
    "@types/react": "^19.2.5",
    "@types/react-dom": "^19.2.3",
    "@vitejs/plugin-react": "^5.1.1",
    "autoprefixer": "^10.4.24",
    "eslint": "^9.39.1",
    "eslint-plugin-jsx-a11y": "^6.10.2",
    "eslint-plugin-react-hooks": "^7.0.1",
    "eslint-plugin-react-refresh": "^0.4.24",
    "globals": "^16.5.0",
    "jsdom": "^28.0.0",
    "msw": "^2.12.9",
    "postcss": "^8.5.6",
    "prettier": "^3.8.1",
    "prettier-plugin-tailwindcss": "^0.7.2",
    "tailwindcss": "^4.1.18",
    "typescript": "~5.9.3",
    "typescript-eslint": "^8.46.4",
    "vite": "^7.2.4",
    "vitest": "^4.0.18",
    "vitest-axe": "^0.1.0"
  }
}
```

**Step 2.4** — Create `frontend/tsconfig.json`:
```json
{
  "files": [],
  "references": [
    { "path": "./tsconfig.app.json" },
    { "path": "./tsconfig.node.json" }
  ]
}
```

**Step 2.5** — Create `frontend/tsconfig.app.json`:
```json
{
  "compilerOptions": {
    "tsBuildInfoFile": "./node_modules/.tmp/tsconfig.app.tsbuildinfo",
    "target": "ES2022",
    "useDefineForClassFields": true,
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "types": ["vite/client", "@testing-library/jest-dom"],
    "skipLibCheck": true,

    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    },

    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "verbatimModuleSyntax": true,
    "moduleDetection": "force",
    "noEmit": true,
    "jsx": "react-jsx",

    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "erasableSyntaxOnly": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedSideEffectImports": true
  },
  "include": ["src"]
}
```

**Step 2.6** — Create `frontend/tsconfig.node.json`:
```json
{
  "compilerOptions": {
    "tsBuildInfoFile": "./node_modules/.tmp/tsconfig.node.tsbuildinfo",
    "target": "ES2023",
    "lib": ["ES2023"],
    "module": "ESNext",
    "types": ["node"],
    "skipLibCheck": true,

    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "verbatimModuleSyntax": true,
    "moduleDetection": "force",
    "noEmit": true,

    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "erasableSyntaxOnly": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedSideEffectImports": true
  },
  "include": ["vite.config.ts"]
}
```

**Step 2.7** — Create `frontend/vite.config.ts`:
```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  optimizeDeps: {
    include: [
      'react-hook-form',
      '@hookform/resolvers/zod',
      'zod',
      '@radix-ui/react-slider',
      '@radix-ui/react-tabs',
      '@radix-ui/react-select',
      '@radix-ui/react-dialog',
      '@mui/icons-material/Add',
      '@mui/icons-material/ArrowBack',
      '@mui/icons-material/ArrowForward',
      '@mui/icons-material/RocketLaunch',
      '@mui/icons-material/Edit',
      '@mui/icons-material/Info',
      '@mui/icons-material/AccessTime',
      '@mui/icons-material/Dashboard',
      '@mui/icons-material/Delete',
      '@mui/icons-material/People',
      '@mui/icons-material/CheckCircle',
      '@mui/icons-material/CalendarToday',
      '@mui/icons-material/KeyboardArrowDown',
      '@mui/icons-material/Check',
      '@mui/icons-material/Star',
      '@mui/icons-material/Email',
      '@mui/icons-material/Score',
      '@mui/icons-material/StopCircle',
      '@mui/icons-material/Refresh',
      '@mui/icons-material/Mail',
      '@mui/icons-material/AutoAwesome',
      '@mui/icons-material/Send',
      '@mui/icons-material/SearchOff',
      '@mui/icons-material/OpenInNew',
      '@mui/icons-material/ContentCopy',
      '@mui/icons-material/Bookmark',
      '@mui/icons-material/BookmarkBorder',
      '@mui/icons-material/ThumbUp',
      '@mui/icons-material/Phone',
      '@mui/icons-material/LocationOn',
      '@mui/icons-material/Language',
      '@mui/icons-material/Visibility',
      '@mui/icons-material/TrendingUp',
      '@mui/icons-material/Search',
      '@mui/icons-material/PlayCircleOutline',
      '@mui/icons-material/ListAlt',
      'date-fns',
      '@supabase/supabase-js',
      '@tanstack/react-query',
    ],
  },
})
```

**Step 2.8** — Create `frontend/vitest.config.ts`:
```ts
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/index.ts',
      ],
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

**Step 2.9** — Create `frontend/eslint.config.js`:
```js
import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import jsxA11y from 'eslint-plugin-jsx-a11y'
import tseslint from 'typescript-eslint'
import { defineConfig, globalIgnores } from 'eslint/config'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      js.configs.recommended,
      tseslint.configs.recommended,
      reactHooks.configs.flat.recommended,
      reactRefresh.configs.vite,
    ],
    plugins: {
      'jsx-a11y': jsxA11y,
    },
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
    },
    rules: {
      'jsx-a11y/alt-text': 'error',
      'jsx-a11y/anchor-has-content': 'error',
      'jsx-a11y/anchor-is-valid': 'warn',
      'jsx-a11y/aria-props': 'error',
      'jsx-a11y/aria-proptypes': 'error',
      'jsx-a11y/aria-unsupported-elements': 'error',
      'jsx-a11y/click-events-have-key-events': 'warn',
      'jsx-a11y/heading-has-content': 'error',
      'jsx-a11y/html-has-lang': 'error',
      'jsx-a11y/img-redundant-alt': 'error',
      'jsx-a11y/interactive-supports-focus': 'warn',
      'jsx-a11y/label-has-associated-control': 'error',
      'jsx-a11y/no-access-key': 'error',
      'jsx-a11y/no-autofocus': 'warn',
      'jsx-a11y/no-distracting-elements': 'error',
      'jsx-a11y/no-redundant-roles': 'error',
      'jsx-a11y/role-has-required-aria-props': 'error',
      'jsx-a11y/role-supports-aria-props': 'error',
      'jsx-a11y/scope': 'error',
      'jsx-a11y/tabindex-no-positive': 'error',
    },
  },
])
```

**Step 2.10** — Create `frontend/.prettierrc`:
```json
{
  "semi": false,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100,
  "plugins": ["prettier-plugin-tailwindcss"]
}
```

**Step 2.11** — Create `frontend/postcss.config.js`:
```js
export default {
  plugins: {
    '@tailwindcss/postcss': {},
  },
}
```

**Step 2.12** — Create `frontend/.gitignore`:
```gitignore
# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

node_modules
dist
dist-ssr
*.local

# Editor directories and files
.vscode/*
!.vscode/extensions.json
.idea
.DS_Store
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?

# E2E test credentials and session files
e2e/.env
/tmp/partner-scout-e2e-session.json
```

**Step 2.13** — Create `frontend/index.html`:
```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>PartnerScout AI</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

**Step 2.14** — Create `frontend/.env.example`:
```env
# PartnerScout AI - Frontend Environment Variables
# Copy this file to .env and fill in your values

# =============================================================================
# Supabase Configuration
# =============================================================================
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key

# =============================================================================
# API Configuration (must end with /api)
# =============================================================================
VITE_API_BASE_URL=http://localhost:8000/api

# =============================================================================
# Application Configuration
# =============================================================================
VITE_APP_NAME=PartnerScout AI
VITE_APP_VERSION=1.0.0
```

**Step 2.15** — Create `frontend/.env` (actual values — NEVER committed):
```env
VITE_SUPABASE_URL=https://your-actual-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-actual-anon-key
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_NAME=PartnerScout AI
VITE_APP_VERSION=1.0.0
```
> Replace with your real Supabase credentials from Supabase dashboard > Project Settings > API.

**Step 2.16** — Create `frontend/e2e/.env.example`:
```env
# E2E Test Credentials
# Copy this file to .env and fill in your test account credentials

# Test user email (must be a valid Supabase auth account)
E2E_TEST_EMAIL=your-test@email.com

# Test user password
E2E_TEST_PASSWORD=your-password

# Optional: Override the target URL (default: http://localhost:5173)
# TEST_URL=http://localhost:5173
```

---

### 2C — Backend Configuration

**Step 2.17** — Create `backend/requirements.txt`:
```txt
# PartnerScout AI - Backend Dependencies

# FastAPI and Server
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
python-multipart>=0.0.6

# Pydantic and Settings
pydantic[email]>=2.5.0
pydantic-settings>=2.1.0

# Supabase
supabase>=2.3.0

# LangChain and LLM Providers
langchain>=0.1.0
langchain-openai>=0.0.5
langchain-google-genai>=0.0.6
langchain-community>=0.0.13
langchain-huggingface>=0.0.1

# OpenAI
openai>=1.10.0

# Google Generative AI
google-generativeai>=0.3.0

# Apify Integration
apify-client>=1.6.0

# HTTP Client
httpx>=0.26.0
aiohttp>=3.9.0

# YAML Configuration
pyyaml>=6.0.1

# JWT and Security
python-jose[cryptography]>=3.3.0
PyJWT[crypto]>=2.8.0
passlib[bcrypt]>=1.7.4

# Environment Variables
python-dotenv>=1.0.0

# HTML Parsing (Contact Enrichment)
beautifulsoup4>=4.12.0
lxml>=5.1.0

# Utilities
tenacity>=8.2.0
numpy>=1.26.0

# Testing
pytest>=7.4.0
pytest-asyncio>=0.23.0
pytest-cov>=4.1.0

# Development Tools
black>=24.1.0
isort>=5.13.0
flake8>=7.0.0
mypy>=1.8.0
```

**Step 2.18** — Create `backend/runtime.txt`:
```
python-3.11.0
```

**Step 2.19** — Create `backend/pytest.ini`:
```ini
[pytest]
# PartnerScout AI - Pytest Configuration

# Test discovery
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Markers
markers =
    unit: Unit tests (run quickly, no external dependencies)
    integration: Integration tests (may require mocked external services)
    slow: Slow tests (take more than 5 seconds)
    security: Security tests
    contract: Contract tests (verify response formats)

# Async mode for pytest-asyncio
asyncio_mode = auto

# Output configuration
addopts =
    -v
    --tb=short
    --strict-markers
    -ra

# Coverage configuration
[pytest:coverage]
source = app
branch = True
omit =
    */tests/*
    */__pycache__/*
    */venv/*

# Warnings
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
```

**Step 2.20** — Create `backend/.env.example`:
```env
# PartnerScout AI - Environment Variables Example
# Copy this file to .env and fill in your values

# =============================================================================
# Environment
# =============================================================================
ENVIRONMENT=development
DEBUG=false
LOG_LEVEL=INFO

# =============================================================================
# API Configuration
# =============================================================================
API_HOST=0.0.0.0
API_PORT=8000

# =============================================================================
# Supabase (Required)
# =============================================================================
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret

# =============================================================================
# LLM Provider Selection
# Options: openai, gemini, ollama, openrouter, huggingface
# =============================================================================
LLM_PROVIDER=openai

# =============================================================================
# OpenAI
# =============================================================================
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview

# =============================================================================
# Google Gemini
# =============================================================================
GEMINI_API_KEY=AIza...
GEMINI_MODEL=gemini-pro

# =============================================================================
# Ollama (Local LLM)
# =============================================================================
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# =============================================================================
# OpenRouter (Access to Claude, GPT-4, Llama via single API)
# Get your key at: https://openrouter.ai/keys
# =============================================================================
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# =============================================================================
# Hugging Face (Open-source models)
# Get your key at: https://huggingface.co/settings/tokens
# =============================================================================
HUGGINGFACE_API_KEY=hf_...
HUGGINGFACE_MODEL=mistralai/Mistral-7B-Instruct-v0.2

# =============================================================================
# Embedding Provider
# Options: openai, gemini, huggingface
# =============================================================================
EMBEDDING_PROVIDER=openai

# =============================================================================
# Apify (Instagram Scraping)
# =============================================================================
APIFY_API_KEY=apify_api_...

# =============================================================================
# N8N Orchestration
# =============================================================================
N8N_SERVICE_KEY=your-service-key
N8N_WEBHOOK_URL=http://localhost:5678/webhook/partner-discovery
```

**Step 2.21** — Create `backend/.env` (actual values — NEVER committed):
```env
ENVIRONMENT=development
DEBUG=false
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000

SUPABASE_URL=https://your-actual-project.supabase.co
SUPABASE_ANON_KEY=your-actual-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-actual-service-role-key
SUPABASE_JWT_SECRET=your-actual-jwt-secret

LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-actual-key
OPENAI_MODEL=gpt-4-turbo-preview

APIFY_API_KEY=apify_api_your-actual-key
EMBEDDING_PROVIDER=openai
```
> Replace with your real keys. SUPABASE_SERVICE_ROLE_KEY is the **service role** key (not the anon key). Get it from Supabase dashboard > Project Settings > API > service_role.

**Step 2.22** — Create `backend/app/core/settings/agents.yaml`:
```yaml
# PartnerScout AI - Agent Configuration

global:
  default_model: "gpt-4-turbo-preview"
  default_temperature: 0.7
  default_max_tokens: 2048
  max_retries: 3
  retry_delay_seconds: 2

agents:
  brand_analyzer:
    name: "Brand Analyzer"
    description: "Analyzes brand identity from description and reference profiles"
    enabled: true
    temperature: 0.5
    max_tokens: 2048
    output:
      min_hashtags: 5
      max_hashtags: 20
      min_keywords: 5
      max_keywords: 15
      embedding_dimensions: 1536
    prompts:
      system: "brand_analyzer/system.txt"
      user: "brand_analyzer/user.txt"

  discovery:
    name: "Discovery Agent"
    description: "Discovers similar Instagram profiles using hashtags and keywords"
    enabled: true
    temperature: 0.3
    max_tokens: 1024
    discovery:
      default_limit: 50
      max_limit: 100
      min_followers: 1000
      max_followers: 1000000
      batch_size: 10
    deduplication:
      enabled: true
      check_username: true
      check_profile_url: true
    prompts:
      system: "discovery/system.txt"
      user: "discovery/user.txt"

  scorer:
    name: "Profile Scorer"
    description: "Scores discovered profiles across 6 dimensions"
    enabled: true
    temperature: 0.3
    max_tokens: 2048
    scoring:
      batch_size: 5
      parallel_scoring: false
      include_reasoning: true
    fake_detection:
      enabled: true
      engagement_threshold: 0.01
      follower_following_ratio_min: 0.1
      suspicious_patterns:
        - "buy followers"
        - "get followers fast"
        - "dm for promo"
    contact_extraction:
      extract_email: true
      extract_website: true
      check_business_account: true
    prompts:
      system: "scorer/system.txt"
      user: "scorer/user.txt"

  email_composer:
    name: "Email Composer"
    description: "Generates personalized outreach emails"
    enabled: true
    temperature: 0.7
    max_tokens: 1024
    email:
      default_tone: "friendly"
      available_tones:
        - professional
        - friendly
        - casual
      max_subject_length: 100
      max_body_length: 2000
      include_personalization: true
    prompts:
      system: "email_composer/system.txt"
      user: "email_composer/user.txt"

  contact_enricher:
    name: "Contact Enricher"
    description: "Enriches profile contact info by scraping websites and extracting emails, phones, addresses"
    enabled: true
    temperature: 0.3
    max_tokens: 1024
    enrichment:
      max_pages_to_fetch: 3
      request_timeout_seconds: 10
      max_content_length: 4000
    prompts:
      system: "contact_enricher/system.txt"
      user: "contact_enricher/user.txt"

apify:
  instagram_profile_scraper:
    actor_id: "apify/instagram-profile-scraper"
    timeout_seconds: 60
    memory_mbytes: 1024
    max_retries: 1
  instagram_hashtag_scraper:
    actor_id: "apify/instagram-hashtag-scraper"
    timeout_seconds: 90
    memory_mbytes: 1024
    max_retries: 1
    results_limit: 20
```

**Step 2.23** — Create `backend/app/core/settings/scoring.yaml`:
```yaml
# PartnerScout AI - Scoring Configuration
# Weights, thresholds, and dimension configurations for profile scoring

# Scoring dimension weights (must sum to 1.0)
weights:
  visual_aesthetic_match: 0.15
  content_theme_alignment: 0.20
  engagement_rate_score: 0.25
  follower_quality: 0.15
  business_indicators: 0.15
  activity_recency: 0.10

# Score thresholds
thresholds:
  min_recommendation_score: 50
  high_score: 80
  excellent:
    min: 90
    max: 100
    label: "Excellent Match"
    color: "#22c55e"
  good:
    min: 75
    max: 89
    label: "Good Match"
    color: "#3b82f6"
  moderate:
    min: 50
    max: 74
    label: "Moderate Match"
    color: "#f59e0b"
  low:
    min: 0
    max: 49
    label: "Low Match"
    color: "#ef4444"

# Scoring dimensions configuration
dimensions:
  visual_aesthetic_match:
    name: "Visual Aesthetic Match"
    description: "How well the profile's visual style matches your brand"
    min_score: 0
    max_score: 100
    factors:
      - "Color palette consistency"
      - "Photography style"
      - "Visual branding elements"
      - "Feed cohesiveness"

  content_theme_alignment:
    name: "Content Theme Alignment"
    description: "Alignment of content topics and messaging with your brand"
    min_score: 0
    max_score: 100
    factors:
      - "Topic relevance"
      - "Messaging alignment"
      - "Niche compatibility"
      - "Content quality"

  engagement_rate_score:
    name: "Engagement Rate"
    description: "Quality and authenticity of audience engagement"
    min_score: 0
    max_score: 100
    benchmarks:
      excellent: 6.0
      good: 3.0
      average: 1.5
      below_average: 0.5
      poor: 0.0
    factors:
      - "Like-to-follower ratio"
      - "Comment quality"
      - "Share/save indicators"

  follower_quality:
    name: "Follower Quality"
    description: "Authenticity and relevance of the follower base"
    min_score: 0
    max_score: 100
    factors:
      - "Follower authenticity"
      - "Geographic relevance"
      - "Demographic alignment"
      - "Follower engagement"
    red_flags:
      - "High percentage of fake followers"
      - "Sudden follower spikes"
      - "Low follower-to-following ratio"

  business_indicators:
    name: "Business Readiness"
    description: "Signs of professionalism and partnership readiness"
    min_score: 0
    max_score: 100
    factors:
      - "Business/creator account"
      - "Contact information available"
      - "Media kit presence"
      - "Previous brand collaborations"
      - "Professional bio"

  activity_recency:
    name: "Activity Recency"
    description: "How recently and consistently the account is active"
    min_score: 0
    max_score: 100
    recency_rules:
      last_post_within_7_days: 100
      last_post_within_14_days: 85
      last_post_within_30_days: 70
      last_post_within_60_days: 40
      last_post_within_90_days: 20
      last_post_over_90_days: 0

# Recommendation logic
recommendations:
  minimum_requirements:
    min_score: 50
    required_dimensions_above_40:
      - engagement_rate_score
      - content_theme_alignment
  tiebreaker_priority:
    - engagement_rate_score
    - content_theme_alignment
    - business_indicators
    - visual_aesthetic_match
    - follower_quality
    - activity_recency
  output:
    include_reasoning: true
    include_dimension_breakdown: true
    include_improvement_suggestions: false
```

**Step 2.24** — Create `backend/app/core/settings/limits.yaml`:
```yaml
# PartnerScout AI - Rate Limits and Timeouts Configuration

# User rate limits
rate_limits:
  jobs:
    daily_limit: 10
    hourly_limit: 5
    concurrent_limit: 2
  profiles:
    max_per_job: 100
    default_per_job: 50
    min_per_job: 10
  api:
    requests_per_minute: 60
    requests_per_hour: 1000
  email:
    daily_limit: 50
    per_profile_limit: 3

# Timeouts (in seconds)
timeouts:
  api_request: 30
  llm_request: 60
  llm_streaming: 120
  profile_scraping: 60
  hashtag_scraping: 90
  batch_scraping: 180
  brand_analysis: 60
  profile_discovery: 300
  profile_scoring: 30
  email_generation: 30
  full_discovery_workflow: 1800
  database_query: 10
  database_transaction: 30

# Retry configuration
retry:
  default:
    max_retries: 3
    initial_delay_seconds: 1
    max_delay_seconds: 30
    exponential_base: 2
    jitter: true
  llm:
    max_retries: 3
    initial_delay_seconds: 2
    max_delay_seconds: 60
    exponential_base: 2
    retryable_errors:
      - "rate_limit_exceeded"
      - "server_error"
      - "timeout"
  scraping:
    max_retries: 1
    initial_delay_seconds: 5
    max_delay_seconds: 30
    exponential_base: 2
  database:
    max_retries: 3
    initial_delay_seconds: 0.5
    max_delay_seconds: 5
    exponential_base: 2

# Batch processing configuration
batching:
  scoring:
    batch_size: 5
    delay_between_batches_seconds: 1
    parallel_requests: 3
  discovery:
    batch_size: 10
    delay_between_batches_seconds: 2
  status_updates:
    batch_size: 20
    delay_between_batches_seconds: 0.5

# Queue configuration
queue:
  jobs:
    max_queue_size: 100
    processing_concurrency: 2
    job_visibility_timeout_seconds: 600
  profiles:
    max_queue_size: 1000
    processing_concurrency: 5
    job_visibility_timeout_seconds: 120

# Circuit breaker configuration
circuit_breaker:
  llm:
    failure_threshold: 5
    recovery_timeout_seconds: 60
    half_open_requests: 3
  apify:
    failure_threshold: 3
    recovery_timeout_seconds: 120
    half_open_requests: 2
  n8n:
    failure_threshold: 3
    recovery_timeout_seconds: 60
    half_open_requests: 2

# Caching configuration
caching:
  profiles:
    ttl_seconds: 3600
    max_size: 10000
  brand_dna:
    ttl_seconds: 86400
    max_size: 1000
  llm_responses:
    enabled: false
    ttl_seconds: 1800
```

**Step 2.25** — Create `backend/app/core/settings/__init__.py`:
```
(This file will be created by Claude Code when building Module 2 — it loads the YAML configs above)
```
> Leave this as an empty file for now. Claude Code will populate it during Phase 8.

---

## PHASE 3: Copy Specification Documents

Paste content from your Notion backup into these files:

| File to create | Notion source |
|---|---|
| `docs/prd.md` | Product Requirements Document |
| `docs/database-spec.md` | Database Specification |
| `docs/api-spec.md` | API Specification |
| `docs/ui-spec.md` | UI Design Specification |
| `.claude/agents/db-architect.md` | DB Architect sub-agent |
| `.claude/agents/backend-dev.md` | Backend Developer sub-agent |
| `.claude/agents/frontend-dev.md` | Frontend Developer sub-agent |
| `.claude/agents/qa-validator.md` | QA Validator sub-agent |
| `.claude/agents/deployer.md` | Deployer sub-agent |
| `.claude/settings.json` | Claude Code project settings |

For each file, open it in Cursor, paste the full content from Notion, save.

---

## PHASE 4: Copy Mockup Files

**Step 4.1** — Manually copy the mockups folder:
- Open your old repo folder: `C:\Users\DELL\Desktop\modern-partner-scout`
- Navigate to `frontend/src/mockups/`
- Copy the entire `mockups/` folder (15 files including `_data/` subfolder)
- Paste it into your new project at `partner-scout-v2/frontend/src/mockups/`

**Step 4.2** — Verify:
```bash
ls frontend/src/mockups/
# Should see: _data/  MockGallery.tsx  MockDashboardLayout.tsx  ... (15 files)
```

---

## PHASE 5: Create CLAUDE.md

**Step 5.1** — Create `CLAUDE.md` in the project root:
```markdown
# PartnerScout AI — Hackathon Rebuild

## Context
This is a from-scratch rebuild of PartnerScout AI for a 2-week hackathon.
All specifications are in the `docs/` folder. Visual mockups are in `frontend/src/mockups/`.

## Build Approach
Agile incremental — complete, test, and commit each module before starting the next.

## Build Order
1. Database (Supabase tables, views, RLS policies)
2. Backend Core (FastAPI app, config, auth middleware, Supabase client)
3. Backend API (REST endpoints: jobs, profiles, status, email, agents, demo)
4. Frontend Foundation (Vite, Tailwind, design tokens, UI primitives)
5. Frontend Pages (all 7 pages with real hooks/services)
6. AI Agents (brand analyzer, discovery, scorer, email composer, contact enricher)
7. Integration & E2E Testing
8. Deployment (Vercel + Render)

## Key References
- `docs/prd.md` — Product requirements
- `docs/database-spec.md` — Complete DB schema with SQL
- `docs/api-spec.md` — All API endpoints with request/response shapes
- `docs/ui-spec.md` — UI components, pages, design tokens
- `frontend/src/mockups/` — Visual blueprint React components (run at /mockups)

## Tech Stack
- Frontend: React 19, TypeScript 5.9, Tailwind CSS 4, React Query 5, React Router 7
- Backend: Python 3.11, FastAPI, LangChain (5 providers: OpenAI, Gemini, Ollama, OpenRouter, HuggingFace)
- Database: Supabase (PostgreSQL)
- Auth: Supabase Auth (JWT)
- Scraping: Apify (Instagram)
- Deployment: Vercel (frontend) + Render (backend)

## Coding Standards
- TypeScript: strict mode, no `any`, interfaces over types, path aliases (@/*)
- Python: type hints everywhere, async I/O, Pydantic models, PEP 8
- All components: functional with hooks
- Test every module before committing

## Frontend Architecture
- Entry: src/main.tsx -> App.tsx (ErrorBoundary -> QueryClientProvider -> AuthProvider -> ToastProvider -> RouterProvider)
- Lib modules: lib/api/ (client, errors), lib/query/ (client), lib/supabase/ (client), lib/tokens/ (colors, borders, shadows, motion), lib/utils/ (cn)
- Component hierarchy: ui/ (primitives) -> composite/ (combinations) -> features/ (page-specific) -> layouts/
- Testing: Vitest + React Testing Library + MSW for API mocking
- E2E: Playwright

## Backend Architecture
- Entry: app/main.py (FastAPI with CORS, exception handlers, lifespan, route registration)
- Config: app/core/config.py (pydantic-settings), app/core/settings/*.yaml (agents, scoring, limits)
- Routes: app/api/routes/ (health, jobs, status, email, agents, profiles, demo)
- Agents: app/agents/ (base, brand_analyzer, discovery, scorer, contact_enricher)
- Services: app/services/ (llm_service, orchestration_service, email_service)
- Prompts: app/prompts/{agent_name}/system.txt + user.txt
- Testing: pytest with async support, markers (unit, integration, slow, security, contract)
```

**Step 5.2** — Copy the same content into `.cursorrules` (if you haven't already from Step 2.2).

---

## PHASE 6: Initial Commit & Push

```bash
git add -A
git commit -m "chore: scaffold project with specs, mockups, and config"
git branch -M main
git push -u origin main
```

This is your clean starting point. Everything from here is module-by-module.

---

## PHASE 7: Module 1 — Database (Supabase)

> **Reference**: `docs/database-spec.md`
> **Goal**: All tables, views, RLS policies, and indexes created in Supabase

**Step 7.1** — Tell Claude Code:
```
Read docs/database-spec.md and generate the complete SQL migration script
for all tables, views, indexes, and RLS policies. Output it as backend/db/migrations/001_initial_schema.sql
```

**Step 7.2** — Open your Supabase dashboard (or create a new project if starting fresh)

**Step 7.3** — Run the SQL in Supabase:
- Go to Supabase > SQL Editor
- Paste the migration SQL
- Execute

**Step 7.4** — Verify in Supabase:
- Tables tab: `users`, `discovery_jobs`, `brand_dna`, `discovered_profiles`, `profile_scores`, `profile_contacts`
- Views: `v_job_summary`, `v_complete_profiles`
- Check RLS policies are active

**Step 7.5** — Tell Claude Code to create a test script:
```
Create backend/tests/test_db_schema.py that connects to Supabase and verifies
all tables and views exist with correct columns. Reference docs/database-spec.md.
```

**Step 7.6** — Run the test:
```bash
cd backend
python -m venv venv
venv\Scripts\activate       # Windows
pip install -r requirements.txt
pytest tests/test_db_schema.py -v
```

**Step 7.7** — Once all tests pass, commit and push:
```bash
git add -A
git commit -m "feat: Module 1 — database schema, migrations, and tests"
git push
```

---

## PHASE 8: Module 2 — Backend Core

> **Reference**: `docs/api-spec.md` (intro sections), `docs/database-spec.md`
> **Goal**: FastAPI app boots, connects to Supabase, auth middleware works

**Step 8.1** — Tell Claude Code:
```
Read docs/api-spec.md and the YAML configs in backend/app/core/settings/.
Create the backend core:
1. backend/app/__init__.py
2. backend/app/core/__init__.py
3. backend/app/core/config.py — pydantic-settings loading from .env (all providers, Supabase, Apify, N8N)
4. backend/app/core/constants.py — HTTP status codes, error codes
5. backend/app/core/exceptions.py — PartnerScoutError, AgentError, custom exception hierarchy
6. backend/app/core/settings/__init__.py — YAML config loader for agents/scoring/limits
7. backend/app/main.py — FastAPI app with CORS, exception handlers, lifespan, route registration
8. backend/app/db/supabase.py — Supabase client singleton
9. backend/app/middleware/auth.py — Supabase JWT auth dependency
10. backend/app/models/__init__.py — Base Pydantic models
11. backend/app/api/__init__.py
12. backend/app/api/routes/__init__.py
13. backend/app/api/routes/health.py — health and detailed health endpoints
```

**Step 8.2** — Test boot:
```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload
```

**Step 8.3** — Verify:
- Open `http://localhost:8000/docs` — Swagger UI loads
- Hit `http://localhost:8000/api/health` — returns OK

**Step 8.4** — Write and run tests:
```bash
pytest tests/test_core.py -v
```

**Step 8.5** — Commit:
```bash
git add -A
git commit -m "feat: Module 2 — backend core with FastAPI, config, auth, Supabase client"
git push
```

---

## PHASE 9: Module 3 — Backend API Endpoints

> **Reference**: `docs/api-spec.md`
> **Goal**: All REST endpoints working with Supabase

Build one group at a time:

**Step 9.1 — Jobs API** (`backend/app/api/routes/jobs.py`, `backend/app/models/job.py`):
```
Read docs/api-spec.md. Create the Jobs API:
- CRUD endpoints for discovery_jobs
- Pydantic models for Job, CreateJobRequest, etc.
- Full test coverage
Register the router in main.py under /api/jobs
```
```bash
pytest tests/test_jobs_api.py -v
git add -A && git commit -m "feat: Module 3a — Jobs API endpoints" && git push
```

**Step 9.2 — Profiles API** (`backend/app/api/routes/profiles.py`, `backend/app/models/profile.py`):
```
Read docs/api-spec.md. Create the Profiles API:
- List, get, bookmark, skip profiles
- Pydantic models
- Tests
Register under /api/profiles
```
```bash
pytest tests/test_profiles_api.py -v
git add -A && git commit -m "feat: Module 3b — Profiles API endpoints" && git push
```

**Step 9.3 — Status API** (`backend/app/api/routes/status.py`, `backend/app/models/status.py`):
```
Read docs/api-spec.md. Create the Status API:
- Update job status, profile status, batch updates
- Tests
Register under /api
```
```bash
pytest tests/test_status_api.py -v
git add -A && git commit -m "feat: Module 3c — Status API endpoints" && git push
```

**Step 9.4 — Email API** (`backend/app/api/routes/email.py`, `backend/app/models/email.py`):
```
Read docs/api-spec.md. Create the Email API:
- Generate and send email endpoints
- Available tones endpoint
- Tests
Register under /api/email
```
```bash
pytest tests/test_email_api.py -v
git add -A && git commit -m "feat: Module 3d — Email API endpoints" && git push
```

**Step 9.5 — Demo API** (`backend/app/api/routes/demo.py`):
```
Read docs/api-spec.md. Create the Demo API:
- Seed demo data, reset demo
- Tests
Register under /api/demo
```
```bash
pytest tests/test_demo_api.py -v
git add -A && git commit -m "feat: Module 3e — Demo API endpoints" && git push
```

---

## PHASE 10: Module 4 — Frontend Foundation

> **Reference**: `docs/ui-spec.md`, `frontend/src/mockups/`
> **Goal**: Vite app boots, design system loaded, all UI primitives built

**Step 10.1** — Install dependencies:
```bash
cd frontend
npm install
```

**Step 10.2** — Tell Claude Code to create entry points:
```
Create these foundation files. Reference the mockups for exact design token values:
1. frontend/src/main.tsx — React root: StrictMode -> createRoot -> App
2. frontend/src/App.tsx — ErrorBoundary -> QueryClientProvider -> AuthProvider -> ToastProvider -> RouterProvider
3. frontend/src/index.css — Full Tailwind CSS 4 @theme with Apple design tokens (colors, radii, shadows, fonts, animations)
4. frontend/src/lib/utils/cn.ts — cn() utility using clsx + tailwind-merge
5. frontend/src/lib/utils/index.ts — barrel export
6. frontend/src/lib/supabase/client.ts — Supabase client init from VITE_SUPABASE_URL/KEY
7. frontend/src/lib/supabase/index.ts — barrel export
8. frontend/src/lib/api/client.ts — fetch wrapper with auth headers from Supabase session
9. frontend/src/lib/api/errors.ts — API error types
10. frontend/src/lib/api/index.ts — barrel export
11. frontend/src/lib/query/client.ts — React Query client config
12. frontend/src/lib/query/index.ts — barrel export
13. frontend/src/lib/tokens/colors.ts, borders.ts, shadows.ts, motion.ts, index.ts — design token constants
14. frontend/src/contexts/AuthContext.tsx — Supabase Auth provider with login/logout/session
15. frontend/src/components/ui/Toast.tsx — ToastProvider and useToast hook
16. frontend/src/components/ErrorBoundary.tsx — Error boundary component
17. frontend/src/routes.tsx — All routes with lazy loading (include mockup routes)
18. frontend/src/test/setup.ts — Vitest setup with MSW server
19. frontend/src/test/mocks/server.ts — MSW mock server
```

**Step 10.3** — Verify app boots:
```bash
npm run dev
# Open http://localhost:5173 — should show without console errors
```

**Step 10.4** — Build all UI primitives:
```
Build all UI primitive components (one file per component in frontend/src/components/ui/):
Button, Card, Badge, Input, Textarea, Avatar, Modal (Radix Dialog), ScoreRing,
Spinner, Slider (Radix Slider), TagInput, Stepper.
Each must have TypeScript interfaces for props, use cn(), match the Apple design tokens.
Reference frontend/src/mockups/ for exact styling.
```

**Step 10.5** — Build composite components:
```
Build composite components in frontend/src/components/composite/:
SessionCard, StatsGrid, ActivityLog, ScoreBreakdown.
Reference the mockups for exact layouts.
```

**Step 10.6** — Build feature components:
```
Build feature components in frontend/src/components/features/:
ProfileCard, ProfileGrid, ProfileDetail, PipelineProgress,
EmailComposer, FollowerPresets.
Reference the mockups for exact layouts and data shapes.
```

**Step 10.7** — Build layout components:
```
Build layout components:
frontend/src/components/layouts/DashboardLayout/DashboardLayout.tsx
frontend/src/components/layouts/AuthLayout/AuthLayout.tsx
frontend/src/components/ProtectedRoute.tsx
```

**Step 10.8** — Verify mockups still work:
```bash
npm run build
npm run dev
# Navigate to http://localhost:5173/mockups — gallery should render
```

**Step 10.9** — Commit:
```bash
npm run build && npm run lint
git add -A
git commit -m "feat: Module 4 — frontend foundation, design system, all components"
git push
```

---

## PHASE 11: Module 5 — Frontend Pages & Hooks

> **Reference**: `docs/ui-spec.md`, `frontend/src/mockups/` (open side-by-side)
> **Goal**: All 7 pages working with real data from backend

**Step 11.1** — Build TypeScript types:
```
Read docs/api-spec.md. Create all TypeScript types in frontend/src/types/api/:
job.ts, profile.ts, email.ts, index.ts
Must match the Pydantic models in the backend exactly.
```

**Step 11.2** — Build service layer:
```
Create API service functions in frontend/src/services/:
jobs.ts, profiles.ts, email.ts
Each uses the lib/api/client.ts and returns typed data.
```

**Step 11.3** — Build React Query hooks:
```
Create custom hooks in frontend/src/hooks/:
useJobs.ts, useProfiles.ts, useEmail.ts, useRealtime.ts, useAuth.ts
```

**Step 11.4** — Build pages one at a time (for each, open corresponding mockup side by side):
1. `LoginPage.tsx` — reference `MockLoginPage.tsx`
2. `SessionsPage.tsx` — reference `MockSessionsPage.tsx`
3. `DiscoveryConfigPage.tsx` — reference `MockDiscoveryConfigPage.tsx`
4. `ProcessingPage.tsx` — reference `MockProcessingPage.tsx`
5. `DashboardPage.tsx` — reference `MockDashboardPage.tsx` (most complex)
6. `NotFoundPage.tsx` — reference `MockNotFoundPage.tsx`

**Step 11.5** — Verify:
```bash
npm run build && npm run lint && npm run test
```

**Step 11.6** — Commit:
```bash
git add -A
git commit -m "feat: Module 5 — all frontend pages, hooks, services, and routing"
git push
```

---

## PHASE 12: Module 6 — AI Agents

> **Reference**: `docs/api-spec.md`, `backend/app/core/settings/agents.yaml`
> **Goal**: All AI agents working end-to-end

**Step 12.1** — Build LLM service and base agent:
```
Create:
1. backend/app/services/llm_service.py — LLMService with 5 provider factories (OpenAI, Gemini, Ollama, OpenRouter, HuggingFace)
2. backend/app/agents/base.py — BaseAgent abstract class with prompt loading, chain building, metrics
3. backend/app/prompts/__init__.py
4. backend/app/prompts/loader.py — Load prompts from app/prompts/{agent}/system.txt and user.txt
```
```bash
pytest tests/test_llm_service.py tests/test_base_agent.py -v
git add -A && git commit -m "feat: Module 6a — LLM service and base agent" && git push
```

**Step 12.2** — Brand Analyzer Agent:
```
Create backend/app/agents/brand_analyzer.py
Create backend/app/prompts/brand_analyzer/system.txt and user.txt
Add POST /api/agent/analyze-brand to backend/app/api/routes/agents.py
```
```bash
pytest tests/test_brand_analyzer.py -v
git add -A && git commit -m "feat: Module 6b — Brand Analyzer agent" && git push
```

**Step 12.3** — Discovery Agent:
```
Create backend/app/agents/discovery.py
Create backend/app/prompts/discovery/system.txt and user.txt
Add POST /api/agent/discover to agents router
```
```bash
pytest tests/test_discovery_agent.py -v
git add -A && git commit -m "feat: Module 6c — Discovery agent" && git push
```

**Step 12.4** — Scorer Agent:
```
Create backend/app/agents/scorer.py
Create backend/app/prompts/scorer/system.txt and user.txt
Add POST /api/agent/score to agents router
```
```bash
pytest tests/test_scorer.py -v
git add -A && git commit -m "feat: Module 6d — Scorer agent" && git push
```

**Step 12.5** — Email Composer + Contact Enricher:
```
Create backend/app/agents/contact_enricher.py
Create backend/app/prompts/email_composer/system.txt and user.txt
Create backend/app/prompts/contact_enricher/system.txt and user.txt
Create backend/app/services/email_service.py
Create backend/app/services/orchestration_service.py — orchestrates the full pipeline
```
```bash
pytest tests/ -v
git add -A && git commit -m "feat: Module 6e — Email composer, contact enricher, orchestration" && git push
```

---

## PHASE 13: Module 7 — Integration & E2E Testing

> **Goal**: Full pipeline works end-to-end

**Step 13.1** — Start both servers:
```bash
# Terminal 1
cd backend && venv\Scripts\activate && uvicorn app.main:app --reload

# Terminal 2
cd frontend && npm run dev
```

**Step 13.2** — Manual smoke test:
1. Open `http://localhost:5173`
2. Login/signup with Supabase Auth
3. Create a new discovery session
4. Watch processing pipeline
5. View dashboard with results
6. Open profile detail, compose email
7. Test bookmark, filter, sort

**Step 13.3** — Tell Claude Code to write E2E tests:
```
Create Playwright E2E tests in frontend/e2e/:
- login.spec.ts
- create-session.spec.ts
- dashboard.spec.ts
Cover the critical user journey.
```

**Step 13.4** — Run E2E:
```bash
cd frontend
npx playwright install
npx playwright test
```

**Step 13.5** — Commit:
```bash
git add -A
git commit -m "feat: Module 7 — integration tests and E2E"
git push
```

---

## PHASE 14: Module 8 — Deployment

> **Goal**: Live on Vercel (frontend) + Render (backend)

**Step 14.1** — Frontend to Vercel:
- Connect GitHub repo on Vercel
- Root directory: `frontend/`
- Build command: `npm run build`
- Output directory: `dist`
- Set environment variables:
  - `VITE_SUPABASE_URL`
  - `VITE_SUPABASE_ANON_KEY`
  - `VITE_API_BASE_URL` (your Render backend URL + `/api`)
  - `VITE_APP_NAME`
  - `VITE_APP_VERSION`

**Step 14.2** — Backend to Render:
- Create new Web Service on Render
- Connect your GitHub repo
- Root directory: `backend/`
- Runtime: Python 3.11
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Set ALL environment variables from `backend/.env`

**Step 14.3** — Update backend CORS to allow your Vercel domain

**Step 14.4** — Test live:
- Open your Vercel URL
- Full smoke test on production

**Step 14.5** — Commit:
```bash
git add -A
git commit -m "feat: Module 8 — deployment config for Vercel and Render"
git push
```

---

## PHASE 15: Merge (if using branches)

If you created a dev branch:
```bash
gh pr create --title "Hackathon Rebuild" --body "Complete rebuild of PartnerScout AI"
gh pr merge --squash
```

---

## Quick Reference: Commit Sequence

| # | Commit | Contents |
|---|---|---|
| 0 | `chore: scaffold project` | Folders, all configs, specs, mockups, CLAUDE.md |
| 1 | `feat: Module 1 — database schema` | SQL migrations, schema tests |
| 2 | `feat: Module 2 — backend core` | FastAPI, config, auth, Supabase, health |
| 3a | `feat: Module 3a — Jobs API` | Jobs CRUD + tests |
| 3b | `feat: Module 3b — Profiles API` | Profiles endpoints + tests |
| 3c | `feat: Module 3c — Status API` | Status update endpoints + tests |
| 3d | `feat: Module 3d — Email API` | Email generate/send + tests |
| 3e | `feat: Module 3e — Demo API` | Demo seed/reset + tests |
| 4 | `feat: Module 4 — frontend foundation` | Design system, all components, lib modules |
| 5 | `feat: Module 5 — frontend pages` | All 7 pages, hooks, services, types |
| 6a | `feat: Module 6a — LLM service + base agent` | LLMService, BaseAgent, prompt loader |
| 6b | `feat: Module 6b — Brand Analyzer` | Agent + prompts + endpoint |
| 6c | `feat: Module 6c — Discovery Agent` | Agent + prompts + endpoint |
| 6d | `feat: Module 6d — Scorer Agent` | Agent + prompts + endpoint |
| 6e | `feat: Module 6e — Email + Contact agents` | Agents + orchestration service |
| 7 | `feat: Module 7 — integration tests` | E2E + integration |
| 8 | `feat: Module 8 — deployment` | Vercel + Render config |

---

## Tips for Working with Claude Code

- **One module at a time.** Don't ask Claude to build everything at once.
- **Always say "Read [spec file] first"** before asking it to build something.
- **Point to the mockups.** Say "Reference `frontend/src/mockups/MockDashboardPage.tsx` for the exact layout."
- **Test before committing.** Run `pytest` or `npm run build` after each module.
- **If something breaks,** tell Claude Code the exact error and which spec to reference for the fix.
- **YAML configs matter.** The agents, scoring, and limits YAML files control all agent behavior — tell Claude Code to read them when building agents.

---

## Files Checklist

### Root (3 files)
- [ ] `.gitignore`
- [ ] `.cursorrules`
- [ ] `CLAUDE.md`

### Frontend Config (14 files)
- [ ] `frontend/package.json`
- [ ] `frontend/tsconfig.json`
- [ ] `frontend/tsconfig.app.json`
- [ ] `frontend/tsconfig.node.json`
- [ ] `frontend/vite.config.ts`
- [ ] `frontend/vitest.config.ts`
- [ ] `frontend/eslint.config.js`
- [ ] `frontend/.prettierrc`
- [ ] `frontend/postcss.config.js`
- [ ] `frontend/.gitignore`
- [ ] `frontend/index.html`
- [ ] `frontend/.env.example`
- [ ] `frontend/.env`
- [ ] `frontend/e2e/.env.example`

### Backend Config (8 files)
- [ ] `backend/requirements.txt`
- [ ] `backend/runtime.txt`
- [ ] `backend/pytest.ini`
- [ ] `backend/.env.example`
- [ ] `backend/.env`
- [ ] `backend/app/core/settings/agents.yaml`
- [ ] `backend/app/core/settings/scoring.yaml`
- [ ] `backend/app/core/settings/limits.yaml`

### Spec Documents (10 files)
- [ ] `docs/prd.md`
- [ ] `docs/database-spec.md`
- [ ] `docs/api-spec.md`
- [ ] `docs/ui-spec.md`
- [ ] `.claude/agents/db-architect.md`
- [ ] `.claude/agents/backend-dev.md`
- [ ] `.claude/agents/frontend-dev.md`
- [ ] `.claude/agents/qa-validator.md`
- [ ] `.claude/agents/deployer.md`
- [ ] `.claude/settings.json`

### Mockups (15 files — copied from old repo)
- [ ] `frontend/src/mockups/_data/mockJobs.ts`
- [ ] `frontend/src/mockups/_data/mockProfiles.ts`
- [ ] `frontend/src/mockups/_data/mockAnalytics.ts`
- [ ] `frontend/src/mockups/_data/mockLogEntries.ts`
- [ ] `frontend/src/mockups/_data/mockPipelineStages.ts`
- [ ] `frontend/src/mockups/MockGallery.tsx`
- [ ] `frontend/src/mockups/MockDashboardLayout.tsx`
- [ ] `frontend/src/mockups/MockLoginPage.tsx`
- [ ] `frontend/src/mockups/MockErrorPage.tsx`
- [ ] `frontend/src/mockups/MockNotFoundPage.tsx`
- [ ] `frontend/src/mockups/MockSessionsPage.tsx`
- [ ] `frontend/src/mockups/MockDiscoveryConfigPage.tsx`
- [ ] `frontend/src/mockups/MockProcessingPage.tsx`
- [ ] `frontend/src/mockups/MockDashboardPage.tsx`
- [ ] `frontend/src/mockups/index.ts`

**Total: 50 files before you write a single line of application code.**
