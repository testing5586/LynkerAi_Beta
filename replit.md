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
-   **Purpose**: Database and backend services (e.g., `verified_charts`, `life_event_weights`, `user_life_tags`, `soulmate_matches`, `child_ai_insights` tables).
-   **Authentication**: `SUPABASE_URL` and `SUPABASE_KEY` environment variables.

## Python Package Dependencies
-   `openai`: OpenAI Python client.
-   `supabase`: Supabase Python client.
-   `uv`: Replit's package manager for dependency installation.
-   `numpy`: Used for vectorized similarity computations.
-   `sentence-transformers`: For semantic model loading and embeddings.
-   `functools.lru_cache`: For model caching.
-   Standard libraries: `subprocess`, `os`, `sys`, `concurrent.futures`.

## Development Environment
-   **Platform**: Replit.
-   **Deployment Model**: Direct execution within the Replit environment.