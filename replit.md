# Overview

This is LynkerAI, an AI-powered task execution system that uses OpenAI's API to generate and execute code based on natural language task descriptions. The system acts as an intelligent code generator that can interpret user requests and create corresponding code files automatically.

# Recent Changes

**October 19, 2025**
- **Created Soulmate Matcher Module (`soulmate_matcher.py`)**:
  - Semantic similarity-based matching system using Chinese language model
  - Computes life_tags similarity between users to find soulmates
  - Auto-detects and creates `soulmate_matches` table in Supabase
  - Returns top N most similar users with shared tags analysis
  - Integrated into main.py control engine
  - Updated SQL schema to include soulmate_matches table with indexes
- **Added Intelligent Weight Learning System & Life Tags Storage (`ai_truechart_verifier.py` v3.3)**:
  - Implemented `update_event_weights()`: Dynamic event weight adjustment based on similarity scores
  - Implemented `save_life_tags()`: User life profile storage (career, marriage, children, event count)
  - Integrated with Supabase tables: `life_event_weights`, `user_life_tags`
  - Smart learning: Increases weight for high-similarity unmatched events, decreases for low-similarity
  - Created SQL schema file: `supabase_tables_schema.sql` for easy database setup
- **Upgraded Supabase Initialization Module (`supabase_init.py` v2.0)**:
  - Extended table detection to include `life_event_weights` and `user_life_tags`
  - Auto-checks all three required tables on initialization
- **Created Lynker Master AI Main Control Engine (`main.py`)**:
  - Centralized entry point for all LynkerAI modules
  - Integrates `supabase_init.py`, `ai_truechart_verifier.py`
  - Unified logging system with `master_log.json`
  - Modular architecture ready for future expansion (guru_apprentice, soulmate_matcher)
- **Refactored Supabase Initialization Module (`supabase_init.py`)**:
  - Created independent module for database connection management
  - Auto-detection of `verified_charts` table
  - Reusable across all modules
- **Enhanced TrueChart Verifier (`ai_truechart_verifier.py` v3.2)**:
  - Added `run_truechart_verifier()` function for external module calls
  - Simplified main logic with `supabase_init` integration
  - Fixed indentation errors and environment variable handling
- **Integrated AI Rule Engine with Chart Verification**:
  - Added `verify_chart()` check in `ai_rule_engine_v1.py`
  - Multi-layer permission system: chart verification → user status → daily limits
- **Unified LynkerAI Firewall Protection Across All AI Modules**:
  - Added `ai_guard_middleware` firewall checks to all major AI modules
  - Protected files: `on_user_login_ai.py`, `pattern_match_engine_v3.py`, `insert_birthchart.py`, `match_recommend.py`
  - Firewall blocks unauthorized AI calls with 403 responses for:
    - Users who are blocked/banned
    - Users who exceed daily AI call limits
    - When Lynker Master suspends all AI services
  - All API keys and secrets now loaded from environment variables (no hardcoded credentials)
  - Successfully tested all firewall-protected modules

**October 18, 2025**
- Fixed all type safety issues in `lynker_master_ai.py` by adding null checks for AI responses
- Added command-line interface to accept task descriptions as arguments
- Improved parsing logic with regex-based extraction for better handling of markdown code blocks
- Added defensive checks for empty OpenAI response arrays to prevent IndexError
- Cleaned up duplicate imports and reorganized file structure
- Successfully tested code generation functionality
- **Fixed package installation to work with Replit's `uv` package manager**:
  - Updated commands from `pip install` to `uv add` to comply with Replit's environment
  - Added comprehensive dependency sanitization to prevent shell injection attacks
  - Support for version specifiers (e.g., `requests==2.32.3`, `Django>=3.0,<4.0`)
  - Support for extras syntax (e.g., `uvicorn[standard]`)
  - Validation to ignore invalid dependency declarations (无, none, malicious inputs)
  - Clean extraction of dependencies from code blocks to prevent syntax errors

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Core Design Pattern
The application follows a command-line interface (CLI) architecture with an AI-driven code generation pipeline:

1. **Task Interpretation Layer**: Accepts natural language task descriptions from users
2. **AI Generation Layer**: Uses OpenAI's chat completion API to generate code based on prompts
3. **File Management Layer**: Handles file creation and command execution through a bridge module

## Language & Runtime
- **Language**: Python 3.x
- **Rationale**: Chosen for rapid prototyping, excellent AI/ML library support, and simple scripting capabilities
- **Execution Model**: Single-process, synchronous execution

## Modular Architecture

### Main Control Engine (`main.py`)
- **Purpose**: Centralized orchestration hub for all LynkerAI subsystems
- **Key Functions**:
  - `main()`: Initializes Supabase, runs all active modules in sequence
  - `log_event()`: Unified JSON logging to `master_log.json`
- **Module Integration**:
  - `supabase_init.py` - Database connection
  - `ai_truechart_verifier.py` - Birth chart validation
  - `soulmate_matcher.py` - Soulmate matching system
  - (Future) `guru_apprentice.py`
- **Design Decision**: Single entry point enables coordinated execution and comprehensive logging

### Code Generator (`lynker_master_ai.py`)
- **Purpose**: AI-powered code generation from natural language tasks
- **Key Functions**:
  - `check_environment()`: Validates required API credentials before execution
  - `instruct_and_execute()`: Processes task descriptions and coordinates with OpenAI API
- **Design Decision**: Centralized control flow to maintain simplicity and transparency

### Database Layer (`supabase_init.py`)
- **Purpose**: Centralized Supabase connection management
- **Key Function**:
  - `init_supabase()`: Initializes client and checks/creates required tables
- **Features**:
  - Auto-detection of `verified_charts` table
  - Environment variable configuration
  - Graceful degradation for local-only operation
- **Design Decision**: Single source of truth for database connections across all modules

### TrueChart Verifier (`ai_truechart_verifier.py`)
- **Purpose**: Semantic validation of birth charts against life events
- **Key Functions**:
  - `run_truechart_verifier()`: Main entry point for external calls
  - `verify_chart()`: Single chart validation with semantic similarity
  - `verify_multiple_charts()`: Multi-chart comparison
  - `update_event_weights()`: Intelligent weight learning system
  - `save_life_tags()`: User life profile storage
- **AI Model**: shibing624/text2vec-base-chinese (free Chinese semantic model)
- **Design Decision**: Uses sentence transformers for Chinese semantic understanding

### Soulmate Matcher (`soulmate_matcher.py`)
- **Purpose**: Find users with similar life experiences using semantic matching
- **Key Functions**:
  - `run_soulmate_matcher()`: Main entry point for soulmate matching
  - `compute_similarity()`: Calculate semantic similarity between user life_tags
  - `init_match_table()`: Auto-detect and create soulmate_matches table
- **Matching Algorithm**:
  - Encodes life_tags into semantic vectors using Chinese language model
  - Computes cosine similarity between user profiles
  - Returns top N most similar users with shared tag analysis
- **AI Model**: shibing624/text2vec-base-chinese (shared with TrueChart Verifier)
- **Database Integration**: Stores match results in `soulmate_matches` table with JSONB shared_tags
- **Design Decision**: Leverages semantic understanding for deeper compatibility analysis beyond simple tag matching

### Bridge Module (`replit_bridge.py`)
- **Purpose**: Abstracts file system and command execution operations
- **Key Functions**:
  - `write_file()`: Creates files with UTF-8 encoding support
  - `run_command()`: Executes shell commands and captures output
- **Design Decision**: Separated I/O operations to enable future extensibility (e.g., remote file systems, containerized execution)

### Security Layer (`ai_guard_middleware.py`)
- **Purpose**: Provides centralized access control for all AI operations
- **Key Function**:
  - `check_permission(user_id)`: Validates user authorization before AI calls
- **Protection Rules**:
  - Blocks users who are banned/disabled
  - Enforces daily AI call limits per user
  - Allows Lynker Master to suspend all AI services globally
- **Integration**: All AI modules (`on_user_login_ai.py`, `pattern_match_engine_v3.py`, `insert_birthchart.py`, `match_recommend.py`) check permissions before execution
- **Design Decision**: Centralized security layer ensures consistent access control across all AI features

## Prompt Engineering Strategy
The system uses structured prompt templates that enforce specific output formats:
- Filename specification with clear markers
- Code content wrapped in markdown code blocks
- Dependency installation instructions included in responses

This approach ensures parseable, predictable AI responses that can be programmatically processed.

## Error Handling
- Environment validation before task execution
- Graceful degradation when optional services (Supabase) are unavailable
- Output capture for both successful and failed command executions

# External Dependencies

## Required Services

### OpenAI API
- **Purpose**: Powers the core AI code generation functionality
- **Authentication**: API key via `OPENAI_API_KEY` environment variable
- **API Used**: Chat Completions API
- **Integration Point**: `lynker_master_ai.py` - Direct client initialization
- **Criticality**: Required for core functionality

## Optional Services

### Supabase
- **Purpose**: Database and backend services (not yet implemented in current code)
- **Authentication**: URL and key via `SUPABASE_URL` and `SUPABASE_KEY` environment variables
- **Integration Point**: Environment validation only (implementation pending)
- **Criticality**: Optional - system functions without it
- **Future Use Case**: Likely intended for task history, user management, or generated code storage

## Python Package Dependencies
- `openai`: Official OpenAI Python client library
- `supabase`: Supabase Python client (imported but not actively used)
- `subprocess`: Standard library for command execution
- `os`, `sys`: Standard libraries for environment and system operations

## Development Environment
- **Platform**: Replit (evidenced by replit_bridge module and file operations)
- **Deployment Model**: Direct execution in Replit environment with file system access