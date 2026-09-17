import tkinter as tk
from tkinter import ttk
import pystray
from PIL import Image, ImageTk
import threading
import os
from semantic_search import semantic_search
import datetime

class MemoryApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI Memory Assistant")
        self.root.geometry("600x700")
        
        # Hide the window initially (it waits in the system tray!)
        self.root.withdraw()
        
        # Make the popup stay on top of other windows
        self.root.attributes('-topmost', True)
        
        # Set the window icon
        if os.path.exists("icon.jpg"):
            icon_img = Image.open("icon.jpg")
            icon_photo = ImageTk.PhotoImage(icon_img)
            self.root.iconphoto(False, icon_photo)
        
        # --- UI Elements ---
        # Search Bar
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.root, textvariable=self.search_var, font=('Arial', 14))
        self.search_entry.pack(pady=20, padx=20, fill='x')
        self.search_entry.bind('<Return>', self.perform_search)
        
        # Info Text (Time, App, Title)
        self.info_label = ttk.Label(self.root, text="Type a search and press Enter", font=('Arial', 12), justify="center")
        self.info_label.pack(pady=5)
        
        # The Screenshot Image (Clickable!)
        self.image_label = ttk.Label(self.root, cursor="hand2")
        self.image_label.pack(pady=10)
        self.image_label.bind("<Button-1>", self.open_full_image)
        
        self.hint_label = ttk.Label(self.root, text="(Click image to view full screen)", font=('Arial', 9, 'italic'), foreground="gray")
        self.hint_label.pack()
        
        # --- NEW: Navigation Buttons ---
        self.nav_frame = ttk.Frame(self.root)
        self.nav_frame.pack(pady=5)
        
        self.prev_btn = ttk.Button(self.nav_frame, text="< Previous", command=self.show_prev, state=tk.DISABLED)
        self.prev_btn.pack(side=tk.LEFT, padx=10)
        
        self.match_label = ttk.Label(self.nav_frame, text="", font=('Arial', 10))
        self.match_label.pack(side=tk.LEFT, padx=10)
        
        self.next_btn = ttk.Button(self.nav_frame, text="Next >", command=self.show_next, state=tk.DISABLED)
        self.next_btn.pack(side=tk.LEFT, padx=10)
        
        # Store current results
        self.current_results = []
        self.current_index = 0
        self.current_filepath = None
        
        # Handle close button (X) to minimize to tray instead of quitting
        self.root.protocol('WM_DELETE_WINDOW', self.hide_window)
        
    def open_full_image(self, event):
        if self.current_filepath and os.path.exists(self.current_filepath):
            # Opens the image in the default Windows Photo Viewer!
            os.startfile(self.current_filepath)
        
    def perform_search(self, event=None):
        query = self.search_var.get()
        if not query.strip():
            return
            
        self.info_label.config(text="Searching (Loading AI)...")
        self.root.update()
        
        # Call our flawless semantic search backend (Get top 5 now!)
        self.current_results = semantic_search(query, top_k=5, silent=True)
        self.current_index = 0
        
        if not self.current_results:
            self.info_label.config(text="No memories found for that search.")
            self.image_label.config(image='')
            self.match_label.config(text="")
            self.prev_btn.config(state=tk.DISABLED)
            self.next_btn.config(state=tk.DISABLED)
            return
            
        self.display_current_result()
        
    def display_current_result(self):
        # Update buttons
        self.prev_btn.config(state=tk.NORMAL if self.current_index > 0 else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if self.current_index < len(self.current_results) - 1 else tk.DISABLED)
        self.match_label.config(text=f"Match {self.current_index + 1} of {len(self.current_results)}")
        
        # Get the current result
        score, timestamp, app, title, filepath, _ = self.current_results[self.current_index]
        self.current_filepath = filepath
        
        time_str = datetime.datetime.fromtimestamp(timestamp).strftime('%I:%M %p')
        self.info_label.config(text=f"🕒 {time_str} | 📱 {app}\n{title[:60]}")
        
        if os.path.exists(filepath):
            img = Image.open(filepath)
            img.thumbnail((550, 450), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.image_label.config(image=photo)
            self.image_label.image = photo 
            
    def show_prev(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.display_current_result()
            
    def show_next(self):
        if self.current_index < len(self.current_results) - 1:
            self.current_index += 1
            self.display_current_result()
            
    def hide_window(self):
        self.root.withdraw()
        
    def show_window(self):
        self.root.deiconify()
        self.root.lift()
        self.search_entry.focus()

def setup_tray(app):
    # Load our beautiful AI logo!
    if os.path.exists("icon.jpg"):
        icon_image = Image.open("icon.jpg")
    else:
        icon_image = Image.new('RGB', (64, 64), color=(0, 122, 204))
    
    def on_open(icon, item):
        # When user clicks the tray icon, show the popup window!
        app.root.after(0, app.show_window)
        
    def on_exit(icon, item):
        icon.stop()
        app.root.after(0, app.root.destroy)
        
    menu = pystray.Menu(
        pystray.MenuItem('Open Search', on_open, default=True),
        pystray.MenuItem('Exit', on_exit)
    )
    
    icon = pystray.Icon("MemoryAssistant", icon_image, "Memory Assistant", menu)
    icon.run()

def run_ui():
    app = MemoryApp()
    
    # Run the system tray icon in a background thread
    tray_thread = threading.Thread(target=setup_tray, args=(app,), daemon=True)
    tray_thread.start()
    
    # Run the native Windows GUI loop
    app.root.mainloop()

if __name__ == "__main__":
    print("Starting Native AI Desktop App...")
    print("Look for the blue square icon in your Windows Taskbar (System Tray)!")
    print("You can double click the icon to open the popup.")
    run_ui()
