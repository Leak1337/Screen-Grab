import customtkinter as ctk
from tkinter import filedialog, messagebox
import mss
import requests
import base64
import pyperclip
import os
import webbrowser
from datetime import datetime
import time

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green") 

# ImgBB API-Key
API_KEY = "API KEY"

def upload_to_imgbb(image_path):
    with open(image_path, "rb") as file:
        image_data = base64.b64encode(file.read()).decode('utf-8')
    
    url = "https://api.imgbb.com/1/upload"
    payload = {"key": API_KEY, "image": image_data}
    
    response = requests.post(url, data=payload)
    
    if response.status_code == 200:
        return response.json()['data']['url']
    return None

def take_screenshot():
    app.withdraw()
    app.update()
    time.sleep(0.8)  
    
    with mss.mss() as sct:
        filename = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        sct.shot(output=filename)
    
    app.deiconify()
    app.update()
    return filename

def add_to_history(url):
    timestamp = datetime.now().strftime("%H:%M:%S")
    display_text = url[:60] + "..." if len(url) > 60 else url
    
    link_btn = ctk.CTkButton(
        history_frame,
        text=f"[{timestamp}] {display_text}",
        anchor="w",
        height=35,
        corner_radius=10,
        fg_color="transparent",
        hover_color=("#0f2f0f", "#0f2f0f"),
        font=ctk.CTkFont(family="Consolas", size=12),
        text_color="#00ff88",
        command=lambda u=url: (pyperclip.copy(u), webbrowser.open(u), status_label.configure(text=">> LINK EXECUTED <<", text_color="#00ff00"))
    )
    link_btn.pack(fill="x", padx=10, pady=2, side="top")  

def process_upload(image_path, is_screenshot=False):
    status_label.configure(text=">> UPLOAD INITIATED <<", text_color="#00ff88")
    progress_bar.set(0)
    
    for i in range(101):
        progress_bar.set(i / 100)
        app.update_idletasks()
        time.sleep(0.008)  
    
    url = upload_to_imgbb(image_path)
    
    if is_screenshot and os.path.exists(image_path):
        os.remove(image_path)
    
    if url:
        status_label.configure(text=">> SUCCESS ✓ <<", text_color="#00ff00")
        add_to_history(url)
    else:
        status_label.configure(text=">> FAILED <<", text_color="red")
        messagebox.showerror("ERROR", "Upload failed!")

def upload_screenshot():
    status_label.configure(text=">> CAPTURING <<", text_color="#00ff88")
    file = take_screenshot()
    process_upload(file, is_screenshot=True)

def upload_from_file():
    file_path = filedialog.askopenfilename(
        title="Select file",
        filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.gif *.webp")]
    )
    if file_path:
        process_upload(file_path)

# GUI
app = ctk.CTk()
app.title("Sreen Grab")
app.geometry("600x600")  
app.minsize(550, 700)

ctk.CTkLabel(app, text="Sreen Grab", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=30)

ctk.CTkButton(app, text="📸 FULL SCREEN", font=ctk.CTkFont(size=16, weight="bold"),
              height=50, corner_radius=15, command=upload_screenshot).pack(pady=15, padx=80, fill="x")

ctk.CTkButton(app, text="🖼️ LOCAL FILE", font=ctk.CTkFont(size=16, weight="bold"),
              height=50, corner_radius=15, command=upload_from_file).pack(pady=10, padx=80, fill="x")

status_label = ctk.CTkLabel(app, text="Ready – awaiting command", font=ctk.CTkFont(size=14), text_color="#aaaaaa")
status_label.pack(pady=20)

progress_bar = ctk.CTkProgressBar(app, height=20, corner_radius=10)
progress_bar.pack(pady=10, padx=80, fill="x")
progress_bar.set(0)

ctk.CTkLabel(app, text="HISTORY (click link)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(30,10))

scrollable_history = ctk.CTkScrollableFrame(app, corner_radius=15)
scrollable_history.pack(pady=10, padx=40, fill="both", expand=True)

history_frame = scrollable_history  

app.mainloop()