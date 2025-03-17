# agentic-cursorrules

A Python-based tool for managing multiple AI agents in large codebases by enforcing strict file-tree partitioning, preventing conflicts, and maintaining coherence. Inspired by [cursor-boost](https://github.com/grp06/cursor-boost).

<img src="https://github.com/user-attachments/assets/4937c3da-fbd6-49b3-9c22-86ae02dabec7" width="60%">

## Core Concept

Agentic-cursorrules partitions your codebase into logical domains (frontend, backend, database, etc.) and generates domain-specific markdown files with explicit file-tree boundaries, ensuring AI agents operate within clearly defined contexts.

## Installation

```bash
git clone https://github.com/s-smits/agentic-cursorrules.git .agentic-cursorrules
cd .agentic-cursorrules

python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

cp .cursorrules.example ../.cursorrules
```

Ensure `.cursorrules` is in your working directory or project root.

## Usage

### 1. Manual Configuration

Define domains explicitly in `config.yaml`:

```yaml
project_title: "agentic-cursorrules"

tree_focus:
  - "app"                    # Frontend logic
  - "api"                    # Backend services
  - "db"                     # Database layer
  - "api/auth/middleware"    # Specific auth middleware
  - "app/components/forms"   # Forms components
```

### 2. Automatic Configuration

Generate domains automatically:

- **Filesystem scan** to auto-generate domains:
```bash
python main.py --auto-config
```

- **Interactive tree structure input**:
```bash
python main.py --tree-input
```

- **Reuse previously detected configuration** (`detected_config.yaml`):
```bash
python main.py --use-detected
```

### 3. Run the Generator

```bash
python main.py [OPTIONS]
```

### 4. Reference Generated Agent Files

```markdown
@agent_app.md  # Frontend agent
@agent_api.md  # Backend agent
@agent_db.md   # Database agent
```

## Arguments

| Option                 | Description                                           |
|------------------------|-------------------------------------------------------|
| `--auto-config`        | Auto-generate config domains from filesystem scan     |
| `--tree-input`         | Interactively provide tree structure for config       |
| `--use-detected`       | Use existing `detected_config.yaml` if available      |
| `--verify-config`      | Print current `config.yaml` content                   |
| `--local-agents`       | Store agent files in script directory                 |
| `--project-path PATH`  | Specify target repository location                    |
| `--project-title NAME` | Set project title for generated config                |
| `--recurring`          | Run generator every 60 seconds                        |

## File Organization

- Generated tree structures stored in `tree_files/`
- Default: agent files placed directly in target repo
- With `--local-agents`: agent files remain in agentic-cursorrules directory

## Advanced Features

### 🔍 Smart Directory Analysis

- Multi-phase directory detection (standard → detailed scan → fallback)
- Intelligent identification of significant code directories
- Gitignore-aware file filtering

### 📂 Enhanced File Extension Detection

- Comprehensive extension detection via GitHub repository data
- Robust fallback extension list
- Cached results for improved performance

### 📝 Agent File Generation

- Context-aware markdown files for each domain
- Intelligent naming conventions for nested directories
- Clear directory descriptions and explicit boundaries

### ✅ Enhanced Path Handling

- Absolute path resolution with `.resolve()`
- Improved relative path calculations and graceful fallbacks
- Detailed debug messages for easier troubleshooting

## Best Practices

- Limit to 3-4 concurrent agents for optimal performance
- Clearly define domain boundaries before development
- Regularly review agent interactions at domain boundaries
- Consider separate version control branches per domain

## IDE Compatibility

Primarily designed for Cursor IDE, with experimental support for Windsurf IDE and planned support for other AI-enhanced editors.

Use CMD/CTRL+Shift+P → ">Duplicate Workspace" to manage agents in separate workspace windows.

## Technical Overview

```yaml
Key Features:
- Domain-specific agent rulesets
- Intelligent file-tree partitioning
- Explicit boundary definitions
- Optimized for multiple concurrent agents
- YAML-based flexible configuration
- Markdown-based instruction sets
- Contextual file-tree awareness
```

## Stars

[![Star History Chart](https://api.star-history.com/svg?repos=s-smits/agentic-cursorrules&type=Date)](https://star-history.com/#s-smits/agentic-cursorrules&Date)