
#!/usr/bin/env python3
"""
Create icon index from the configured icon directory
"""

import os
import sys
from config_manager import config_manager

def main():
    """Create icon index from configured directory"""
    # Use the configured icon directory for creating the index
    icon_dir = config_manager.get_icon_base_path()
    index_file = "icon_index.txt"

    print(f"Creating icon index from: {icon_dir}")

    if not os.path.exists(icon_dir):
        print(f"Error: Icon directory {icon_dir} does not exist!")
        print("Please configure the icon base path in the Configuration Paths dialog.")
        sys.exit(1)

    try:
        svg_files = []
        with open(index_file, "w") as f:
            for icon_file in os.listdir(icon_dir):
                if icon_file.endswith(".svg"):
                    f.write(f"{icon_file}\n")
                    svg_files.append(icon_file)
        
        print(f"✅ Icon index created successfully!")
        print(f"   Found {len(svg_files)} SVG icons")
        print(f"   Index saved to: {index_file}")
        
    except Exception as e:
        print(f"Error creating icon index: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

