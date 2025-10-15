#!/usr/bin/env python3
"""
Icon Setup Script for Homepage Editor
Easy setup and management of SVG icons
"""

import sys
import os
from pathlib import Path
from icon_manager import IconManager

def main():
    """Main setup function"""
    print("🚀 Homepage Editor - Icon Setup")
    print("=" * 40)
    
    # Initialize icon manager
    manager = IconManager()
    
    # Check if dashboard icons are available
    if not manager.is_dashboard_icons_available():
        print("📥 Dashboard icons not found. Downloading...")
        if not manager.download_dashboard_icons():
            print("❌ Failed to download dashboard icons. Please check your internet connection.")
            return False
        print("✅ Dashboard icons downloaded successfully!")
    else:
        print("✅ Dashboard icons already available")
    
    # Verify setup
    print("\n🔍 Verifying setup...")
    if not manager.verify_setup():
        print("❌ Setup verification failed")
        return False
    
    # Check used icons
    used_icons = manager.get_used_icons_from_bookmarks()
    if used_icons:
        print(f"\n📋 Found {len(used_icons)} icons used in bookmarks")
        
        # Sync missing icons
        print("🔄 Syncing missing icons...")
        success, total = manager.sync_used_icons()
        if success > 0:
            print(f"✅ Downloaded {success} missing icons")
        else:
            print("✅ All used icons are already available")
    else:
        print("\n📋 No icons found in bookmarks")
        
        # Ask if user wants to download common icons
        response = input("\n🤔 Would you like to download common icons? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            print("📥 Downloading common icons...")
            success, total = manager.download_common_icons()
            print(f"✅ Downloaded {success}/{total} common icons")
    
    print("\n🎉 Icon setup complete!")
    print("\n📖 Usage:")
    print("  python3 icon_manager.py --help          # Show all options")
    print("  python3 icon_manager.py --search docker # Search for icons")
    print("  python3 icon_manager.py --sync          # Sync used icons")
    print("  python3 icon_manager.py --verify        # Verify setup")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
