# agentic-cursorrules

Partition large codebases into domain-specific contexts for multi-agent workflows. Generates isolated markdown rule files that prevent agent conflicts through explicit file-tree boundaries.

## Why agentic-cursorrules

Traditional AI agent workflows give every helper the whole repository, which leads to conflicting edits and confusing cross-domain suggestions. Agentic-cursorrules keeps each agent inside a clearly defined slice of the tree, so conversations stay focused, diffs stay local, and coordination overhead drops without forcing the agents to understand the entire project at once.

## How it works

Agentic-cursorrules reads a configuration that maps directory patterns to named domains. It can build that configuration automatically by scanning the filesystem or you can define the mapping yourself in `config.yaml`. When you run `main.py`, the tool resolves each domain, filters files using `.gitignore` rules, and writes per-domain markdown files that describe the boundaries and relevant paths. These markdown files are referenced inside your IDE so every AI agent receives only the context that matches its domain.

## Quick start

Prerequisites: Python 3.10+

```bash
git clone https://github.com/s-smits/agentic-cursorrules.git .agentic-cursorrules
cd .agentic-cursorrules

uv venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv sync

cp .cursorrules.example ../.cursorrules
```

### Dependency management

- Install updates: `uv sync`
- Add packages: `uv add <package>`
- Remove packages: `uv remove <package>`
- Run commands without activating the venv: `uv run python main.py --auto-config`

## Usage

### Automatic domain detection

```bash
uv run python main.py --auto-config
```

This scans the repository, builds a suggested domain mapping, and stores it in `detected_config.yaml`. Rerun the command to refresh the mapping after large refactors.

### Manual domain definition

Edit `config.yaml` when you want to control boundaries precisely:

```yaml
project_title: "your-project"
tree_focus:
  - "backend/api"
  - "frontend/components"
  - "ml/training"
```

Generate the agent files with:

```bash
uv run python main.py
```

### Other entry points

- Inspect the current config without writing files: `uv run python main.py --verify-config`
- Provide your own tree interactively: `uv run python main.py --tree-input`
- Use the last detected config: `uv run python main.py --use-detected`

## Agent files

Each domain produces a markdown file such as `@agent_backend_api.md` or `@agent_frontend_components.md`. Reference these from your IDE (for example, Cursor or Windsurf) when prompting an agent. The file lists the directories, key files, and guardrails that apply to that domain so the agent stays within its lane.

## Repository layout (for orientation)

```
.agentic-cursorrules/
├── main.py             # orchestration and file generation
├── config.yaml         # primary configuration
├── config_manual.yaml  # sample manual setup
├── smart_analyzer.py   # directory and extension detection logic
└── tests/              # pytest-based checks
```
