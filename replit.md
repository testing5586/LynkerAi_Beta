# Overview

This is LynkerAI, an AI-powered task execution system that uses OpenAI's API to generate and execute code based on natural language task descriptions. The system acts as an intelligent code generator that can interpret user requests and create corresponding code files automatically.

# Recent Changes

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

### Main Controller (`lynker_master_ai.py`)
- **Purpose**: Orchestrates the entire workflow from task input to code generation
- **Key Functions**:
  - `check_environment()`: Validates required API credentials before execution
  - `instruct_and_execute()`: Processes task descriptions and coordinates with OpenAI API
- **Design Decision**: Centralized control flow to maintain simplicity and transparency

### Bridge Module (`replit_bridge.py`)
- **Purpose**: Abstracts file system and command execution operations
- **Key Functions**:
  - `write_file()`: Creates files with UTF-8 encoding support
  - `run_command()`: Executes shell commands and captures output
- **Design Decision**: Separated I/O operations to enable future extensibility (e.g., remote file systems, containerized execution)

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