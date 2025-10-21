# Overview

LynkerAI is an AI-powered task execution system designed to generate and execute code from natural language descriptions using OpenAI's API. It functions as an intelligent code generator, interpreting user requests to create and manage code files automatically. The project aims to provide a robust platform for semantic-based analysis, including birth chart verification and soulmate matching, by leveraging advanced AI models for deeper compatibility insights.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Core Design Pattern
The application utilizes a command-line interface (CLI) with an AI-driven code generation pipeline:
1.  **Task Interpretation Layer**: Processes natural language task descriptions.
2.  **AI Generation Layer**: Generates code using OpenAI's chat completion API.
3.  **File Management Layer**: Manages file creation and command execution via a bridge module.

## Language & Runtime
-   **Language**: Python 3.x, chosen for rapid prototyping and AI/ML support.
-   **Execution Model**: Single-process, synchronous.

## Modular Architecture

### Main Control Engine (`main.py`)
-   Acts as the centralized orchestration hub, initializing Supabase and coordinating execution of all LynkerAI modules such as `supabase_init.py`, `ai_truechart_verifier.py`, `soulmate_matcher.py`, and `child_ai_insight.py`.
-   Includes a unified JSON logging system (`master_log.json`).

### Code Generator (`lynker_master_ai.py`)
-   Handles AI-powered code generation, processing task descriptions, and interacting with the OpenAI API.
-   Includes environment validation before execution.

### Database Layer (`supabase_init.py`)
-   Manages Supabase connections, including client initialization and automatic creation/checking of required tables (`verified_charts`, `life_event_weights`, `user_life_tags`, `soulmate_matches`, `child_ai_insights`).
-   Supports environment variable configuration and graceful degradation.

### TrueChart Verifier (`ai_truechart_verifier.py`)
-   Performs semantic validation of birth charts against life events.
-   Includes functions for single and multi-chart verification, intelligent weight learning (`update_event_weights`), and user life profile storage (`save_life_tags`).
-   Uses the `shibing624/text2vec-base-chinese` model for semantic understanding.
-   Optimized for performance using batch vectorization and concurrency for faster verification.

### Soulmate Matcher (`soulmate_matcher.py`)
-   Identifies users with similar life experiences using semantic matching of `life_tags`.
-   Calculates cosine similarity between user profiles encoded into semantic vectors using the `shibing624/text2vec-base-chinese` model.
-   Stores match results in the `soulmate_matches` table.

### Child AI Insight Generator (`child_ai_insight.py`)
-   Generates independent, rule-based insights for match results without consuming main AI tokens.
-   Utilizes templates to generate insights categorized by similarity levels.
-   Stores insights in the Supabase `child_ai_insights` table with a local JSON file backup for redundancy.

### Child AI Memory Vault (`child_ai_memory.py`)
-   Manages user interaction history with matched partners, tracking memories and engagement.
-   Automatically generates memory summaries from insights and extracts meaningful tags.
-   Supports updating interaction counts and last interaction timestamps.
-   Provides data for the frontend React component `ChildAIMemoryVault.jsx`.
-   Stores data in Supabase `child_ai_memory` table with JSONB support for flexible tag storage.

### Google Drive Sync (`google_drive_sync.py`)
-   **Manual Integration** (Replit connector declined by user)
-   Enables users to backup AI memories to their personal Google Drive.
-   Uses OAuth 2.0 for secure authorization (access_token managed by backend).
-   Automatically creates "LynkerAI_Memories" folder in user's Drive.
-   Uploads memories as JSON files with timestamps.
-   OAuth credentials stored in Supabase `users` table (`drive_access_token`, `drive_refresh_token`).

### OAuth Authorization Flow (`google_oauth_real_flow.py`, Flask API)
-   **Interactive Authorization Script**: Command-line tool for initiating Google OAuth flow.
-   **Flask API Integration**: Handles OAuth callbacks at `/`, `/callback`, `/oauth2callback` routes.
-   **Token Exchange**: Automatically exchanges authorization code for access_token and refresh_token.
-   **User Info Retrieval**: Calls Google OAuth v1 API (`https://www.googleapis.com/oauth2/v1/userinfo?alt=json`) to get user email.
-   **Data Persistence**: Saves OAuth credentials to Supabase `users` table with `upsert` operation.
-   **Success Page**: Displays beautiful HTML success page after authorization.

### Lynker Master Vault (`lynker_master_vault/`)
-   **Intelligent Document Management System**: Automatically categorizes and indexes project documentation.
-   **Auto-Classification**: Documents sorted into `project_docs`, `api_docs`, and `dev_brainstorm` based on filename keywords.
-   **Import Tool** (`master_ai_importer.py`): CLI tool for importing, listing, and searching documents.
-   **Upload API** (`master_ai_uploader_api.py`): RESTful API with web interface for file uploads, running on port 8008.
-   **Upload Logger** (`upload_logger.py`): Self-learning logging system that records upload metadata (filename, category, uploader, timestamp, summary, import result) to `upload_log.json`.
-   **Context API** (`master_ai_context_api.py`): RESTful API providing knowledge summaries for AI assistants.
-   **YAML Index**: Human-readable index system tracking all imported documents.
-   **Search Functionality**: Full-text search across document names and content.
-   **API Endpoints**:
    - `POST /api/master-ai/upload` - Upload files with automatic logging
    - `GET /api/master-ai/context` - View Vault contents
    - `GET /api/master-ai/upload-history` - View upload history (supports filtering by category and limit)
    - `GET /api/master-ai/upload-stats` - View upload statistics (total uploads, by category, by uploader)
    - `GET /upload` - Web-based file upload interface
-   **Current Status**: 11+ documents indexed (6 project docs, 3 API docs, 1 dev brainstorm, 1 memory).

### Domain Auto-Detection (`update_redirect_uri.py`)
-   **Dynamic Domain Detection**: Automatically detects current Replit Sisko domain from environment variables.
-   **Redirect URI Validation**: Compares current OAuth redirect URI configuration with detected domain.
-   **Interactive Guide**: Provides step-by-step instructions for updating Google OAuth redirect URIs.
-   **Multi-Method Detection**: Uses `REPLIT_DOMAINS`, `REPLIT_DEV_DOMAIN`, or constructs from `REPL_ID`.
-   **Accessibility Check**: Verifies domain accessibility before suggesting updates.

### Bridge Module (`replit_bridge.py`)
-   Abstracts file system operations (`write_file`) and command execution (`run_command`) for platform independence.

### Security Layer (`ai_guard_middleware.py`)
-   Provides centralized access control for all AI operations, checking user permissions, daily AI call limits, and global service suspension status.
-   Integrated across all major AI modules.

## Prompt Engineering Strategy
Utilizes structured prompt templates to ensure predictable and parseable AI responses, specifying filename formats, markdown code blocks, and dependency installation instructions.

## Error Handling
Includes environment validation, graceful degradation for optional services, and comprehensive output capture.

# External Dependencies

## Required Services

### OpenAI API
-   **Purpose**: Core AI code generation.
-   **Authentication**: `OPENAI_API_KEY` environment variable.
-   **API Used**: Chat Completions API.

## Optional Services

### Supabase
-   **Purpose**: Database and backend services (e.g., `users`, `verified_charts`, `life_event_weights`, `user_life_tags`, `soulmate_matches`, `child_ai_insights`, `child_ai_memory` tables).
-   **Authentication**: `SUPABASE_URL` and `SUPABASE_KEY` environment variables.
-   **Users Table**: Stores user profiles and Google Drive OAuth credentials (`name`, `email`, `drive_email`, `drive_access_token`, `drive_refresh_token`, `drive_connected`, `created_at`, `updated_at`).

### Google Drive API (Optional)
-   **Purpose**: User data backup to personal cloud storage.
-   **Authentication**: OAuth 2.0 (user-provided access_token).
-   **Configuration**: `VITE_GOOGLE_CLIENT_ID` and `VITE_GOOGLE_REDIRECT_URI` environment variables.
-   **Note**: Manual integration - user declined Replit's Google Drive connector.

## Python Package Dependencies
-   `openai`: OpenAI Python client.
-   `supabase`: Supabase Python client.
-   `requests`: HTTP library for Google Drive API calls.
-   `uv`: Replit's package manager for dependency installation.
-   `numpy`: Used for vectorized similarity computations.
-   `sentence-transformers`: For semantic model loading and embeddings.
-   `functools.lru_cache`: For model caching.
-   Standard libraries: `subprocess`, `os`, `sys`, `concurrent.futures`, `json`, `datetime`.

## Development Environment
-   **Platform**: Replit.
-   **Deployment Model**: Direct execution within the Replit environment.