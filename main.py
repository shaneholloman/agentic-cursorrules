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
from collections import defaultdict, Counter
from smart_analyzer import SmartCodeAnalyzer

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

    def _update_config(self, focus_dirs):
        """Update config.yaml with the identified focus directories."""
        # Define the auto config path
        config_auto_path = self.config_dir / 'config_auto.yaml'
        
        # Create config
        config = {}
        config['project_title'] = self.project_dir.name
        config['tree_focus'] = focus_dirs
        
        # Add exclude dirs
        config['exclude_dirs'] = list(self.exclude_dirs)
        
        # Ensure ordered structure
        ordered_config = {}
        ordered_config['project_title'] = config.pop('project_title')
        ordered_config['tree_focus'] = config.pop('tree_focus')
        ordered_config.update(config)  # Add remaining sections
        
        # Write the updated config
        with open(config_auto_path, 'w') as f:
            yaml.dump(ordered_config, f, default_flow_style=False, sort_keys=False)
        
        # Also update standard config.yaml as a backup
        with open(self.config_path, 'w') as f:
            yaml.dump(ordered_config, f, default_flow_style=False, sort_keys=False)
        
        print(f"\n✅ Updated config_auto.yaml with {len(focus_dirs)} focus directories")
        print(f"File saved to: {config_auto_path}")
        
        return focus_dirs

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
        print(f"\n🔍 Looking for focus directories in: {directory}")
        
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
        
        # Sort by path depth (shortest first) to handle parent folders first
        normalized_focus_dirs.sort(key=lambda p: len(p.parts))
        
        # Try exact directory matching first
        for focus_path in normalized_focus_dirs:
            try:
                # Check for exact path
                target_path = (directory / focus_path).resolve()
                if target_path.exists() and target_path.is_dir():
                    print(f"✅ Found exact path: {target_path}")
                    found_dirs.append(target_path)
                    continue
                
                # Check simple name at top level
                simple_path = (directory / focus_path.name).resolve()
                if simple_path.exists() and simple_path.is_dir():
                    print(f"✅ Found directory by name: {simple_path}")
                    found_dirs.append(simple_path)
                    continue
                
                # Look one level deeper for matching directory name
                for item in directory.iterdir():
                    if item.is_dir():
                        nested_path = (item / focus_path.name).resolve()
                        if nested_path.exists() and nested_path.is_dir():
                            print(f"✅ Found nested directory: {nested_path}")
                            found_dirs.append(nested_path)
                            break
                
                # Still not found - try searching by walking the tree
                if not any(focus_path.name in str(d) for d in found_dirs):
                    print(f"🔍 Searching for '{focus_path.name}' in directory tree...")
                    # Walk no more than 3 levels deep to find matching directory names
                    for root, dirs, _ in os.walk(str(directory)):
                        depth = root[len(str(directory)):].count(os.sep)
                        if depth > 3:  # Limit depth
                            continue
                        
                        for dir_name in dirs:
                            if dir_name == focus_path.name:
                                match_path = Path(os.path.join(root, dir_name))
                                print(f"✅ Found directory by walking tree: {match_path}")
                                found_dirs.append(match_path)
                                break
                        
                        # Break after finding first match to avoid too many results
                        if any(focus_path.name in str(d) for d in found_dirs):
                            break
                
            except Exception as e:
                print(f"⚠️ Error processing {focus_path}: {str(e)}")
        
        # If we found no directories, fall back to scanning for code directories
        if not found_dirs:
            print("\n⚠️ Exact matching failed. Falling back to code directory detection...")
            # Look for directories with most code files
            code_dirs = self._find_code_directories(directory)
            if code_dirs:
                found_dirs = code_dirs
        
        print(f"\n📂 Final directories found: {len(found_dirs)}")
        for d in found_dirs:
            print(f"  - {d}")
        
        return found_dirs

    def _find_code_directories(self, directory: Path, max_dirs=5) -> List[Path]:
        """
        Find directories containing the most code files by scanning the filesystem.
        Used as a fallback when directory names aren't found.
        """
        print(f"Scanning for code files in {directory}...")
        
        # Common file extensions to look for
        code_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx', '.html', '.css', '.scss',
            '.java', '.c', '.cpp', '.h', '.cs', '.go', '.rb', '.php',
            '.vue', '.svelte', '.json', '.yaml', '.yml', '.md'
        }
        
        # Directories to exclude
        exclude_dirs = {
            'node_modules', 'dist', 'build', '.git', '__pycache__',
            'venv', 'env', '.next', 'out', 'coverage', 'tmp', 'temp'
        }
        
        # Count code files per directory
        dir_counts = defaultdict(int)
        
        try:
            # Walk through the directory tree
            for root, dirs, files in os.walk(str(directory)):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
                
                # Skip if we're too deep
                depth = root[len(str(directory)):].count(os.sep)
                if depth > 4:  # Limit depth to 4 levels
                    continue
                
                # Count code files in this directory
                code_file_count = sum(1 for f in files if any(f.endswith(ext) for ext in code_extensions))
                
                if code_file_count > 0:
                    rel_path = os.path.relpath(root, str(directory))
                    if rel_path == '.':
                        continue  # Skip root
                    
                    # Record directory and count
                    dir_counts[rel_path] += code_file_count
        
            # Get the top directories by file count
            top_dirs = sorted(dir_counts.items(), key=lambda x: -x[1])[:max_dirs]
            
            # Convert to Path objects
            result = []
            for rel_path, count in top_dirs:
                full_path = (directory / rel_path).resolve()
                if full_path.exists():
                    print(f"✅ Found code directory: {full_path} ({count} files)")
                    result.append(full_path)
            
            return result
        
        except Exception as e:
            print(f"⚠️ Error scanning for code directories: {str(e)}")
            return []

def generate_agent_files(focus_dirs: List[str], config_dir: Path, project_dir: Path, output_dir: Path):
    """
    Generates agent-specific markdown files for each focus directory.
    """
    created_files = set()
    print(f"\n📝 Generating agent files in project directory: {project_dir}")

    for dir_path in focus_dirs:
        try:
            # Ensure dir_path is a Path object
            if isinstance(dir_path, str):
                dir_path = Path(dir_path)
            
            # Make sure we have a full resolved path
            if not dir_path.is_absolute():
                dir_path = (project_dir / dir_path).resolve()
            
            # Check if the directory exists
            if not dir_path.exists() or not dir_path.is_dir():
                print(f"⚠️ Skipping non-existent directory: {dir_path}")
                continue
                
            # Get directory name and parent for agent file naming
            dir_name = dir_path.name
            
            # Calculate relative path to project dir for naming
            try:
                rel_path = dir_path.relative_to(project_dir)
                parent_path = rel_path.parent if rel_path.parent != Path('.') else None
                parent_name = parent_path.name if parent_path else None
            except ValueError:
                # Handle case where dir_path is not relative to project_dir
                rel_path = dir_path.name
                parent_name = dir_path.parent.name
            
            # Generate the agent file name based on the path structure
            if str(rel_path).count('/') > 0 or str(rel_path).count('\\') > 0:
                # Handle paths with depth
                parts = str(rel_path).replace('\\', '/').split('/')
                agent_name = f"agent_{parts[0]}_{parts[-1]}.md"
            elif parent_name and parent_name != project_dir.name and not dir_name.startswith('__'):
                agent_name = f"agent_{parent_name}_{dir_name}.md"
            else:
                agent_name = f"agent_{dir_name}.md"
            
            if agent_name in created_files:
                print(f"⚠️ Skipping duplicate agent file: {agent_name}")
                continue
                
            # Use the last part of the path for the tree file name
            tree_file = config_dir / f'tree_{dir_name}.txt'
            tree_content = ""
            if tree_file.exists():
                with open(tree_file, 'r', encoding='utf-8') as f:
                    tree_content = f.read()
            else:
                print(f"⚠️ No tree file found at {tree_file}")
            
            # Generate appropriate directory description
            if parent_name and parent_name != project_dir.name:
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
            print(f"✅ Created {output_path}")
            
            created_files.add(agent_name)
            
        except Exception as e:
            print(f"❌ Error processing directory '{dir_path}': {str(e)}")
            import traceback
            traceback.print_exc()

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
    parser.add_argument('--use-detected', action='store_true',
                        help='Use detected_config.yaml if available')
    parser.add_argument('--local-agents', action='store_true',
                        help='Store agent files in script directory instead of project directory')

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        add_arguments(parser)
        args = parser.parse_args()

        # Get the config directory (where the script is located)
        config_dir = Path(__file__).parent

        # Set project directory from argument or use parent of config dir
        project_dir = Path(args.project_path).resolve() if args.project_path else config_dir.parent.resolve()
        print(f"Using project directory: {project_dir} (absolute path)")
        
        # Determine which config file to use
        if args.auto_config:
            config_path = config_dir / 'config_auto.yaml'
            print(f"Using auto-generated config: {config_path}")
        elif args.use_detected and (config_dir / 'detected_config.yaml').exists():
            config_path = config_dir / 'detected_config.yaml' 
            print(f"Using detected config: {config_path}")
        else:
            config_path = config_dir / 'config_manual.yaml'
            print(f"Using manual config: {config_path}")

        # Verify config if requested
        if args.verify_config:
            if config_path.exists():
                print(f"\nCurrent config content at {config_path}:")
                print("-" * 40)
                with open(config_path, 'r') as f:
                    print(f.read())
                print("-" * 40)
            else:
                print(f"\n❌ No config found at {config_path}")
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
                # Use the ConfigUpdater to process the tree
                updater = ConfigUpdater(config_dir)
                success = updater.from_tree_text(tree_text, args.project_title)
                
                if not success:
                    print("❌ Failed to update config from tree text")
                    sys.exit(1)
                
                # If we're just updating config, exit
                if input("Continue with agent generation? (y/n): ").lower() != 'y':
                    sys.exit(0)
            else:
                print("❌ No tree text provided.")
                sys.exit(1)
        
        # Auto-config from filesystem
        elif args.auto_config:
            analyzer = SmartCodeAnalyzer(project_dir, config_dir)
            focus_dirs = analyzer.analyze()
            print(f"Smart structure analysis complete!")
            
            # Verify the config was updated
            if config_path.exists():
                print("\nVerifying config contents:")
                with open(config_path, 'r') as f:
                    for i, line in enumerate(f):
                        if i < 15:  # First 15 lines
                            print(f"  {line.rstrip()}")
                        else:
                            print("  ...")
                            break
            
            # If we're just updating config, exit
            if input("\nContinue with agent generation? (y/n): ").lower() != 'y':
                sys.exit(0)

        # Create default config file if it doesn't exist
        if not config_path.exists():
            # If detected_config exists and we want to use it, copy it
            if args.use_detected and (config_dir / 'detected_config.yaml').exists():
                shutil.copy2(config_dir / 'detected_config.yaml', config_path)
                print(f"Copied detected_config.yaml to {config_path}")
            else:
                # Create default config
                default_config = {
                    'project_title': args.project_title,
                    'tree_focus': ['api', 'app']
                }
                with open(config_path, 'w') as f:
                    yaml.dump(default_config, f, default_flow_style=False)
                print(f"Created default config at {config_path} with {', '.join(default_config['tree_focus'])} focus directories")

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
                
                # Create tree_files directory if it doesn't exist
                tree_files_dir = config_dir / 'tree_files'
                tree_files_dir.mkdir(exist_ok=True)
                
                # Save tree files in tree_files directory
                with open(tree_files_dir / f'tree_{focus_dir.name}.txt', 'w', encoding='utf-8') as f:
                    f.write('\n'.join(tree_content))
                
                processed_dirs.add(rel_path)
            
            # Generate agent files in project directory
            output_dir = config_dir if args.local_agents else project_dir
            generate_agent_files([str(d.relative_to(project_dir)) for d in found_dirs], config_dir, project_dir, output_dir)

            if not args.recurring:
                break
                
            time.sleep(60)  # Wait for 1 minute before next iteration
            
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)