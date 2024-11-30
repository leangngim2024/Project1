import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.colorchooser import askcolor
from PIL import Image, ImageTk
import customtkinter as ctk

def add_draw_tab(notebook):
    # Create a new tab for drawing
    draw_frame = ttk.Frame(notebook)
    notebook.add(draw_frame, text="Drawing Board")

    # Create a canvas with border effect
    canvas_frame = tk.Frame(draw_frame, bg="#ffffff", padx=2, pady=2)
    canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    canvas = tk.Canvas(
        canvas_frame,
        bg="white",
        width=500,
        height=400,
        highlightthickness=1,
        highlightbackground="#e0e0e0"
    )
    canvas.pack(fill=tk.BOTH, expand=True)

    # Initialize canvas data
    canvas.data = {
        "pen_color": "#000000",
        "pen_width": 3,
        "strokes": [],
        "redo_strokes": [],
        "current_stroke": []
    }

    # Define all drawing functions first
    def choose_pen_width(width):
        canvas.data["pen_width"] = width

    def start_draw(event):
        canvas.data["current_stroke"] = []
        canvas.data["last_x"] = event.x
        canvas.data["last_y"] = event.y

    def draw(event):
        if "last_x" in canvas.data and "last_y" in canvas.data:
            x1, y1 = canvas.data["last_x"], canvas.data["last_y"]
            x2, y2 = event.x, event.y
            
            line_id = canvas.create_line(
                x1, y1, x2, y2,
                fill=canvas.data["pen_color"],
                width=canvas.data["pen_width"],
                capstyle=tk.ROUND,
                smooth=True
            )
            
            canvas.data["current_stroke"].append({
                "id": line_id,
                "coords": (x1, y1, x2, y2),
                "color": canvas.data["pen_color"],
                "width": canvas.data["pen_width"]
            })
            
            canvas.data["last_x"] = x2
            canvas.data["last_y"] = y2

    def stop_draw(event):
        if canvas.data["current_stroke"]:
            canvas.data["strokes"].append(canvas.data["current_stroke"])
            canvas.data["redo_strokes"].clear()
        canvas.data["current_stroke"] = []
        canvas.data.pop("last_x", None)
        canvas.data.pop("last_y", None)

    def clear_canvas():
        canvas.delete("all")
        canvas.data["strokes"].clear()
        canvas.data["redo_strokes"].clear()

    def undo_last():
        if canvas.data["strokes"]:
            last_stroke = canvas.data["strokes"].pop()
            for segment in last_stroke:
                canvas.delete(segment["id"])
            canvas.data["redo_strokes"].append(last_stroke)

    def redo_last():
        if canvas.data["redo_strokes"]:
            stroke = canvas.data["redo_strokes"].pop()
            new_stroke = []
            for segment in stroke:
                line_id = canvas.create_line(
                    *segment["coords"],
                    fill=segment["color"],
                    width=segment["width"],
                    capstyle=tk.ROUND,
                    smooth=True
                )
                new_stroke.append({
                    "id": line_id,
                    "coords": segment["coords"],
                    "color": segment["color"],
                    "width": segment["width"]
                })
            canvas.data["strokes"].append(new_stroke)

    def upload_image():
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")]
        )
        if file_path:
            try:
                image = Image.open(file_path)
                image = image.resize((500, 400))
                photo = ImageTk.PhotoImage(image)
                canvas.create_image(0, 0, anchor=tk.NW, image=photo)
                canvas.image = photo  # Keep a reference!
            except Exception as e:
                print(f"Error uploading image: {e}")

    # Create modern toolbar
    toolbar = ctk.CTkFrame(draw_frame)
    toolbar.pack(fill=tk.X, padx=10, pady=5)

    # Button style
    button_style = {
        "width": 120,
        "height": 35,
        "corner_radius": 8,
        "border_width": 0,
        "font": ("Helvetica", 12),
        "text_color": "white"
    }

    # Create buttons with modern styling
    buttons_data = [
        ("🎨 Color", "#3498db", lambda: choose_color()),
        ("✏️ Fine", "#2ecc71", lambda: choose_pen_width(3)),
        ("✏️ Medium", "#2ecc71", lambda: choose_pen_width(5)),
        ("✏️ Thick", "#2ecc71", lambda: choose_pen_width(8)),
        ("↶ Undo", "#95a5a6", undo_last),
        ("↷ Redo", "#95a5a6", redo_last),
        ("🗑️ Clear", "#e74c3c", clear_canvas),
        ("📁 Upload", "#9b59b6", upload_image)
    ]

    def choose_color():
        color = askcolor(title="Choose Color")[1]
        if color:
            canvas.data["pen_color"] = color

    # Create and pack buttons
    for text, color, command in buttons_data:
        btn = ctk.CTkButton(
            toolbar,
            text=text,
            command=command,
            fg_color=color,
            hover_color=adjust_color_brightness(color, -20),
            **button_style
        )
        btn.pack(side=tk.LEFT, padx=5, pady=5)

    # Bind canvas events
    canvas.bind("<Button-1>", start_draw)
    canvas.bind("<B1-Motion>", draw)
    canvas.bind("<ButtonRelease-1>", stop_draw)

    return canvas

def adjust_color_brightness(hex_color, factor):
    """Adjust the brightness of a hex color"""
    # Convert hex to RGB
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    # Adjust brightness
    new_rgb = tuple(
        min(max(int(c * (1 + factor/100)), 0), 255)
        for c in rgb
    )
    
    # Convert back to hex
    return '#{:02x}{:02x}{:02x}'.format(*new_rgb)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Modern Drawing Board")
    
    # Configure the appearance mode
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    # Create notebook
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True)
    
    # Add drawing tab
    canvas = add_draw_tab(notebook)
    
    # Set window size
    root.geometry("800x600")
    
    root.mainloop()
