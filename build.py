import PyInstaller.__main__
import os

# 获取所有需要打包的JSON文件
json_files = [
    'ccf_data.json',
    'FMS.json',
    'ajg_2024.json',
    'zufe.json'
]

# 构建打包命令
command = [
    'app.py',
    '--name=RIS文件处理器',
    '--windowed',  # 不显示终端窗口
    '--onefile',   # 生成单个可执行文件
    '--icon=filter.ico',  # 使用自定义图标
    '--clean',  # 清理临时文件
    '--noconfirm',  # 覆盖已存在的打包文件
]

# 添加所有JSON文件到打包列表
for json_file in json_files:
    command.extend(['--add-data', f'{json_file};.'])

# 添加图标文件
command.extend(['--add-data', 'filter.ico;.'])

# 运行打包命令
PyInstaller.__main__.run(command) 