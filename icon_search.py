import os
import shutil
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import io
import threading
import time
from collections import defaultdict
import re
from config_manager import config_manager
from icon_manager import IconManager

# Try to import cairosvg for SVG support, fallback to PNG if not available
try:
    import cairosvg
    SVG_SUPPORT = True
except ImportError:
    SVG_SUPPORT = False
    print("Warning: cairosvg not installed. SVG icons will fallback to PNG versions.")

class IconSearchWindow(tk.Toplevel):
    def __init__(self, parent, initial_query=""):
        super().__init__(parent)
        self.transient(parent)
        self.title("Icon Search - Enhanced")
        self.parent = parent
        self.geometry("900x700")
        
        # Performance optimization variables
        self.icon_cache = {}  # Cache for loaded images
        self.icon_names = []
        self.filtered_icons = []
        self.current_page = 0
        self.icons_per_page = 50
        self.search_debounce_timer = None
        self.loading = False
        
        # UI state
        self.selected_icon = None
        self.preview_size = (64, 64)
        self.grid_size = (8, 6)  # 8 columns, 6 rows = 48 icons per page
        
        self.create_widgets()
        self.search_entry.insert(0, initial_query)
        self.load_icon_index_async()
        
    def create_widgets(self):
        # Main container with padding
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Search frame with improved layout
        search_frame = ttk.LabelFrame(main_frame, text="Search Icons", padding="10")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Search entry with placeholder-like behavior
        search_container = ttk.Frame(search_frame)
        search_container.pack(fill=tk.X)
        
        self.search_entry = ttk.Entry(search_container, width=50, font=("Arial", 11))
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.on_search_change)
        self.search_entry.bind("<Return>", self.on_search_enter)
        
        # Search info label
        self.search_info = ttk.Label(search_container, text="", foreground="gray")
        self.search_info.pack(side=tk.RIGHT)
        
        # Results frame with scrollable area
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas and scrollbar for scrolling
        canvas_frame = ttk.Frame(results_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg="white")
        self.scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        
        # Preview and control frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Preview frame
        preview_frame = ttk.LabelFrame(control_frame, text="Preview", padding="5")
        preview_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        self.preview_label = ttk.Label(preview_frame, text="Select an icon to preview")
        self.preview_label.pack()
        
        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.select_button = ttk.Button(button_frame, text="Select Icon", 
                                      command=self.select_current_icon, state="disabled")
        self.select_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        self.cancel_button = ttk.Button(button_frame, text="Cancel", 
                                      command=self.destroy)
        self.cancel_button.pack(side=tk.RIGHT)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Loading icons...")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, pady=(10, 0))

    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling on the canvas"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def load_icon_index_async(self):
        """Load icon index in a separate thread to avoid blocking UI"""
        def load_icons():
            try:
                # Try to load from icon_index.txt first, then scan directory if not found
                icon_index_path = "icon_index.txt"
                if os.path.exists(icon_index_path):
                    with open(icon_index_path, "r") as f:
                        self.icon_names = [line.strip() for line in f if line.strip()]
                else:
                    # If no index file, scan the icon directory directly
                    icon_dir = config_manager.get_icon_base_path()
                    if os.path.exists(icon_dir):
                        self.icon_names = [f for f in os.listdir(icon_dir) if f.endswith('.svg')]
                    else:
                        self.icon_names = []
                
                # Sort icons alphabetically for better organization
                self.icon_names.sort()
                
                # Update UI in main thread
                self.after(0, self.on_icons_loaded)
            except FileNotFoundError:
                self.after(0, lambda: messagebox.showerror("Error", "Icon index file not found and icon directory is not accessible!"))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"Failed to load icons: {e}"))
        
        threading.Thread(target=load_icons, daemon=True).start()

    def on_icons_loaded(self):
        """Called when icon index is loaded"""
        self.status_var.set(f"Loaded {len(self.icon_names)} icons")
        
        # If there's an initial query, perform search automatically
        initial_query = self.search_entry.get().strip()
        if initial_query:
            self.perform_search()
        else:
            # Show all icons if no initial query
            self.filtered_icons = self.icon_names.copy()
            self.current_page = 0
            self.display_icons_page()

    def on_search_change(self, event):
        """Handle search input changes with debouncing"""
        if self.search_debounce_timer:
            self.after_cancel(self.search_debounce_timer)
        
        # Debounce search by 300ms
        self.search_debounce_timer = self.after(300, self.perform_search)

    def on_search_enter(self, event):
        """Handle Enter key in search box"""
        if self.search_debounce_timer:
            self.after_cancel(self.search_debounce_timer)
        self.perform_search()

    def perform_search(self):
        """Perform the actual search operation"""
        query = self.search_entry.get().strip().lower()
        
        if not query:
            self.filtered_icons = self.icon_names.copy()
        else:
            # Improved search with multiple strategies
            self.filtered_icons = self.advanced_search(query)
        
        self.current_page = 0
        self.display_icons_page()

    def advanced_search(self, query):
        """Advanced search with multiple matching strategies"""
        results = []
        query_words = query.split()
        
        for icon_name in self.icon_names:
            name_lower = icon_name.lower()
            score = 0
            
            # Exact match gets highest priority
            if query in name_lower:
                score += 100
            
            # Word boundary matches
            for word in query_words:
                if re.search(r'\b' + re.escape(word), name_lower):
                    score += 50
                elif word in name_lower:
                    score += 25
            
            # Prefix matches
            if name_lower.startswith(query):
                score += 75
            
            if score > 0:
                results.append((score, icon_name))
        
        # Sort by score (highest first) then alphabetically
        results.sort(key=lambda x: (-x[0], x[1]))
        return [name for _, name in results]

    def display_icons_page(self):
        """Display current page of icons with lazy loading"""
        if self.loading:
            return
            
        self.loading = True
        self.status_var.set(f"Loading page {self.current_page + 1}...")
        
        # Clear current display
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Calculate page range
        start_idx = self.current_page * self.icons_per_page
        end_idx = min(start_idx + self.icons_per_page, len(self.filtered_icons))
        page_icons = self.filtered_icons[start_idx:end_idx]
        
        if not page_icons:
            no_results_label = ttk.Label(self.scrollable_frame, 
                                       text="No icons found matching your search",
                                       font=("Arial", 12), foreground="gray")
            no_results_label.pack(pady=50)
            self.loading = False
            return
        
        # Create grid layout
        for i, icon_name in enumerate(page_icons):
            row = i // self.grid_size[0]
            col = i % self.grid_size[0]
            
            self.create_icon_button(icon_name, row, col)
        
        # Update search info
        total_pages = (len(self.filtered_icons) + self.icons_per_page - 1) // self.icons_per_page
        self.search_info.config(text=f"Page {self.current_page + 1} of {total_pages} ({len(self.filtered_icons)} total)")
        
        self.loading = False
        self.status_var.set(f"Showing {len(page_icons)} icons")

    def create_icon_button(self, icon_name, row, col):
        """Create an icon button with improved styling"""
        try:
            icon_path = os.path.join(config_manager.get_icon_base_path(), icon_name)
            
            # Load icon with caching
            if icon_path not in self.icon_cache:
                img = self.load_icon_as_image(icon_path, (48, 48))
                if img:
                    self.icon_cache[icon_path] = ImageTk.PhotoImage(img)
                else:
                    return
            
            photo = self.icon_cache[icon_path]
            
            # Create button with better styling
            btn = tk.Button(
                self.scrollable_frame,
                image=photo,
                command=lambda: self.select_icon_preview(icon_name, icon_path),
                relief="flat",
                bd=1,
                bg="white",
                activebackground="#e0e0e0",
                width=60,
                height=60
            )
            
            # Add hover effects
            def on_enter(e):
                btn.config(relief="raised", bg="#f0f0f0")
            def on_leave(e):
                btn.config(relief="flat", bg="white")
            
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
            
            # Configure grid weights for proper resizing
            self.scrollable_frame.grid_rowconfigure(row, weight=1)
            self.scrollable_frame.grid_columnconfigure(col, weight=1)
            
        except Exception as e:
            print(f"Error creating icon button for {icon_name}: {e}")

    def load_icon_as_image(self, icon_path, size=(48, 48)):
        """Load an icon with improved error handling and caching"""
        try:
            if icon_path.endswith('.svg'):
                if SVG_SUPPORT:
                    # Convert SVG to PNG using cairosvg
                    png_data = cairosvg.svg2png(url=icon_path, output_width=size[0], output_height=size[1])
                    return Image.open(io.BytesIO(png_data))
                else:
                    # Fallback to PNG version if cairosvg not available
                    png_path = icon_path.replace('/svg/', '/png/').replace('.svg', '.png')
                    if os.path.exists(png_path):
                        return Image.open(png_path).resize(size, Image.Resampling.LANCZOS)
                    else:
                        return None
            else:
                # Handle PNG files
                return Image.open(icon_path).resize(size, Image.Resampling.LANCZOS)
        except Exception as e:
            print(f"Error loading image {icon_path}: {e}")
            return None

    def select_icon_preview(self, icon_name, icon_path):
        """Select an icon for preview"""
        self.selected_icon = (icon_name, icon_path)
        
        # Update preview
        try:
            img = self.load_icon_as_image(icon_path, self.preview_size)
            if img:
                photo = ImageTk.PhotoImage(img)
                self.preview_label.config(image=photo, text="")
                self.preview_label.image = photo  # Keep reference
            else:
                self.preview_label.config(image="", text="Preview not available")
        except Exception as e:
            self.preview_label.config(image="", text="Error loading preview")
        
        # Enable select button
        self.select_button.config(state="normal")

    def select_current_icon(self):
        """Select the currently previewed icon"""
        if not self.selected_icon:
            return
            
        icon_name, icon_path = self.selected_icon
        
        try:
            # Copy the icon to the configured output directory
            new_icon_path = os.path.join(config_manager.get_icon_output_path(), os.path.basename(icon_path))
            shutil.copy(icon_path, new_icon_path)
            
            # Update the icon field in the parent window with the correct path for Homepage
            icon_path_for_homepage = f"/images/icons/{os.path.basename(icon_path)}"
            self.update_parent_icon_field(icon_path_for_homepage)
            
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy icon: {e}")
    
    def update_parent_icon_field(self, icon_path):
        """Update the parent window's icon field with the icon path"""
        try:
            # icon_path should already be in the correct format for Homepage (e.g., /images/icons/iconname.svg)
            
            # Just set the icon_var - this is what BookmarkDialog uses
            if hasattr(self.parent, 'icon_var'):
                self.parent.icon_var.set(icon_path)
            else:
                # For main GUI, update the Icon entry field directly
                if hasattr(self.parent, 'entries') and 'Icon' in self.parent.entries:
                    self.parent.entries['Icon'].delete(0, tk.END)
                    self.parent.entries['Icon'].insert(0, icon_path)
                else:
                    # Fallback message
                    messagebox.showinfo("Icon Selected", f"Icon path: {icon_path}")
        except Exception as e:
            print(f"Error updating parent icon field: {e}")
            messagebox.showinfo("Icon Selected", f"Icon path: {icon_path}")

    def select_icon(self, icon_path):
        """Legacy method for backward compatibility"""
        try:
            # Copy the icon to the configured output directory
            new_icon_path = os.path.join(config_manager.get_icon_output_path(), os.path.basename(icon_path))
            shutil.copy(icon_path, new_icon_path)
            
            # Update the icon field in the parent window with the correct path for Homepage
            icon_path_for_homepage = f"/images/icons/{os.path.basename(icon_path)}"
            self.update_parent_icon_field(icon_path_for_homepage)
            
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy icon: {e}")
    
    def download_and_select_icon(self, icon_name):
        """Download icon from dashboard-icons and select it"""
        try:
            # Initialize icon manager
            icon_manager = IconManager()
            
            # Check if dashboard icons are available
            if not icon_manager.is_dashboard_icons_available():
                response = messagebox.askyesno(
                    "Download Required", 
                    "Dashboard icons not available. Would you like to download them now?\n\nThis will download ~200MB of icon data."
                )
                if response:
                    # Download dashboard icons
                    self.status_label.config(text="Downloading dashboard icons...")
                    self.update()
                    
                    if not icon_manager.download_dashboard_icons():
                        messagebox.showerror("Error", "Failed to download dashboard icons. Please check your internet connection.")
                        return
                    
                    self.status_label.config(text="Dashboard icons downloaded successfully!")
                else:
                    return
            
            # Download the specific icon to the icon manager's output directory first
            self.status_label.config(text=f"Downloading {icon_name}...")
            self.update()
            
            if icon_manager.download_icon(icon_name):
                # Now copy it to the configured icon output path for Homepage
                source_path = icon_manager.output_dir / f"{icon_name}.svg"
                dest_path = os.path.join(config_manager.get_icon_output_path(), f"{icon_name}.svg")
                
                # Ensure the destination directory exists
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                
                # Copy the icon to the configured path
                shutil.copy2(source_path, dest_path)
                
                # Update the parent with the correct path for Homepage
                icon_path = f"/images/icons/{icon_name}.svg"
                self.update_parent_icon_field(icon_path)
                self.status_label.config(text=f"✅ Downloaded and selected: {icon_name}")
                self.destroy()
            else:
                messagebox.showerror("Error", f"Failed to download icon: {icon_name}")
                self.status_label.config(text="Download failed")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download icon: {e}")
            self.status_label.config(text="Download failed")