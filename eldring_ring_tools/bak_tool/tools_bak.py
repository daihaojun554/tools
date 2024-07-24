import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import time
import zipfile
import configparser
# 读取配置文件
config = configparser.ConfigParser()

# 检查settings.ini文件是否存在，如果不存在则创建
if not os.path.exists('settings.ini'):
    # 添加BackupSettings部分
    config.add_section('BackupSettings')
    # 设置默认的备份目录为空
    config.set('BackupSettings', 'backup_directory', '')

    # 将配置写入settings.ini文件
    with open('settings.ini', 'w',encoding='gbk') as configfile:
        config.write(configfile)

# 现在可以读取配置文件
config.read('settings.ini')
    
# 从配置文件中获取备份目录，如果没有则默认为None
backup_dir = config.get('BackupSettings', 'backup_directory', fallback=None)
print(backup_dir)

def choose_backup_dir():
    global backup_dir
    backup_dir = filedialog.askdirectory()
    if backup_dir:
        backup_dir_label.config(text=f"备份目录: {backup_dir}")
        load_backups()
        # 更新配置文件
        config.set('BackupSettings', 'backup_directory', backup_dir)
        with open('settings.ini', 'w',encoding='gbk') as configfile:
            config.write(configfile)

def backup_elden_ring():
    # 获取用户输入的存档名称
    save_name = entry.get()
    
    # 确保存档名称不为空
    if not save_name or not backup_dir:
        messagebox.showerror("错误", "请输入存档名称并选择备份目录！")
        return
    
    elden_ring_save_dir_path = os.path.expanduser('~\\AppData\\Roaming\\EldenRing')
    # 检查是否有这个文件夹
    if not os.path.isdir(elden_ring_save_dir_path):
        messagebox.showerror("错误", "无法找到Elden Ring的存档目录！")
        return
    zip_name = f'{backup_dir}\\backup_{save_name}_{time.strftime("%Y-%m-%d_%H时%M分%S秒", time.localtime())}.zip'
    
    try:
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as back_zip:
            for path, dirs, files in os.walk(elden_ring_save_dir_path):
                tmp = path.replace(elden_ring_save_dir_path, '')
                for name in files:
                    full_name = os.path.join(path, name)
                    name = tmp + '\\' + name
                    back_zip.write(full_name, name)
        
        listbox.insert(tk.END, zip_name)  # 在listbox中插入新备份的存档
        messagebox.showinfo("成功", f'备份完成\n存档文件储存在：{zip_name}')
    except Exception as e:
        messagebox.showerror("错误", f"备份失败：{str(e)}")

def load_backups():
    if backup_dir and os.path.isdir(backup_dir):
        # 清空listbox
        listbox.delete(0, tk.END)
        
        # 列出备份目录下的所有文件
        for filename in os.listdir(backup_dir):
            # 假设存档文件以"backup_"开头
            print(f'...{filename}')
            if filename.startswith('backup_'):
                # 插入到listbox中
                listbox.insert(tk.END, filename)
def open_file_location(event):
    # 获取选中的项目索引
    index = listbox.curselection()
    if index:
        # 获取选中的项目文本
        selected_item = listbox.get(index)
        # 构建完整的文件路径
        full_path = os.path.join(backup_dir, selected_item)
        # 检查文件是否存在
        if os.path.isfile(full_path):
            # 打开文件所在目录
            os.startfile(os.path.dirname(full_path))  # Windows


def restore_selected_backup():
    # 获取选中的项目索引
    index = listbox.curselection()
    if index:
        # 获取选中的项目文本
        selected_item = listbox.get(index)
        # 构建完整的文件路径
        full_path = os.path.join(backup_dir, selected_item)
        # 检查文件是否存在
        if os.path.isfile(full_path):
            try:
                # 解压存档文件到临时目录
                temp_dir = os.path.join(backup_dir, 'temp_restore')
                os.makedirs(temp_dir, exist_ok=True)
                
                with zipfile.ZipFile(full_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # 游戏存档目录
                elden_ring_save_dir_path = os.path.expanduser('~\\AppData\\Roaming\\EldenRing')
                
                # 遍历临时目录中的所有文件并复制到游戏存档目录
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        src = os.path.join(root, file)
                        dst = src.replace(temp_dir, elden_ring_save_dir_path)
                        os.makedirs(os.path.dirname(dst), exist_ok=True)
                        shutil.copy2(src, dst)
                
                # 删除临时目录
                shutil.rmtree(temp_dir)
                
                messagebox.showinfo("成功", "存档恢复完成！")
            except Exception as e:
                messagebox.showerror("错误", f"恢复存档失败：{str(e)}")
        else:
            messagebox.showerror("错误", "选择的存档文件不存在！")
    else:
        messagebox.showerror("错误", "请先选择一个存档文件！")
# 创建主窗口


root = tk.Tk()
root.title("艾尔登法环存档备份工具")

# 使用ttk风格
style = ttk.Style()
style.theme_use('clam')  # 可以尝试不同的主题，如 'clam', 'alt', 'default', 'classic'
style.configure('TLabel', font=('Helvetica', 12))
style.configure('TButton', font=('Helvetica', 12), padding=10)
style.configure('TEntry', padding=10)
# 创建框架以组织控件
main_frame = ttk.Frame(root, padding="20")
main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# 显示存档路径
save_path_label = ttk.Label(main_frame, text=f"当前游戏的存档路径: {os.path.expanduser(r'~/AppData/Roaming/EldenRing')}")
save_path_label.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky=tk.W)

# 创建标签和输入框
label = ttk.Label(main_frame, text="请输入存档名称:")
label.grid(row=1, column=0, pady=(0, 10), sticky=tk.W)
entry = ttk.Entry(main_frame)
entry.grid(row=1, column=1, pady=(0, 10), sticky=(tk.W, tk.E))

# 创建按钮选择备份目录
choose_dir_button = ttk.Button(main_frame, text="选择备份目录", command=choose_backup_dir)
choose_dir_button.grid(row=2, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))

# 显示备份目录
backup_dir_label = ttk.Label(main_frame, text=f"备份目录: {backup_dir if backup_dir else ''}")
backup_dir_label.grid(row=3, column=0, columnspan=2, pady=(0, 10), sticky=tk.W)

# 创建按钮并绑定备份函数
button = ttk.Button(main_frame, text="开始备份", command=backup_elden_ring)
button.grid(row=4, column=0, columnspan=2, pady=(20, 10), sticky=(tk.W, tk.E))

# 创建Listbox显示备份存档列表
listbox = tk.Listbox(main_frame, selectmode=tk.BROWSE)
listbox.grid(row=5, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E, tk.N, tk.S))
scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=listbox.yview)
scrollbar.grid(row=5, column=2, pady=(0, 10), sticky=(tk.N, tk.S))
listbox.config(yscrollcommand=scrollbar.set)
# 创建按钮并绑定恢复函数
restore_button = ttk.Button(main_frame, text="恢复存档", command=restore_selected_backup)
restore_button.grid(row=6, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))
# 程序启动时自动加载备份存档
# 绑定双击事件到open_file_location函数
listbox.bind('<Double-Button-1>', open_file_location)
load_backups()

# 设置网格权重以适应窗口大小变化
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
main_frame.columnconfigure(1, weight=1)
main_frame.rowconfigure(5, weight=1)

# 运行主循环
# 设置窗口大小不可变
root.resizable(width=False, height=False)
root.mainloop()

