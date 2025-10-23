# Overview
LynkerAI is an AI-powered task execution system designed to generate and execute code from natural language descriptions using OpenAI's API. It functions as an intelligent code generator, interpreting user requests to create and manage code files automatically. The project provides a robust platform for semantic-based analysis, including birth chart verification and soulmate matching, by leveraging advanced AI models for deeper compatibility insights, and a comprehensive system for managing and interacting with AI-generated content and user data.

# User Preferences
Preferred communication style: Simple, everyday language.

# System Architecture

## Core Design Pattern
The application utilizes a command-line interface (CLI) with an AI-driven code generation pipeline:
1.  **Task Interpretation Layer**: Processes natural language task descriptions.
2.  **AI Generation Layer**: Generates code using OpenAI's chat completion API.
3.  **File Management Layer**: Manages file creation and command execution via a bridge module.

## Modular Architecture
-   **Main Control Engine (`main.py`)**: Centralized orchestration hub, coordinating all LynkerAI modules and managing a unified JSON logging system.
-   **Code Generator (`lynker_master_ai.py`)**: Handles AI-powered code generation, processes task descriptions, and interacts with the OpenAI API.
-   **Database Layer (`supabase_init.py`)**: Manages Supabase connections, including client initialization and automatic table creation for various features.
-   **TrueChart Verifier (`ai_truechart_verifier.py`)**: Performs semantic validation of birth charts against life events, supporting single and multi-chart verification, intelligent weight learning, and user life profile storage.
-   **Soulmate Matcher (`soulmate_matcher.py`)**: Identifies users with similar life experiences using semantic matching of `life_tags` and cosine similarity.
-   **Child AI Insight Generator (`child_ai_insight.py`)**: Generates independent, rule-based insights for match results using templates, with local JSON backup.
-   **Child AI Memory Vault (`child_ai_memory.py`)**: Manages user interaction history with matched partners, tracks memories and engagement, and provides data for a React frontend component.
-   **Google Drive Sync (`google_drive_sync.py`)**: Enables users to back up AI memories to their personal Google Drive via OAuth 2.0.
-   **OAuth Authorization Flow (`google_oauth_real_flow.py`, Flask API)**: Handles Google OAuth for token exchange, user info retrieval, and persistence of credentials to Supabase.
-   **Lynker Master Vault (`lynker_master_vault/`)**: An intelligent document management system for categorizing, indexing, and searching project documentation. Includes a CLI import tool, a unified Flask API for uploads and queries, and a React-based memory dashboard.
-   **Multi-Model AI Chat (`multi_model_ai.py`, Flask API integration)**: Provides a unified interface for multiple AI providers (ChatGPT, Gemini, ChatGLM, DeepSeek) with an automatic fallback mechanism and RAG integration. Includes performance monitoring and a visual dashboard.
-   **Message Hub / Conversation Bus (`conversation_bus.py`, Flask API integration)**: An event-driven, three-party collaboration system (Master AI ↔ Child AI ↔ User) for task delegation, conversation tracking, and async execution with callbacks. Includes a full-screen visual chat interface (`static/tri_chat.html`) accessible at `/tri-chat` for real-time three-party conversation monitoring and interaction.
-   **Domain Auto-Detection (`update_redirect_uri.py`)**: Dynamically detects Replit Sisko domain and provides guidance for updating Google OAuth redirect URIs.
-   **Bridge Module (`replit_bridge.py`)**: Abstracts file system operations and command execution for platform independence.
-   **Security Layer (`ai_guard_middleware.py`)**: Centralized access control for AI operations, checking user permissions, call limits, and service status.
-   **TMS - Trusted Metaphysics System (`master_ai/`)**: Global trusted chart verification network with pseudonym protection, signature verification, regional adaptation, confidence voting, and hierarchical validation architecture. Includes Master Validator API (port 8080), PostgreSQL database schema, and comprehensive documentation.

## Language & Runtime
-   **Language**: Python 3.x
-   **Execution Model**: Single-process, synchronous.

## Prompt Engineering Strategy
Utilizes structured prompt templates to ensure predictable and parseable AI responses.

## Error Handling
Includes environment validation, graceful degradation, and comprehensive output capture.

# External Dependencies

## Required Services
-   **OpenAI API**: Core AI code generation and chat completions.

## Optional Services
-   **Supabase**: Database and backend services for storing various project data (e.g., user profiles, verified charts, life events, soulmate matches, AI insights, memory data).
-   **Google Drive API**: For user data backup to personal cloud storage.

## Python Package Dependencies
-   `openai`
-   `supabase`
-   `requests`
-   `uv`
-   `numpy`
-   `sentence-transformers`
-   Standard Python libraries for system operations, concurrency, JSON, and datetime.

## Development Environment
-   **Platform**: Replit.
-   **Deployment Model**: Direct execution within the Replit environment.