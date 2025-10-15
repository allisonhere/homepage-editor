# Homepage Editor

A comprehensive GUI application for managing your [Homepage](https://gethomepage.dev/) bookmarks, categories, and configuration with advanced icon management capabilities.

## 🚀 Features

### 📚 **Bookmark Management**
- Add, edit, and delete bookmarks with validation
- Support for custom abbreviations and icons
- YAML validation and error checking
- Data integrity checks and error reporting

### 📁 **Category Management**
- Create and delete bookmark categories
- Organize bookmarks within categories
- Category selection and navigation
- Automatic category synchronization with Homepage

### 🎨 **Advanced Icon Management**
- **Smart Icon Downloader** - Download icons from dashboard-icons repository
- **Icon Search** - Search and preview icons before selection
- **Automatic Icon Sync** - Sync icons used in your bookmarks
- **Icon Manager CLI** - Command-line tool for advanced icon management
- **Common Icons** - Pre-download popular service icons

### ⚙️ **Configuration Management**
- Centralized configuration path management
- Support for custom Homepage installation directories
- Automatic path validation and error checking
- Configuration backup and restore

### 🔧 **Developer Features**
- Comprehensive YAML validation
- Error logging and debugging tools
- Modular architecture for easy extension
- Command-line interface for automation

## 📦 Installation

### Quick Setup (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/allisonhere/homepage-editor.git
   cd homepage-editor
   ```

2. **Run the automated setup:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Launch the application:**
   ```bash
   python3 simple_homepage_gui.py
   ```

### Manual Installation

1. **Install Python dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Set up icons (optional but recommended):**
   ```bash
   python3 setup_icons.py
   ```

3. **Run the application:**
   ```bash
   python3 simple_homepage_gui.py
   ```

## 🎯 Usage

### Basic Usage

1. **Configure Paths**: Set your Homepage configuration directory
2. **Manage Categories**: Create and organize your bookmark categories
3. **Add Bookmarks**: Add bookmarks with custom icons and abbreviations
4. **Select Icons**: Use the built-in icon search to find and download icons
5. **Save Changes**: All changes are automatically saved to your Homepage config

### Icon Management

#### GUI Icon Search
- Click the icon search button when adding/editing bookmarks
- Search for icons by name or service
- Preview icons before selection
- Download missing icons automatically

#### Command Line Icon Management
```bash
# Download all common icons
python3 icon_manager.py --download-common

# Search for specific icons
python3 icon_manager.py --search "github"

# Sync icons used in your bookmarks
python3 icon_manager.py --sync-used

# Download specific icons
python3 icon_manager.py --download github docker nginx
```

### Configuration Management

The application supports multiple configuration modes:

- **Default Mode**: Uses `~/.config/homepage/` directory
- **Custom Mode**: Specify custom Homepage installation directory
- **Portable Mode**: Use relative paths for portable installations

## 📁 Project Structure

```
homepage-editor/
├── simple_homepage_gui.py    # Main GUI application
├── config_manager.py         # Configuration management
├── config_ui.py             # Configuration UI
├── icon_search.py           # Icon search and selection
├── icon_manager.py          # Icon management system
├── setup_icons.py           # Icon setup script
├── setup.sh                 # Automated setup script
├── requirements.txt         # Python dependencies
├── ICON_MANAGEMENT.md       # Icon management documentation
└── images/icons/            # Local icon storage
```

## 🔧 Configuration

### Configuration Files

- `config_paths.json` - Configuration file paths
- `bookmarks.yaml` - Your Homepage bookmarks
- `settings.yaml` - Homepage layout settings
- `services.yaml` - Service configurations

### Icon Configuration

Icons are automatically managed and stored in your Homepage's `images/icons/` directory. The application handles:

- Downloading icons from the dashboard-icons repository
- Copying icons to the correct location
- Updating bookmark references
- Cleaning up unused icons

## 🐛 Troubleshooting

### Common Issues

1. **"Invalid path" errors**: Check that your Homepage directory exists and is writable
2. **Icon not displaying**: Ensure the icon was copied to the correct directory
3. **YAML errors**: Use the built-in validation to check for syntax errors
4. **Permission errors**: Ensure you have write access to your Homepage config directory

### Debug Mode

Run with debug logging:
```bash
python3 simple_homepage_gui.py --debug
```

### Reset Configuration

To reset all configuration:
```bash
rm config_paths.json
python3 simple_homepage_gui.py
```

## 📚 Documentation

- [Icon Management Guide](ICON_MANAGEMENT.md) - Complete guide to icon management
- [Configuration Reference](docs/configuration.md) - Detailed configuration options
- [API Reference](docs/api.md) - Developer API documentation

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Homepage](https://gethomepage.dev/) - The amazing dashboard this tool manages
- [Dashboard Icons](https://github.com/walkxcode/dashboard-icons) - Icon repository
- [Tkinter](https://docs.python.org/3/library/tkinter.html) - GUI framework

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/allisonhere/homepage-editor/issues)
- **Discussions**: [GitHub Discussions](https://github.com/allisonhere/homepage-editor/discussions)
- **Documentation**: [Wiki](https://github.com/allisonhere/homepage-editor/wiki)

---

**Version**: v1.2.0  
**Last Updated**: October 2024  
**Python**: 3.7+