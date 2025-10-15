# Simple Homepage Editor

A simple, clean bookmark editor for managing your homepage configuration files.

## Features

- **📁 Folder Selection**: Choose any folder to work with your config files
- **📂 Category Management**: Add, edit, and delete bookmark categories
- **🔖 Bookmark Management**: Add, edit, and delete bookmarks within categories
- **🔍 Icon Search**: Auto-searching, fast search through available icons
- **🔄 Data Reload**: Refresh data from the current folder
- **⌨️ Keyboard Shortcuts**: Quick access to common functions

## How to Use

### 1. Start the Application
```bash
./run.sh
# or
python3 simple_homepage_gui.py
```

### 2. Select Your Config Folder
- **Menu**: File → Select Config Folder...
- **Keyboard**: Ctrl+O
- Choose the folder containing your `bookmarks.yaml` and `settings.yaml` files

### 3. Manage Your Bookmarks
- **Left Panel**: Categories (click to select)
- **Right Panel**: Bookmarks for selected category
- **Buttons**: Add, Edit, Delete categories and bookmarks

### 4. Icon Search
- **Menu**: Tools → Icon Search
- **Keyboard**: Ctrl+I
- **In Bookmark Dialog**: Click "Search" button next to Icon field
- **Features**: Fast search through available icons with live preview
- **Auto-Search**: Automatically searches when window opens with pre-populated query
- **Smart Search**: Pre-populates search when editing existing bookmarks

### 5. Reload Data
- **Menu**: File → Reload Data
- **Keyboard**: F5
- Refreshes data from the current config folder

## File Structure

The app looks for these files in your selected folder:
- `bookmarks.yaml` - Your bookmark data
- `settings.yaml` - Layout and settings

## Keyboard Shortcuts

- `Ctrl+O` - Select Config Folder
- `Ctrl+I` - Open Icon Search
- `F5` - Reload Data

## Data Formats

### New Format (Recommended)
```yaml
- Category Name:
  - name: Bookmark Name
    url: https://example.com
    icon: icon.svg
```

### Old Format (Auto-converted when editing)
```yaml
- Category Name:
  - Bookmark Name:
    - abbr: BN
      href: https://example.com
      icon: icon.svg
```

## Requirements

- Python 3.6+
- PyYAML
- Pillow (for basic image support)
- cairosvg (for SVG icon support)

## Installation

```bash
# Install dependencies
pip install PyYAML Pillow cairosvg

# Run the application
python3 simple_homepage_gui.py
```

## Troubleshooting

- **No bookmarks showing**: Make sure you've selected the correct config folder
- **Can't save**: Check that the config folder is writable
- **Missing files**: The app will offer to create default config files if they don't exist