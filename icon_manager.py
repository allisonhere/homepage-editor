#!/usr/bin/env python3
"""
Smart Icon Manager for Homepage Editor
Manages SVG icon downloads, synchronization, and organization
"""

import os
import shutil
import json
import yaml
import requests
import zipfile
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IconManager:
    """Smart icon manager for downloading and organizing SVG icons"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.source_dir = self.project_root / "dashboard-icons-main" / "svg"
        self.output_dir = self.project_root / "images" / "icons"
        self.metadata_file = self.project_root / "dashboard-icons-main" / "metadata.json"
        self.tree_file = self.project_root / "dashboard-icons-main" / "tree.json"
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Icon cache for performance
        self._available_icons: Optional[Set[str]] = None
        self._icon_metadata: Optional[Dict] = None
    
    def is_dashboard_icons_available(self) -> bool:
        """Check if dashboard-icons repository is available"""
        return self.source_dir.exists() and self.metadata_file.exists()
    
    def download_dashboard_icons(self, force: bool = False) -> bool:
        """Download the dashboard-icons repository if not available"""
        if self.is_dashboard_icons_available() and not force:
            logger.info("Dashboard icons already available")
            return True
        
        try:
            logger.info("Downloading dashboard-icons repository...")
            
            # Download the repository as ZIP
            url = "https://github.com/walkxcode/dashboard-icons/archive/refs/heads/main.zip"
            zip_path = self.project_root / "dashboard-icons-main.zip"
            
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Extract the ZIP
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.project_root)
            
            # Rename extracted folder
            extracted_dir = self.project_root / "dashboard-icons-main"
            if extracted_dir.exists():
                shutil.rmtree(extracted_dir)
            
            shutil.move(self.project_root / "dashboard-icons-main", extracted_dir)
            
            # Clean up ZIP file
            zip_path.unlink()
            
            logger.info("✅ Dashboard icons downloaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to download dashboard icons: {e}")
            return False
    
    def get_available_icons(self) -> Set[str]:
        """Get list of available icons from the source directory"""
        if self._available_icons is not None:
            return self._available_icons
        
        if not self.is_dashboard_icons_available():
            logger.warning("Dashboard icons not available")
            return set()
        
        try:
            # Get all SVG files from source directory
            svg_files = list(self.source_dir.glob("*.svg"))
            self._available_icons = {f.stem for f in svg_files}
            logger.info(f"Found {len(self._available_icons)} available icons")
            return self._available_icons
        except Exception as e:
            logger.error(f"Failed to get available icons: {e}")
            return set()
    
    def get_icon_metadata(self) -> Dict:
        """Get icon metadata from the repository"""
        if self._icon_metadata is not None:
            return self._icon_metadata
        
        if not self.metadata_file.exists():
            logger.warning("Icon metadata not available")
            return {}
        
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                self._icon_metadata = json.load(f)
            return self._icon_metadata
        except Exception as e:
            logger.error(f"Failed to load icon metadata: {e}")
            return {}
    
    def search_icons(self, query: str, limit: int = 20) -> List[Dict]:
        """Search for icons by name or alias"""
        if not self.is_dashboard_icons_available():
            return []
        
        query = query.lower()
        results = []
        metadata = self.get_icon_metadata()
        
        for icon_name, icon_data in metadata.items():
            if query in icon_name.lower():
                results.append({
                    'name': icon_name,
                    'aliases': icon_data.get('aliases', []),
                    'categories': icon_data.get('categories', []),
                    'available': icon_name in self.get_available_icons()
                })
            elif query in ' '.join(icon_data.get('aliases', [])).lower():
                results.append({
                    'name': icon_name,
                    'aliases': icon_data.get('aliases', []),
                    'categories': icon_data.get('categories', []),
                    'available': icon_name in self.get_available_icons()
                })
        
        # Sort by relevance (exact match first, then partial)
        results.sort(key=lambda x: (
            0 if query in x['name'].lower() else 1,
            x['name']
        ))
        
        return results[:limit]
    
    def download_icon(self, icon_name: str) -> bool:
        """Download a single icon"""
        if not self.is_dashboard_icons_available():
            logger.error("Dashboard icons not available. Run download_dashboard_icons() first.")
            return False
        
        source = self.source_dir / f"{icon_name}.svg"
        dest = self.output_dir / f"{icon_name}.svg"
        
        if not source.exists():
            logger.error(f"Icon not found: {icon_name}.svg")
            return False
        
        try:
            shutil.copy2(source, dest)
            logger.info(f"✅ Downloaded: {icon_name}.svg")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to download {icon_name}.svg: {e}")
            return False
    
    def download_icons(self, icon_names: List[str]) -> Tuple[int, int]:
        """Download multiple icons
        
        Returns:
            Tuple of (successful_downloads, total_attempted)
        """
        if not icon_names:
            return 0, 0
        
        logger.info(f"Downloading {len(icon_names)} icons...")
        
        success_count = 0
        for icon_name in icon_names:
            if self.download_icon(icon_name):
                success_count += 1
        
        logger.info(f"📊 Downloaded {success_count}/{len(icon_names)} icons")
        return success_count, len(icon_names)
    
    def get_used_icons_from_bookmarks(self) -> Set[str]:
        """Extract icon names from bookmarks.yaml"""
        bookmarks_file = self.project_root / "bookmarks.yaml"
        if not bookmarks_file.exists():
            logger.warning("bookmarks.yaml not found")
            return set()
        
        try:
            with open(bookmarks_file, 'r', encoding='utf-8') as f:
                bookmarks = yaml.safe_load(f)
            
            used_icons = set()
            
            for category in bookmarks:
                if isinstance(category, dict):
                    for category_name, bookmarks_list in category.items():
                        if isinstance(bookmarks_list, list):
                            for bookmark in bookmarks_list:
                                if isinstance(bookmark, dict):
                                    for bookmark_name, bookmark_data in bookmark.items():
                                        if isinstance(bookmark_data, list) and len(bookmark_data) > 0:
                                            icon_path = bookmark_data[0].get('icon', '')
                                            if icon_path and icon_path.startswith('/images/icons/'):
                                                icon_name = Path(icon_path).stem
                                                used_icons.add(icon_name)
            
            logger.info(f"Found {len(used_icons)} icons used in bookmarks")
            return used_icons
            
        except Exception as e:
            logger.error(f"Failed to parse bookmarks.yaml: {e}")
            return set()
    
    def sync_used_icons(self) -> Tuple[int, int]:
        """Download all icons that are used in bookmarks but missing locally"""
        used_icons = self.get_used_icons_from_bookmarks()
        if not used_icons:
            logger.info("No icons found in bookmarks")
            return 0, 0
        
        # Check which icons are missing locally
        missing_icons = []
        for icon_name in used_icons:
            local_path = self.output_dir / f"{icon_name}.svg"
            if not local_path.exists():
                missing_icons.append(icon_name)
        
        if not missing_icons:
            logger.info("All used icons are already available locally")
            return 0, len(used_icons)
        
        logger.info(f"Found {len(missing_icons)} missing icons: {', '.join(missing_icons)}")
        return self.download_icons(missing_icons)
    
    def download_common_icons(self) -> Tuple[int, int]:
        """Download commonly used icons"""
        common_icons = [
            'github', 'docker', 'nginx', 'apache', 'mysql', 'postgresql',
            'redis', 'mongodb', 'elasticsearch', 'kibana', 'grafana',
            'prometheus', 'jenkins', 'gitlab', 'bitbucket', 'jira',
            'confluence', 'slack', 'discord', 'teams', 'zoom',
            'youtube', 'netflix', 'spotify', 'twitch', 'steam',
            'gmail', 'outlook', 'yahoo', 'protonmail', 'tutanota',
            'facebook', 'twitter', 'instagram', 'linkedin', 'reddit',
            'pinterest', 'tiktok', 'snapchat', 'whatsapp', 'telegram',
            'signal', 'viber', 'skype', 'zoom', 'meet',
            'aws', 'azure', 'gcp', 'digitalocean', 'linode',
            'vultr', 'heroku', 'netlify', 'vercel', 'cloudflare',
            'homeassistant', 'homebridge', 'domoticz', 'openhab',
            'plex', 'jellyfin', 'emby', 'kodi', 'sonarr',
            'radarr', 'lidarr', 'readarr', 'bazarr', 'ombi',
            'tautulli', 'jackett', 'prowlarr', 'qbit', 'transmission',
            'deluge', 'rtorrent', 'sabnzbd', 'nzbget', 'sickchill',
            'couchpotato', 'headphones', 'lazy', 'watcher', 'medusa',
            'nextcloud', 'owncloud', 'seafile', 'syncthing', 'resilio',
            'dropbox', 'onedrive', 'googledrive', 'mega', 'pcloud',
            'bitwarden', 'vaultwarden', 'passbolt', '1password', 'lastpass',
            'adguard', 'pihole', 'unbound', 'cloudflared', 'wireguard',
            'openvpn', 'tailscale', 'zerotier', 'fritzbox', 'ubiquiti',
            'mikrotik', 'cisco', 'fortinet', 'sonicwall', 'pfsense',
            'opnsense', 'vyos', 'vyatta', 'junos', 'ios',
            'nxos', 'eos', 'cumulus', 'arista', 'extreme',
            'alcatel', 'nokia', 'huawei', 'zte', 'ericsson'
        ]
        
        logger.info(f"Downloading {len(common_icons)} common icons...")
        return self.download_icons(common_icons)
    
    def get_local_icons(self) -> Set[str]:
        """Get list of locally available icons"""
        if not self.output_dir.exists():
            return set()
        
        svg_files = list(self.output_dir.glob("*.svg"))
        return {f.stem for f in svg_files}
    
    def verify_setup(self) -> bool:
        """Verify that the icon setup is working correctly"""
        logger.info("Verifying icon setup...")
        
        # Check if dashboard icons are available
        if not self.is_dashboard_icons_available():
            logger.error("❌ Dashboard icons not available")
            return False
        
        # Check if output directory exists
        if not self.output_dir.exists():
            logger.error("❌ Output directory does not exist")
            return False
        
        # Check if we can access metadata
        metadata = self.get_icon_metadata()
        if not metadata:
            logger.warning("⚠️  Icon metadata not available")
        else:
            logger.info(f"✅ Icon metadata loaded ({len(metadata)} icons)")
        
        # Check local icons
        local_icons = self.get_local_icons()
        logger.info(f"✅ Local icons: {len(local_icons)}")
        
        # Check used icons
        used_icons = self.get_used_icons_from_bookmarks()
        missing_icons = used_icons - local_icons
        if missing_icons:
            logger.warning(f"⚠️  Missing icons: {', '.join(missing_icons)}")
        else:
            logger.info("✅ All used icons are available locally")
        
        logger.info("✅ Icon setup verification complete")
        return True
    
    def cleanup_old_icons(self, keep_used: bool = True) -> int:
        """Remove icons that are no longer used
        
        Args:
            keep_used: If True, keep icons that are used in bookmarks
            
        Returns:
            Number of icons removed
        """
        if not self.output_dir.exists():
            return 0
        
        local_icons = self.get_local_icons()
        if not local_icons:
            return 0
        
        icons_to_remove = set()
        
        if keep_used:
            used_icons = self.get_used_icons_from_bookmarks()
            icons_to_remove = local_icons - used_icons
        else:
            icons_to_remove = local_icons
        
        removed_count = 0
        for icon_name in icons_to_remove:
            icon_path = self.output_dir / f"{icon_name}.svg"
            try:
                icon_path.unlink()
                removed_count += 1
                logger.info(f"🗑️  Removed: {icon_name}.svg")
            except Exception as e:
                logger.error(f"Failed to remove {icon_name}.svg: {e}")
        
        logger.info(f"📊 Removed {removed_count} unused icons")
        return removed_count


def main():
    """Command line interface for the icon manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Smart Icon Manager for Homepage Editor")
    parser.add_argument("--download-repo", action="store_true", help="Download dashboard-icons repository")
    parser.add_argument("--sync", action="store_true", help="Sync icons used in bookmarks")
    parser.add_argument("--common", action="store_true", help="Download common icons")
    parser.add_argument("--search", type=str, help="Search for icons")
    parser.add_argument("--download", nargs="+", help="Download specific icons")
    parser.add_argument("--verify", action="store_true", help="Verify setup")
    parser.add_argument("--cleanup", action="store_true", help="Remove unused icons")
    parser.add_argument("--list-local", action="store_true", help="List local icons")
    parser.add_argument("--list-used", action="store_true", help="List used icons")
    
    args = parser.parse_args()
    
    manager = IconManager()
    
    if args.download_repo:
        manager.download_dashboard_icons()
    elif args.sync:
        manager.sync_used_icons()
    elif args.common:
        manager.download_common_icons()
    elif args.search:
        results = manager.search_icons(args.search)
        for result in results:
            print(f"{result['name']} - {', '.join(result['aliases'])}")
    elif args.download:
        manager.download_icons(args.download)
    elif args.verify:
        manager.verify_setup()
    elif args.cleanup:
        manager.cleanup_old_icons()
    elif args.list_local:
        local_icons = manager.get_local_icons()
        for icon in sorted(local_icons):
            print(icon)
    elif args.list_used:
        used_icons = manager.get_used_icons_from_bookmarks()
        for icon in sorted(used_icons):
            print(icon)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
