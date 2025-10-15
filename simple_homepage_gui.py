#!/usr/bin/env python3
"""
Simple Homepage Editor - Just for editing bookmarks
No complex config management, just basic bookmark CRUD operations
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import yaml
import os
from PIL import Image, ImageTk
from icon_search import IconSearchWindow
from config_ui import ConfigPathWindow
from config_manager import config_manager

class SimpleHomepageGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Homepage Editor - Simple")
        self.geometry("800x600")
        
        # Data files - will be set by folder selection
        self.config_folder = os.getcwd()  # Default to current directory
        self.bookmarks_file = "bookmarks.yaml"
        self.settings_file = "settings.yaml"
        
        # Load data
        self.bookmarks = self.load_bookmarks()
        self.settings = self.load_settings()
        
        # Create UI
        self.create_widgets()
        self.create_menu()
        self.bind_shortcuts()
        self.populate_categories()
        
    def load_bookmarks(self):
        """Load bookmarks from YAML file"""
        try:
            bookmarks_path = config_manager.get_config_path('bookmarks')
            if os.path.exists(bookmarks_path):
                with open(bookmarks_path, 'r') as f:
                    return yaml.safe_load(f) or []
            return []
        except Exception as e:
            print(f"Error loading bookmarks: {e}")
            return []
    
    def save_bookmarks(self, data):
        """Save bookmarks to YAML file"""
        try:
            bookmarks_path = config_manager.get_config_path('bookmarks')
            with open(bookmarks_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save bookmarks: {e}")
            return False
    
    def load_settings(self):
        """Load settings from YAML file"""
        try:
            settings_path = config_manager.get_config_path('settings')
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    return yaml.safe_load(f) or {}
            return {"layout": []}
        except Exception as e:
            print(f"Error loading settings: {e}")
            return {"layout": []}
    
    def save_settings(self, data):
        """Save settings to YAML file"""
        try:
            settings_path = config_manager.get_config_path('settings')
            with open(settings_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
            return False
    
    def create_widgets(self):
        """Create the main UI"""
        # Main frame with two panes
        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left pane for categories
        category_frame = ttk.LabelFrame(main_pane, text="Categories")
        main_pane.add(category_frame, weight=1)
        
        # Category buttons
        category_button_frame = ttk.Frame(category_frame)
        category_button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(category_button_frame, text="Add Category", command=self.add_category).pack(side=tk.LEFT, padx=2)
        ttk.Button(category_button_frame, text="Delete Category", command=self.delete_category).pack(side=tk.LEFT, padx=2)
        
        # Categories list
        self.categories_listbox = tk.Listbox(category_frame)
        self.categories_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.categories_listbox.bind('<<ListboxSelect>>', self.on_category_select)
        
        # Right pane for bookmarks
        bookmark_frame = ttk.LabelFrame(main_pane, text="Bookmarks")
        main_pane.add(bookmark_frame, weight=2)
        
        # Bookmark buttons
        bookmark_button_frame = ttk.Frame(bookmark_frame)
        bookmark_button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(bookmark_button_frame, text="Add Bookmark", command=self.add_bookmark).pack(side=tk.LEFT, padx=2)
        ttk.Button(bookmark_button_frame, text="Edit Bookmark", command=self.edit_bookmark).pack(side=tk.LEFT, padx=2)
        ttk.Button(bookmark_button_frame, text="Delete Bookmark", command=self.delete_bookmark).pack(side=tk.LEFT, padx=2)
        
        # Bookmarks list
        self.bookmarks_listbox = tk.Listbox(bookmark_frame)
        self.bookmarks_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set(f"Config folder: {self.config_folder}")
        status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.current_category = None
    
    def create_menu(self):
        """Create the menu bar"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Reload Data", command=self.reload_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Configuration...", command=self.open_configuration)
        tools_menu.add_separator()
        tools_menu.add_command(label="Icon Search", command=self.open_icon_search)
    
    def open_icon_search(self):
        """Open the icon search window"""
        try:
            search_window = IconSearchWindow(self)
            # The window will handle its own lifecycle
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open icon search: {e}")
    
    def search_icon(self):
        """Alias for open_icon_search for consistency"""
        self.open_icon_search()
    
    def open_configuration(self):
        """Open unified configuration window"""
        ConfigPathWindow(self, config_folder=self.config_folder)
    
    def bind_shortcuts(self):
        """Bind keyboard shortcuts"""
        self.bind('<Control-o>', lambda e: self.select_config_folder())
        self.bind('<F5>', lambda e: self.reload_data())
        self.bind('<Control-i>', lambda e: self.search_icon())
    
    def select_config_folder(self):
        """Open folder selection dialog"""
        folder = filedialog.askdirectory(
            title="Select Configuration Folder",
            initialdir=self.config_folder
        )
        
        if folder:
            self.config_folder = folder
            self.title(f"Homepage Editor - Simple ({os.path.basename(folder)})")
            self.reload_data()
            messagebox.showinfo("Success", f"Switched to config folder:\n{folder}")
    
    def reload_data(self):
        """Reload data from the current config paths"""
        # Update config folder from config_manager if it has changed
        bookmarks_path = config_manager.get_config_path('bookmarks')
        if bookmarks_path:
            self.config_folder = os.path.dirname(bookmarks_path)
        
        # Clear current data
        self.bookmarks_listbox.delete(0, tk.END)
        self.current_category = None
        
        # Load new data
        self.bookmarks = self.load_bookmarks()
        self.settings = self.load_settings()
        
        # Populate categories with new data
        self.populate_categories()
        
        # Force UI update with multiple methods
        self.update_idletasks()
        self.update()
        self.categories_listbox.update()
        self.categories_listbox.update_idletasks()
        
        # Update title and status
        self.title(f"Homepage Editor - Simple ({os.path.basename(self.config_folder)})")
        self.status_var.set(f"Config folder: {self.config_folder}")
        
        # Check if config files exist
        bookmarks_path = config_manager.get_config_path('bookmarks')
        settings_path = config_manager.get_config_path('settings')
        
        if not os.path.exists(bookmarks_path) or not os.path.exists(settings_path):
            if messagebox.askyesno("Create Config Files", 
                                 f"Config files not found in:\n{self.config_folder}\n\nCreate new config files?"):
                self.create_default_configs()
    
    def create_default_configs(self):
        """Create default configuration files"""
        try:
            # Create default bookmarks
            default_bookmarks = [
                {"Sample Category": [
                    {"name": "Example Bookmark", "url": "https://example.com", "icon": "example.svg"}
                ]}
            ]
            
            # Create default settings
            default_settings = {
                "layout": [
                    {"Sample Category": {"style": "row", "columns": 3}}
                ]
            }
            
            # Save the files
            self.save_bookmarks(default_bookmarks)
            self.save_settings(default_settings)
            
            # Reload data
            self.reload_data()
            messagebox.showinfo("Success", "Default configuration files created!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create config files: {e}")
    
    def populate_categories(self):
        """Populate the categories listbox"""
        self.categories_listbox.delete(0, tk.END)
        for item in self.bookmarks:
            if isinstance(item, dict):
                for category_name in item.keys():
                    self.categories_listbox.insert(tk.END, category_name)
    
    def on_category_select(self, event):
        """Handle category selection"""
        selection = self.categories_listbox.curselection()
        if selection:
            category_name = self.categories_listbox.get(selection[0])
            self.current_category = category_name
            self.populate_bookmarks(category_name)
    
    def populate_bookmarks(self, category_name):
        """Populate bookmarks for selected category"""
        self.bookmarks_listbox.delete(0, tk.END)
        
        for item in self.bookmarks:
            if isinstance(item, dict) and category_name in item:
                bookmarks = item[category_name]
                for bookmark in bookmarks:
                    if isinstance(bookmark, dict):
                        # Handle new format: {name: "Name", url: "URL", icon: "ICON"}
                        if 'name' in bookmark:
                            self.bookmarks_listbox.insert(tk.END, bookmark['name'])
                        # Handle old format: {BookmarkName: [{abbr: "AB", href: "URL", icon: "ICON"}]}
                        else:
                            for bookmark_name, bookmark_data in bookmark.items():
                                if isinstance(bookmark_data, list) and len(bookmark_data) > 0:
                                    bookmark_info = bookmark_data[0]
                                    if isinstance(bookmark_info, dict) and 'href' in bookmark_info:
                                        self.bookmarks_listbox.insert(tk.END, bookmark_name)
                break
        
        # Update status
        count = self.bookmarks_listbox.size()
        self.status_var.set(f"Category: {category_name} ({count} bookmarks)")
    
    def add_category(self):
        """Add a new category"""
        category_name = simpledialog.askstring("Add Category", "Enter category name:")
        if not category_name:
            return
        
        # Check if category already exists
        for item in self.bookmarks:
            if isinstance(item, dict) and category_name in item:
                messagebox.showerror("Error", "Category already exists!")
                return
        
        # Add new category
        self.bookmarks.append({category_name: []})
        self.save_bookmarks(self.bookmarks)
        
        self.populate_categories()
        self.status_var.set(f"Added category: {category_name}")
        messagebox.showinfo("Success", "Category added successfully!")
    
    def delete_category(self):
        """Delete selected category"""
        selection = self.categories_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a category to delete!")
            return
        
        category_name = self.categories_listbox.get(selection[0])
        
        if messagebox.askyesno("Confirm Delete", f"Delete category '{category_name}' and all its bookmarks?"):
            # Remove from bookmarks
            self.bookmarks = [item for item in self.bookmarks if not (isinstance(item, dict) and category_name in item)]
            self.save_bookmarks(self.bookmarks)
            
            # Remove from layout
            if "layout" in self.settings:
                self.settings["layout"] = [item for item in self.settings["layout"] if not (isinstance(item, dict) and category_name in item)]
                self.save_settings(self.settings)
            
            self.populate_categories()
            self.bookmarks_listbox.delete(0, tk.END)
            self.current_category = None
            self.status_var.set("Category deleted")
            messagebox.showinfo("Success", "Category deleted successfully!")
    
    def add_bookmark(self):
        """Add a new bookmark"""
        if not self.current_category:
            messagebox.showwarning("Warning", "Please select a category first!")
            return
        
        # Simple dialog for bookmark details
        dialog = BookmarkDialog(self, "Add Bookmark")
        if dialog.result:
            bookmark = dialog.result
            
            # Convert to proper YAML structure
            name = bookmark['name']
            url = bookmark['url']
            icon = bookmark['icon']
            abbr = bookmark['abbr']
            
            # Create proper bookmark structure
            proper_bookmark = {
                name: [{
                    'abbr': abbr,
                    'href': url,  # Convert 'url' to 'href'
                    'icon': icon
                }]
            }
            
            # Add to bookmarks
            for item in self.bookmarks:
                if isinstance(item, dict) and self.current_category in item:
                    item[self.current_category].append(proper_bookmark)
                    break
            
            self.save_bookmarks(self.bookmarks)
            self.populate_bookmarks(self.current_category)
            self.status_var.set(f"Added bookmark: {name}")
            messagebox.showinfo("Success", "Bookmark added successfully!")
    
    def edit_bookmark(self):
        """Edit selected bookmark"""
        if not self.current_category:
            messagebox.showwarning("Warning", "Please select a category first!")
            return
        
        selection = self.bookmarks_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a bookmark to edit!")
            return
        
        bookmark_name = self.bookmarks_listbox.get(selection[0])
        
        # Find the bookmark and convert to new format if needed
        bookmark = None
        for item in self.bookmarks:
            if isinstance(item, dict) and self.current_category in item:
                for bm in item[self.current_category]:
                    if isinstance(bm, dict):
                        # New format
                        if bm.get('name') == bookmark_name:
                            bookmark = bm
                            break
                        # Old format - convert to new format
                        elif bookmark_name in bm:
                            bookmark_data = bm[bookmark_name]
                            if isinstance(bookmark_data, list) and len(bookmark_data) > 0:
                                info = bookmark_data[0]
                                bookmark = {
                                    'name': bookmark_name,
                                    'url': info.get('href', ''),
                                    'icon': info.get('icon', '')
                                }
                                # Update the bookmark in place
                                bm.clear()
                                bm.update(bookmark)
                                break
                break
        
        if bookmark:
            dialog = BookmarkDialog(self, "Edit Bookmark", bookmark)
            if dialog.result:
                # Convert to proper YAML structure
                name = dialog.result['name']
                url = dialog.result['url']
                icon = dialog.result['icon']
                abbr = dialog.result['abbr']
                
                # Find and update the bookmark in the proper structure
                for item in self.bookmarks:
                    if isinstance(item, dict) and self.current_category in item:
                        for i, bm in enumerate(item[self.current_category]):
                            if isinstance(bm, dict) and bookmark_name in bm:
                                # Update the bookmark structure
                                item[self.current_category][i] = {
                                    name: [{
                                        'abbr': abbr,
                                        'href': url,  # Convert 'url' to 'href'
                                        'icon': icon
                                    }]
                                }
                                break
                        break
                
                self.save_bookmarks(self.bookmarks)
                self.populate_bookmarks(self.current_category)
                self.status_var.set(f"Updated bookmark: {name}")
                messagebox.showinfo("Success", "Bookmark updated successfully!")
    
    def delete_bookmark(self):
        """Delete selected bookmark"""
        if not self.current_category:
            messagebox.showwarning("Warning", "Please select a category first!")
            return
        
        selection = self.bookmarks_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a bookmark to delete!")
            return
        
        bookmark_name = self.bookmarks_listbox.get(selection[0])
        
        if messagebox.askyesno("Confirm Delete", f"Delete bookmark '{bookmark_name}'?"):
            # Remove bookmark (handle both old and new formats)
            for item in self.bookmarks:
                if isinstance(item, dict) and self.current_category in item:
                    # Filter out bookmarks that match the name
                    item[self.current_category] = [bm for bm in item[self.current_category] 
                                                 if not (isinstance(bm, dict) and 
                                                        (bm.get('name') == bookmark_name or bookmark_name in bm))]
                    break
            
            self.save_bookmarks(self.bookmarks)
            self.populate_bookmarks(self.current_category)
            self.status_var.set("Bookmark deleted")
            messagebox.showinfo("Success", "Bookmark deleted successfully!")


class BookmarkDialog(tk.Toplevel):
    def __init__(self, parent, title, bookmark=None):
        super().__init__(parent)
        self.transient(parent)
        self.title(title)
        self.parent = parent
        self.result = None
        
        # Default values
        if bookmark:
            self.name_var = tk.StringVar(value=bookmark.get('name', ''))
            self.url_var = tk.StringVar(value=bookmark.get('url', ''))
            self.icon_var = tk.StringVar(value=bookmark.get('icon', ''))
            self.abbr_var = tk.StringVar(value=bookmark.get('abbr', ''))
        else:
            self.name_var = tk.StringVar()
            self.url_var = tk.StringVar()
            self.icon_var = tk.StringVar()
            self.abbr_var = tk.StringVar()
        
        self.create_widgets()
        self.grab_set()
        self.wait_window(self)
    
    def create_widgets(self):
        """Create dialog widgets"""
        frame = ttk.Frame(self, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Name
        ttk.Label(frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(frame, textvariable=self.name_var, width=30).grid(row=0, column=1, sticky=tk.W, pady=2)
        
        # Abbreviation
        ttk.Label(frame, text="Abbr:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(frame, textvariable=self.abbr_var, width=30).grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # URL
        ttk.Label(frame, text="URL:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(frame, textvariable=self.url_var, width=30).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # Icon
        ttk.Label(frame, text="Icon:").grid(row=3, column=0, sticky=tk.W, pady=2)
        icon_frame = ttk.Frame(frame)
        icon_frame.grid(row=3, column=1, sticky=tk.W, pady=2)
        ttk.Entry(icon_frame, textvariable=self.icon_var, width=25).pack(side=tk.LEFT)
        ttk.Button(icon_frame, text="Search", command=self.search_icon, width=8).pack(side=tk.LEFT, padx=(5, 0))
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=5)
    
    def search_icon(self):
        """Open icon search window"""
        try:
            # Get current icon value for initial search
            current_icon = self.icon_var.get().strip()
            if current_icon:
                # Extract icon name from path if it's a full path
                if '/' in current_icon:
                    current_icon = os.path.basename(current_icon)
                if current_icon.endswith('.svg'):
                    current_icon = current_icon[:-4]  # Remove .svg extension
            
            # Open icon search window
            search_window = IconSearchWindow(self, current_icon)
            
            # The IconSearchWindow will automatically update self.icon_var
            # when an icon is selected, so we don't need to do anything here
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open icon search: {e}")
    
    def ok_clicked(self):
        """Handle OK button click"""
        name = self.name_var.get().strip()
        url = self.url_var.get().strip()
        icon = self.icon_var.get().strip()
        abbr = self.abbr_var.get().strip()
        
        if not name or not url:
            messagebox.showerror("Error", "Name and URL are required!")
            return
        
        # Auto-generate abbreviation if not provided
        if not abbr:
            abbr = name[:2].upper()
        
        self.result = {
            'name': name,
            'url': url,
            'icon': icon,
            'abbr': abbr
        }
        self.destroy()


def main():
    """Main function"""
    app = SimpleHomepageGUI()
    app.mainloop()


if __name__ == "__main__":
    main()