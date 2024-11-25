from pathlib import Path
from typing import List, Set

from config import *

class ProjectTreeGenerator:
    """
    Generates various representations of a project's file structure,
    including lists of files by type, a combined file list,
    a project tree, and a shortened file content summary.
    """

    def __init__(self, project_root: Path):
        """
        Initializes the generator with exclusion patterns and the project root.

        Args:
            project_root: The root directory of the project.
        """
        self.project_root = project_root
        self.EXCLUDE_DIRS: Set[str] = {
            '__pycache__',
            'node_modules',
            '.next',
            '.git',
            'venv',
            'env',
            '.pytest_cache',
            'dist',
            'build',
            'coverage',
            'components/ui',
            'fonts',
            'logs',
            'cache',
            'public'
        }
        
        self.EXCLUDE_FILES: Set[str] = {
            'next.config.js',
            'tailwind.config.js',
            'postcss.config.js', 
            'tsconfig.json',
            'package.json',
            'package-lock.json',
            'README.md',
            '.env',
            'test_*.py',
            'next-env.d.ts'
        }
        
        self.INCLUDE_EXTENSIONS: Set[str] = {
            '.py', '.tsx', '.ts', '.json'
        }

    def find_focus_dirs(self, directory: Path, focus_dirs: List[str]) -> List[Path]:
        """
        Finds directories matching the focus names within one level of the root.
        
        Args:
            directory: The directory to search in
            focus_dirs: List of directory names to focus on
            
        Returns:
            List of Path objects for matching directories
        """
        found_dirs = []
        for item in directory.iterdir():
            if item.is_dir():
                if item.name in focus_dirs:
                    found_dirs.append(item)
                else:
                    # Check one level deeper
                    for subitem in item.iterdir():
                        if subitem.is_dir() and subitem.name in focus_dirs:
                            found_dirs.append(subitem)
        return found_dirs

    def generate_tree(self, directory: Path, file_types: List[str] = None, max_depth: int = 3) -> List[str]:
        """
        Generates a visual tree representation of the directory structure.

        Args:
            directory: The directory to generate the tree for.
            file_types: A list of file extensions to include in the tree.
            max_depth: The maximum depth to traverse into directories.

        Returns:
            A list of strings representing the directory tree.
        """
        tree_lines = []

        def _generate_tree(dir_path: Path, prefix: str = "", depth: int = 0):
            if depth > max_depth:
                return

            items = sorted(list(dir_path.iterdir()), key=lambda x: (not x.is_file(), x.name))
            for i, item in enumerate(items):
                if any(excluded in item.parts for excluded in self.EXCLUDE_DIRS) or \
                   any(item.match(pattern) for pattern in self.EXCLUDE_FILES):
                    continue

                is_last = i == len(items) - 1
                display_path = item.name  # Only display name in tree

                if item.is_dir():
                    tree_lines.append(f"{prefix}{'└── ' if is_last else '├── '}{display_path}/")
                    _generate_tree(item, prefix + ('    ' if is_last else '│   '), depth + 1)
                elif item.is_file() and (file_types is None or any(item.name.endswith(ext) for ext in file_types)):
                    tree_lines.append(f"{prefix}{'└── ' if is_last else '├── '}{display_path}")

        _generate_tree(directory)
        return tree_lines

def generate_agent_files(focus_dirs: List[str]):
    """
    Generates agent-specific markdown files for each focus directory.
    
    Args:
        focus_dirs: List of focus directory names from config
    """
    # Read the base cursor rules
    try:
        with open('.cursorrules.md', 'r', encoding='utf-8') as f:
            base_rules = f.read()
    except FileNotFoundError:
        print("Warning: .cursorrules.md not found")
        base_rules = ""

    # Create agent files for each focus directory
    for dir_name in focus_dirs:
        agent_content = f"{base_rules}\n\nYou will focus on the current files only:\n"
        
        # Create the agent file
        output_path = f"agent_{dir_name}.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(agent_content)
        print(f"Created {output_path}")

if __name__ == "__main__":
    import yaml
    
    project_root = Path(__file__).parent
    generator = ProjectTreeGenerator(project_root)
    
    # Load focus directories from YAML config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        focus_dirs = config.get('focus_directories', [])
    
    # Generate tree for each focus directory
    found_dirs = generator.find_focus_dirs(project_root, focus_dirs)
    
    for focus_dir in found_dirs:
        print(f"\nTree for {focus_dir.name}:")
        print("=" * (len(focus_dir.name) + 9))
        tree_content = generator.generate_tree(focus_dir, ['.py', '.ts', '.tsx'])
        print('\n'.join(tree_content))
        
        # Save to separate files
        with open(f'tree_{focus_dir.name}.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(tree_content))
    
    # Generate agent files
    generate_agent_files([d.name for d in found_dirs])



