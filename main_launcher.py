import subprocess
import sys
import json
import tkinter as tk
from tkinter import ttk, messagebox
import os
from datetime import datetime
import logging

CONFIG_FILE = "config.json"
LOG_ROOT = "./log"
RECORD_DIR = "./record"
USER_DATA = "./user_data"
ASSET_DIR = "./assets"
SPLASH_W = 450
SPLASH_H = 260
SPLASH_BG = f"{ASSET_DIR}/splash_bg.png"
SPLASH_LOGO = f"{ASSET_DIR}/logo.png"
for d in [LOG_ROOT, RECORD_DIR, USER_DATA, ASSET_DIR]:
    os.makedirs(d, exist_ok=True)

# 全局配置变量
proxy_enable = False
proxy_type = "http"
proxy_host = "127.0.0.1"
proxy_port = "7890"
login_success = False
user_info = {}

def init_log(name):
    t = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(LOG_ROOT, f"{t}-{name}.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[logging.FileHandler(log_path, encoding="utf-8"), logging.StreamHandler(sys.stdout)]
    )
    return logging.getLogger("Launcher")

def load_cfg():
    global proxy_enable, proxy_type, proxy_host, proxy_port
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    else:
        cfg = {
            "users": {}, "last_login": "", "auto_login": False, "server": "127.0.0.1:8080",
            "proxy":{"enable":False,"type":"http","host":"127.0.0.1","port":"7890"},
            "log_path": LOG_ROOT
        }
        save_cfg(cfg)
    p = cfg.get("proxy", {})
    proxy_enable = p["enable"]
    proxy_type = p["type"]
    proxy_host = p["host"]
    proxy_port = p["port"]
    return cfg

def save_cfg(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, indent=2, fp=f, ensure_ascii=False)

# 内置启动画面
def run_splash():
    root = tk.Tk()
    root.geometry(f"{SPLASH_W}x{SPLASH_H}")
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.config(bg="#10141c")
    x = (root.winfo_screenwidth() - SPLASH_W) // 2
    y = (root.winfo_screenheight() - SPLASH_H) // 2
    root.geometry(f"{SPLASH_W}x{SPLASH_H}+{x}+{y}")
    canvas = tk.Canvas(root, width=SPLASH_W, height=SPLASH_H, bg="#10141c", highlightthickness=0)
    canvas.pack()
    if os.path.exists(SPLASH_BG):
        from PIL import Image, ImageTk
        bg_img = Image.open(SPLASH_BG).resize((SPLASH_W, SPLASH_H), Image.Resampling.LANCZOS)
        bg_tk = ImageTk.PhotoImage(bg_img)
        canvas.create_image(0,0,image=bg_tk, anchor="nw")
    if os.path.exists(SPLASH_LOGO):
        from PIL import Image, ImageTk
        raw = Image.open(SPLASH_LOGO)
        scale = 90 / raw.height
        nw, nh = int(raw.width*scale), int(raw.height*scale)
        logo = raw.resize((nw, nh), Image.Resampling.LANCZOS)
        logo_tk = ImageTk.PhotoImage(logo)
        canvas.create_image(SPLASH_W//2, SPLASH_H//2-20, image=logo_tk, anchor="center")
    canvas.create_text(SPLASH_W//2, SPLASH_H//2+60, text="Vision System Loading", fill="#ccc", font=("微软雅黑",11))
    canvas.create_text(SPLASH_W//2, SPLASH_H-30, text="由InvincibleHacker开发", fill="#777777", font=("微软雅黑",9))
    root.after(3000, root.destroy)
    root.mainloop()

# 内置登录窗口
def login_window():
    global login_success, user_info, proxy_enable, proxy_type, proxy_host, proxy_port
    cfg = load_cfg()
    root = tk.Tk()
    root.geometry("480x420")
    root.title("登录 | 注册 | 代理")
    uname_var = tk.StringVar(value=cfg["last_login"])
    pwd_var = tk.StringVar()
    srv_var = tk.StringVar(value=cfg["server"])
    auto_var = tk.BooleanVar(value=cfg["auto_login"])
    pro_en = tk.BooleanVar(value=proxy_enable)
    pro_tp = tk.StringVar(value=proxy_type)
    pro_h = tk.StringVar(value=proxy_host)
    pro_p = tk.StringVar(value=proxy_port)
    main = ttk.Frame(root, padding=12)
    main.pack(fill="both", expand=True)
    row=0
    ttk.Label(main, text="====登录====", font=("",10,"bold")).grid(row=row,column=0,columnspan=2,pady=(0,6))
    row+=1
    ttk.Label(main, text="用户名:").grid(row=row,column=0,sticky="w")
    ttk.Combobox(main, textvariable=uname_var, width=26, values=list(cfg["users"].keys()) if cfg["users"] else ["无用户"]).grid(row=row,column=1,padx=6)
    row+=1
    ttk.Label(main, text="密码:").grid(row=row,column=0,sticky="w")
    ttk.Entry(main, textvariable=pwd_var, show="*", width=28).grid(row=row,column=1)
    row+=1
    ttk.Label(main, text="服务端:").grid(row=row,column=0,sticky="w")
    ttk.Entry(main, textvariable=srv_var, width=28).grid(row=row,column=1)
    row+=1
    ttk.Checkbutton(main, text="自动登录", variable=auto_var).grid(row=row,column=0,columnspan=2,sticky="w")
    row+=1
    ttk.Separator(main, orient="horizontal").grid(row=row,column=0,columnspan=2,pady=8)
    row+=1
    ttk.Label(main, text="====代理====", font=("",10,"bold")).grid(row=row,column=0,columnspan=2)
    row+=1
    ttk.Checkbutton(main, text="启用代理", variable=pro_en).grid(row=row,column=0,columnspan=2,sticky="w")
    row+=1
    ttk.Label(main, text="类型").grid(row=row,column=0,sticky="w")
    ttk.Combobox(main, textvariable=pro_tp, values=["http","socks5"], width=14).grid(row=row,column=1)
    row+=1
    ttk.Label(main, text="地址").grid(row=row,column=0,sticky="w")
    ttk.Entry(main, textvariable=pro_h, width=28).grid(row=row,column=1)
    row+=1
    ttk.Label(main, text="端口").grid(row=row,column=0,sticky="w")
    ttk.Entry(main, textvariable=pro_p, width=28).grid(row=row,column=1)
    row+=1
    def save_proxy():
        global proxy_enable, proxy_type, proxy_host, proxy_port
        cfg["proxy"]["enable"] = pro_en.get()
        cfg["proxy"]["type"] = pro_tp.get()
        cfg["proxy"]["host"] = pro_h.get().strip()
        cfg["proxy"]["port"] = pro_p.get().strip()
        save_cfg(cfg)
        proxy_enable = cfg["proxy"]["enable"]
        proxy_type = cfg["proxy"]["type"]
        proxy_host = cfg["proxy"]["host"]
        proxy_port = cfg["proxy"]["port"]
        messagebox.showinfo("提示","代理已保存")
    ttk.Button(main, text="保存代理", command=save_proxy).grid(row=row,column=0,columnspan=2,pady=4)
    row+=1
    ttk.Separator(main, orient="horizontal").grid(row=row,column=0,columnspan=2,pady=8)
    row+=1
    btn_fr = ttk.Frame(main)
    btn_fr.grid(row=row,column=0,columnspan=2)
    def reg_win():
        w = tk.Toplevel(root)
        w.geometry("340x220")
        w.title("注册")
        w.transient(root)
        un = tk.StringVar()
        pw = tk.StringVar()
        sv = tk.StringVar(value=srv_var.get())
        ttk.Label(w,text="用户名").place(x=25,y=25)
        ttk.Entry(w,textvariable=un,width=22).place(x=90,y=25)
        ttk.Label(w,text="密码").place(x=25,y=65)
        ttk.Entry(w,textvariable=pw,show="*",width=22).place(x=90,y=65)
        ttk.Label(w,text="服务端").place(x=25,y=100)
        ttk.Entry(w,textvariable=sv,width=22).place(x=90,y=100)
        def do_reg():
            u = un.get().strip()
            p = pw.get().strip()
            s = sv.get().strip()
            if not u or not p or not s:
                messagebox.showerror("错误","不能为空")
                return
            import requests
            sess = requests.Session()
            if proxy_enable:
                sess.proxies = {"http":f"{proxy_type}://{proxy_host}:{proxy_port}","https":f"{proxy_type}://{proxy_host}:{proxy_port}"}
            try:
                res = sess.post(f"http://{s}/api/register", json={"username":u,"password":p}, timeout=5).json()
                if res["code"] !=0:
                    messagebox.showerror("注册失败", res["msg"])
                    return
            except Exception as e:
                messagebox.showerror("网络错误", str(e))
                return
            messagebox.showinfo("成功","注册完成")
            w.destroy()
        ttk.Button(w,text="确认注册",command=do_reg).place(x=100,y=140,width=140)
    def do_login():
        u = uname_var.get().strip()
        p = pwd_var.get().strip()
        s = srv_var.get().strip()
        if not u or not p or not s:
            messagebox.showerror("错误","信息不全")
            return
        import requests
        sess = requests.Session()
        if proxy_enable:
            sess.proxies = {"http":f"{proxy_type}://{proxy_host}:{proxy_port}","https":f"{proxy_type}://{proxy_host}:{proxy_port}"}
        try:
            ret = sess.post(f"http://{s}/api/login", json={"username":u,"password":p}, timeout=5).json()
            if ret["code"] !=0:
                messagebox.showerror("登录失败", ret["msg"])
                return
        except Exception as e:
            messagebox.showerror("连接失败", str(e))
            return
        cfg["last_login"] = u
        cfg["server"] = s
        cfg["auto_login"] = auto_var.get()
        save_cfg(cfg)
        global login_success, user_info
        login_success = True
        user_info = {"username":u,"server":s,"token":ret["data"]["token"]}
        root.destroy()
    ttk.Button(btn_fr, text="登录", command=do_login).pack(side="left",padx=4)
    ttk.Button(btn_fr, text="注册", command=reg_win).pack(side="left",padx=4)
    root.mainloop()

# ========== 子进程启动函数 ==========
def start_render():
    args = [sys.executable, "render_backend.py", f"--user={user_info['username']}", f"--server={user_info['server']}", f"--token={user_info['token']}"]
    return subprocess.Popen(args, creationflags=subprocess.CREATE_NEW_CONSOLE)

def open_cam():
    args = [sys.executable, "sub_camera.py", f"--user={user_info['username']}"]
    subprocess.Popen(args, creationflags=subprocess.CREATE_NEW_CONSOLE)

def open_virtual_cam():
    args = [sys.executable, "virtual_cam_engine.py", f"--user={user_info['username']}", "--yolo=1", "--mode=pose"]
    subprocess.Popen(args, creationflags=subprocess.CREATE_NEW_CONSOLE)

def open_window_capture():
    args = [sys.executable, "window_capture_engine.py", f"--user={user_info['username']}", "--yolo=1"]
    subprocess.Popen(args, creationflags=subprocess.CREATE_NEW_CONSOLE)

def open_stream_url():
    import webbrowser
    webbrowser.open(f"http://{user_info['server']}/api/stream/live")

# ========== 主面板UI ==========
class MainUI:
    def __init__(self, root, render_proc):
        self.root = root
        self.render_proc = render_proc
        self.root.geometry("1100x720")
        self.root.title("Vision 主调度面板")
        self.root.minsize(900, 600)
        pan = ttk.PanedWindow(root, orient="horizontal")
        pan.pack(fill="both", expand=True)
        side = ttk.Frame(pan, width=200, padding=10)
        pan.add(side, weight=0)
        main_fr = ttk.Frame(pan, padding=20)
        pan.add(main_fr, weight=1)
        self.build_sidebar(side)
        self.build_main(main_fr)

    def build_sidebar(self, side_root):
        ttk.Label(side_root, text=f"用户：{user_info['username']}", font=("", 11, "bold")).pack(pady=(0, 10), anchor="w")
        ttk.Separator(side_root).pack(fill="x", pady=8)
        ttk.Label(side_root, text="功能入口", font=("", 10, "bold")).pack(anchor="w", pady=(0, 4))
        ttk.Button(side_root, text="摄像头预览录制", command=open_cam).pack(fill="x", pady=4)
        ttk.Button(side_root, text="虚拟摄像头注入", command=open_virtual_cam).pack(fill="x", pady=4)
        ttk.Button(side_root, text="窗口捕获注入", command=open_window_capture).pack(fill="x", pady=4)
        ttk.Button(side_root, text="查看直播流", command=open_stream_url).pack(fill="x", pady=4)
        ttk.Separator(side_root).pack(fill="x", pady=10)
        ttk.Button(side_root, text="退出程序", command=self.exit_all).pack(fill="x", pady=4, side="bottom")

    def build_main(self, main_root):
        ttk.Label(main_root, text="系统运行状态", font=("", 14, "bold")).pack(anchor="w", pady=(0, 15))
        status_frame = ttk.LabelFrame(main_root, text="核心服务", padding=15)
        status_frame.pack(fill="x", pady=6)
        status_items = [
            ("渲染后端", f"运行中  PID: {self.render_proc.pid}" if self.render_proc else "未启动"),
            ("服务端地址", user_info["server"]),
            ("录像保存目录", RECORD_DIR),
            ("渲染后端", "Vulkan GPU 加速")
        ]
        for idx, (label, value) in enumerate(status_items):
            ttk.Label(status_frame, text=label, width=12, foreground="#666").grid(row=idx, column=0, sticky="w", pady=6)
            ttk.Label(status_frame, text=value).grid(row=idx, column=1, sticky="w", padx=10)
        ttk.Label(main_root, text="快捷操作", font=("", 14, "bold")).pack(anchor="w", pady=(25, 15))
        btn_row = ttk.Frame(main_root)
        btn_row.pack(fill="x")
        ttk.Button(btn_row, text="打开摄像头预览", command=open_cam).pack(side="left", padx=(0, 10), ipadx=15, ipady=8)
        ttk.Button(btn_row, text="重启渲染后端", command=self.restart_render).pack(side="left", padx=10, ipadx=15, ipady=8)

    def restart_render(self):
        if self.render_proc:
            self.render_proc.terminate()
        self.render_proc = start_render()
        messagebox.showinfo("提示", f"渲染后端已重启，新PID: {self.render_proc.pid}")

    def exit_all(self):
        if self.render_proc:
            self.render_proc.terminate()
        self.root.destroy()

if __name__ == "__main__":
    logger = init_log("launcher")
    logger.info("启动5秒加载画面")
    run_splash()
    logger.info("弹出登录窗口")
    login_window()
    if not login_success:
        logger.info("未登录，退出程序")
        sys.exit(0)
    logger.info(f"{user_info['username']} 登录成功")
    try:
        render_proc = start_render()
    except:
        render_proc = None
    main_win = tk.Tk()
    MainUI(main_win, render_proc)
    main_win.mainloop()
    if render_proc:
        render_proc.terminate()
