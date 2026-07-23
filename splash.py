import tkinter as tk
from PIL import Image, ImageTk
import os

SPLASH_W = 450
SPLASH_H = 260
ASSET_DIR = "./assets"
SPLASH_BG = f"{ASSET_DIR}/splash_bg.png"
SPLASH_LOGO = f"{ASSET_DIR}/logo.png"
os.makedirs(ASSET_DIR, exist_ok)

class SplashApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry(f"{SPLASH_W}x{SPLASH_H}")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.config(bg="#10141c")
        x = (self.root.winfo_screenwidth() - SPLASH_W) // 2
        y = (self.root.winfo_screenheight() - SPLASH_H) // 2
        self.root.geometry(f"{SPLASH_W}x{SPLASH_H}+{x}+{y}")
        self.canvas = tk.Canvas(self.root, width=SPLASH_W, height=SPLASH_H, bg="#10141c", highlightthickness=0)
        self.canvas.pack()
        self.load_img()
        self.root.after(3000, self.close_splash)
        self.root.mainloop()

    def load_img(self):
        if os.path.exists(SPLASH_BG):
            bg = Image.open(SPLASH_BG).resize((SPLASH_W, SPLASH_H), Image.Resampling.LANCZOS)
            self.bg_tk = ImageTk.PhotoImage(bg)
            self.canvas.create_image(0,0,image=self.bg_tk,anchor="nw")
        if os.path.exists(SPLASH_LOGO):
            raw = Image.open(SPLASH_LOGO)
            scale = 90 / raw.height
            nw = int(raw.width * scale)
            nh = int(raw.height * scale)
            logo = raw.resize((nw, nh), Image.Resampling.LANCZOS)
            self.logo_tk = ImageTk.PhotoImage(logo)
            self.canvas.create_image(SPLASH_W//2, SPLASH_H//2-20, image=self.logo_tk, anchor="center")
        self.canvas.create_text(SPLASH_W//2, SPLASH_H//2+60, text="Vision System Loading", fill="#ccc", font=("微软雅黑",11))
        self.canvas.create_text(SPLASH_W//2, SPLASH_H-30, text="由InvincibleHacker开发", fill="#777777", font=("微软雅黑",9))

    def close_splash(self):
        self.root.destroy()

if __name__ == "__main__":
    SplashApp()
