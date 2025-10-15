#!/usr/bin/env python3
"""
Configuration UI Manager
Provides GUI for managing external configuration files and privilege elevation
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from typing import Dict, Any
import threading
import os
from config_manager import config_manager

class ConfigPathWindow(tk.Toplevel):
    """Window for managing configuration file paths"""
    
    def __init__(self, parent, config_folder=None):
        super().__init__(parent)
        self.transient(parent)
        self.title("Configuration Manager")
        self.geometry("800x600")
        self.parent = parent
        self.config_folder = config_folder
        
        self.create_widgets()
        self.load_current_paths()
        
    def create_widgets(self):
        """Create the UI widgets"""
        # Main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Configuration File Paths", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Instructions
        instructions = ttk.Label(main_frame, 
                               text="Configure the paths for your Homepage configuration files.\n"
                                    "You can use external paths for better organization and backup.",
                               font=("Arial", 10))
        instructions.pack(pady=(0, 20))
        
        # Create notebook for different config types
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Folder selection tab
        self.create_folder_selection_tab()
        
        # Core configs tab
        self.create_core_configs_tab()
        
        # Icon configuration tab
        self.create_icon_config_tab()
        
        # Services tab
        self.create_services_tab()
        
        # Advanced tab
        self.create_advanced_tab()
        
        # Status frame
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(side=tk.LEFT)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Test All Paths", 
                  command=self.test_all_paths).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Reset to Defaults", 
                  command=self.reset_to_defaults).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Save", 
                  command=self.save_paths).pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Button(button_frame, text="Cancel", 
                  command=self.destroy).pack(side=tk.RIGHT)
    
    def create_folder_selection_tab(self):
        """Create the folder selection tab"""
        folder_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(folder_frame, text="📁 Folder")
        
        # Header description
        header_frame = ttk.Frame(folder_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, 
                 text="Select the folder containing your Homepage configuration files",
                 font=("TkDefaultFont", 10, "bold")).pack(anchor="w")
        
        ttk.Label(header_frame, 
                 text="This determines which configuration files the editor will work with.",
                 foreground="gray").pack(anchor="w", pady=(2, 0))
        
        # Current folder display
        current_frame = ttk.LabelFrame(folder_frame, text="Current Configuration Folder", padding="10")
        current_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.current_folder_var = tk.StringVar()
        self.current_folder_entry = ttk.Entry(current_frame, textvariable=self.current_folder_var, 
                                            state="readonly", width=60)
        self.current_folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(current_frame, text="Browse", 
                  command=self.browse_config_folder).pack(side=tk.RIGHT, padx=(10, 0))
        
        # Folder info
        info_frame = ttk.LabelFrame(folder_frame, text="Folder Information", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.folder_info_var = tk.StringVar()
        self.folder_info_label = ttk.Label(info_frame, textvariable=self.folder_info_var, 
                                         font=("Courier", 9), foreground="blue")
        self.folder_info_label.pack(anchor="w")
        
        # Load current folder
        if self.config_folder:
            self.current_folder_var.set(self.config_folder)
            self.update_folder_info()
    
    def browse_config_folder(self):
        """Browse for configuration folder"""
        folder = filedialog.askdirectory(
            title="Select Configuration Folder",
            initialdir=self.config_folder or os.getcwd()
        )
        if folder:
            self.current_folder_var.set(folder)
            self.config_folder = folder
            self.update_folder_info()
            self.auto_update_config_paths(folder)
    
    def update_folder_info(self):
        """Update folder information display"""
        folder = self.current_folder_var.get()
        if not folder:
            self.folder_info_var.set("No folder selected")
            return
        
        try:
            # Check what files exist in the folder
            files = os.listdir(folder) if os.path.exists(folder) else []
            yaml_files = [f for f in files if f.endswith('.yaml')]
            json_files = [f for f in files if f.endswith('.json')]
            
            info_text = f"Folder: {folder}\n"
            info_text += f"YAML files: {', '.join(yaml_files) if yaml_files else 'None'}\n"
            info_text += f"JSON files: {', '.join(json_files) if json_files else 'None'}\n"
            info_text += f"Total files: {len(files)}"
            
            self.folder_info_var.set(info_text)
        except Exception as e:
            self.folder_info_var.set(f"Error reading folder: {e}")
    
    def auto_update_config_paths(self, folder):
        """Automatically update all config paths when a new folder is selected"""
        if not folder:
            return
        
        # Define the standard config files and their expected names
        config_files = {
            "bookmarks": "bookmarks.yaml",
            "settings": "settings.yaml", 
            "services": "services.yaml",
            "widgets": "widgets.yaml",
            "docker": "docker.yaml",
            "kubernetes": "kubernetes.yaml",
            "proxmox": "proxmox.yaml"
        }
        
        # Update all config path entries
        all_entries = {**self.core_entries, **self.services_entries}
        updated_count = 0
        
        for config_name, filename in config_files.items():
            if config_name in all_entries:
                new_path = os.path.join(folder, filename)
                # Clear the entry and insert the new path
                entry = all_entries[config_name]
                entry.delete(0, tk.END)
                entry.insert(0, new_path)
                updated_count += 1
        
        # Update icon paths to be relative to the new folder
        if hasattr(self, 'icon_base_path_var'):
            # Keep the relative path structure
            self.icon_base_path_var.set("dashboard-icons-main/svg")
        
        if hasattr(self, 'icon_output_path_var'):
            # Keep the relative path structure  
            self.icon_output_path_var.set("images/icons")
        
        # Show status message
        if hasattr(self, 'status_var'):
            self.status_var.set(f"✅ Automatically updated {updated_count} configuration paths to use folder: {os.path.basename(folder)}")
    
    def create_core_configs_tab(self):
        """Create the core configurations tab"""
        core_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(core_frame, text="Core Configs")
        
        # Create scrollable frame
        canvas = tk.Canvas(core_frame)
        scrollbar = ttk.Scrollbar(core_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Core configuration entries
        self.core_entries = {}
        core_configs = ["bookmarks", "settings", "widgets"]
        
        for i, config_name in enumerate(core_configs):
            self.create_config_entry(scrollable_frame, config_name, i, core_configs)
    
    def create_services_tab(self):
        """Create the services configurations tab"""
        services_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(services_frame, text="Services")
        
        # Create scrollable frame
        canvas = tk.Canvas(services_frame)
        scrollbar = ttk.Scrollbar(services_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Services configuration entries
        self.services_entries = {}
        service_configs = ["services", "docker", "kubernetes", "proxmox"]
        
        for i, config_name in enumerate(service_configs):
            self.create_config_entry(scrollable_frame, config_name, i, service_configs)
    
    def create_icon_config_tab(self):
        """Create the icon configuration tab"""
        icon_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(icon_frame, text="🎨 Icons")
        
        # Header description
        header_frame = ttk.Frame(icon_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, 
                 text="Configure where to find icon files and where to store selected icons",
                 font=("TkDefaultFont", 10, "bold")).pack(anchor="w")
        
        ttk.Label(header_frame, 
                 text="This affects the Icon Search feature and how icons are stored in your bookmarks.",
                 foreground="gray").pack(anchor="w", pady=(2, 0))
        
        # Icon base path configuration
        base_path_frame = ttk.LabelFrame(icon_frame, text="Icon Source Path", padding="10")
        base_path_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(base_path_frame, 
                 text="Source directory for icon files when copying selected icons (e.g., dashboard-icons-main/svg):").pack(anchor="w")
        
        base_path_input_frame = ttk.Frame(base_path_frame)
        base_path_input_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.icon_base_path_var = tk.StringVar()
        self.icon_base_path_entry = ttk.Entry(base_path_input_frame, textvariable=self.icon_base_path_var, width=50)
        self.icon_base_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(base_path_input_frame, text="Browse", 
                  command=self.browse_icon_base_path).pack(side=tk.RIGHT, padx=(10, 0))
        
        # Icon output path configuration
        output_path_frame = ttk.LabelFrame(icon_frame, text="Icon Output Path", padding="10")
        output_path_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(output_path_frame, 
                 text="Directory where selected icons will be copied (e.g., images/icons):").pack(anchor="w")
        
        output_path_input_frame = ttk.Frame(output_path_frame)
        output_path_input_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.icon_output_path_var = tk.StringVar()
        self.icon_output_path_entry = ttk.Entry(output_path_input_frame, textvariable=self.icon_output_path_var, width=50)
        self.icon_output_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(output_path_input_frame, text="Browse", 
                  command=self.browse_icon_output_path).pack(side=tk.RIGHT, padx=(10, 0))
        
        # Icon path preview
        preview_frame = ttk.LabelFrame(icon_frame, text="Path Preview", padding="10")
        preview_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(preview_frame, text="Example: If you select 'webmin.svg', it will be stored as:").pack(anchor="w")
        
        self.icon_preview_var = tk.StringVar()
        self.icon_preview_label = ttk.Label(preview_frame, textvariable=self.icon_preview_var, 
                                          font=("Courier", 10), foreground="blue")
        self.icon_preview_label.pack(anchor="w", pady=(5, 0))
        
        # Icon index management
        index_frame = ttk.LabelFrame(icon_frame, text="Icon Index Management", padding="10")
        index_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(index_frame, 
                 text="The icon index is used for fast searching. Regenerate it if you change the icon source directory.").pack(anchor="w")
        
        index_button_frame = ttk.Frame(index_frame)
        index_button_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(index_button_frame, text="Regenerate Icon Index", 
                  command=self.regenerate_icon_index).pack(side=tk.LEFT, padx=(0, 10))
        
        self.index_status_var = tk.StringVar()
        self.index_status_label = ttk.Label(index_button_frame, textvariable=self.index_status_var, 
                                          foreground="gray")
        self.index_status_label.pack(side=tk.LEFT)
        
        # Bind to update preview
        self.icon_base_path_var.trace('w', self.update_icon_preview)
        self.icon_output_path_var.trace('w', self.update_icon_preview)
    
    def browse_icon_base_path(self):
        """Browse for icon base directory"""
        directory = filedialog.askdirectory(
            title="Select Icon Base Directory",
            initialdir=config_manager.get_icon_base_path()
        )
        if directory:
            self.icon_base_path_var.set(directory)
    
    def browse_icon_output_path(self):
        """Browse for icon output directory"""
        directory = filedialog.askdirectory(
            title="Select Icon Output Directory",
            initialdir=config_manager.get_icon_output_path()
        )
        if directory:
            self.icon_output_path_var.set(directory)
    
    def update_icon_preview(self, *args):
        """Update the icon path preview"""
        base_path = self.icon_base_path_var.get()
        output_path = self.icon_output_path_var.get()
        
        if base_path and output_path:
            preview_text = f"Icon name: webmin.svg\nSource: {base_path}/webmin.svg\nCopied to: {output_path}/webmin.svg\nStored as: /{output_path}/webmin.svg"
            self.icon_preview_var.set(preview_text)
        else:
            self.icon_preview_var.set("Configure both paths to see preview")
    
    def regenerate_icon_index(self):
        """Regenerate the icon index from the current base path"""
        base_path = self.icon_base_path_var.get()
        if not base_path:
            messagebox.showerror("Error", "Please set the icon base path first!")
            return
        
        if not os.path.exists(base_path):
            messagebox.showerror("Error", f"Icon base path does not exist: {base_path}")
            return
        
        self.index_status_var.set("Regenerating index...")
        self.update()
        
        try:
            # Count SVG files
            svg_files = [f for f in os.listdir(base_path) if f.endswith('.svg')]
            
            # Write index file
            with open("icon_index.txt", "w") as f:
                for icon_file in sorted(svg_files):
                    f.write(f"{icon_file}\n")
            
            self.index_status_var.set(f"Index regenerated with {len(svg_files)} icons")
            messagebox.showinfo("Success", f"Icon index regenerated successfully!\nFound {len(svg_files)} SVG icons in {base_path}")
            
        except Exception as e:
            self.index_status_var.set("Error regenerating index")
            messagebox.showerror("Error", f"Failed to regenerate icon index: {e}")
    
    def create_advanced_tab(self):
        """Create the advanced settings tab"""
        advanced_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(advanced_frame, text="Advanced")
        
        # Backup settings
        backup_frame = ttk.LabelFrame(advanced_frame, text="Backup Settings", padding="10")
        backup_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.backup_enabled = tk.BooleanVar(value=True)
        ttk.Checkbutton(backup_frame, text="Enable automatic backups", 
                       variable=self.backup_enabled).pack(anchor="w")
        
        # Privilege elevation settings
        privilege_frame = ttk.LabelFrame(advanced_frame, text="Privilege Elevation", padding="10")
        privilege_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(privilege_frame, 
                 text="When files require elevated privileges, the application will attempt to use sudo.").pack(anchor="w")
        
        ttk.Button(privilege_frame, text="Test Privilege Elevation", 
                  command=self.test_privilege_elevation).pack(anchor="w", pady=(10, 0))
        
        # Configuration validation
        validation_frame = ttk.LabelFrame(advanced_frame, text="Configuration Validation", padding="10")
        validation_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(validation_frame, text="Validate All Configurations", 
                  command=self.validate_all_configs).pack(anchor="w")
        
        # Validation results
        self.validation_text = tk.Text(validation_frame, height=10, width=70)
        self.validation_text.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Add scrollbar for validation text
        validation_scrollbar = ttk.Scrollbar(validation_frame, orient="vertical", 
                                           command=self.validation_text.yview)
        self.validation_text.configure(yscrollcommand=validation_scrollbar.set)
        validation_scrollbar.pack(side="right", fill="y")
    
    def create_config_entry(self, parent, config_name, row, config_list):
        """Create a configuration entry widget"""
        # Main frame for this config
        config_frame = ttk.LabelFrame(parent, text=config_name.title(), padding="10")
        config_frame.pack(fill=tk.X, pady=5)
        
        # Path entry
        path_frame = ttk.Frame(config_frame)
        path_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(path_frame, text="Path:", width=10).pack(side=tk.LEFT)
        
        entry = ttk.Entry(path_frame, width=50)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        
        ttk.Button(path_frame, text="Browse", 
                  command=lambda: self.browse_for_file(entry, config_name)).pack(side=tk.RIGHT)
        
        # Status and actions
        status_frame = ttk.Frame(config_frame)
        status_frame.pack(fill=tk.X)
        
        self.status_labels = getattr(self, 'status_labels', {})
        self.status_labels[config_name] = ttk.Label(status_frame, text="", foreground="gray")
        self.status_labels[config_name].pack(side=tk.LEFT)
        
        ttk.Button(status_frame, text="Test", 
                  command=lambda: self.test_config_path(config_name)).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(status_frame, text="Reset", 
                  command=lambda: self.reset_config_path(config_name)).pack(side=tk.RIGHT)
        
        # Store the entry
        if config_name in ["bookmarks", "settings", "widgets"]:
            self.core_entries[config_name] = entry
        else:
            self.services_entries[config_name] = entry
    
    def browse_for_file(self, entry_widget, config_name):
        """Browse for a configuration file"""
        initial_dir = str(Path.home())
        if entry_widget.get():
            initial_dir = str(Path(entry_widget.get()).parent)
        
        filename = filedialog.askopenfilename(
            title=f"Select {config_name} configuration file",
            initialdir=initial_dir,
            filetypes=[
                ("YAML files", "*.yaml *.yml"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        
        if filename:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filename)
            self.test_config_path(config_name)
    
    def load_current_paths(self):
        """Load current configuration paths"""
        all_entries = {**self.core_entries, **self.services_entries}
        
        for config_name, entry in all_entries.items():
            current_path = config_manager.get_config_path(config_name)
            entry.delete(0, tk.END)
            entry.insert(0, current_path)
            self.test_config_path(config_name)
        
        # Load icon configuration
        if hasattr(self, 'icon_base_path_var'):
            self.icon_base_path_var.set(config_manager.get_icon_base_path())
        if hasattr(self, 'icon_output_path_var'):
            self.icon_output_path_var.set(config_manager.get_icon_output_path())
    
    def test_config_path(self, config_name):
        """Test a configuration path"""
        all_entries = {**self.core_entries, **self.services_entries}
        entry = all_entries[config_name]
        path = entry.get().strip()
        
        if not path:
            self.status_labels[config_name].config(text="No path set", foreground="orange")
            return
        
        # Validate path
        if not config_manager.validate_config_path(path):
            self.status_labels[config_name].config(text="Invalid path", foreground="red")
            return
        
        # Check privileges
        has_access, error_msg = config_manager.check_privileges(path)
        if has_access:
            exists = Path(path).exists()
            status_text = "OK" if exists else "File not found (will be created)"
            self.status_labels[config_name].config(text=status_text, foreground="green")
        else:
            self.status_labels[config_name].config(text=f"Access denied: {error_msg}", foreground="red")
    
    def test_all_paths(self):
        """Test all configuration paths"""
        self.status_var.set("Testing all paths...")
        
        def test_thread():
            all_entries = {**self.core_entries, **self.services_entries}
            for config_name in all_entries:
                self.after(0, lambda name=config_name: self.test_config_path(name))
            
            self.after(0, lambda: self.status_var.set("All paths tested"))
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def reset_config_path(self, config_name):
        """Reset a configuration path to default"""
        default_path = str(config_manager.app_dir / f"{config_name}.yaml")
        all_entries = {**self.core_entries, **self.services_entries}
        all_entries[config_name].delete(0, tk.END)
        all_entries[config_name].insert(0, default_path)
        self.test_config_path(config_name)
    
    def reset_to_defaults(self):
        """Reset all paths to defaults"""
        if messagebox.askyesno("Reset to Defaults", 
                              "Are you sure you want to reset all paths to defaults?"):
            all_entries = {**self.core_entries, **self.services_entries}
            for config_name in all_entries:
                self.reset_config_path(config_name)
    
    def save_paths(self):
        """Save all configuration paths"""
        # Handle folder selection first
        if hasattr(self, 'current_folder_var') and self.current_folder_var.get():
            new_folder = self.current_folder_var.get()
            if hasattr(self.parent, 'config_folder'):
                self.parent.config_folder = new_folder
                self.parent.title(f"Homepage Editor - Simple ({os.path.basename(new_folder)})")
        
        all_entries = {**self.core_entries, **self.services_entries}
        
        # Validate all paths first
        invalid_paths = []
        for config_name, entry in all_entries.items():
            path = entry.get().strip()
            if path and not config_manager.validate_config_path(path):
                invalid_paths.append(config_name)
        
        if invalid_paths:
            messagebox.showerror("Invalid Paths", 
                               f"Please fix the following invalid paths:\n{', '.join(invalid_paths)}")
            return
        
        # Save all paths
        for config_name, entry in all_entries.items():
            path = entry.get().strip()
            if path:
                config_manager.set_config_path(config_name, path)
        
        # Save icon configuration
        if hasattr(self, 'icon_base_path_var'):
            base_path = self.icon_base_path_var.get().strip()
            if base_path:
                config_manager.set_icon_base_path(base_path)
        
        if hasattr(self, 'icon_output_path_var'):
            output_path = self.icon_output_path_var.get().strip()
            if output_path:
                config_manager.set_icon_output_path(output_path)
        
        # Reload data in parent GUI to reflect new config paths
        if hasattr(self.parent, 'reload_data'):
            # Force immediate reload
            self.parent.reload_data()
            # Also force update of the parent window
            self.parent.update_idletasks()
            self.parent.update()
        
        messagebox.showinfo("Success", "Configuration paths saved successfully!")
        self.destroy()
    
    def test_privilege_elevation(self):
        """Test privilege elevation functionality"""
        self.status_var.set("Testing privilege elevation...")
        
        def test_thread():
            # Test with a temporary file
            test_path = str(config_manager.app_dir / "test_privilege.tmp")
            
            try:
                # Create test file
                with open(test_path, 'w') as f:
                    f.write("test")
                
                # Try to elevate privileges
                success = config_manager.elevate_privileges(test_path)
                
                if success:
                    self.after(0, lambda: messagebox.showinfo("Success", 
                        "Privilege elevation test successful!"))
                else:
                    self.after(0, lambda: messagebox.showwarning("Warning", 
                        "Privilege elevation test failed. You may need to run with sudo."))
                
                # Clean up
                Path(test_path).unlink(missing_ok=True)
                
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"Test failed: {e}"))
            
            self.after(0, lambda: self.status_var.set("Ready"))
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def validate_all_configs(self):
        """Validate all configurations"""
        self.validation_text.delete(1.0, tk.END)
        self.validation_text.insert(tk.END, "Validating configurations...\n")
        
        def validate_thread():
            try:
                is_valid, errors = config_manager.validate_all_configs()
                
                self.after(0, lambda: self.validation_text.delete(1.0, tk.END))
                
                if is_valid:
                    self.after(0, lambda: self.validation_text.insert(tk.END, 
                        "✅ All configurations are valid!\n"))
                else:
                    self.after(0, lambda: self.validation_text.insert(tk.END, 
                        "❌ Configuration validation failed:\n\n"))
                    for error in errors:
                        self.after(0, lambda e=error: self.validation_text.insert(tk.END, f"• {e}\n"))
                
            except Exception as e:
                self.after(0, lambda: self.validation_text.insert(tk.END, f"Error: {e}\n"))
        
        threading.Thread(target=validate_thread, daemon=True).start()

class BackupRestoreWindow(tk.Toplevel):
    """Window for managing configuration backups"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.transient(parent)
        self.title("Backup & Restore")
        self.geometry("600x500")
        self.parent = parent
        
        self.create_widgets()
        self.load_backups()
    
    def create_widgets(self):
        """Create the UI widgets"""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Configuration Backup & Restore", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Backup list
        list_frame = ttk.LabelFrame(main_frame, text="Available Backups", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Treeview for backups
        columns = ("Config", "Backup File", "Date", "Size")
        self.backup_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.backup_tree.heading(col, text=col)
            self.backup_tree.column(col, width=120)
        
        # Scrollbar for treeview
        tree_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.backup_tree.yview)
        self.backup_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.backup_tree.pack(side="left", fill="both", expand=True)
        tree_scrollbar.pack(side="right", fill="y")
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Refresh", 
                  command=self.load_backups).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Create Backup", 
                  command=self.create_backup).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Restore Selected", 
                  command=self.restore_selected).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Delete Selected", 
                  command=self.delete_selected).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Close", 
                  command=self.destroy).pack(side=tk.RIGHT)
    
    def load_backups(self):
        """Load available backups"""
        # Clear existing items
        for item in self.backup_tree.get_children():
            self.backup_tree.delete(item)
        
        # Load backups for each config
        for config_name in config_manager.config_files.keys():
            backups = config_manager.list_backups(config_name)
            for backup_path in backups:
                backup_file = Path(backup_path)
                size = backup_file.stat().st_size
                date = backup_file.stat().st_mtime
                
                self.backup_tree.insert("", "end", values=(
                    config_name,
                    backup_file.name,
                    str(Path(backup_path).stat().st_mtime),
                    f"{size} bytes"
                ))
    
    def create_backup(self):
        """Create a backup of current configurations"""
        # This would need to be implemented based on current config state
        messagebox.showinfo("Info", "Backup creation would be implemented here")
    
    def restore_selected(self):
        """Restore selected backup"""
        selection = self.backup_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a backup to restore")
            return
        
        item = self.backup_tree.item(selection[0])
        config_name = item['values'][0]
        backup_file = item['values'][1]
        backup_path = config_manager.backup_dir / backup_file
        
        if messagebox.askyesno("Confirm Restore", 
                              f"Are you sure you want to restore {config_name} from {backup_file}?"):
            if config_manager.restore_backup(config_name, str(backup_path)):
                messagebox.showinfo("Success", "Backup restored successfully!")
                self.load_backups()
            else:
                messagebox.showerror("Error", "Failed to restore backup")
    
    def delete_selected(self):
        """Delete selected backup"""
        selection = self.backup_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a backup to delete")
            return
        
        item = self.backup_tree.item(selection[0])
        backup_file = item['values'][1]
        backup_path = config_manager.backup_dir / backup_file
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete {backup_file}?"):
            try:
                backup_path.unlink()
                messagebox.showinfo("Success", "Backup deleted successfully!")
                self.load_backups()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete backup: {e}")