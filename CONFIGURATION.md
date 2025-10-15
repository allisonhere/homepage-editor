# Configuration Management Guide

## Overview

The Homepage Editor now supports external configuration files and automatic privilege elevation. This allows you to:

- Store configuration files in any location (e.g., `/etc/homepage/`, `~/Documents/`, etc.)
- Automatically handle file permissions and privilege elevation
- Create and restore backups of your configurations
- Validate configuration integrity

## Configuration Files

The application manages the following configuration files:

### Core Configuration Files (Required)
- **`bookmarks.yaml`** - Main bookmark data and categories
- **`settings.yaml`** - Homepage layout and appearance settings
- **`widgets.yaml`** - Widget configuration

### Service Configuration Files (Optional)
- **`services.yaml`** - Service definitions with monitoring widgets
- **`docker.yaml`** - Docker container configuration
- **`kubernetes.yaml`** - Kubernetes configuration
- **`proxmox.yaml`** - Proxmox configuration

## Setting Up External Configuration Paths

### Method 1: Using the GUI
1. Launch the Homepage Editor
2. Go to **Tools → Configuration Paths...**
3. Set the path for each configuration file
4. Click **Save**

### Method 2: Using the Command Line
```bash
# Set configuration paths programmatically
python3 -c "
from config_manager import config_manager
config_manager.set_config_path('bookmarks', '/etc/homepage/bookmarks.yaml')
config_manager.set_config_path('settings', '/etc/homepage/settings.yaml')
config_manager.save_config_paths()
"
```

### Method 3: Manual Configuration
Edit `config_paths.json` in the application directory:
```json
{
  "bookmarks": "/etc/homepage/bookmarks.yaml",
  "settings": "/etc/homepage/settings.yaml",
  "services": "/etc/homepage/services.yaml",
  "widgets": "/etc/homepage/widgets.yaml"
}
```

## Privilege Elevation

The application automatically handles privilege elevation when needed:

### Automatic Elevation
- The application detects when files require elevated privileges
- Automatically attempts to use `sudo` to change file ownership
- Sets appropriate file permissions (644)

### Manual Elevation
If automatic elevation fails, you can run the application with elevated privileges:

```bash
# Run with sudo
sudo python3 homepage_gui.py

# Or use the startup script
sudo python3 startup.py
```

### Configuration for Elevated Access
For system-wide configuration files, you may want to:

1. Create a dedicated directory:
   ```bash
   sudo mkdir -p /etc/homepage
   sudo chown $USER:$USER /etc/homepage
   ```

2. Set configuration paths to use this directory
3. The application will handle permissions automatically

## Backup and Restore

### Automatic Backups
- Backups are created automatically before any write operation
- Stored in the `backups/` directory
- Timestamped for easy identification

### Manual Backup Management
1. Go to **File → Backup & Restore...**
2. View available backups
3. Create new backups or restore from existing ones

### Command Line Backup
```bash
# Create backup of current configurations
python3 -c "
from config_manager import config_manager
for config_name in config_manager.config_files:
    config_manager.create_backup(config_manager.get_config_path(config_name))
"
```

## Configuration Validation

### GUI Validation
1. Go to **Tools → Validate Configurations**
2. View validation results and error messages

### Command Line Validation
```bash
python3 -c "
from config_manager import config_manager
is_valid, errors = config_manager.validate_all_configs()
if is_valid:
    print('All configurations are valid!')
else:
    for error in errors:
        print(f'Error: {error}')
"
```

## Troubleshooting

### Permission Denied Errors
1. Check if the directory exists and is writable
2. Try running with elevated privileges
3. Use the **Tools → Test All Paths** to diagnose issues

### Configuration Not Found
1. Verify the path is correct
2. Check if the file exists
3. Ensure the parent directory is accessible

### Backup/Restore Issues
1. Check backup directory permissions
2. Ensure source files are readable
3. Verify target paths are writable

## Security Considerations

### File Permissions
- Configuration files are set to 644 (readable by all, writable by owner)
- Backup files inherit similar permissions
- Sensitive data (passwords, API keys) should be in protected directories

### Privilege Elevation
- Only attempts elevation when necessary
- Uses `sudo` only for file operations
- Does not run the entire application as root

### Backup Security
- Backups contain the same data as original files
- Store backups in secure locations
- Consider encrypting sensitive backup files

## Advanced Configuration

### Custom Configuration Directory
```bash
# Set a custom configuration directory
export HOMEPAGE_CONFIG_DIR="/custom/path"
python3 homepage_gui.py
```

### Environment Variables
- `HOMEPAGE_CONFIG_DIR` - Override default configuration directory
- `HOMEPAGE_BACKUP_DIR` - Override backup directory
- `HOMEPAGE_LOG_LEVEL` - Set logging level (DEBUG, INFO, WARNING, ERROR)

### Logging
Configuration operations are logged to help with troubleshooting:
```bash
# View logs
tail -f logs/homepage.log
```

## Migration from Old System

If you're upgrading from the old system:

1. **Backup existing configurations**:
   ```bash
   cp *.yaml backup/
   ```

2. **Set new configuration paths**:
   - Use the GUI to set paths to your existing files
   - Or manually edit `config_paths.json`

3. **Test the new system**:
   - Use **Tools → Validate Configurations**
   - Test all operations to ensure everything works

4. **Clean up old files** (optional):
   - Remove old configuration files once you're satisfied
   - Keep backups for safety

## Support

For issues or questions:
1. Check the logs in `logs/homepage.log`
2. Use the built-in validation tools
3. Test with default configuration paths first
4. Report issues with detailed error messages