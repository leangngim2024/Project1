import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from tkinter import filedialog, messagebox
# from ttkbootstrap import Style
import hashlib
from drawing import add_draw_tab
from PIL import Image, ImageTk

# Connect to the SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect("notes_app.db")
cursor = conn.cursor()

# Add this near the top of your file, after the database connection
# This will remove the user_files table if it exists
# try:
#     cursor.execute("DROP TABLE IF EXISTS user_files")
#     conn.commit()
#     print("Successfully removed user_files table")
# except sqlite3.Error as e:
#     print(f"Error removing table: {e}")

# Create tables if they don't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT NOT NULL)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS notes (
                    user TEXT,
                    title TEXT,
                    content TEXT,
                    FOREIGN KEY (user) REFERENCES users(username))''')



conn.commit()

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Save user to the database
def save_user(username, password):
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Username already exists.")

# Verify user login
def verify_user(username, password):
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    if row and row[0] == password:
        return True
    return False

# Save notes to the database
def save_note_to_db(user, title, content):
    cursor.execute("INSERT OR REPLACE INTO notes (user, title, content) VALUES (?, ?, ?)", (user, title, content))
    conn.commit()

# Load notes from the database for a specific user
def load_notes_from_db(user):
    cursor.execute("SELECT title, content FROM notes WHERE user = ?", (user,))
    return {title: content for title, content in cursor.fetchall()}

# Delete note from the database
def delete_note_from_db(user, title):
    cursor.execute("DELETE FROM notes WHERE user = ? AND title = ?", (user, title))
    conn.commit()

# Create the main application window
root = tk.Tk()
root.title("P.Note")
root.geometry("600x600")
# customtkinter.set_appearance_mode("Dark")
# style = Style(theme='journal') # 'darkly or journal'

# Global variables
logged_in_user = None
notes = {}


# Update the color scheme to smoother colors
color1 = '#F0E6FF'  # Light lavender
color2 = '#B8A2E3'  # Soft purple
color3 = '#2E1F47'  # Deep purple
color4 = '#4A4A4A'  # Soft black
color5 = '#6B4FA0'  # Medium purple

def startup_screen():
    # Clear the window
    for widget in root.winfo_children():
        widget.destroy()

    # Create startup screen UI with gradient effect
    startup_frame = tk.Frame(root, bg=color2, pady=40)
    startup_frame.pack(fill=tk.BOTH, expand=True)
    startup_frame.columnconfigure(0, weight=1)
    startup_frame.rowconfigure(0, weight=1)

    # App Logo/Title Section
    title_frame = tk.Frame(startup_frame, bg=color2)
    title_frame.pack(fill=tk.X, pady=(20, 30))

    welcome_label = tk.Label(
        title_frame,
        background=color2,
        foreground=color3,
        text="Welcome to P.Note",
        font=("Times New Roman", 36, "bold")
    )
    welcome_label.pack()

    subtitle_label = tk.Label(
        title_frame,
        background=color2,
        foreground=color4,
        text="Your Smart Digital Notebook Solution",
        font=("Helvetica", 14, "italic")
    )
    subtitle_label.pack(pady=(5, 0))

    # Main Features Section
    features_frame = tk.Frame(startup_frame, bg=color1, padx=30, pady=20)
    features_frame.pack(fill=tk.X, padx=50)

    features_title = tk.Label(
        features_frame,
        text="Discover the Power of Modern Note-Taking",
        background=color1,
        foreground=color3,
        font=("Helvetica", 16, "bold"),
        pady=10
    )
    features_title.pack()

    # Key Features with icons (you can add actual icons if desired)
    features_text = [
        "📝 Smart Notes - Create, edit, and organize your thoughts with rich text formatting",
        "🎨 Creative Canvas - Express your ideas through our intuitive drawing tools",
        "🖼️ Image Gallery - Upload and manage your visual content effortlessly",
        "🎯 Task Management - Keep track of your to-dos and deadlines",
        "🔒 Secure Storage - Your data is protected with advanced encryption",
        "📱 Modern Interface - Enjoy a clean, intuitive user experience"
    ]

    for feature in features_text:
        feature_label = tk.Label(
            features_frame,
            text=feature,
            background=color1,
            foreground=color4,
            font=("Helvetica", 12),
            anchor="w",
            pady=5
        )
        feature_label.pack(fill=tk.X)

    # Getting Started Section
    start_frame = tk.Frame(startup_frame, bg=color2, pady=20)
    start_frame.pack(fill=tk.X, padx=50)

    start_label = tk.Label(
        start_frame,
        text="Get Started Today",
        background=color2,
        foreground=color3,
        font=("Helvetica", 14, "bold")
    )
    start_label.pack(pady=(0, 10))

    # Modern styled buttons
    button_frame = tk.Frame(start_frame, bg=color2)
    button_frame.pack(pady=10)

    login_button = tk.Button(
        button_frame,
        text="Login",
        command=login_screen,
        font=("Arial", 14, "bold"),
        bg=color5,
        fg="white",
        activebackground=color3,
        activeforeground="white",
        relief="flat",
        cursor="hand2",
        width=15,
        height=2
    )
    login_button.pack(side=tk.LEFT, padx=10)

    signup_button = tk.Button(
        button_frame,
        text="Create Account",
        command=signup_screen,
        font=("Arial", 14, "bold"),
        bg=color1,
        fg=color3,
        activebackground=color2,
        activeforeground=color3,
        relief="flat",
        cursor="hand2",
        width=15,
        height=2
    )
    signup_button.pack(side=tk.LEFT, padx=10)

    # Footer with additional info
    footer_frame = tk.Frame(startup_frame, bg=color2)
    footer_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=20)

    security_note = tk.Label(
        footer_frame,
        text="🔐 Your privacy and security are our top priority",
        background=color2,
        foreground=color4,
        font=("Helvetica", 10)
    )
    security_note.pack()

    version_label = tk.Label(
        footer_frame,
        text="Version 1.0",
        background=color2,
        foreground=color4,
        font=("Helvetica", 8)
    )
    version_label.pack(pady=(5, 0))

def login_screen():
    for widget in root.winfo_children():
        widget.destroy()

    # Modern login UI with better layout and styling
    login_frame = tk.Frame(root, bg=color2)
    login_frame.pack(fill=tk.BOTH, expand=True)

    # Header
    header_frame = tk.Frame(login_frame, bg=color2)
    header_frame.pack(fill=tk.X, pady=(50, 30))
    
    tk.Label(header_frame, 
            text="Welcome Back", 
            font=("Helvetica", 24, "bold"),
            bg=color2,
            fg=color3).pack()

    tk.Label(header_frame,
            text="Please login to your account",
            font=("Helvetica", 12),
            bg=color2,
            fg=color4).pack(pady=(5, 0))

    # Input container
    input_frame = tk.Frame(login_frame, bg=color2)
    input_frame.pack(fill=tk.X, padx=50)

    # Username
    username_frame = tk.Frame(input_frame, bg=color2)
    username_frame.pack(fill=tk.X, pady=(20, 10))
    
    tk.Label(username_frame, 
            text="Username",
            font=("Helvetica", 11),
            bg=color2,
            fg=color4).pack(anchor='w')
    
    username_entry = tk.Entry(username_frame,
                            font=("Helvetica", 12),
                            bg='white',
                            relief='flat',
                            highlightthickness=1,
                            highlightbackground=color5)
    username_entry.pack(fill=tk.X, pady=(5, 0), ipady=8)

    # Password
    password_frame = tk.Frame(input_frame, bg=color2)
    password_frame.pack(fill=tk.X, pady=10)
    
    tk.Label(password_frame,
            text="Password",
            font=("Helvetica", 11),
            bg=color2,
            fg=color4).pack(anchor='w')
    
    password_entry = tk.Entry(password_frame,
                            font=("Helvetica", 12),
                            show="•",
                            bg='white',
                            relief='flat',
                            highlightthickness=1,
                            highlightbackground=color5)
    password_entry.pack(fill=tk.X, pady=(5, 0), ipady=8)

    def login():
        username = username_entry.get()
        password = hash_password(password_entry.get())
        if verify_user(username, password):
            global logged_in_user
            logged_in_user = username
            main_screen()
        else:
            messagebox.showerror("Error", "Invalid username or password.")

    # Buttons
    button_frame = tk.Frame(input_frame, bg=color2)
    button_frame.pack(fill=tk.X, pady=30)

    login_btn = tk.Button(button_frame,
                        text="Login",
                        font=("Helvetica", 12, "bold"),
                        bg=color5,
                        fg="white",
                        activebackground=color3,
                        activeforeground="white",
                        relief='flat',
                        cursor='hand2',
                        command=login)
    login_btn.pack(fill=tk.X, ipady=10)

    back_btn = tk.Button(button_frame,
                        text="Back to Start",
                        font=("Helvetica", 12),
                        bg=color1,
                        fg=color3,
                        activebackground=color2,
                        activeforeground=color3,
                        relief='flat',
                        cursor='hand2',
                        command=startup_screen)
    back_btn.pack(fill=tk.X, ipady=10, pady=(10, 0))

def signup_screen():
    for widget in root.winfo_children():
        widget.destroy()

    # Modern signup UI with better layout and styling
    signup_frame = tk.Frame(root, bg=color2)
    signup_frame.pack(fill=tk.BOTH, expand=True)

    # Header
    header_frame = tk.Frame(signup_frame, bg=color2)
    header_frame.pack(fill=tk.X, pady=(50, 30))
    
    tk.Label(header_frame,
            text="Create Account",
            font=("Helvetica", 24, "bold"),
            bg=color2,
            fg=color3).pack()

    tk.Label(header_frame,
            text="Please fill in the details below",
            font=("Helvetica", 12),
            bg=color2,
            fg=color4).pack(pady=(5, 0))

    # Input container
    input_frame = tk.Frame(signup_frame, bg=color2)
    input_frame.pack(fill=tk.X, padx=50)

    # Username
    username_frame = tk.Frame(input_frame, bg=color2)
    username_frame.pack(fill=tk.X, pady=(20, 10))
    
    tk.Label(username_frame,
            text="Choose Username",
            font=("Helvetica", 11),
            bg=color2,
            fg=color4).pack(anchor='w')
    
    username_entry = tk.Entry(username_frame,
                            font=("Helvetica", 12),
                            bg='white',
                            relief='flat',
                            highlightthickness=1,
                            highlightbackground=color5)
    username_entry.pack(fill=tk.X, pady=(5, 0), ipady=8)

    # Username requirement hint
    tk.Label(input_frame,
        text="Username can be anyname",
        font=("Helvetica", 10),
        bg=color2,
        fg=color4).pack(anchor='w')

    # Password
    password_frame = tk.Frame(input_frame, bg=color2)
    password_frame.pack(fill=tk.X, pady=10)
    
    tk.Label(password_frame,
            text="Create Password",
            font=("Helvetica", 11),
            bg=color2,
            fg=color4).pack(anchor='w')
    
    password_entry = tk.Entry(password_frame,
                            font=("Helvetica", 12),
                            show="•",
                            bg='white',
                            relief='flat',
                            highlightthickness=1,
                            highlightbackground=color5)
    password_entry.pack(fill=tk.X, pady=(5, 0), ipady=8)

    # Password requirement hint
    tk.Label(input_frame,
            text="Password must be at least 6 characters",
            font=("Helvetica", 10),
            bg=color2,
            fg=color4).pack(anchor='w')

    def signup():
        username = username_entry.get()
        password = password_entry.get()
        if len(password) < 6:
            messagebox.showwarning("Warning", "Password must be at least 6 characters long.")
            return
        save_user(username, hash_password(password))
        messagebox.showinfo("Success", "Account created successfully!")
        login_screen()

    # Buttons
    button_frame = tk.Frame(input_frame, bg=color2)
    button_frame.pack(fill=tk.X, pady=30)

    signup_btn = tk.Button(button_frame,
                        text="Sign Up",
                        font=("Helvetica", 12, "bold"),
                        bg=color5,
                        fg="white",
                        activebackground=color3,
                        activeforeground="white",
                        relief='flat',
                        cursor='hand2',
                        command=signup)
    signup_btn.pack(fill=tk.X, ipady=10)

    back_btn = tk.Button(button_frame,
                        text="Back to Start",
                        font=("Helvetica", 12),
                        bg=color1,
                        fg=color3,
                        activebackground=color2,
                        activeforeground=color3,
                        relief='flat',
                        cursor='hand2',
                        command=startup_screen)
    back_btn.pack(fill=tk.X, ipady=10, pady=(10, 0))


# Function to log out the user
def logout():
    # Clear the current window
    for widget in root.winfo_children():
        widget.destroy()
    
    # Reset the logged_in_user variable
    global logged_in_user
    logged_in_user = None
    
    # Call your existing start screen function
    startup_screen()  # or whatever your start screen function is named

    # Optional: Reset window title
    root.title("P.Note - Welcome")

def main_screen():
    # Clear the window
    for widget in root.winfo_children():
        widget.destroy()

    def create_note_content(parent_frame, title="", content="", is_new=True):
        """Helper function to create consistent note content for both new and saved notes"""
        # Title section
        title_frame = tk.Frame(parent_frame)
        title_frame.pack(fill=tk.X, pady=5)

        title_label = tk.Label(title_frame, text="Title:", font=("Arial", 12))
        title_label.pack(side=tk.LEFT)

        title_entry = tk.Entry(title_frame, width=50)
        title_entry.pack(side=tk.LEFT, padx=10)
        if is_new:
            title_entry.insert(0, "Enter your title")
            title_entry.bind('<FocusIn>', lambda e: title_entry.delete(0, tk.END) if title_entry.get() == "Enter your title" else None)
        else:
            title_entry.insert(0, title)

        # Save button
        def save_current():
            current_title = title_entry.get()
            current_content = content_text.get("1.0", tk.END)
            save_note_content(current_title, current_content)

        save_btn = tk.Button(
            title_frame,
            text="Save",
            command=save_current,
            bg=color5,
            fg='white',
            font=("Helvetica", 11),
            relief='flat',
            cursor='hand2'
        )
        save_btn.pack(side=tk.RIGHT, padx=5)

        # Content section
        content_frame = tk.Frame(parent_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=10) #change1

        content_label = tk.Label(content_frame, text="Content:", font=("Arial", 12))
        content_label.pack(anchor="w")

        content_text = tk.Text(content_frame, height=15, width=50)
        content_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True) 
        if is_new:
            content_text.insert("1.0", "Type your note here")
            content_text.bind('<FocusIn>', lambda e: content_text.delete("1.0", tk.END) if content_text.get("1.0", tk.END).strip() == "Type your note here" else None)
        else:
            content_text.insert("1.0", content)

        # Edit options frame
        edit_frame = tk.Frame(parent_frame)
        edit_frame.pack(side=tk.RIGHT, padx=20, fill=tk.Y)

        edit_label = tk.Label(edit_frame, text="Edit option >", font=("Arial", 12))
        edit_label.pack(pady=5)

        # Font selection
        font_combo = ttk.Combobox(
            edit_frame,
            values=["Times New Roman", "Arial", "Helvetica"],
            state="readonly",
            width=20
        )
        font_combo.set("Times New Roman")
        font_combo.pack(pady=5)

        def apply_font(event):
            content_text.configure(font=(font_combo.get(), int(size_combo.get())))

        font_combo.bind('<<ComboboxSelected>>', apply_font)

        # Size selection
        size_combo = ttk.Combobox(
            edit_frame,
            values=[str(i) for i in range(8, 25, 2)],
            state="readonly",
            width=20
        )
        size_combo.set("12")
        size_combo.pack(pady=5)
        size_combo.bind('<<ComboboxSelected>>', apply_font)

        # Color selection
        color_combo = ttk.Combobox(
            edit_frame,
            values=["Black", "Blue", "Red", "Green"],
            state="readonly",
            width=20
        )
        color_combo.set("Color")
        color_combo.pack(pady=5)

        def apply_color(event):
            content_text.configure(fg=color_combo.get())

        color_combo.bind('<<ComboboxSelected>>', apply_color)

        # Upload photo button
        def upload_photo():
            file_path = filedialog.askopenfilename(
                filetypes=[
                    ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                    ("All files", "*.*")
                ]
            )
            if file_path:
                try:
                    # Open and resize image
                    image = Image.open(file_path)
                    # Resize image if too large
                    max_size = (300, 300)
                    image.thumbnail(max_size, Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    
                    # Store the PhotoImage object to prevent garbage collection
                    if not hasattr(content_text, 'images'):
                        content_text.images = []
                    content_text.images.append(photo)
                    
                    # Insert the image at current cursor position
                    content_text.image_create(tk.INSERT, image=photo)
                    
                    # Add a newline after the image
                    content_text.insert(tk.INSERT, '\n')
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to insert image: {str(e)}")

        upload_btn = tk.Button(
            edit_frame,
            text="Upload photo",
            font=("Arial", 10),
            width=15,
            command=upload_photo
        )
        upload_btn.pack(pady=5)

        return title_entry, content_text

    # Configure the root window with the new background color
    root.configure(bg=color2)  # Using the soft purple background
    
    # Create main content area with new colors
    main_content = tk.Frame(root, bg=color1)  # Light lavender background
    main_content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Style the notebook
    style = ttk.Style()
    style.configure("TNotebook", background=color1)  # Light lavender
    style.configure("TNotebook.Tab", background=color2, foreground=color4)  # Soft purple tabs with soft black text
    style.map("TNotebook.Tab",
        background=[("selected", color5)],  # Medium purple for selected tab
        foreground=[("selected", "white")])  # White text for selected tab
    
    # Create notebook globally within the function
    global notebook
    # Style the notebook
    style = ttk.Style()
    style.configure("TNotebook", background=color1)  # Light lavender
    style.configure("TNotebook.Tab", background=color2, foreground=color4)  # Soft purple tabs with soft black text
    style.map("TNotebook.Tab",
        background=[("selected", color5)],  # Medium purple for selected tab
        foreground=[("selected", "white")])  # White text for selected tab
    
    global notebook
    notebook = ttk.Notebook(main_content)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Create left sidebar with new colors
    sidebar = tk.Frame(root, bg=color2, width=200)  # Soft purple sidebar
    sidebar.pack(side=tk.LEFT, fill=tk.Y)
    sidebar.pack_propagate(False)

    # Username label with new colors
    username_label = tk.Label(
        sidebar,
        text=logged_in_user,
        font=("Arial", 14, "bold"),
        bg=color2,  # Soft purple background
        fg=color3,  # Deep purple text
        pady=20
    )
    username_label.pack(fill=tk.X, padx=10)

    # Define other helper functions
    def save_note():
        current_tab = notebook.select()
        if current_tab:
            tab = notebook.index(current_tab)
            note_frame = notebook.winfo_children()[tab]
            
            title_entry = None
            content_text = None
            
            for widget in note_frame.winfo_children():
                if isinstance(widget, tk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Entry):
                            title_entry = child
                        elif isinstance(child, tk.Text):
                            content_text = child
                
            if title_entry and content_text:
                title = title_entry.get()
                content = content_text.get("1.0", tk.END)
                save_note_content(title, content)
            else:
                messagebox.showerror("Error", "Could not find note content!")

    def delete_note():
        current_tab = notebook.select()
        if current_tab:
            tab_id = notebook.index(current_tab)
            title = notebook.tab(current_tab, "text")
            if messagebox.askyesno("Confirm Delete", f"Delete note '{title}'?"):
                delete_note_from_db(logged_in_user, title)
                notebook.forget(tab_id)

    def view_old_notes():
        # Clear existing tabs safely
        while len(notebook.tabs()) > 0:
            notebook.select(0)  # Select the first tab
            notebook.forget(notebook.select())  # Remove the selected tab
        
        # Create main frame for old notes
        old_notes_frame = ttk.Frame(notebook, padding=10)
        notebook.add(old_notes_frame, text="My Notes")
        
        # Create left panel for note list
        list_frame = tk.Frame(old_notes_frame, bg=color1, width=200)
        list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Create right panel for note content
        content_frame = tk.Frame(old_notes_frame, bg=color1)
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add title for notes list
        tk.Label(
            list_frame,
            text="Your Title Notes",
            font=("Helvetica", 14, "bold"),
            bg=color1,
            fg=color3
        ).pack(pady=(0, 10), padx=5)
        
        # Create scrollable listbox for notes with scrollbar
        listbox_frame = tk.Frame(list_frame, bg=color1)
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=5)
        
        notes_listbox = tk.Listbox(
            listbox_frame,
            bg='white',
            fg=color4,
            font=("Helvetica", 11),
            selectmode=tk.SINGLE,
            relief='flat',
            highlightthickness=1,
            highlightbackground=color5
        )
        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=notes_listbox.yview)
        notes_listbox.configure(yscrollcommand=scrollbar.set)
        
        notes_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create text widget for note content
        title_label = tk.Label(
            content_frame,
            text="Select a title of your note to view your content",
            font=("Helvetica", 16, "bold"),
            bg=color1,
            fg=color3
        )
        title_label.pack(anchor='w', pady=(0, 10))
        
        content_text = tk.Text(
            content_frame,
            wrap=tk.WORD,
            font=("Helvetica", 12),
            bg='white',
            relief='flat',
            highlightthickness=1,
            highlightbackground=color5
        )
        content_text.pack(fill=tk.BOTH, expand=True)
        content_text.config(state='disabled')  # Initially disabled
        
        # Load notes from database
        notes = load_notes_from_db(logged_in_user)
        
        if not notes:
            tk.Label(
                content_frame,
                text="No saved notes found",
                font=("Helvetica", 12),
                bg=color1,
                fg=color4
            ).pack(pady=20)
            return
        
        # Add notes to listbox
        for title in sorted(notes.keys()):  # Sort titles alphabetically
            notes_listbox.insert(tk.END, title)
        
        def on_select(event):
            if not notes_listbox.curselection():
                return
            
            # Get selected title
            selected_title = notes_listbox.get(notes_listbox.curselection())
            
            # Update title label
            title_label.config(text=selected_title)
            
            # Enable text widget for updating
            content_text.config(state='normal')
            
            # Clear and update content
            content_text.delete(1.0, tk.END)
            content_text.insert(1.0, notes[selected_title])
            
            # Disable text widget again
            content_text.config(state='disabled')
        
        notes_listbox.bind('<<ListboxSelect>>', on_select)
        
        # Add buttons frame
        button_frame = tk.Frame(content_frame, bg=color1)
        button_frame.pack(fill=tk.X, pady=10)
        
        def edit_note():
            if not notes_listbox.curselection():
                messagebox.showwarning("Warning", "Please select a note to edit")
                return
            
            selected_title = notes_listbox.get(notes_listbox.curselection())
            
            # Create new tab for editing
            note_frame = ttk.Frame(notebook, padding=10)
            notebook.add(note_frame, text=selected_title)
            create_note_content(note_frame, selected_title, notes[selected_title], is_new=False)
            notebook.select(notebook.index(note_frame))
        
        # Add control buttons
        tk.Button(
            button_frame,
            text="Edit Note",
            command=edit_note,
            bg=color5,
            fg='white',
            font=("Helvetica", 11),
            relief='flat',
            cursor='hand2',
            padx=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Back to Notes",
            command=lambda: main_screen(),
            bg=color1,
            fg=color3,
            font=("Helvetica", 11),
            relief='flat',
            cursor='hand2',
            padx=15
        ).pack(side=tk.LEFT, padx=5)

    # Update button style with new colors
    button_style = {
        "width": 15,
        "font": ("Arial", 11),
        "bg": color1,  # Light lavender background
        "fg": color3,  # Deep purple text
        "bd": 1,
        "relief": "solid",
        "cursor": "hand2",
        "pady": 5,
        "activebackground": color5,  # Medium purple when clicked
        "activeforeground": "white"
    }

    def add_note():
        note_frame = ttk.Frame(notebook, padding=10)
        notebook.add(note_frame, text="+ New Note")
        create_note_content(note_frame)

    # Now add all sidebar buttons
    add_note_btn = tk.Button(sidebar, text="Add New Note", command=add_note, **button_style)
    add_note_btn.pack(pady=5, padx=10)

    save_note_btn = tk.Button(
        sidebar,
        text="Save note",
        command=save_note,
        **button_style
    )
    save_note_btn.pack(pady=5, padx=10)

    delete_btn = tk.Button(sidebar, text="Delete", command=delete_note, **button_style)
    delete_btn.pack(pady=5, padx=10)

    draw_btn = tk.Button(sidebar, text="Drawing", command=lambda: add_draw_tab(notebook), **button_style)
    draw_btn.pack(pady=5, padx=10)

    view_old_btn = tk.Button(sidebar, text="View old notes", command=view_old_notes, **button_style)
    view_old_btn.pack(pady=5, padx=10)

    # Update logout button style
    logout_btn = tk.Button(
        sidebar,
        text="Logout",
        command=logout,
        font=("Arial", 11),
        bg=color5,  # Medium purple background
        fg="white",
        bd=0,
        width=15,
        pady=5,
        cursor="hand2",
        activebackground=color3,  # Deep purple when clicked
        activeforeground="white"
    )
    logout_btn.pack(side=tk.BOTTOM, pady=20, padx=10)

    # Load existing notes
    notes = load_notes_from_db(logged_in_user)
    for title, content in notes.items():
        note_frame = ttk.Frame(notebook, padding=10)
        notebook.add(note_frame, text=title)
        create_note_content(note_frame, title, content, is_new=False)

    return notebook

def save_note_content(title, content):
    if not logged_in_user:
        messagebox.showerror("Error", "No user logged in!")
        return
        
    if not title or not content.strip():
        messagebox.showwarning("Warning", "Title and content cannot be empty!")
        return
    
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO notes (user, title, content)
            VALUES (?, ?, ?)
        """, (logged_in_user, title, content.strip()))
        
        conn.commit()
        messagebox.showinfo("Success", "Note saved successfully!")
        
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Database error: {str(e)}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Show the startup screen initially
startup_screen()
root.mainloop()

# Close the database connection when the application ends
conn.close()
