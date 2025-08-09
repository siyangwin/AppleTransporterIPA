import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import webbrowser
import json

CONFIG_FILE = "uploader_config.json"
APP_STORE_CONNECT_URL = "https://appstoreconnect.apple.com/apps"

# === 读取配置 ===
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

# === 保存配置 ===
def save_config():
    config = {
        "ipa_dir": entry_dir.get().strip(),
        "apple_id": entry_id.get().strip(),
        "app_password": entry_pwd.get().strip(),
        "transporter_path": entry_transporter.get().strip()
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

# === 选择 IPA 文件夹 ===
def choose_dir():
    folder = filedialog.askdirectory()
    if folder:
        entry_dir.delete(0, tk.END)
        entry_dir.insert(0, folder)

# === 选择 Transporter 路径 ===
def choose_transporter():
    file_path = filedialog.askopenfilename(filetypes=[("CMD 文件", "*.cmd"), ("所有文件", "*.*")])
    if file_path:
        entry_transporter.delete(0, tk.END)
        entry_transporter.insert(0, file_path)

# === 上传 IPA ===
def upload_ipa():
    ipa_dir = entry_dir.get().strip()
    apple_id = entry_id.get().strip()
    app_password = entry_pwd.get().strip()
    transporter_path = entry_transporter.get().strip()

    if not os.path.exists(transporter_path):
        messagebox.showerror("错误", f"找不到 Transporter 工具:\n{transporter_path}")
        return

    if not ipa_dir or not os.path.isdir(ipa_dir):
        messagebox.showerror("错误", "请选择有效的 IPA 文件夹")
        return

    ipa_files = [f for f in os.listdir(ipa_dir) if f.lower().endswith(".ipa")]
    if not ipa_files:
        messagebox.showerror("错误", "未找到任何 IPA 文件")
        return

    ipa_files.sort(key=lambda f: os.path.getmtime(os.path.join(ipa_dir, f)), reverse=True)
    latest_ipa = os.path.join(ipa_dir, ipa_files[0])

    log_box.insert(tk.END, f"找到最新 IPA: {latest_ipa}\n")
    log_box.insert(tk.END, "开始上传...\n")
    log_box.see(tk.END)
    root.update()

    def run_upload():
        cmd = [
            transporter_path,
            "-m", "upload",
            "-f", latest_ipa,
            "-u", apple_id,
            "-p", app_password,
            "-v", "informational"
        ]
        return subprocess.call(cmd, shell=True)

    if run_upload() != 0:
        log_box.insert(tk.END, "第一次上传失败，正在重试...\n")
        root.update()
        if run_upload() != 0:
            messagebox.showerror("上传失败", "两次上传均失败，请检查日志")
            return

    log_box.insert(tk.END, "上传成功！\n")
    root.update()
    webbrowser.open(APP_STORE_CONNECT_URL)

# === GUI ===
root = tk.Tk()
root.title("Apple Transporter IPA 上传工具")
root.geometry("650x420")

config = load_config()

tk.Label(root, text="IPA 文件夹:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
entry_dir = tk.Entry(root, width=50)
entry_dir.grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="浏览", command=choose_dir).grid(row=0, column=2, padx=5)

tk.Label(root, text="Apple ID:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
entry_id = tk.Entry(root, width=50)
entry_id.grid(row=1, column=1, padx=5, pady=5, columnspan=2)

tk.Label(root, text="App 专用密码:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
entry_pwd = tk.Entry(root, width=50, show="*")
entry_pwd.grid(row=2, column=1, padx=5, pady=5, columnspan=2)

tk.Label(root, text="Transporter 路径:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
entry_transporter = tk.Entry(root, width=50)
entry_transporter.grid(row=3, column=1, padx=5, pady=5)
tk.Button(root, text="选择", command=choose_transporter).grid(row=3, column=2, padx=5)

tk.Button(root, text="上传 IPA", command=upload_ipa, bg="green", fg="white", width=20).grid(row=4, column=0, columnspan=3, pady=10)

log_box = tk.Text(root, height=12)
log_box.grid(row=5, column=0, columnspan=3, padx=5, pady=5)

# === 加载配置 ===
entry_dir.insert(0, config.get("ipa_dir", ""))
entry_id.insert(0, config.get("apple_id", ""))
entry_pwd.insert(0, config.get("app_password", ""))
entry_transporter.insert(0, config.get("transporter_path", ""))

# === 退出保存配置 ===
def on_close():
    save_config()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

root.mainloop()
