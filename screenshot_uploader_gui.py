import base64
import os
import tempfile
import threading
import time
import webbrowser
from datetime import datetime

import customtkinter as ctk
import mss
import pyperclip
import requests
from tkinter import filedialog, messagebox


ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

IMGBB_UPLOAD_URL = "https://api.imgbb.com/1/upload"
REQUEST_TIMEOUT_SECONDS = 30


def get_imgbb_api_key():
    """Read the key outside the source code and at call time."""
    return os.environ.get("IMGBB_API_KEY", "").strip()


def upload_to_imgbb(image_path):
    api_key = get_imgbb_api_key()
    if not api_key:
        raise RuntimeError(
            "Kein ImgBB API-Key gefunden. Bitte die Umgebungsvariable "
            "IMGBB_API_KEY setzen."
        )

    with open(image_path, "rb") as file:
        image_data = base64.b64encode(file.read()).decode("utf-8")

    response = requests.post(
        IMGBB_UPLOAD_URL,
        data={"key": api_key, "image": image_data},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()

    image_url = response.json().get("data", {}).get("url")
    if not image_url:
        raise RuntimeError("ImgBB hat keine Bild-URL zurückgegeben.")
    return image_url


def take_screenshot():
    app.withdraw()
    app.update_idletasks()
    time.sleep(0.3)

    try:
        with mss.mss() as screen:
            filename = tempfile.NamedTemporaryFile(
                prefix="screenshot_uploader_",
                suffix=".png",
                delete=False,
            ).name
            screen.shot(mon=-1, output=filename)
            return filename
    finally:
        app.deiconify()
        app.lift()
        app.update_idletasks()


def open_link(url):
    try:
        pyperclip.copy(url)
    except pyperclip.PyperclipException:
        pass
    webbrowser.open(url)
    status_label.configure(text=">> LINK OPENED <<", text_color="#00ff00")


def add_to_history(url):
    timestamp = datetime.now().strftime("%H:%M:%S")
    display_text = url[:60] + "..." if len(url) > 60 else url

    link_button = ctk.CTkButton(
        history_frame,
        text=f"[{timestamp}] {display_text}",
        anchor="w",
        height=35,
        corner_radius=10,
        fg_color="transparent",
        hover_color=("#0f2f0f", "#0f2f0f"),
        font=ctk.CTkFont(family="Consolas", size=12),
        text_color="#00ff88",
        command=lambda image_url=url: open_link(image_url),
    )
    link_button.pack(fill="x", padx=10, pady=2, side="top")


def set_upload_state(is_uploading):
    global upload_in_progress
    upload_in_progress = is_uploading

    state = "disabled" if is_uploading else "normal"
    screenshot_button.configure(state=state)
    file_button.configure(state=state)

    if is_uploading:
        progress_bar.start()
    else:
        progress_bar.stop()
        progress_bar.set(0)


def finish_upload(image_path, is_screenshot, image_url, error):
    if is_screenshot and os.path.exists(image_path):
        try:
            os.remove(image_path)
        except OSError:
            pass

    set_upload_state(False)

    if error is None:
        status_label.configure(text=">> SUCCESS ✓ <<", text_color="#00ff00")
        add_to_history(image_url)
        return

    status_label.configure(text=">> FAILED <<", text_color="red")
    messagebox.showerror("Upload fehlgeschlagen", str(error))


def process_upload(image_path, is_screenshot=False):
    if upload_in_progress:
        return

    set_upload_state(True)
    status_label.configure(text=">> UPLOAD INITIATED <<", text_color="#00ff88")

    def upload_worker():
        image_url = None
        error = None
        try:
            image_url = upload_to_imgbb(image_path)
        except (OSError, requests.RequestException, ValueError, RuntimeError) as exc:
            error = exc
        except Exception as exc:
            error = RuntimeError(f"Unerwarteter Fehler: {exc}")

        app.after(
            0,
            lambda: finish_upload(image_path, is_screenshot, image_url, error),
        )

    threading.Thread(target=upload_worker, daemon=True).start()


def upload_screenshot():
    if upload_in_progress:
        return

    status_label.configure(text=">> CAPTURING <<", text_color="#00ff88")
    try:
        screenshot_path = take_screenshot()
    except (OSError, mss.exception.ScreenShotError) as exc:
        status_label.configure(text=">> FAILED <<", text_color="red")
        messagebox.showerror("Screenshot fehlgeschlagen", str(exc))
        return

    process_upload(screenshot_path, is_screenshot=True)


def upload_from_file():
    if upload_in_progress:
        return

    file_path = filedialog.askopenfilename(
        title="Bild auswählen",
        filetypes=[("Bilder", "*.png *.jpg *.jpeg *.bmp *.gif *.webp")],
    )
    if file_path:
        process_upload(file_path)


# GUI
app = ctk.CTk()
app.title("Screen Grab")
app.geometry("600x600")
app.minsize(550, 700)

ctk.CTkLabel(
    app,
    text="Screen Grab",
    font=ctk.CTkFont(size=28, weight="bold"),
).pack(pady=30)

screenshot_button = ctk.CTkButton(
    app,
    text="📸 FULL SCREEN",
    font=ctk.CTkFont(size=16, weight="bold"),
    height=50,
    corner_radius=15,
    command=upload_screenshot,
)
screenshot_button.pack(pady=15, padx=80, fill="x")

file_button = ctk.CTkButton(
    app,
    text="🖼️ LOCAL FILE",
    font=ctk.CTkFont(size=16, weight="bold"),
    height=50,
    corner_radius=15,
    command=upload_from_file,
)
file_button.pack(pady=10, padx=80, fill="x")

status_label = ctk.CTkLabel(
    app,
    text="Ready – awaiting command",
    font=ctk.CTkFont(size=14),
    text_color="#aaaaaa",
)
status_label.pack(pady=20)

progress_bar = ctk.CTkProgressBar(app, height=20, corner_radius=10)
progress_bar.pack(pady=10, padx=80, fill="x")
progress_bar.set(0)

ctk.CTkLabel(
    app,
    text="HISTORY (click link)",
    font=ctk.CTkFont(size=16, weight="bold"),
).pack(pady=(30, 10))

history_frame = ctk.CTkScrollableFrame(app, corner_radius=15)
history_frame.pack(pady=10, padx=40, fill="both", expand=True)

upload_in_progress = False
app.mainloop()
