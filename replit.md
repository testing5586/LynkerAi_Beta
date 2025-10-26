# Overview
LynkerAI is an AI-powered task execution system designed to generate and execute code from natural language descriptions using OpenAI's API. It functions as an intelligent code generator, interpreting user requests to create and manage code files automatically. The project provides a robust platform for semantic-based analysis, including birth chart verification and soulmate matching, by leveraging advanced AI models for deeper compatibility insights, and a comprehensive system for managing and interacting with AI-generated content and user data.

LynkerAI's core vision is to establish a self-learning, self-validating intelligent system for "scientizing, socializing, and datafying" metaphysics. It aims to build a global database of verified birth times to advance "Second-Pillar Metaphysics" by collecting 1 million accurate birth times.

# User Preferences
Preferred communication style: Simple, everyday language.

# System Architecture
The application utilizes a command-line interface (CLI) with an AI-driven code generation pipeline: Task Interpretation, AI Generation, and File Management. It employs a modular architecture with a central control engine coordinating various AI-powered components.

## UI/UX Decisions
The system includes several web-based interfaces:
-   A full-screen visual chat interface (`/tri-chat`) for real-time three-party conversation monitoring and interaction.
-   An admin dashboard (`/admin`) with real-time system monitoring, database statistics, token consumption tracking, and an AI chatroom (`/chatroom`).
-   A web-based batch import center (`/import`) with real-time progress tracking.
-   A true-chart verification view (`/verify_view`) and a guided "True Birth Verification Wizard" (`/verify`).
-   An admin-only questionnaire management center (`/superintendent/questionnaire`) for managing verification content.

## Technical Implementations & Feature Specifications
-   **Core AI Generation**: Handled by `lynker_master_ai.py` using OpenAI's chat completion API.
-   **Database Management**: Supabase integration via `supabase_init.py` for various data storage.
-   **Birth Chart Verification**: `ai_truechart_verifier.py` and `admin_dashboard/verify/ai_verifier.py` perform semantic validation using qualitative confidence levels (高/中高/中/偏低/低) instead of numeric scores to align with traditional metaphysical practices.
-   **Soulmate Matching**: `soulmate_matcher.py` uses semantic matching and cosine similarity.
-   **AI Insight Generation**: `child_ai_insight.py` generates rule-based insights.
-   **User Memory & Interaction**: `child_ai_memory.py` tracks user interactions and engagement.
-   **Google Drive Sync**: `google_drive_sync.py` and `google_oauth_real_flow.py` manage OAuth and data backup.
-   **Intelligent Document Management**: `lynker_master_vault/` categorizes, indexes, and searches project documentation with a Flask API and React dashboard.
-   **Multi-Model AI Chat**: `multi_model_ai.py` provides a unified interface for multiple AI providers with RAG integration.
-   **Conversation Bus**: `conversation_bus.py` implements an event-driven, three-party collaboration system (Master AI ↔ Child AI ↔ User).
-   **Security Layer**: `ai_guard_middleware.py` provides centralized access control.
-   **Trusted Metaphysics System (TMS)**: `master_ai/` includes a global trusted chart verification network with pseudonym protection and hierarchical validation.
-   **Master Vault Engine**: Secure AES256 encryption for Master AI's learning knowledge.
-   **Master AI Evolution Engine**: Self-learning system for analyzing birthchart patterns, discovering statistical insights, and encrypting findings.
-   **Master AI Reasoner**: Advanced multi-source prediction engine integrating birthcharts, match results, and user feedback.
-   **Login AI Trigger**: `on_user_login_api.py` invokes Master AI Reasoner for real-time predictions on user login.
-   **Multi-Model Dispatcher**: Dynamically assigns OpenAI models based on user tier and routes API keys.
-   **Master AI Scheduler**: Automated periodic learning system for executing Evolution Engine and Reasoner modules.
-   **Three-Party AI Collaboration Engine**: A multi-agent system (`admin_dashboard/ai_agents/`) with Master AI, Group Leader, and Child AI roles for deep reasoning, task decomposition, and database queries.
-   **LKK Knowledge Base**: A three-tier intelligent knowledge management system (`lkk_knowledge_base/`) for rules, auto-generated patterns, and case studies, enhancing AI verification accuracy.
-   **Knowledge Retrieval Router**: Lightweight RAG system for real-time knowledge enhancement for all three AI agents.

## Language & Runtime
-   **Language**: Python 3.x
-   **Execution Model**: Single-process, synchronous.
-   **Platform**: Replit.

## Design Choices
-   **Prompt Engineering**: Utilizes structured prompt templates for predictable AI responses.
-   **Error Handling**: Includes environment validation, graceful degradation, and comprehensive output capture.
-   **Verification Philosophy**: True Birth Chart Verification uses qualitative confidence assessments (高/中高/中/偏低/低) rather than numeric scores, avoiding over-quantification of metaphysical insights. Frontend displays color-coded confidence levels (green=高, yellow=中, red=偏低/低) with supporting evidence and conflicts.

# External Dependencies

## Required Services
-   **OpenAI API**: For core AI code generation and chat completions.

## Optional Services
-   **Supabase**: Database and backend services for storing user profiles, verified charts, life events, soulmate matches, AI insights, and memory data.
-   **Google Drive API**: For user data backup to personal cloud storage.

## Python Package Dependencies
-   `openai`
-   `supabase`
-   `requests`
-   `uv`
-   `numpy`
-   `sentence-transformers`
-   `psycopg2-binary`
-   `cryptography`