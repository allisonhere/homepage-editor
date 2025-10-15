#!/usr/bin/env python

import tkinter as tk
from tkinter import ttk, messagebox
import yaml
from ttkthemes import ThemedTk
from PIL import Image, ImageTk
from icon_search import IconSearchWindow
from config_manager import config_manager
from config_ui import ConfigPathWindow, BackupRestoreWindow

# --- Data Persistence Functions (using config_manager) ---

def get_settings():
    """Reads and returns the entire settings structure."""
    return config_manager.read_config("settings")

def save_settings(data):
    """Saves the entire settings structure."""
    return config_manager.write_config("settings", data)

def get_bookmarks():
    """Reads and returns the entire bookmarks structure."""
    return config_manager.read_config("bookmarks")

def save_bookmarks(data):
    """Saves the entire bookmarks structure."""
    return config_manager.write_config("bookmarks", data)

def get_categories():
    """Returns a list of all category names."""
    bookmarks = get_bookmarks()
    return [list(item.keys())[0] for item in bookmarks]

def get_bookmarks_for_category(category_name):
    """Returns a list of bookmark names for a given category."""
    bookmarks = get_bookmarks()
    for item in bookmarks:
        if category_name in item:
            # Ensure item[category_name] is a list
            if isinstance(item[category_name], list):
                return [list(bookmark.keys())[0] for bookmark in item[category_name]]
    return []

def add_bookmark(category, name, abbr, href, icon):
    """Adds a new bookmark."""
    bookmarks = get_bookmarks()
    new_bookmark_data = {"abbr": abbr, "href": href, "icon": icon}
    new_bookmark = {name: [new_bookmark_data]}

    # Find the category and add the new bookmark
    category_found = False
    for item in bookmarks:
        if category in item:
            if isinstance(item[category], list):
                item[category].append(new_bookmark)
            else: # If category exists but has no bookmarks yet
                item[category] = [new_bookmark]
            category_found = True
            break

    # If category doesn't exist, create it
    if not category_found:
        bookmarks.append({category: [new_bookmark]})

    save_bookmarks(bookmarks)

def delete_bookmark(category_name, bookmark_name):
    """Deletes a bookmark from a specific category."""
    bookmarks = get_bookmarks()
    for item in bookmarks:
        if category_name in item and isinstance(item[category_name], list):
            # Filter out the bookmark to be deleted
            item[category_name] = [bm for bm in item[category_name] if bookmark_name not in bm]
            break
    save_bookmarks(bookmarks)

def delete_category(category_name):
    """Deletes a category from bookmarks.yaml and settings.yaml."""
    bookmarks = get_bookmarks()
    bookmarks = [item for item in bookmarks if category_name not in item]
    save_bookmarks(bookmarks)

    settings = get_settings()
    if "layout" in settings:
        settings["layout"] = [item for item in settings["layout"] if category_name not in item]
        save_settings(settings)

# --- GUI Application ---

class HomepageGUI(ThemedTk):
    def __init__(self):
        super().__init__()
        self.set_theme("arc")

        self.title("Homepage Manager")
        self.geometry("800x600")

        # Load icons
        self.add_icon = ImageTk.PhotoImage(Image.open("add.png"))
        self.edit_icon = ImageTk.PhotoImage(Image.open("edit.png"))
        self.delete_icon = ImageTk.PhotoImage(Image.open("delete.png"))

        self.create_widgets()
        self.create_menu_bar()
        self.populate_categories()

    def create_widgets(self):
        # Main frame with two panes
        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left pane for categories
        category_frame = ttk.LabelFrame(main_pane, text="Categories")
        main_pane.add(category_frame, weight=1)

        category_button_frame = ttk.Frame(category_frame)
        category_button_frame.pack(fill=tk.X, padx=5, pady=5)

        add_cat_button = ttk.Button(category_button_frame, image=self.add_icon, command=self.add_category_window)
        add_cat_button.pack(side=tk.LEFT)

        edit_cat_button = ttk.Button(category_button_frame, image=self.edit_icon, command=self.edit_category_window)
        edit_cat_button.pack(side=tk.LEFT, padx=5)

        delete_cat_button = ttk.Button(category_button_frame, image=self.delete_icon, command=self.delete_selected_category)
        delete_cat_button.pack(side=tk.LEFT)

        self.categories_listbox = tk.Listbox(category_frame, exportselection=False)
        self.categories_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.categories_listbox.bind("<<ListboxSelect>>", self.on_category_select)

        # Right pane for bookmarks
        bookmark_frame = ttk.LabelFrame(main_pane, text="Bookmarks")
        main_pane.add(bookmark_frame, weight=3)

        self.bookmarks_listbox = tk.Listbox(bookmark_frame)
        self.bookmarks_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Button frame
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        add_button = ttk.Button(button_frame, text="Add Bookmark", image=self.add_icon, compound="left", command=self.add_bookmark_window)
        add_button.pack(side=tk.LEFT, padx=(0, 5))

        edit_button = ttk.Button(button_frame, text="Edit Bookmark", image=self.edit_icon, compound="left", command=self.edit_selected_bookmark)
        edit_button.pack(side=tk.LEFT, padx=5)

        delete_button = ttk.Button(button_frame, text="Delete Bookmark", image=self.delete_icon, compound="left", command=self.delete_selected_bookmark)
        delete_button.pack(side=tk.LEFT)

    def populate_categories(self):
        self.categories_listbox.delete(0, tk.END)
        for category in get_categories():
            self.categories_listbox.insert(tk.END, category)
        # Select the first category by default
        if self.categories_listbox.size() > 0:
            self.categories_listbox.select_set(0)
            self.categories_listbox.event_generate("<<ListboxSelect>>")

    def on_category_select(self, event):
        widget = event.widget if hasattr(event, 'widget') else self.categories_listbox
        selection = widget.curselection()
        if selection:
            index = selection[0]
            category = widget.get(index)
            self.populate_bookmarks(category)

    def populate_bookmarks(self, category):
        self.bookmarks_listbox.delete(0, tk.END)
        for bookmark in get_bookmarks_for_category(category):
            self.bookmarks_listbox.insert(tk.END, bookmark)

    def add_bookmark_window(self):
        selected_cat_indices = self.categories_listbox.curselection()
        default_category = ""
        if selected_cat_indices:
            default_category = self.categories_listbox.get(selected_cat_indices[0])

        AddBookmarkWindow(self, default_category, self.refresh_data)

    def add_category_window(self):
        AddCategoryWindow(self, self.refresh_data)

    def edit_category_window(self):
        cat_selection = self.categories_listbox.curselection()
        if not cat_selection:
            messagebox.showerror("Error", "Please select a category to edit.")
            return
        category_name = self.categories_listbox.get(cat_selection[0])
        EditCategoryWindow(self, category_name, self.refresh_data)

    def delete_selected_category(self):
        cat_selection = self.categories_listbox.curselection()
        if not cat_selection:
            messagebox.showerror("Error", "Please select a category to delete.")
            return

        category_name = self.categories_listbox.get(cat_selection[0])

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the category '{category_name}' and all its bookmarks?"):
            delete_category(category_name)
            self.refresh_data()
            messagebox.showinfo("Success", "Category deleted successfully!")

    def edit_selected_bookmark(self):
        cat_selection = self.categories_listbox.curselection()
        bm_selection = self.bookmarks_listbox.curselection()

        if not cat_selection or not bm_selection:
            messagebox.showerror("Error", "Please select a category and a bookmark to edit.")
            return

        category_name = self.categories_listbox.get(cat_selection[0])
        bookmark_name = self.bookmarks_listbox.get(bm_selection[0])

        bookmarks = get_bookmarks()
        for item in bookmarks:
            if category_name in item and isinstance(item[category_name], list):
                for bookmark in item[category_name]:
                    if bookmark_name in bookmark:
                        bookmark_data = bookmark[bookmark_name][0]
                        EditBookmarkWindow(self, category_name, bookmark_name, bookmark_data, self.refresh_data)
                        return

    def delete_selected_bookmark(self):
        cat_selection = self.categories_listbox.curselection()
        bm_selection = self.bookmarks_listbox.curselection()

        if not cat_selection or not bm_selection:
            messagebox.showerror("Error", "Please select a category and a bookmark to delete.")
            return

        category_name = self.categories_listbox.get(cat_selection[0])
        bookmark_name = self.bookmarks_listbox.get(bm_selection[0])

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the bookmark '{bookmark_name}' from category '{category_name}'?"):
            delete_bookmark(category_name, bookmark_name)
            self.refresh_data()
            messagebox.showinfo("Success", "Bookmark deleted successfully!")


    def refresh_data(self):
        current_selection = self.categories_listbox.curselection()
        self.populate_categories()
        if current_selection:
            self.categories_listbox.select_set(current_selection[0])
            self.on_category_select(tk.Event()) # Simulate event

    def create_menu_bar(self):
        """Create the application menu bar"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Backup & Restore...", command=self.open_backup_restore)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Configuration...", command=self.open_configuration)
        tools_menu.add_separator()
        tools_menu.add_command(label="Validate Configurations", command=self.validate_configurations)
        tools_menu.add_command(label="Test All Paths", command=self.test_all_paths)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def open_configuration(self):
        """Open unified configuration window"""
        ConfigPathWindow(self)

    def open_backup_restore(self):
        """Open backup and restore window"""
        BackupRestoreWindow(self)

    def validate_configurations(self):
        """Validate all configurations"""
        is_valid, errors = config_manager.validate_all_configs()
        
        if is_valid:
            messagebox.showinfo("Validation", "All configurations are valid!")
        else:
            error_text = "Configuration validation failed:\n\n" + "\n".join(f"• {error}" for error in errors)
            messagebox.showerror("Validation Failed", error_text)

    def test_all_paths(self):
        """Test all configuration paths"""
        status = config_manager.get_config_status()
        
        results = []
        for config_name, info in status.items():
            if info['required']:
                status_icon = "✅" if info['accessible'] else "❌"
                results.append(f"{status_icon} {config_name}: {info['path']}")
                if not info['accessible'] and info['error']:
                    results.append(f"   Error: {info['error']}")
        
        result_text = "Configuration Path Status:\n\n" + "\n".join(results)
        messagebox.showinfo("Path Test Results", result_text)

    def show_about(self):
        """Show about dialog"""
        about_text = """Homepage Editor v2.0
        
Enhanced configuration management with:
• External configuration file support
• Privilege elevation for protected files
• Automatic backup and restore
• Configuration validation
• Advanced icon search

For more information, visit the project repository."""
        messagebox.showinfo("About Homepage Editor", about_text)

class AddCategoryWindow(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.transient(parent)
        self.title("Add New Category")
        self.parent = parent
        self.callback = callback

        form_frame = ttk.Frame(self, padding="10")
        form_frame.pack(fill=tk.BOTH, expand=True)

        label = ttk.Label(form_frame, text="Category Name:")
        label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.entry = ttk.Entry(form_frame, width=40)
        self.entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)

        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)

        add_btn = ttk.Button(button_frame, text="Add Category", command=self.add)
        add_btn.pack(side=tk.LEFT, padx=5)
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_btn.pack(side=tk.LEFT)

        self.grab_set()
        self.wait_window(self)

    def add(self):
        category_name = self.entry.get().strip()
        if not category_name:
            messagebox.showerror("Error", "Category name cannot be empty.", parent=self)
            return

        bookmarks = get_bookmarks()
        for item in bookmarks:
            if category_name in item:
                messagebox.showerror("Error", "Category already exists.", parent=self)
                return

        bookmarks.append({category_name: []})
        save_bookmarks(bookmarks)

        settings = get_settings()
        if "layout" not in settings:
            settings["layout"] = []
        settings["layout"].append({category_name: {"style": "row", "columns": 3}})
        save_settings(settings)

        self.callback()
        messagebox.showinfo("Success", "Category added successfully!", parent=self.parent)
        self.destroy()

class EditCategoryWindow(tk.Toplevel):
    def __init__(self, parent, old_name, callback):
        super().__init__(parent)
        self.transient(parent)
        self.title("Edit Category")
        self.parent = parent
        self.old_name = old_name
        self.callback = callback

        form_frame = ttk.Frame(self, padding="10")
        form_frame.pack(fill=tk.BOTH, expand=True)

        label = ttk.Label(form_frame, text="New Category Name:")
        label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.entry = ttk.Entry(form_frame, width=40)
        self.entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        self.entry.insert(0, old_name)

        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)

        save_btn = ttk.Button(button_frame, text="Save Changes", command=self.save)
        save_btn.pack(side=tk.LEFT, padx=5)
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_btn.pack(side=tk.LEFT)

        self.grab_set()
        self.wait_window(self)

    def save(self):
        new_name = self.entry.get().strip()
        if not new_name:
            messagebox.showerror("Error", "Category name cannot be empty.", parent=self)
            return

        bookmarks = get_bookmarks()
        for item in bookmarks:
            if self.old_name in item:
                item[new_name] = item.pop(self.old_name)
                break
        save_bookmarks(bookmarks)

        settings = get_settings()
        if "layout" in settings:
            for item in settings["layout"]:
                if self.old_name in item:
                    item[new_name] = item.pop(self.old_name)
                    break
            save_settings(settings)

        self.callback()
        messagebox.showinfo("Success", "Category updated successfully!", parent=self.parent)
        self.destroy()

class EditBookmarkWindow(tk.Toplevel):
    def __init__(self, parent, category_name, bookmark_name, bookmark_data, callback):
        super().__init__(parent)
        self.transient(parent)
        self.title("Edit Bookmark")
        self.parent = parent
        self.category_name = category_name
        self.original_bookmark_name = bookmark_name
        self.callback = callback

        self.entries = {}
        fields = ["Name", "Abbreviation", "URL", "Icon"]
        
        form_frame = ttk.Frame(self, padding="10")
        form_frame.pack(fill=tk.BOTH, expand=True)

        for i, field in enumerate(fields):
            label = ttk.Label(form_frame, text=f"{field}:")
            label.grid(row=i, column=0, sticky=tk.W, padx=5, pady=5)
            entry = ttk.Entry(form_frame, width=40)
            entry.grid(row=i, column=1, sticky=tk.EW, padx=5, pady=5)
            self.entries[field] = entry

        icon_search_button = ttk.Button(form_frame, text="Search", command=self.open_icon_search)
        icon_search_button.grid(row=3, column=2, padx=5)

        self.entries["Name"].insert(0, bookmark_name)
        self.entries["Abbreviation"].insert(0, bookmark_data.get("abbr", ""))
        self.entries["URL"].insert(0, bookmark_data.get("href", ""))
        self.entries["Icon"].insert(0, bookmark_data.get("icon", ""))

        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)

        save_btn = ttk.Button(button_frame, text="Save Changes", command=self.save)
        save_btn.pack(side=tk.LEFT, padx=5)
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_btn.pack(side=tk.LEFT)

        self.grab_set()
        self.wait_window(self)

    def open_icon_search(self):
        initial_query = self.entries["Icon"].get()
        IconSearchWindow(self, initial_query)

    def save(self):
        new_values = {f: e.get().strip() for f, e in self.entries.items()}
        if not all(new_values.values()):
            messagebox.showerror("Error", "All fields are required.", parent=self)
            return

        bookmarks = get_bookmarks()
        for item in bookmarks:
            if self.category_name in item and isinstance(item[self.category_name], list):
                for i, bookmark in enumerate(item[self.category_name]):
                    if self.original_bookmark_name in bookmark:
                        # Update the bookmark in place
                        updated_bookmark_data = {
                            "abbr": new_values["Abbreviation"],
                            "href": new_values["URL"],
                            "icon": new_values["Icon"]
                        }
                        item[self.category_name][i] = {new_values["Name"]: [updated_bookmark_data]}
                        break
                break
        
        save_bookmarks(bookmarks)
        self.callback()
        messagebox.showinfo("Success", "Bookmark updated successfully!", parent=self.parent)
        self.destroy()

class AddBookmarkWindow(tk.Toplevel):
    def __init__(self, parent, default_category, callback):
        super().__init__(parent)
        self.transient(parent)
        self.title("Add New Bookmark")
        self.parent = parent
        self.callback = callback

        # Form entries
        self.entries = {}
        fields = ["Category", "Name", "Abbreviation", "URL", "Icon"]
        
        form_frame = ttk.Frame(self, padding="10")
        form_frame.pack(fill=tk.BOTH, expand=True)

        for i, field in enumerate(fields):
            label = ttk.Label(form_frame, text=f"{field}:")
            label.grid(row=i, column=0, sticky=tk.W, padx=5, pady=5)
            entry = ttk.Entry(form_frame, width=40)
            entry.grid(row=i, column=1, sticky=tk.EW, padx=5, pady=5)
            self.entries[field] = entry

        icon_search_button = ttk.Button(form_frame, text="Search", command=self.open_icon_search)
        icon_search_button.grid(row=4, column=2, padx=5)

        self.entries["Category"].insert(0, default_category)

        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)

        add_btn = ttk.Button(button_frame, text="Add Bookmark", command=self.add)
        add_btn.pack(side=tk.LEFT, padx=5)
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_btn.pack(side=tk.LEFT)

        self.grab_set() # Modal window
        self.wait_window(self)

    def open_icon_search(self):
        initial_query = self.entries["Icon"].get()
        IconSearchWindow(self, initial_query)

    def add(self):
        values = {f: e.get().strip() for f, e in self.entries.items()}
        if not all(values.values()):
            messagebox.showerror("Error", "All fields are required.", parent=self)
            return

        add_bookmark(values["Category"], values["Name"], values["Abbreviation"], values["URL"], values["Icon"])
        self.callback() # Refresh parent listboxes
        messagebox.showinfo("Success", "Bookmark added successfully!", parent=self.parent)
        self.destroy()

if __name__ == "__main__":
    # Check for dependencies and provide guidance
    try:
        import yaml
    except ImportError:
        print("PyYAML is not installed. Please install it using: pip install pyyaml")
        exit()

    app = HomepageGUI()
    app.mainloop()