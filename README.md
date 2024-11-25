# Agentic cursorrules

A practical approach to managing multiple AI agents in large codebases by enforcing strict file-tree partitioning. Inspired by [cursor-boost](https://github.com/grp06/cursor-boost).

## Core Concept

This tool addresses a critical challenge in AI-assisted development: preventing merge conflicts and maintaining codebase coherence when using AI assistance across different parts of your codebase. It does this by:

1. Partitioning the codebase into logical domains (e.g., frontend, API, database)
2. Generating domain-specific markdown files with explicit file-tree boundaries
3. Providing clear context and access rules for AI assistants through these markdown files

## Why This Matters

When working with AI assistance across different parts of a codebase:
- AI responses might modify files outside their intended domain
- Changes in one area can cascade into unintended modifications elsewhere
- Maintaining proper context becomes increasingly difficult as the codebase grows

## Installation

1. Clone the repository:```bash
git clone https://github.com/yourusername/agentic-cursorrules.git .agentic-cursorrules
cd agentic-cursorrules
```

2. Create and activate a virtual environment:
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your `.cursorrules` file ()):
```bash
# Copy the example rules file
cp .cursorrules.example .cursorrules

# Edit the file with your specific rules, using cursor-boost as reference
nano .cursorrules  # or use your preferred editor
```
Important note: The `.cursorrules` file needs to be in your current working directory where you'll run the agent generator.
If there's already a `.cursorrules` file available in the root folder, it will be used instead of the current directory files.

## Using Domain-Specific Markdown Files

### Setup Requirements
- A project with distinct architectural boundaries
- Clear domain separation (e.g., frontend/backend/database)

### Creating Multiple Agent Windows
1. Use `CMD/CTRL + Shift + P` to open the command palette
2. Search for "Duplicate as Workspace in New Window"
3. Repeat this process for each desired agent window
4. Arrange the windows according to your preferred layout

### Using the Generated Markdown Files
1. Generate domain-specific markdown files using the tool
2. When working with an AI assistant:
   - Reference the appropriate markdown file for the domain you're working in
   - Use `@domain_name.md` to provide context to the AI
   - Keep the AI focused on files within the specified domain

### Best Practices
- Empirically tested to work well with up to 4 concurrent agents
- Consider system resources when running multiple instances
- Organize windows logically based on domain responsibilities

## Usage

1. Configure your domains in `config.yaml`:
```yaml
project_title: "agentic-cursorrules"
tree_focus:
  - "src"    # Frontend logic
  - "api"    # Backend services
  - "db"     # Database layer
```

2. Run the generator:
```bash
python main.py
```

If you want to run it every minute, use `--recurring` flag:
```bash
python main.py --recurring
```

3. Use the generated agent files in your prompts:
```
agentic-cursorrules_agent_src.md  # Frontend-focused agent
agentic-cursorrules_agent_api.md  # Backend-focused agent
agentic-cursorrules_agent_db.md   # Database-focused agent
```

4. Reference these files in your agent windows:
   - Use `@agentic-cursorrules_agent_src.md` in the frontend agent window
   - Use `@agentic-cursorrules_agent_api.md` in the backend agent window
   - Use `@agentic-cursorrules_agent_db.md` in the database agent window

This @ reference system ensures each agent stays within its designated boundaries, preventing conflicting file edits across domains!

- Use one markdown file per domain
- Reference the appropriate markdown file when switching domains
- Keep domain boundaries clear and well-defined

## Default Configuration

The tool comes with sensible defaults for web development projects, tailor it as you like:

```yaml
# Important directories that should always be included
important_dirs:
  - components
  - pages
  - app
  # ... and more common directories

# Directories that should always be excluded
exclude_dirs:
  - node_modules
  - dist
  - build
  # ... and more build/dependency directories

# File extensions to include
include_extensions:
  - .py
  - .ts
  - .tsx
  # ... and a lot more file types
```

## How It Works

1. **Codebase Partitioning**
   - Defines clear boundaries through YAML configuration
   - Generates separate file-trees for each domain
   - Creates agent-specific markdown files containing:
     - Base cursor rules
     - Domain-specific file access rules
     - Relevant file-tree context

2. **Access Control**
   - Each agent receives only the file-tree information for its assigned domain
   - Explicit instructions to operate only within defined boundaries
   - Clear documentation of domain responsibilities

3. **Conflict Prevention**
   - Physical separation of concerns through file-tree partitioning
   - Clear ownership boundaries for each agent
   - Reduced risk of overlapping modifications

## Best Practices

- Limit to 3-4 agents for optimal management
- Define clear domain boundaries before starting
- Use semantic naming for domains
- Review agent interactions at domain boundaries
- Maintain separate version control branches per domain when possible

## Limitations

- Not a complete solution for all merge conflicts
- Requires careful domain boundary definition
- Best suited for codebases with clear architectural separation
- May need adjustment for highly interconnected modules

## Development Setup

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Set up pre-commit hooks:
```bash
pre-commit install
```

## Contributing

Contributions are welcome, particularly in these areas:
- Enhanced domain boundary detection
- Improved conflict prevention strategies
- Additional tooling for agent coordination

## Technical Overview

```yaml
Agentic Cursor Rules: A practical implementation for managing multi-agent development through strict file-tree partitioning and access control.

Technical Overview:
- Generates domain-specific agent rulesets from base cursor rules
- Enforces physical separation of concerns through file-tree partitioning
- Prevents merge conflicts through explicit boundary definition
- Scales effectively up to 4 concurrent agents
- Supports custom domain definition via YAML configuration
- Generates markdown-based agent instruction sets
- Includes file-tree context for domain awareness

Primary Use Case:
Managing concurrent AI agent operations in large codebases where traditional merge resolution becomes impractical. Particularly effective for projects with clear architectural boundaries (e.g., frontend/backend separation, microservices).

Key Differentiator:
Unlike simple multi-agent approaches, this tool enforces physical boundaries through file-tree partitioning, significantly reducing the risk of conflicting modifications while maintaining agent context awareness.
