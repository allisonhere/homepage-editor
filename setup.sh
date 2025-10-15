#!/bin/bash
# Homepage Editor - Easy Setup Script

echo "🚀 Homepage Editor - Easy Setup"
echo "================================"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "simple_homepage_gui.py" ]; then
    echo "❌ Please run this script from the Homepage Editor directory"
    exit 1
fi

echo "✅ Python 3 found"
echo "✅ Homepage Editor files found"

# Install required Python packages
echo ""
echo "📦 Installing required packages..."
pip3 install -r requirements.txt 2>/dev/null || {
    echo "⚠️  requirements.txt not found, installing basic packages..."
    pip3 install requests pillow pyyaml
}

# Setup icons
echo ""
echo "🎨 Setting up icons..."
python3 setup_icons.py

# Make scripts executable
chmod +x icon_manager.py
chmod +x setup_icons.py

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📖 Quick Start:"
echo "  ./run.sh                    # Start the GUI"
echo "  python3 icon_manager.py --help  # Manage icons"
echo "  python3 setup_icons.py     # Re-setup icons"
echo ""
echo "🔧 Icon Management:"
echo "  python3 icon_manager.py --search docker    # Search for icons"
echo "  python3 icon_manager.py --sync             # Sync used icons"
echo "  python3 icon_manager.py --download github  # Download specific icons"
echo "  python3 icon_manager.py --verify           # Verify setup"
