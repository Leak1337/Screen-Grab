import base64
import json
import os
import tempfile
import threading
import time
import webbrowser
from datetime import datetime
from pathlib import Path

import customtkinter as ctk
import mss
import pyperclip
import requests
from tkinter import filedialog, messagebox


ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

IMGBB_UPLOAD_URL = "https://api.imgbb.com/1/upload"
REQUEST_TIMEOUT_SECONDS = 30
MAX_HISTORY_ITEMS = 25
APP_DATA_DIR = Path(os.environ.get("APPDATA") or Path.home()) / "ScreenGrab"
HISTORY_FILE = APP_DATA_DIR / "history.json"

COLORS = {
    "background": "#070A0F",
    "surface": "#0D131C",
    "surface_light": "#121C28",
    "border": "#1C2B3A",
    "text": "#F4F8FB",
    "muted": "#8192A5",
    "green": "#00F5A0",
    "green_dark": "#0A6B4D",
    "blue": "#38BDF8",
    "red": "#FF5C77",
}


def get_imgbb_api_key():
    """Read the API key outside the source code and at call time."""
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
    time.sleep(0.25)

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
        app.after(10, app.lift)
        app.update_idletasks()


def set_status(text, color=None):
    status_label.configure(
        text=text,
        text_color=color or COLORS["muted"],
    )


def copy_link(url, show_status=True):
    try:
        pyperclip.copy(url)
    except pyperclip.PyperclipException:
        if show_status:
            set_status("CLIPBOARD NOT AVAILABLE", COLORS["red"])
        return

    if show_status:
        set_status("LINK COPIED TO CLIPBOARD", COLORS["green"])


def open_link(url):
    copy_link(url, show_status=False)
    webbrowser.open(url)
    set_status("LINK OPENED IN BROWSER", COLORS["green"])


def load_history():
    if not HISTORY_FILE.exists():
        return []

    try:
        entries = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []

    if not isinstance(entries, list):
        return []

    return [
        {
            "url": entry["url"],
            "created_at": entry.get("created_at", ""),
        }
        for entry in entries[:MAX_HISTORY_ITEMS]
        if isinstance(entry, dict) and isinstance(entry.get("url"), str)
    ]


def save_history():
    try:
        APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
        HISTORY_FILE.write_text(
            json.dumps(history_entries, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except OSError:
        set_status("HISTORY COULD NOT BE SAVED", COLORS["red"])


def render_history():
    for child in history_frame.winfo_children():
        child.destroy()

    if not history_entries:
        ctk.CTkLabel(
            history_frame,
            text="Noch keine Uploads\nDein Verlauf erscheint hier.",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["muted"],
            justify="center",
        ).pack(expand=True, pady=42)
        history_count_label.configure(text="0 UPLOADS")
        return

    history_count_label.configure(
        text=f"{len(history_entries)} UPLOADS"
    )

    for index, entry in enumerate(history_entries):
        row = ctk.CTkFrame(
            history_frame,
            fg_color=COLORS["surface_light"],
            border_width=1,
            border_color=COLORS["border"],
            corner_radius=12,
        )
        row.pack(fill="x", padx=6, pady=5)
        row.grid_columnconfigure(0, weight=1)

        timestamp = entry["created_at"].replace("T", " ") or "Unbekannte Zeit"
        ctk.CTkLabel(
            row,
            text=f"{index + 1:02d}  /  {timestamp}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["blue"],
            anchor="w",
        ).grid(row=0, column=0, padx=(14, 8), pady=(10, 1), sticky="w")

        ctk.CTkLabel(
            row,
            text=entry["url"],
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color=COLORS["text"],
            anchor="w",
            wraplength=470,
        ).grid(row=1, column=0, padx=(14, 8), pady=(1, 10), sticky="ew")

        action_frame = ctk.CTkFrame(row, fg_color="transparent")
        action_frame.grid(row=0, column=1, rowspan=2, padx=(0, 10), pady=8)

        ctk.CTkButton(
            action_frame,
            text="COPY",
            width=68,
            height=30,
            corner_radius=8,
            fg_color=COLORS["green_dark"],
            hover_color="#0D8F68",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda url=entry["url"]: copy_link(url),
        ).pack(side="left", padx=3)

        ctk.CTkButton(
            action_frame,
            text="OPEN",
            width=68,
            height=30,
            corner_radius=8,
            fg_color=COLORS["border"],
            hover_color="#29435A",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda url=entry["url"]: open_link(url),
        ).pack(side="left", padx=3)


def add_to_history(url):
    history_entries.insert(
        0,
        {
            "url": url,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        },
    )
    del history_entries[MAX_HISTORY_ITEMS:]
    save_history()
    render_history()


def clear_history():
    if not history_entries:
        return
    if not messagebox.askyesno(
        "Verlauf löschen",
        "Möchtest du den gesamten Upload-Verlauf löschen?",
    ):
        return

    history_entries.clear()
    save_history()
    render_history()
    set_status("HISTORY CLEARED", COLORS["green"])


def update_key_status():
    if get_imgbb_api_key():
        key_status.configure(
            text="● API KEY READY",
            text_color=COLORS["green"],
            fg_color="#0B3027",
        )
    else:
        key_status.configure(
            text="● API KEY MISSING",
            text_color=COLORS["red"],
            fg_color="#341622",
        )


def set_upload_state(is_uploading):
    global upload_in_progress
    upload_in_progress = is_uploading

    state = "disabled" if is_uploading else "normal"
    capture_button.configure(state=state)
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
        set_status("UPLOAD COMPLETE  •  LINK READY", COLORS["green"])
        add_to_history(image_url)
        return

    set_status("UPLOAD FAILED", COLORS["red"])
    messagebox.showerror("Upload fehlgeschlagen", str(error))


def process_upload(image_path, is_screenshot=False):
    if upload_in_progress:
        return

    set_upload_state(True)
    set_status("UPLOADING  •  PLEASE WAIT", COLORS["green"])

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

    set_status("CAPTURING ALL SCREENS", COLORS["blue"])
    try:
        screenshot_path = take_screenshot()
    except Exception as exc:
        set_status("CAPTURE FAILED", COLORS["red"])
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


def hotkey_handler(_event):
    upload_screenshot()
    return "break"


def close_app():
    if upload_in_progress and not messagebox.askyesno(
        "Upload läuft noch",
        "Der Upload läuft noch. Anwendung trotzdem schließen?",
    ):
        return
    app.destroy()


# GUI
app = ctk.CTk()
app.title("Screen Grab  //  Capture Node")
app.geometry("900x720")
app.minsize(760, 620)
app.configure(fg_color=COLORS["background"])
app.protocol("WM_DELETE_WINDOW", close_app)
app.bind("<Control-Shift-s>", hotkey_handler)

shell = ctk.CTkFrame(app, fg_color="transparent")
shell.pack(fill="both", expand=True, padx=28, pady=24)

header = ctk.CTkFrame(shell, fg_color="transparent")
header.pack(fill="x", pady=(0, 22))

brand = ctk.CTkFrame(header, fg_color="transparent")
brand.pack(side="left")

ctk.CTkLabel(
    brand,
    text="◈  SCREEN GRAB",
    font=ctk.CTkFont(size=25, weight="bold"),
    text_color=COLORS["text"],
).pack(anchor="w")

ctk.CTkLabel(
    brand,
    text="CAPTURE  /  UPLOAD  /  SHARE",
    font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
    text_color=COLORS["green"],
).pack(anchor="w", pady=(3, 0))

key_status = ctk.CTkLabel(
    header,
    text="● API KEY MISSING",
    width=150,
    height=32,
    font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
    text_color=COLORS["red"],
    fg_color="#341622",
    corner_radius=20,
)
key_status.pack(side="right", pady=4)

hero = ctk.CTkFrame(
    shell,
    fg_color=COLORS["surface"],
    border_width=1,
    border_color=COLORS["border"],
    corner_radius=18,
)
hero.pack(fill="x", pady=(0, 18))

hero_copy = ctk.CTkFrame(hero, fg_color="transparent")
hero_copy.pack(side="left", padx=28, pady=26)

ctk.CTkLabel(
    hero_copy,
    text="Your screenshots.\nInstantly shareable.",
    font=ctk.CTkFont(size=27, weight="bold"),
    text_color=COLORS["text"],
    justify="left",
).pack(anchor="w")

ctk.CTkLabel(
    hero_copy,
    text="One shortcut from screen to share link.",
    font=ctk.CTkFont(size=13),
    text_color=COLORS["muted"],
).pack(anchor="w", pady=(9, 0))

button_row = ctk.CTkFrame(hero, fg_color="transparent")
button_row.pack(side="right", padx=24, pady=26)

capture_button = ctk.CTkButton(
    button_row,
    text="▣  CAPTURE SCREEN",
    width=190,
    height=48,
    corner_radius=12,
    fg_color=COLORS["green"],
    hover_color="#54FFC0",
    text_color="#03130D",
    font=ctk.CTkFont(size=13, weight="bold"),
    command=upload_screenshot,
)
capture_button.pack(pady=(0, 9))

file_button = ctk.CTkButton(
    button_row,
    text="▧  UPLOAD FILE",
    width=190,
    height=40,
    corner_radius=10,
    fg_color=COLORS["border"],
    hover_color="#29435A",
    text_color=COLORS["text"],
    font=ctk.CTkFont(size=12, weight="bold"),
    command=upload_from_file,
)
file_button.pack()

status_card = ctk.CTkFrame(
    shell,
    fg_color=COLORS["surface"],
    border_width=1,
    border_color=COLORS["border"],
    corner_radius=14,
)
status_card.pack(fill="x", pady=(0, 18))

status_label = ctk.CTkLabel(
    status_card,
    text="READY  •  AWAITING COMMAND",
    font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
    text_color=COLORS["muted"],
    anchor="w",
)
status_label.pack(fill="x", padx=18, pady=(14, 7))

progress_bar = ctk.CTkProgressBar(
    status_card,
    height=7,
    corner_radius=5,
    fg_color=COLORS["border"],
    progress_color=COLORS["green"],
)
progress_bar.pack(fill="x", padx=18, pady=(0, 14))
progress_bar.set(0)

history_header = ctk.CTkFrame(shell, fg_color="transparent")
history_header.pack(fill="x", pady=(0, 8))

ctk.CTkLabel(
    history_header,
    text="RECENT UPLOADS",
    font=ctk.CTkFont(size=15, weight="bold"),
    text_color=COLORS["text"],
).pack(side="left")

history_count_label = ctk.CTkLabel(
    history_header,
    text="0 UPLOADS",
    font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
    text_color=COLORS["green"],
)
history_count_label.pack(side="left", padx=12)

clear_button = ctk.CTkButton(
    history_header,
    text="CLEAR",
    width=68,
    height=28,
    corner_radius=8,
    fg_color="transparent",
    hover_color="#341622",
    text_color=COLORS["red"],
    font=ctk.CTkFont(size=10, weight="bold"),
    command=clear_history,
)
clear_button.pack(side="right")

history_frame = ctk.CTkScrollableFrame(
    shell,
    fg_color=COLORS["surface"],
    border_width=1,
    border_color=COLORS["border"],
    corner_radius=14,
)
history_frame.pack(fill="both", expand=True)

footer = ctk.CTkLabel(
    shell,
    text="CTRL + SHIFT + S   •   FULL SCREEN CAPTURE",
    font=ctk.CTkFont(family="Consolas", size=10, weight="bold"),
    text_color=COLORS["muted"],
)
footer.pack(pady=(12, 0))

history_entries = load_history()
upload_in_progress = False
update_key_status()
render_history()
app.mainloop()
