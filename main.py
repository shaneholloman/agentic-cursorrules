from pathlib import Path
from typing import List, Set
import yaml
from gitignore_parser import parse_gitignore
import time
import argparse
import sys
import shutil
import os
import re
from collections import defaultdict

class ConfigUpdater:
    """Handles config.yaml generation and updates."""
    
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.config_path = config_dir / 'config.yaml'
        
        # Default configuration sections
        self.defaults = {
            'important_dirs': [
                'components', 'pages', 'app', 'src', 'lib', 'utils', 'hooks', 
                'styles', 'public', 'assets', 'layouts', 'services', 'context', 'types'
            ],
            'exclude_dirs': [
                'node_modules', 'dist', 'build', '.next', 'out', '__pycache__', 
                'venv', 'env', '.git', 'coverage', 'tmp', 'temp'
            ],
            'include_extensions': [
                '.py', '.ts', '.tsx', '.js', '.jsx', '.json', '.css', '.scss', 
                '.html', '.md', '.vue', '.svelte'
            ]
        }
    
    def from_tree_text(self, tree_text, project_name="cursorrules-agentic"):
        """Generate config from tree text and save it."""
        print("\nUpdating config.yaml from tree text...")
        
        # Parse directories from tree text
        directories = self._parse_directories(tree_text)
        print(f"Found {len(directories)} directories in tree text")
        
        # Identify focus directories and exclude directories
        focus_dirs = self._identify_focus_dirs(directories)
        exclude_dirs = self._identify_exclude_dirs(directories)
        
        # Create or update config
        config = self._create_config(project_name, focus_dirs, exclude_dirs)
        
        # Save and verify
        return self._save_config(config)
    
    def _parse_directories(self, tree_text):
        """Extract directories from tree text."""
        directories = set()
        dir_pattern = re.compile(r'[│├└─\s]*([^/\n]+)/')
        
        for line in tree_text.split('\n'):
            if '/' in line:  # Directory lines end with /
                match = dir_pattern.search(line)
                if match:
                    dir_name = match.group(1).strip()
                    if dir_name and not dir_name.startswith('.'):
                        directories.add(dir_name)
        
        return directories
    
    def _identify_focus_dirs(self, directories):
        """Identify which directories should be in tree_focus."""
        focus_dirs = []
        
        # First add important directories
        important = set(self.defaults['important_dirs'])
        for dir_name in directories:
            if dir_name in important:
                focus_dirs.append(dir_name)
        
        # Then add common top-level directories
        common_top = ['api', 'app', 'src', 'backend', 'frontend', 'server', 'client']
        for dir_name in common_top:
            if dir_name in directories and dir_name not in focus_dirs:
                focus_dirs.append(dir_name)
        
        # If still empty, add remaining non-excluded directories
        if not focus_dirs:
            exclude_set = set(self.defaults['exclude_dirs'])
            focus_dirs = [d for d in directories if d not in exclude_set]
        
        return sorted(focus_dirs)
    
    def _identify_exclude_dirs(self, directories):
        """Identify which directories should be excluded."""
        exclude_dirs = []
        standard_excludes = set(self.defaults['exclude_dirs'])
        
        for dir_name in directories:
            if dir_name.lower() in [d.lower() for d in standard_excludes]:
                exclude_dirs.append(dir_name)
            # Also add binary/media directories
            elif dir_name.lower() in ['fonts', 'images', 'img', 'media', 'static']:
                exclude_dirs.append(dir_name)
        
        return sorted(exclude_dirs)
    
    def _create_config(self, project_name, focus_dirs, exclude_dirs):
        """Create properly structured config dictionary."""
        # Start with existing config if available
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f) or {}
        except FileNotFoundError:
            config = {}
        
        # Create ordered config with proper structure
        ordered_config = {}
        
        # Project title always first
        ordered_config['project_title'] = project_name
        
        # Tree focus always second
        ordered_config['tree_focus'] = focus_dirs
        
        # Add exclude dirs (with existing ones if present)
        if 'exclude_dirs' in config:
            exclude_set = set(config['exclude_dirs']).union(exclude_dirs)
            ordered_config['exclude_dirs'] = sorted(exclude_set)
        else:
            ordered_config['exclude_dirs'] = exclude_dirs
        
        # Add remaining sections from defaults if not present
        for section, values in self.defaults.items():
            if section != 'exclude_dirs' and section not in ordered_config:
                ordered_config[section] = config.get(section, values)
        
        return ordered_config
    
    def _save_config(self, config):
        """Save config to file and verify it was written."""
        try:
            # Save with consistent formatting
            with open(self.config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            
            # Verify file was created
            if os.path.exists(self.config_path):
                file_size = os.path.getsize(self.config_path)
                print(f"✅ Config successfully written to {self.config_path} ({file_size} bytes)")
                print(f"  - Added {len(config['tree_focus'])} focus directories")
                print(f"  - Added {len(config['exclude_dirs'])} excluded directories")
                return True
            else:
                print(f"❌ Failed to create config file at {self.config_path}")
                return False
        except Exception as e:
            print(f"❌ Error saving config: {str(e)}")
            return False

class ProjectTreeGenerator:
    def __init__(self, project_root: Path, config_dir: Path):
        """
        Initializes the generator with gitignore-based exclusions and the project root.
        """
        self.project_root = project_root
        self.config_dir = config_dir
        
        # Load config from YAML in the config directory
        config_path = config_dir / 'config.yaml'
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

    def generate_tree(self, directory: Path, file_types: List[str] = None, max_depth: int = 3, skip_dirs: Set[str] = None, config_paths: Set[str] = None) -> List[str]:
        """
        Generates a visual tree representation of the directory structure.
        
        Args:
            directory: Directory to generate tree for
            file_types: List of file extensions to include
            max_depth: Maximum depth to traverse
            skip_dirs: Set of directory paths to skip (already processed in parent trees)
            config_paths: Set of all paths from config.yaml for exclusion checking
        """
        tree_lines = []
        skip_dirs = skip_dirs or set()
        config_paths = config_paths or set()

        def _generate_tree(dir_path: Path, prefix: str = "", depth: int = 0):
            if depth > max_depth:
                return

            items = sorted(list(dir_path.iterdir()), key=lambda x: (not x.is_file(), x.name))
            for i, item in enumerate(items):
                rel_path = str(item.relative_to(self.project_root))
                
                if (item.name in self.EXCLUDE_DIRS or 
                    self.matches(str(item)) or 
                    rel_path in skip_dirs or
                    (item.is_dir() and any(cp.startswith(rel_path) for cp in config_paths))):
                    print(f"Skipping {rel_path}")  # Debug print
                    continue

                is_last = i == len(items) - 1
                display_path = item.name

                if item.is_dir():
                    tree_lines.append(f"{prefix}{'└── ' if is_last else '├── '}{display_path}/")
                    _generate_tree(item, prefix + ('    ' if is_last else '│   '), depth + 1)
                elif item.is_file():
                    extensions_to_check = file_types if file_types else self.INCLUDE_EXTENSIONS
                    if any(item.name.endswith(ext) for ext in extensions_to_check):
                        tree_lines.append(f"{prefix}{'└── ' if is_last else '├── '}{display_path}")

            return tree_lines

        return _generate_tree(directory)

    def find_focus_dirs(self, directory: Path, focus_dirs: List[str]) -> List[Path]:
        """
        Finds directories matching the focus names, handling nested paths and special cases.
        """
        found_dirs = []
        print("\nDebug - Input focus_dirs:", focus_dirs)
        
        # First, normalize all focus dirs and preserve special paths
        normalized_focus_dirs = []
        for fd in focus_dirs:
            # Preserve paths with double underscores
            if '__' in fd:
                normalized_focus_dirs.append(Path(fd))
            # Convert single underscores to paths
            elif '_' in fd and '/' not in fd:
                normalized_focus_dirs.append(Path(fd.replace('_', '/')))
            else:
                normalized_focus_dirs.append(Path(fd))
        
        print("Debug - Normalized dirs:", normalized_focus_dirs)
        
        # Sort by path depth (shortest first) to handle parent folders first
        normalized_focus_dirs.sort(key=lambda p: len(p.parts))
        print("Debug - Sorted dirs:", normalized_focus_dirs)
        
        for focus_path in normalized_focus_dirs:
            print(f"\nDebug - Processing: {focus_path}")
            
            # New skip condition: only skip if the exact path is already found
            if str(focus_path) in [str(found.relative_to(directory)) for found in found_dirs]:
                print(f"Debug - Skipping {focus_path} as it's already processed")
                continue
            
            # Handle both direct paths and nested paths
            target_path = directory / focus_path
            print(f"Debug - Looking for path: {target_path}")
            if target_path.exists() and target_path.is_dir():
                print(f"Debug - Found directory: {target_path}")
                found_dirs.append(target_path)
                continue
            
            # If not found directly, search one level deeper
            for item in directory.iterdir():
                if item.is_dir():
                    nested_path = item / focus_path.name
                    if nested_path.exists() and nested_path.is_dir():
                        print(f"Debug - Found nested directory: {nested_path}")
                        found_dirs.append(nested_path)
                        break
        
        print("\nDebug - Final found_dirs:", found_dirs)
        return found_dirs

def generate_agent_files(focus_dirs: List[str], config_dir: Path, project_dir: Path):
    """
    Generates agent-specific markdown files for each focus directory.
    """
    created_files = set()

    for dir_path in focus_dirs:
        try:
            # Convert string to Path if it's not already
            if isinstance(dir_path, str):
                dir_path = Path(dir_path)
            
            # Handle both Path objects and strings safely
            dir_name = dir_path.name if isinstance(dir_path, Path) else dir_path
            parent_path = dir_path.parent if isinstance(dir_path, Path) else Path(dir_path).parent
            parent_name = parent_path.name if parent_path != project_dir else None
            
            # Generate the agent file name based on the path structure
            if str(dir_path).count('/') > 0:
                parts = str(dir_path).split('/')
                agent_name = f"agent_{parts[0]}_{parts[-1]}.md"
            elif parent_name and not dir_name.startswith('__'):
                agent_name = f"agent_{parent_name}_{dir_name}.md"
            else:
                agent_name = f"agent_{dir_name}.md"
            
            if agent_name in created_files:
                continue
                
            # Use the last part of the path for the tree file name
            tree_file = config_dir / f'tree_{dir_path.name}.txt'
            tree_content = ""
            if tree_file.exists():
                with open(tree_file, 'r', encoding='utf-8') as f:
                    tree_content = f.read()
            
            # Generate appropriate directory description
            if '/' in str(dir_path):
                dir_description = f"the {dir_path.name} directory within {dir_path.parent.name}"
            elif parent_name:
                dir_description = f"the {dir_name} directory within {parent_name}"
            else:
                dir_description = f"the {dir_name} portion"
            
            agent_content = f"""You are an agent that specializes in {dir_description} of this project. Your expertise and responses should focus specifically on the code and files within this directory structure:

{tree_content}

When providing assistance, only reference and modify files within this directory structure. If you need to work with files outside this structure, list the required files and ask the user for permission first."""
            
            # Save to project directory
            output_path = project_dir / agent_name
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(agent_content)
            print(f"Created {output_path}")
            
            created_files.add(agent_name)
            
        except Exception as e:
            print(f"Error processing directory '{dir_path}': {str(e)}")
            print("Please ensure your config.yaml uses one of these formats:")
            print("  - Simple directory: 'api'")
            print("  - Nested directory: 'api/tests'")
            print("  - Special directory: '__tests__'")
            continue

def add_arguments(parser):
    """Add command-line arguments to the parser."""
    parser.add_argument('--recurring', action='store_true', 
                        help='Run the script every minute')
    parser.add_argument('--project-path', type=str, 
                        help='Path to the target project directory')
    parser.add_argument('--tree-input', action='store_true',
                        help='Provide a tree structure to generate config')
    parser.add_argument('--auto-config', action='store_true',
                        help='Automatically generate config from filesystem')
    parser.add_argument('--verify-config', action='store_true',
                        help='Print the current config.yaml content')
    parser.add_argument('--project-title', type=str, default="cursorrules-agentic",
                        help='Project title for generated config')

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        add_arguments(parser)
        args = parser.parse_args()

        # Get the config directory (where the script is located)
        config_dir = Path(__file__).parent

        # Set project directory from argument or use parent of config dir
        project_dir = Path(args.project_path) if args.project_path else config_dir.parent
        
        # Verify config if requested
        if args.verify_config:
            config_path = config_dir / 'config.yaml'
            if config_path.exists():
                print(f"\nCurrent config.yaml content at {config_path}:")
                print("-" * 40)
                with open(config_path, 'r') as f:
                    print(f.read())
                print("-" * 40)
            else:
                print(f"\n❌ No config.yaml found at {config_path}")
            sys.exit(0)
        
        # If tree input mode is enabled, handle that first
        if args.tree_input:
            print("Please paste your file tree below (Ctrl+D or Ctrl+Z+Enter when done):")
            tree_text = ""
            try:
                while True:
                    line = input()
                    tree_text += line + "\n"
            except (EOFError, KeyboardInterrupt):
                pass
            
            if tree_text.strip():
                # Use the new ConfigUpdater to process the tree
                updater = ConfigUpdater(config_dir)
                success = updater.from_tree_text(tree_text, args.project_title)
                
                if not success:
                    print("❌ Failed to update config.yaml from tree text")
                    sys.exit(1)
                
                # If we're just updating config, exit
                if input("Continue with agent generation? (y/n): ").lower() != 'y':
                    sys.exit(0)
            else:
                print("❌ No tree text provided.")
                sys.exit(1)
        
        # Auto-config from filesystem
        elif args.auto_config:
            print("\nAutomatic config generation from filesystem is not implemented yet.")
            print("Please use --tree-input to provide a tree structure.")
            sys.exit(1)

        # Ensure project directory exists
        if not project_dir.exists():
            print(f"Error: Project directory {project_dir} does not exist")
            sys.exit(1)

        # Copy .cursorrules to project directory if it doesn't exist
        cursorrules_example = config_dir / '.cursorrules.example'
        project_cursorrules = project_dir / '.cursorrules'
        if not project_cursorrules.exists() and cursorrules_example.exists():
            shutil.copy2(cursorrules_example, project_cursorrules)
            print(f"Copied .cursorrules to {project_cursorrules}")
        
        while True:  # Add while loop for recurring execution
            # Create default config.yaml in the config directory if it doesn't exist
            config_path = config_dir / 'config.yaml'
            if not config_path.exists():
                default_config = {
                    'project_title': args.project_title,
                    'tree_focus': ['api', 'app']
                }
                with open(config_path, 'w') as f:
                    yaml.dump(default_config, f, default_flow_style=False)
                print(f"Created default config.yaml with {', '.join(default_config['tree_focus'])} focus directories")
            
            # Load config with error handling
            try:
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    if not isinstance(config, dict) or 'tree_focus' not in config:
                        raise ValueError("Invalid config format: 'tree_focus' list is required")
                    focus_dirs = config.get('tree_focus', [])
                    if not isinstance(focus_dirs, list):
                        raise ValueError("'tree_focus' must be a list of directories")
            except Exception as e:
                print(f"Error loading config.yaml: {str(e)}")
                print("Using default configuration...")
                focus_dirs = ['api', 'app']
            
            generator = ProjectTreeGenerator(project_dir, config_dir)
            
            # Generate tree for each focus directory
            found_dirs = generator.find_focus_dirs(project_dir, focus_dirs)
            
            # Keep track of processed directories
            processed_dirs = set()
            
            # Create a set of all configured paths for exclusion checking
            config_paths = {str(Path(fd)) for fd in focus_dirs}
            
            for focus_dir in found_dirs:
                # Calculate relative path from project root
                rel_path = focus_dir.relative_to(project_dir)
                
                # Skip if this directory is already included in a parent tree
                if any(str(rel_path).startswith(str(pd)) for pd in processed_dirs 
                       if not any(part.startswith('__') for part in rel_path.parts)):
                    continue
                
                print(f"\nTree for {focus_dir.name}:")
                print("=" * (len(focus_dir.name) + 9))
                
                # Generate skip_dirs for subdirectories that will be processed separately
                skip_dirs = {str(d.relative_to(project_dir)) for d in found_dirs 
                            if str(d.relative_to(project_dir)).startswith(str(rel_path)) 
                            and d != focus_dir 
                            and any(part.startswith('__') for part in d.relative_to(project_dir).parts)}
                
                # Pass the config_paths to generate_tree
                tree_content = generator.generate_tree(
                    focus_dir, 
                    skip_dirs=skip_dirs,
                    config_paths=config_paths
                )
                print('\n'.join(tree_content))
                
                # Save tree files in config directory
                with open(config_dir / f'tree_{focus_dir.name}.txt', 'w', encoding='utf-8') as f:
                    f.write('\n'.join(tree_content))
                
                processed_dirs.add(rel_path)
            
            # Generate agent files in project directory
            generate_agent_files([str(d.relative_to(project_dir)) for d in found_dirs], config_dir, project_dir)

            if not args.recurring:
                break
                
            time.sleep(60)  # Wait for 1 minute before next iteration
            
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)