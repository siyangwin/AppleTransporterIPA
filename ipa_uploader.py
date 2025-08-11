import os
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import webbrowser
import json

CONFIG_FILE = "uploader_config.json"
CONFIG_All_FILE = "uploader_all_config.json"
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

# === 加载所有记录 ===
# 这个函数用于加载所有记录，供下拉框选择
def load_all_records():
    """加载所有记录用于下拉框"""
    try:
        if os.path.exists(CONFIG_All_FILE):
            with open(CONFIG_All_FILE, "r", encoding="utf-8") as f:
                records = json.load(f)
                return records if isinstance(records, list) else []
    except Exception as e:
        print(f"加载记录失败: {e}")
    return []

# === 初始化下拉框 ===
# === 下拉框选择变化时触发的事件 ===
def on_select_record(event):
    """下拉框选择变化时触发，填充数据到文本框"""
    selected = record_combobox.get()
    if not selected:
        return
        
    # 查找选中的记录
    records = load_all_records()
    for record in records:
        # 用team_id和remark组合显示，所以需要拆分判断
        display_text = f"{record.get('team_id')} - {record.get('remark', '无备注')}"
        if display_text == selected:
            # 填充数据到各个文本框
            entry_team_id.delete(0, tk.END)
            entry_team_id.insert(0, record.get("team_id", ""))
            
            entry_remark.delete(0, tk.END)
            entry_remark.insert(0, record.get("remark", ""))
            
            entry_path.delete(0, tk.END)
            entry_path.insert(0, record.get("ipa_path", ""))
            
            entry_id.delete(0, tk.END)
            entry_id.insert(0, record.get("apple_id", ""))
            
            entry_pwd.delete(0, tk.END)
            entry_pwd.insert(0, record.get("app_password", ""))
            
            entry_transporter.delete(0, tk.END)
            entry_transporter.insert(0, record.get("transporter_path", ""))
            break

def refresh_dropdown():
    """刷新下拉框选项"""
    # 先清空现有选项
    record_combobox['values'] = []
    
    # 加载并添加新选项
    records = load_all_records()
    if records:
        # 用team_id+remark作为显示文本，方便识别
        display_values = [
            f"{record.get('team_id')} - {record.get('remark', '无备注')}" 
            for record in records
        ]
        record_combobox['values'] = display_values

# === 保存配置 ===
def save_config():
     # 先定义当前记录数据
    config = {
        # "ipa_dir": entry_dir.get().strip(),
        "team_id": entry_team_id.get().strip(),
        "remark": entry_remark.get().strip(),
        "ipa_path": entry_path.get().strip(),
        "apple_id": entry_id.get().strip(),
        "app_password": entry_pwd.get().strip(),
        "transporter_path": entry_transporter.get().strip()
    }
    # 保存单个配置
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    #current_team_id = entry_team_id.get().strip()
    current_team_id = config["team_id"]
    # 验证team_id不为空
    if not current_team_id:
        print("错误：team_id不能为空，无法执行保存操作，先临时存储")
        return False
    
    #读取已有记录（文件不存在则自动创建空列表）
    all_records = []
    if os.path.exists(CONFIG_All_FILE):
        try:
            with open(CONFIG_All_FILE, "r", encoding="utf-8") as f:
                all_records = json.load(f)
                # 确保是列表格式
                if not isinstance(all_records, list):
                    all_records = []
        except (json.JSONDecodeError, Exception) as e:
            print(f"读取记录失败，将重新创建文件: {str(e)}")
            all_records = []
            #return

    # 添加新的记录 查找是否存在相同team_id的记录
    existing_index = None
    for i, record in enumerate(all_records):
        if record.get("team_id") == current_team_id:
            existing_index = i
            break

    # 如果存在，更新记录
    if existing_index is not None:
        # 更新记录
        all_records[existing_index] = config
    else:
        # 如果不存在，添加新记录
        all_records.append(config)

     #  保存回文件
    try:
        with open(CONFIG_All_FILE, "w", encoding="utf-8") as f:
            json.dump(all_records, f, ensure_ascii=False, indent=2)
        print(f"操作完成，记录已保存到 {CONFIG_All_FILE}")
        return True
    except Exception as e:
        print(f"保存记录失败: {str(e)}")
        return False

# === 选择 IPA 文件夹 ===
# def choose_dir():
#     folder = filedialog.askdirectory()
#     if folder:
#         entry_dir.delete(0, tk.END)
#         entry_dir.insert(0, folder)

# === 选择 IPA 文件 ===
def choose_path():
    folder = filedialog.askopenfilename(filetypes=[("Apple Ipa", "*.ipa"), ("所有文件", "*.*")])
    if folder:
            # 先将输入框临时改为可编辑状态
            entry_path.config(state=tk.NORMAL)
            # 清空现有内容
            entry_path.delete(0, tk.END)
            # 将生成的 plist 文件路径填入输入框
            entry_path.insert(0, folder)
            # 重新设置为禁用状态
            entry_path.config(state=tk.DISABLED)

# === 选择 Transporter 路径 ===
def choose_transporter():
    file_path = filedialog.askopenfilename(filetypes=[("CMD 文件", "*.cmd"), ("所有文件", "*.*")])
    if file_path:
        # 先将输入框临时改为可编辑状态
        entry_transporter.config(state=tk.NORMAL)
        # 清空现有内容
        entry_transporter.delete(0, tk.END)
        # 将生成的 plist 文件路径填入输入框
        entry_transporter.insert(0, file_path)
        # 重新设置为禁用状态
        entry_transporter.config(state=tk.DISABLED)


# === 选择 AppStoreInfo 文件 ===
# def choose_appStoreInfo():
#     folder = filedialog.askopenfilename(filetypes=[("Apple Plist", "*.Plist"), ("所有文件", "*.*")])
#     if folder:
#         AppStoreInfo_path.delete(0, tk.END)
#         AppStoreInfo_path.insert(0, folder)

# === 上传 IPA ===
def upload_ipa():

    # print(config)
    # return

    # ipa_dir = entry_dir.get().strip()
    # 获取IPA的具体文件路径
    ipa_path = entry_path.get().strip()
    # ipa_dir = os.path.dirname(ipa_path)
    #获取账号
    apple_id = entry_id.get().strip()
    #获取密码
    app_password = entry_pwd.get().strip()
    # 获取Transporter路径
    transporter_path = entry_transporter.get().strip()
   # 获取AppStoreInfo.plist文件路径
    appstore_info_path= AppStoreInfo_path.get().strip()
    # 获取团队ID
    team_id = entry_team_id.get().strip()
    #entry_remark = entry_remark.get().strip()

    if not os.path.exists(transporter_path):
        messagebox.showerror("错误", f"找不到 Transporter 工具:\n{transporter_path}")
        return

    # if not ipa_dir or not os.path.isdir(ipa_dir):
    #     messagebox.showerror("错误", "请选择有效的 IPA 文件夹")
    #     return
    
    # ipa_files = [f for f in os.listdir(ipa_dir) if f.lower().endswith(".ipa")]
    # if not ipa_files:
    #     messagebox.showerror("错误", "未找到任何 IPA 文件")
    #     return

    if not team_id:
        messagebox.showerror("错误", "请输入 团队 ID")
        return
    
    if not ipa_path:
        if not os.path.isfile(ipa_path):
            messagebox.showerror("错误", "请选择有效的 IPA 文件")
            return
        
    if not apple_id:
        messagebox.showerror("错误", "请输入 Apple ID")
        return
    
    if not app_password:
        messagebox.showerror("错误", "请输入 App 专用密码")
        return
    
    

    # ipa_files.sort(key=lambda f: os.path.getmtime(os.path.join(ipa_dir, f)), reverse=True)
    # latest_ipa = os.path.join(ipa_dir, ipa_files[0])

    latest_ipa = ipa_path

    log_box.insert(tk.END, f"找到IPA: {latest_ipa}\n")
    log_box.insert(tk.END, "正在检查IPA文件...\n")
    root.update()
   
    #根据IPA文件，生成AppStoreInfo.plist文件
    log_box.insert(tk.END, "正在根据IPA文件生成AppStoreInfo.plist...\n")
    root.update()


    # 要执行的同目录下的generate_appstoreinfo 生成Plist文件
    target_script = os.path.join(os.path.dirname(__file__), "generate_appstoreinfo.py")
    if not os.path.exists(target_script):
        messagebox.showerror("错误", f"找不到生成 AppStoreInfo.plist 的脚本:\n{target_script}")
        return
    
    # plist文件路径
    plist_file =  os.path.join(os.path.dirname(__file__), "AppStoreInfo.plist")
    
    
     # 检查plist文件是否存在，如果存在则删除
    if os.path.exists(plist_file):
        try:
            os.remove(plist_file)
            #print(f"已删除现有文件：{plist_file}")
            log_box.insert(tk.END, f"已删除现有文件：{plist_file}\n")
            root.update()
        except Exception as e:
            #print(f"删除文件 {plist_file} 失败：{str(e)}")
            log_box.insert(tk.END, f"删除文件 {plist_file} 失败：{str(e)}\n")
            root.update()
            # 退出程序
            #sys.exit(1)
            return

     # 执行目标Python脚本
   
   
    
    #python generate_appstoreinfo.py Fresh.ipa AppStoreInfo.plist
    #构建命令：python generate_appstoreinfo.py Fresh.ipa AppStoreInfo.plist
    cmd = [
        sys.executable,  # 使用当前Python解释器
        target_script,
        ipa_path,
        plist_file
    ]   
    
 #print(f"开始执行脚本：{target_script}")
    log_box.insert(tk.END, f"开始执行脚本：{target_script}\n")
    #print(f"执行命令：{' '.join(cmd)}")
    #log_box.insert(tk.END   , f"执行命令：{' '.join(cmd)}\n")
    root.update()

    
    try:
        # 关键修改：指定环境变量的编码为utf-8
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"  # 强制Python输出使用utf-8编码

        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__)),
            env=env,  # 传入修改后的环境变量
            encoding='utf-8',  # 明确指定编码
            errors='ignore'    # 忽略无法解码的字符
        )

        print(result)
        
        #打印命令输出
        #print("\n命令执行输出：")
        #print(result.stdout)

        log_box.insert(tk.END   , f"命令执行输出：\n{result.stdout}\n")
        root.update()
   

        # 检查plist文件是否生成
        if os.path.exists(plist_file):
            #print(f"\n成功生成文件：{plist_file}")
            #print(f"文件大小：{os.path.getsize(plist_file)} 字节")
            log_box.insert(tk.END, f"成功生成文件：{plist_file}。文件大小：{os.path.getsize(plist_file)} 字节\n")
            root.update()

            # 先将输入框临时改为可编辑状态
            AppStoreInfo_path.config(state=tk.NORMAL)
            # 清空现有内容
            AppStoreInfo_path.delete(0, tk.END)
            # 将生成的 plist 文件路径填入输入框
            AppStoreInfo_path.insert(0, plist_file)
            # 重新设置为禁用状态
            AppStoreInfo_path.config(state=tk.DISABLED)

            #AppStoreInfo.plist文件路径
            appstore_info_path = AppStoreInfo_path.get().strip()
           
        else:
            #print(f"\n错误：命令执行完成，但未生成 {plist_file} 文件")
            log_box.insert(tk.END, f"错误：命令执行完成，但未生成 {plist_file} 文件\n")
            #sys.exit(1)
            return

    except subprocess.CalledProcessError as e:
        print(f"\n命令执行失败，返回码：{e.returncode}")
        print("错误输出：")
        print(e.stderr)
        log_box.insert(tk.END, f"命令执行失败，返回码：{e.returncode}\n错误输出：\n{e.stderr}\n")
        #sys.exit(1)
        return
    except Exception as e:
        print(f"\n执行过程中发生错误：{str(e)}")
        log_box.insert(tk.END, f"执行过程中发生错误：{str(e)}\n")
        #sys.exit(1)
        return

    log_box.insert(tk.END, "开始上传...\n")
    log_box.see(tk.END)
    root.update()

    def run_upload():
        cmd = [
            transporter_path,
            "-m", "upload",
            "-assetFile", latest_ipa,
            "-u", apple_id,
            "-p", app_password,
            # "-v", "informational",
            "-assetDescription",appstore_info_path,  #使用 -assetDescription 以指定 AppStoreInfo.plist 文件（由 Xcode 生成）。  Windows无法读取ipa信息，需要手动创建。
            "-itc_provider", team_id  # 替换为你的 ITC Provider ID  团队ID 账号有多个团队，必须要这个参数
         ] 
        return subprocess.call(cmd, shell=True)

    log_box.insert(tk.END, "正在上传...\n")
    root.update()
    if run_upload() != 0:
        # log_box.insert(tk.END, "第一次上传失败，正在重试...\n")
        # root.update()
        # if run_upload() != 0:
        #     messagebox.showerror("上传失败", "两次上传均失败，请检查日志")
        #     return
        log_box.insert(tk.END, "上传失败，请检查日志\n")
        return

    log_box.insert(tk.END, "上传成功！\n")
    root.update()
    webbrowser.open(APP_STORE_CONNECT_URL)

# === GUI ===
root = tk.Tk()
root.title("Apple Transporter IPA 上传工具")
root.geometry("650x530")

config = load_config()

# 添加下拉框标签
tk.Label(root, text="选择记录:").grid(row=0, column=0, sticky="w", padx=5, pady=10)
# 创建下拉框
record_combobox = ttk.Combobox(root, width=48, state="readonly")
record_combobox.grid(row=0, column=1, padx=5, pady=5)
record_combobox.bind("<<ComboboxSelected>>", on_select_record)

# 添加刷新按钮（可选，用于手动刷新下拉框）
refresh_btn = tk.Button(root, text="刷新记录", command=refresh_dropdown)
refresh_btn.grid(row=0, column=2, padx=5, pady=10)


# tk.Label(root, text="IPA 文件夹:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
# entry_dir = tk.Entry(root, width=50)
# entry_dir.grid(row=0, column=1, padx=5, pady=5)
# tk.Button(root, text="浏览", command=choose_dir).grid(row=1, column=2, padx=5)

# team_id输入框
tk.Label(root, text="Team ID:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
entry_team_id = tk.Entry(root, width=50)
entry_team_id.grid(row=1, column=1, padx=5, pady=5)

# remark输入框
tk.Label(root, text="备注:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
entry_remark = tk.Entry(root, width=50)
entry_remark.grid(row=2, column=1, padx=5, pady=5)

# ipa_path输入框
tk.Label(root, text="IPA 文件:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
entry_path = tk.Entry(root, width=50,state=tk.DISABLED)
entry_path.grid(row=3, column=1, padx=5, pady=5)
tk.Button(root, text="浏览", command=choose_path).grid(row=3, column=2, padx=5)

tk.Label(root, text="AppStoreInfo 文件[自动生成]:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
AppStoreInfo_path = tk.Entry(root, width=50,state=tk.DISABLED) # 关键：添加 state 参数
AppStoreInfo_path.grid(row=4, column=1, padx=5, pady=5)

# apple_id输入框
tk.Label(root, text="Apple ID:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
entry_id = tk.Entry(root, width=50)
entry_id.grid(row=5, column=1, padx=5, pady=5)

# app_password输入框
tk.Label(root, text="App 专用密码:").grid(row=6, column=0, sticky="w", padx=5, pady=5)
entry_pwd = tk.Entry(root, width=50, show="*")
entry_pwd.grid(row=6, column=1, padx=5, pady=5)

# transporter_path输入框
tk.Label(root, text="Transporter路径:").grid(row=7, column=0, sticky="w", padx=5, pady=5)
entry_transporter = tk.Entry(root, width=50 ,state=tk.DISABLED)
entry_transporter.grid(row=7, column=1, padx=5, pady=5)
tk.Button(root, text="浏览", command=choose_transporter).grid(row=7, column=2, padx=5)

tk.Button(root, text="上传 IPA", command=upload_ipa, bg="green", fg="white", width=20).grid(row=8, column=0, columnspan=3, pady=10)

log_box = tk.Text(root, height=13)
log_box.grid(row=9, column=0, columnspan=3, padx=5, pady=5)

# === 加载配置 ===
# 初始化时刷新下拉框
refresh_dropdown()

# entry_dir.insert(0, config.get("ipa_dir", ""))

# 先将输入框临时改为可编辑状态
entry_path.config(state=tk.NORMAL)
# 清空现有内容
#entry_path.delete(0, tk.END)
# 将生成的 plist 文件路径填入输入框
entry_path.insert(0, config.get("ipa_path", ""))
# 重新设置为禁用状态
entry_path.config(state=tk.DISABLED)

entry_id.insert(0, config.get("apple_id", ""))
entry_pwd.insert(0, config.get("app_password", ""))

entry_transporter.config(state=tk.NORMAL)
# #entry_transporter.delete(0, tk.END)
entry_transporter.insert(0, config.get("transporter_path", ""))
entry_transporter.config(state=tk.DISABLED)

entry_team_id.insert(0, config.get("team_id", ""))
entry_remark.insert(0, config.get("remark", ""))

# === 退出保存配置 ===
def on_close():
    save_config()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

root.mainloop()
