from pathlib import Path
from typing import List, Set
import yaml
from gitignore_parser import parse_gitignore
import time
import argparse

class ProjectTreeGenerator:
    def __init__(self, project_root: Path):
        """
        Initializes the generator with gitignore-based exclusions and the project root.
        """
        self.project_root = project_root
        
        # Load config from YAML
        config_path = project_root / '.agentic-cursorrules' / 'config.yaml'
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        # Set file extensions from config
        self.INCLUDE_EXTENSIONS: Set[str] = set(config.get('include_extensions', []))
        self.IMPORTANT_DIRS = set(config.get('important_dirs', []))
        self.EXCLUDE_DIRS = set(config.get('exclude_dirs', []))
        
        # Initialize gitignore matcher
        gitignore_path = project_root / '.gitignore'
        if gitignore_path.exists():
            self.matches = parse_gitignore(gitignore_path)
        else:
            # Create temporary gitignore with exclude_dirs from config
            temp_gitignore = project_root / '.temp_gitignore'
            with open(temp_gitignore, 'w') as f:
                f.write('\n'.join(f'{dir}/' for dir in self.EXCLUDE_DIRS))
            self.matches = parse_gitignore(temp_gitignore)
            temp_gitignore.unlink()

    def generate_tree(self, directory: Path, file_types: List[str] = None, max_depth: int = 3) -> List[str]:
        """Generates a visual tree representation of the directory structure."""
        tree_lines = []

        def _generate_tree(dir_path: Path, prefix: str = "", depth: int = 0):
            if depth > max_depth:
                return

            items = sorted(list(dir_path.iterdir()), key=lambda x: (not x.is_file(), x.name))
            for i, item in enumerate(items):
                # Skip if in exclude_dirs or matches gitignore
                if item.name in self.EXCLUDE_DIRS or self.matches(str(item)):
                    continue

                is_last = i == len(items) - 1
                display_path = item.name

                if item.is_dir():
                    # Always include important directories
                    if item.name in self.IMPORTANT_DIRS:
                        tree_lines.append(f"{prefix}{'└── ' if is_last else '├── '}{display_path}/")
                        _generate_tree(item, prefix + ('    ' if is_last else '│   '), depth + 1)
                    else:
                        tree_lines.append(f"{prefix}{'└── ' if is_last else '├── '}{display_path}/")
                        _generate_tree(item, prefix + ('    ' if is_last else '│   '), depth + 1)
                elif item.is_file():
                    # Use configured extensions if no specific file_types provided
                    extensions_to_check = file_types if file_types else self.INCLUDE_EXTENSIONS
                    if any(item.name.endswith(ext) for ext in extensions_to_check):
                        tree_lines.append(f"{prefix}{'└── ' if is_last else '├── '}{display_path}")

        _generate_tree(directory)
        return tree_lines

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

def generate_agent_files(focus_dirs: List[str], agentic_dir: Path):
    """
    Generates agent-specific markdown files for each focus directory.
    """
    root_dir = agentic_dir.parent
    root_rules = root_dir / '.cursorrules'
    
    if not root_rules.exists():
        print("\nWarning: No .cursorrules file found!")
        print("Recommendation: Create a .cursorrules file in your project root with custom instructions.")
        print("For now, only project structure will be included in the agent files.\n")
    
    created_files = set()

    for dir_name in focus_dirs:
        if dir_name in created_files:
            continue
            
        tree_file = agentic_dir / f'tree_{dir_name}.txt'
        tree_content = ""
        if tree_file.exists():
            with open(tree_file, 'r', encoding='utf-8') as f:
                tree_content = f.read()
        
        # Only include the tree content
        agent_content = f"Project structure for {dir_name}:\n\n{tree_content}"
        
        output_path = root_dir / f'agent_{dir_name}.md'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(agent_content)
        print(f"Created {output_path}")
        
        created_files.add(dir_name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--recurring', action='store_true', help='Run the script every minute')
    args = parser.parse_args()
    
    # Get the .agentic-cursorrules directory path
    agentic_dir = Path(__file__).parent
    
    # Create default config.yaml in the .agentic-cursorrules directory
    config_path = agentic_dir / 'config.yaml'
    if not config_path.exists():
        default_config = {
            'tree_focus': ['backend', 'frontend']
        }
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f)
    
    while True:
        # Use parent directory of .agentic-cursorrules as the project root
        project_root = agentic_dir.parent
        generator = ProjectTreeGenerator(project_root)
        
        # Load focus directories from YAML config in .agentic-cursorrules directory
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            focus_dirs = config.get('tree_focus', [])
            include_extensions = config.get('include_extensions', [])
        
        # Generate tree for each focus directory
        found_dirs = generator.find_focus_dirs(project_root, focus_dirs)
        
        for focus_dir in found_dirs:
            print(f"\nTree for {focus_dir.name}:")
            print("=" * (len(focus_dir.name) + 9))
            tree_content = generator.generate_tree(focus_dir, include_extensions)
            print('\n'.join(tree_content))
            
            # Save tree files in .agentic-cursorrules directory
            with open(agentic_dir / f'tree_{focus_dir.name}.txt', 'w', encoding='utf-8') as f:
                f.write('\n'.join(tree_content))
        
        # Generate agent files in .agentic-cursorrules directory
        generate_agent_files([d.name for d in found_dirs], agentic_dir)

        if not args.recurring:
            break
            
        time.sleep(60)
