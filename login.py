import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import requests
import sys

CONFIG_FILE = "config.json"
LOG_ROOT = "./log"
os.makedirs(LOG_ROOT, exist_ok)

proxy_enable = False
proxy_type = "http"
proxy_host = "127.0.0.1"
proxy_port = "7890"

def load_cfg():
    global proxy_enable, proxy_type, proxy_host, proxy_port
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    else:
        cfg = {
            "users": {},
            "last_login": "",
            "auto_login": False,
            "server": "127.0.0.1:8080",
            "proxy":{"enable":False,"type":"http","host":"127.0.0.1","port":"7890"},
            "log_path": LOG_ROOT
        }
        save_cfg(cfg)
    p = cfg.get("proxy",{})
    proxy_enable = p["enable"]
    proxy_type = p["type"]
    proxy_host = p["host"]
    proxy_port = p["port"]
    return cfg

def save_cfg(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, indent=2, fp=f, ensure_ascii=False)

def get_session():
    sess = requests.Session()
    if proxy_enable:
        url = f"{proxy_type}://{proxy_host}:{proxy_port}"
        sess.proxies = {"http":url, "https":url}
    return sess

class LoginWindow:
    def __init__(self):
        self.login_ok = False
        self.user_data = {}
        self.cfg = load_cfg()
        self.root = tk.Tk()
        self.root.geometry("480x420")
        self.root.title("登录 | 注册 | 网络代理")
        self.uname_var = tk.StringVar(value=self.cfg["last_login"])
        self.pwd_var = tk.StringVar()
        self.srv_var = tk.StringVar(value=self.cfg["server"])
        self.auto_var = tk.BooleanVar(value=self.cfg["auto_login"])
        self.pro_en = tk.BooleanVar(value=proxy_enable)
        self.pro_tp = tk.StringVar(value=proxy_type)
        self.pro_h = tk.StringVar(value=proxy_host)
        self.pro_p = tk.StringVar(value=proxy_port)
        self.build()
        self.root.mainloop()

    def build(self):
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill="both", expand=True)
        row = 0
        ttk.Label(main, text="==== 登录区域 ====", font=("",10,"bold")).grid(row=row,column=0,columnspan=2,pady=(0,6))
        row +=1
        ttk.Label(main, text="已有用户:").grid(row=row,column=0,sticky="w")
        cb = ttk.Combobox(main, textvariable=self.uname_var, width=26)
        cb["values"] = list(self.cfg["users"].keys()) if self.cfg["users"] else ["无用户"]
        cb.grid(row=row,column=1,padx=6)
        row +=1
        ttk.Label(main, text="密码:").grid(row=row,column=0,sticky="w")
        ttk.Entry(main, textvariable=self.pwd_var, show="*", width=28).grid(row=row,column=1)
        row +=1
        ttk.Label(main, text="服务端地址:").grid(row=row,column=0,sticky="w")
        ttk.Entry(main, textvariable=self.srv_var, width=28).grid(row=row,column=1)
        row +=1
        ttk.Checkbutton(main, text="自动登录", variable=self.auto_var).grid(row=row,column=0,columnspan=2,sticky="w")
        row +=1
        ttk.Separator(main, orient="horizontal").grid(row=row,column=0,columnspan=2,pady=8)
        row +=1
        ttk.Label(main, text="==== 网络代理 ====", font=("",10,"bold")).grid(row=row,column=0,columnspan=2)
        row +=1
        ttk.Checkbutton(main, text="启用代理", variable=self.pro_en).grid(row=row,column=0,columnspan=2,sticky="w")
        row +=1
        ttk.Label(main, text="类型:").grid(row=row,column=0,sticky="w")
        ttk.Combobox(main, textvariable=self.pro_tp, values=["http","socks5"], width=14).grid(row=row,column=1)
        row +=1
        ttk.Label(main, text="地址:").grid(row=row,column=0,sticky="w")
        ttk.Entry(main, textvariable=self.pro_h, width=28).grid(row=row,column=1)
        row +=1
        ttk.Label(main, text="端口:").grid(row=row,column=0,sticky="w")
        ttk.Entry(main, textvariable=self.pro_p, width=28).grid(row=row,column=1)
        row +=1
        def save_proxy():
            global proxy_enable, proxy_type, proxy_host, proxy_port
            self.cfg["proxy"]["enable"] = self.pro_en.get()
            self.cfg["proxy"]["type"] = self.pro_tp.get()
            self.cfg["proxy"]["host"] = self.pro_h.get().strip()
            self.cfg["proxy"]["port"] = self.pro_p.get().strip()
            save_cfg(self.cfg)
            proxy_enable = self.cfg["proxy"]["enable"]
            proxy_type = self.cfg["proxy"]["type"]
            proxy_host = self.cfg["proxy"]["host"]
            proxy_port = self.cfg["proxy"]["port"]
            messagebox.showinfo("提示","代理已保存")
        ttk.Button(main, text="保存代理", command=save_proxy).grid(row=row,column=0,columnspan=2,pady=4)
        row +=1
        ttk.Separator(main, orient="horizontal").grid(row=row,column=0,columnspan=2,pady=8)
        row +=1
        btn_fr = ttk.Frame(main)
        btn_fr.grid(row=row,column=0,columnspan=2)
        ttk.Button(btn_fr, text="登录", command=self.do_login).pack(side="left",padx=4)
        ttk.Button(btn_fr, text="注册", command=self.open_reg).pack(side="left",padx=4)

    def open_reg(self):
        win = tk.Toplevel(self.root)
        win.geometry("340x220")
        win.title("注册账号")
        win.transient(self.root)
        u = tk.StringVar()
        p = tk.StringVar()
        s = tk.StringVar(value=self.srv.get())
        ttk.Label(win, text="用户名:").place(25,25)
        ttk.Entry(win, textvariable=u, width=22).place(90,25)
        ttk.Label(win, text="密码:").place(25,65)
        ttk.Entry(win, textvariable=p, show="*", width=22).place(90,65)
        ttk.Label(win, text="服务端:").place(25,100)
        ttk.Entry(win, textvariable=s, width=22).place(90,100)
        def reg():
            un = u.get().strip()
            pw = p.get().strip()
            sv = s.get().strip()
            if not un or not pw or not sv:
                messagebox.showerror("错误","不能为空")
                return
            sess = get_session()
            try:
                res = sess.post(f"http://{sv}/api/register", json={"username":un,"password":pw}, timeout=5).json()
                if res["code"] !=0:
                    messagebox.showerror("注册失败", res["msg"])
                    return
            except Exception as e:
                messagebox.showerror("网络错误", str(e))
                return
            messagebox.showinfo("成功","注册完成")
            win.destroy()
        ttk.Button(win, text="确认注册", command=reg).place(100,140,width=140)

    def do_login(self):
        un = self.uname_var.get().strip()
        pw = self.pwd_var.get().strip()
        sv = self.srv_var.get().strip()
        if not un or not pw or not sv:
            messagebox.showerror("错误","信息不全")
            return
        sess = get_session()
        try:
            ret = sess.post(f"http://{sv}/api/login", json={"username":un,"password":pw}, timeout=5).json()
            if ret["code"] !=0:
                messagebox.showerror("登录失败", ret["msg"])
                return
        except Exception as e:
            messagebox.showerror("连接失败", str(e))
            return
        self.cfg["last_login"] = un
        self.cfg["server"] = sv
        self.cfg["auto_login"] = self.auto_var.get()
        save_cfg(self.cfg)
        self.login_ok = True
        self.user_data = {
            "username":un,
            "server":sv,
            "token":ret["data"]["token"],
            "auto":self.auto_var.get()
        }
        self.root.destroy()

if __name__ == "__main__":
    win = LoginWindow()
    if win.login_ok:
        import json
        print(json.dumps(win.user_data, ensure_ascii=False))
        sys.exit(0)
    else:
        sys.exit(1)
