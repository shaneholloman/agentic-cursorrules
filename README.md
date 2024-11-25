# Agentic Cursor Rules

A practical approach to managing multiple AI agents in large codebases by enforcing strict file-tree partitioning.

## Core Concept

This tool addresses a critical challenge in multi-agent development: preventing merge conflicts and maintaining codebase coherence when multiple AI agents work simultaneously. It does this by:

1. Partitioning the codebase into logical domains (e.g., frontend, API, database)
2. Generating agent-specific rulesets with explicit file-tree boundaries
3. Enforcing strict access controls through clear prompting

## Why This Matters

When working with multiple AI agents on a single codebase:
- Agents can inadvertently modify the same files
- Changes in one area can cascade into unintended modifications elsewhere
- Maintaining context becomes increasingly difficult as the codebase grows

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/agentic-cursorrules.git
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

4. Set up your `.cursorrules` file (inspired by [cursor-boost](https://github.com/grp06/cursor-boost)):
```bash
# Clone cursor-boost into your repository
git clone https://github.com/grp06/cursor-boost.git

# Copy the example rules file
cp .cursorrules.example .cursorrules

# Edit the file with your specific rules, using cursor-boost as reference
nano .cursorrules  # or use your preferred editor

# Optional: Remove cursor-boost if you don't need it anymore
rm -rf cursor-boost
```

Note: The `.cursorrules` file needs to be in your current working directory where you'll run the agent generator.

## Setting Up Multiple Agents

### Setup Requirements
- Cursor version 0.43 or higher
- Sufficient system resources for multiple instances

### Creating Multiple Agent Windows
1. Use `CMD/CTRL + Shift + P` to open the command palette
2. Search for "Duplicate as Workspace in New Window"
3. Repeat this process for each desired agent window
4. Arrange the windows according to your preferred layout

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