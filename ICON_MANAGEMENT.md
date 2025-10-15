# 🎨 Icon Management System

The Homepage Editor now includes a comprehensive icon management system that makes it easy to download, organize, and use SVG icons from the [dashboard-icons](https://github.com/walkxcode/dashboard-icons) repository.

## 🚀 Quick Setup

### Option 1: Automated Setup
```bash
./setup.sh
```

### Option 2: Manual Setup
```bash
python3 setup_icons.py
```

## 📖 Usage

### Command Line Interface

#### Basic Commands
```bash
# Verify icon setup
python3 icon_manager.py --verify

# Search for icons
python3 icon_manager.py --search docker
python3 icon_manager.py --search github

# Download specific icons
python3 icon_manager.py --download github docker nginx

# Sync icons used in bookmarks
python3 icon_manager.py --sync

# Download common icons (100+ popular icons)
python3 icon_manager.py --common

# List local icons
python3 icon_manager.py --list-local

# List icons used in bookmarks
python3 icon_manager.py --list-used

# Clean up unused icons
python3 icon_manager.py --cleanup
```

#### Advanced Commands
```bash
# Download the entire dashboard-icons repository
python3 icon_manager.py --download-repo

# Search with custom limit
python3 -c "from icon_manager import IconManager; print(IconManager().search_icons('docker', 50))"
```

### GUI Integration

The icon management system is fully integrated with the Homepage Editor GUI:

1. **Icon Search Window**: When you click "Search" in the icon field, it now includes download functionality
2. **Auto-Download**: Icons are automatically downloaded when selected
3. **Progress Feedback**: Shows download progress and status

## 🔧 Features

### Smart Icon Management
- **Automatic Detection**: Finds icons used in your bookmarks
- **Missing Icon Detection**: Identifies and downloads missing icons
- **Metadata Search**: Search by icon name or aliases
- **Caching**: Efficient caching for better performance

### Icon Repository
- **2,000+ Icons**: Access to the complete dashboard-icons collection
- **Metadata Support**: Rich metadata including aliases and categories
- **SVG Format**: High-quality vector icons
- **Auto-Update**: Easy updates when new icons are added

### Organization
- **Local Storage**: Icons stored in `images/icons/`
- **Path Management**: Automatic path configuration
- **Cleanup Tools**: Remove unused icons to save space

## 📁 File Structure

```
homepage-editor/
├── icon_manager.py          # Main icon management class
├── setup_icons.py           # Easy setup script
├── setup.sh                 # Complete setup script
├── dashboard-icons-main/    # Icon repository (downloaded)
│   ├── svg/                 # SVG icon files
│   ├── metadata.json        # Icon metadata
│   └── ...
├── images/
│   └── icons/               # Local icon storage
│       ├── github.svg
│       ├── docker.svg
│       └── ...
└── bookmarks.yaml           # Your bookmarks (with icon references)
```

## 🎯 Common Use Cases

### 1. First Time Setup
```bash
# Complete setup
./setup.sh

# Or step by step
python3 setup_icons.py
python3 icon_manager.py --verify
```

### 2. Adding New Icons
```bash
# Search for icons
python3 icon_manager.py --search "your search term"

# Download specific icons
python3 icon_manager.py --download icon1 icon2 icon3
```

### 3. Syncing with Bookmarks
```bash
# Download all icons used in your bookmarks
python3 icon_manager.py --sync
```

### 4. Maintenance
```bash
# Check what's missing
python3 icon_manager.py --verify

# Clean up unused icons
python3 icon_manager.py --cleanup
```

## 🔍 Icon Search

The search functionality supports:
- **Exact matches**: `docker` finds `docker`
- **Partial matches**: `doc` finds `docker`, `docker-compose`, etc.
- **Alias search**: `container` finds `docker` (if it has that alias)
- **Case insensitive**: `Docker` and `docker` work the same

## 📊 Icon Statistics

```bash
# Check your icon usage
python3 icon_manager.py --list-used | wc -l  # Icons used in bookmarks
python3 icon_manager.py --list-local | wc -l # Icons downloaded locally
```

## 🛠️ Troubleshooting

### Common Issues

1. **"Dashboard icons not available"**
   ```bash
   python3 icon_manager.py --download-repo
   ```

2. **"Icon not found"**
   ```bash
   # Search for similar icons
   python3 icon_manager.py --search "partial name"
   ```

3. **"Permission denied"**
   ```bash
   # Make sure you have write permissions
   chmod +w images/icons/
   ```

4. **"Network error"**
   ```bash
   # Check internet connection and try again
   python3 icon_manager.py --download-repo
   ```

### Verification
```bash
# Full system check
python3 icon_manager.py --verify
```

## 🎨 Icon Categories

The dashboard-icons repository includes icons for:
- **Development**: GitHub, GitLab, Docker, Kubernetes, etc.
- **Cloud Services**: AWS, Azure, GCP, DigitalOcean, etc.
- **Media**: YouTube, Netflix, Spotify, Plex, etc.
- **Communication**: Gmail, Slack, Discord, Teams, etc.
- **Home Automation**: Home Assistant, Homebridge, etc.
- **And many more...**

## 📝 Notes

- Icons are downloaded on-demand to save space
- The repository is ~200MB when fully downloaded
- Icons are cached locally for better performance
- All icons are in SVG format for crisp display at any size
- The system automatically handles path configuration

## 🤝 Contributing

If you find missing icons or have suggestions:
1. Check the [dashboard-icons repository](https://github.com/walkxcode/dashboard-icons)
2. Submit issues or pull requests there
3. The Homepage Editor will automatically benefit from updates

---

**Happy icon hunting!** 🎨✨
