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
from config_manager import config_manager

class ConfigPathWindow(tk.Toplevel):
    """Window for managing configuration file paths"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.transient(parent)
        self.title("Configuration Paths Manager")
        self.geometry("800x600")
        self.parent = parent
        
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
        
        # Core configs tab
        self.create_core_configs_tab()
        
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