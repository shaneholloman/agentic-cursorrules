<img width="785" height="707" alt="image" src="https://github.com/user-attachments/assets/3b80f21f-e081-4928-82d1-6acb516ec598" />

# agentic-cursorrules

Partition large codebases into domain-specific contexts for multi-agent workflows. Generates isolated markdown rule files that prevent agent conflicts through explicit file-tree boundaries.

## Why agentic-cursorrules

- Enforces strict domain boundaries by mapping directory structures to agent-specific contexts.
- Prevents cross-domain contamination when multiple AI agents work concurrently on the same codebase.
- Auto-generates agent files from filesystem scans or YAML configuration with intelligent directory detection.
- Optimizes context windows by limiting each agent's view to relevant subtrees only.

## Quick start

Prerequisites: Python 3.10+

```bash
git clone https://github.com/s-smits/agentic-cursorrules.git .agentic-cursorrules
cd .agentic-cursorrules

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .cursorrules.example ../.cursorrules
```

Generate agent files from automatic detection:

```bash
python main.py --auto-config
```

Or define domains manually in `config.yaml`:

```yaml
project_title: "your-project"
tree_focus:
  - "backend/api"
  - "frontend/components"
  - "ml/training"
```

Then run:

```bash
python main.py
```

Reference generated agents in your IDE:

```markdown
@agent_backend_api.md
@agent_frontend_components.md
@agent_ml_training.md
```

## Configuration strategies

**Filesystem scan** (recommended for initial setup):
```bash
python main.py --auto-config
```

**Interactive tree input**:
```bash
python main.py --tree-input
```

**Reuse detected configuration**:
```bash
python main.py --use-detected
```

**Manual YAML definition** for precise control over domain boundaries.

## Architecture at a glance

```
.agentic-cursorrules/
├── main.py                    # orchestration and generation
├── config.yaml                # manual domain definitions
├── detected_config.yaml       # auto-generated from filesystem
└── tree_files/                # intermediate tree structures

target-repo/
├── agent_backend_api.md       # backend agent context
├── agent_frontend_components.md
└── agent_ml_training.md
```

## CLI arguments

| Flag                   | Effect                                                |
|------------------------|-------------------------------------------------------|
| `--auto-config`        | Scan filesystem and generate domain configuration     |
| `--tree-input`         | Interactively provide tree structure                  |
| `--use-detected`       | Load `detected_config.yaml` instead of `config.yaml`  |
| `--verify-config`      | Print active configuration to stdout                  |
| `--local-agents`       | Store agent files in script directory                 |
| `--project-path PATH`  | Target repository location                            |
| `--project-title NAME` | Project identifier for generated configs              |
| `--recurring`          | Regenerate every 60 seconds                           |

## Advanced features

**Multi-phase directory detection**: Standard scan → detailed analysis → fallback heuristics ensure domains are identified even in non-standard project layouts.

**Gitignore-aware filtering**: Respects `.gitignore` patterns during tree generation to exclude build artifacts and dependencies.

**Extension detection via GitHub API**: Fetches comprehensive language-specific file extensions with local caching for offline operation.

**Nested domain naming**: Converts `api/auth/middleware` to `agent_api_auth_middleware.md` with clear parent-child relationships in the generated documentation.

## Best practices

- Limit concurrent agents to 3-4 domains to prevent context dilution.
- Define boundaries at architectural layer interfaces (API/DB, frontend/backend, training/inference).
- Use separate workspace windows (CMD+Shift+P → ">Duplicate Workspace") when operating multiple agents simultaneously.
- Regenerate agent files after significant refactoring that changes directory structure.

## IDE support

Primary target: Cursor IDE. Experimental compatibility with Windsurf IDE. The generated markdown files follow standard referencing patterns (`@filename.md`) compatible with most AI-enhanced editors.

## Technical details

```yaml
Core components:
- YAML-based configuration with override hierarchy
- Recursive file-tree traversal with pruning
- Markdown template generation with embedded context
- Path resolution with absolute→relative fallback
- Multi-strategy directory significance scoring
```

Inspired by [cursor-boost](https://github.com/grp06/cursor-boost) but focuses on agent isolation rather than context augmentation.

## Stars

[![Star History Chart](https://api.star-history.com/svg?repos=s-smits/agentic-cursorrules&type=Date)](https://star-history.com/#s-smits/agentic-cursorrules&Date)
