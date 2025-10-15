#!/usr/bin/env python3
"""
Configuration Manager for Homepage Editor
Handles external configuration files, privilege elevation, and path management
"""

import os
import sys
import yaml
import json
import shutil
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ConfigFile:
    """Represents a configuration file with its properties"""
    name: str
    path: str
    required: bool = True
    backup_enabled: bool = True
    permissions: str = "644"  # Default file permissions
    owner: Optional[str] = None
    group: Optional[str] = None

class ConfigManager:
    """Manages configuration files with external path support and privilege elevation"""
    
    def __init__(self, app_dir: str = None):
        self.app_dir = Path(app_dir) if app_dir else Path(__file__).parent
        self.config_dir = self.app_dir / "config"
        self.backup_dir = self.app_dir / "backups"
        self.config_file = self.app_dir / "config_paths.json"
        
        # Define all configuration files
        self.config_files = {
            "bookmarks": ConfigFile("bookmarks.yaml", "", True),
            "settings": ConfigFile("settings.yaml", "", True),
            "services": ConfigFile("services.yaml", "", False),
            "widgets": ConfigFile("widgets.yaml", "", False),
            "docker": ConfigFile("docker.yaml", "", False),
            "kubernetes": ConfigFile("kubernetes.yaml", "", False),
            "proxmox": ConfigFile("proxmox.yaml", "", False),
        }
        
        # Load configuration paths
        self.load_config_paths()
        
        # Ensure backup directory exists
        self.backup_dir.mkdir(exist_ok=True)
    
    def load_config_paths(self):
        """Load configuration file paths from config_paths.json"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    paths = json.load(f)
                    for key, path in paths.items():
                        if key in self.config_files:
                            self.config_files[key].path = path
            else:
                # Initialize with default paths (current directory)
                self.save_config_paths()
        except Exception as e:
            logger.error(f"Error loading config paths: {e}")
            self.save_config_paths()
    
    def save_config_paths(self):
        """Save current configuration file paths"""
        try:
            paths = {key: config.path for key, config in self.config_files.items()}
            with open(self.config_file, 'w') as f:
                json.dump(paths, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving config paths: {e}")
    
    def set_config_path(self, config_name: str, path: str) -> bool:
        """Set the path for a specific configuration file"""
        if config_name not in self.config_files:
            return False
        
        # Validate path
        if not self.validate_config_path(path):
            return False
        
        self.config_files[config_name].path = path
        self.save_config_paths()
        return True
    
    def get_config_path(self, config_name: str) -> str:
        """Get the current path for a configuration file"""
        if config_name not in self.config_files:
            return ""
        
        path = self.config_files[config_name].path
        if not path:
            # Default to current directory
            return str(self.app_dir / f"{config_name}.yaml")
        
        return path
    
    def validate_config_path(self, path: str) -> bool:
        """Validate that a configuration path is accessible"""
        try:
            path_obj = Path(path)
            
            # Check if parent directory exists and is writable
            if not path_obj.parent.exists():
                return False
            
            # Check if we can write to the directory
            test_file = path_obj.parent / ".test_write"
            try:
                test_file.touch()
                test_file.unlink()
                return True
            except (PermissionError, OSError):
                return False
                
        except Exception:
            return False
    
    def check_privileges(self, path: str) -> Tuple[bool, str]:
        """Check if we have sufficient privileges to access a path"""
        try:
            path_obj = Path(path)
            
            # Check if file exists
            if path_obj.exists():
                # Check read permission
                if not os.access(path_obj, os.R_OK):
                    return False, "No read permission"
                
                # Check write permission
                if not os.access(path_obj, os.W_OK):
                    return False, "No write permission"
            else:
                # Check if parent directory is writable
                if not os.access(path_obj.parent, os.W_OK):
                    return False, "No write permission to parent directory"
            
            return True, "OK"
            
        except Exception as e:
            return False, str(e)
    
    def elevate_privileges(self, path: str) -> bool:
        """Attempt to elevate privileges for file access"""
        try:
            path_obj = Path(path)
            
            # Check if we're on a Unix-like system
            if platform.system() in ['Linux', 'Darwin']:
                # Try to change ownership to current user
                current_user = os.getenv('USER', os.getenv('USERNAME', 'unknown'))
                current_group = os.getenv('GROUP', current_user)
                
                # Use sudo to change ownership
                cmd = ['sudo', 'chown', f'{current_user}:{current_group}', str(path_obj)]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    # Set appropriate permissions
                    cmd = ['sudo', 'chmod', '644', str(path_obj)]
                    subprocess.run(cmd, capture_output=True, text=True)
                    return True
                else:
                    logger.error(f"Failed to change ownership: {result.stderr}")
                    return False
            
            return False
            
        except Exception as e:
            logger.error(f"Error elevating privileges: {e}")
            return False
    
    def read_config(self, config_name: str) -> Dict[str, Any]:
        """Read a configuration file with error handling"""
        if config_name not in self.config_files:
            return {}
        
        path = self.get_config_path(config_name)
        
        try:
            # Check privileges first
            has_access, error_msg = self.check_privileges(path)
            if not has_access:
                # Try to elevate privileges
                if not self.elevate_privileges(path):
                    logger.error(f"Cannot access {path}: {error_msg}")
                    return {}
            
            with open(path, 'r', encoding='utf-8') as f:
                if path.endswith('.yaml') or path.endswith('.yml'):
                    return yaml.safe_load(f) or {}
                elif path.endswith('.json'):
                    return json.load(f) or {}
                else:
                    # Try YAML first, then JSON
                    try:
                        f.seek(0)
                        return yaml.safe_load(f) or {}
                    except:
                        f.seek(0)
                        return json.load(f) or {}
                        
        except FileNotFoundError:
            logger.warning(f"Configuration file not found: {path}")
            return {}
        except Exception as e:
            logger.error(f"Error reading {path}: {e}")
            return {}
    
    def write_config(self, config_name: str, data: Dict[str, Any]) -> bool:
        """Write a configuration file with error handling and backup"""
        if config_name not in self.config_files:
            return False
        
        path = self.get_config_path(config_name)
        
        try:
            # Create backup if file exists
            if Path(path).exists() and self.config_files[config_name].backup_enabled:
                self.create_backup(path)
            
            # Check privileges
            has_access, error_msg = self.check_privileges(path)
            if not has_access:
                if not self.elevate_privileges(path):
                    logger.error(f"Cannot write to {path}: {error_msg}")
                    return False
            
            # Ensure parent directory exists
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            
            # Write the file
            with open(path, 'w', encoding='utf-8') as f:
                if path.endswith('.yaml') or path.endswith('.yml'):
                    yaml.dump(data, f, default_flow_style=False, sort_keys=False)
                elif path.endswith('.json'):
                    json.dump(data, f, indent=2)
                else:
                    # Default to YAML
                    yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            # Set appropriate permissions
            if platform.system() in ['Linux', 'Darwin']:
                os.chmod(path, 0o644)
            
            logger.info(f"Successfully wrote {config_name} to {path}")
            return True
            
        except Exception as e:
            logger.error(f"Error writing {path}: {e}")
            return False
    
    def create_backup(self, path: str) -> bool:
        """Create a backup of a configuration file"""
        try:
            path_obj = Path(path)
            if not path_obj.exists():
                return False
            
            # Create backup filename with timestamp
            timestamp = Path(path).stat().st_mtime
            backup_name = f"{path_obj.stem}_{int(timestamp)}.yaml"
            backup_path = self.backup_dir / backup_name
            
            # Copy the file
            shutil.copy2(path, backup_path)
            logger.info(f"Created backup: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return False
    
    def restore_backup(self, config_name: str, backup_path: str) -> bool:
        """Restore a configuration file from backup"""
        try:
            target_path = self.get_config_path(config_name)
            
            # Check if backup exists
            if not Path(backup_path).exists():
                return False
            
            # Create backup of current file
            if Path(target_path).exists():
                self.create_backup(target_path)
            
            # Restore from backup
            shutil.copy2(backup_path, target_path)
            logger.info(f"Restored {config_name} from {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring backup: {e}")
            return False
    
    def list_backups(self, config_name: str) -> List[str]:
        """List available backups for a configuration file"""
        try:
            backups = []
            for backup_file in self.backup_dir.glob(f"{config_name}_*.yaml"):
                backups.append(str(backup_file))
            return sorted(backups, reverse=True)  # Most recent first
        except Exception as e:
            logger.error(f"Error listing backups: {e}")
            return []
    
    def get_config_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all configuration files"""
        status = {}
        
        for name, config in self.config_files.items():
            path = self.get_config_path(name)
            exists = Path(path).exists()
            has_access, error_msg = self.check_privileges(path)
            
            status[name] = {
                "path": path,
                "exists": exists,
                "accessible": has_access,
                "error": error_msg if not has_access else None,
                "required": config.required,
                "backup_enabled": config.backup_enabled
            }
        
        return status
    
    def validate_all_configs(self) -> Tuple[bool, List[str]]:
        """Validate all configuration files"""
        errors = []
        all_valid = True
        
        for name, config in self.config_files.items():
            if not config.required:
                continue
                
            path = self.get_config_path(name)
            has_access, error_msg = self.check_privileges(path)
            
            if not has_access:
                errors.append(f"{name}: {error_msg}")
                all_valid = False
            elif not Path(path).exists():
                errors.append(f"{name}: File not found at {path}")
                all_valid = False
        
        return all_valid, errors

# Global instance
config_manager = ConfigManager()

# Convenience functions for backward compatibility
def get_settings():
    """Get settings configuration"""
    return config_manager.read_config("settings")

def save_settings(data):
    """Save settings configuration"""
    return config_manager.write_config("settings", data)

def get_bookmarks():
    """Get bookmarks configuration"""
    return config_manager.read_config("bookmarks")

def save_bookmarks(data):
    """Save bookmarks configuration"""
    return config_manager.write_config("bookmarks", data)

def get_services():
    """Get services configuration"""
    return config_manager.read_config("services")

def save_services(data):
    """Save services configuration"""
    return config_manager.write_config("services", data)

def get_widgets():
    """Get widgets configuration"""
    return config_manager.read_config("widgets")

def save_widgets(data):
    """Save widgets configuration"""
    return config_manager.write_config("widgets", data)