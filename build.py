import PyInstaller.__main__
import os

# 数据文件目录
data_dir = 'data'
# 资源文件目录
resources_dir = 'resources'

# 获取所有需要打包的数据文件
data_files = [
    os.path.join(data_dir, 'ccf_data.json'),
    os.path.join(data_dir, 'FMS.json'),
    os.path.join(data_dir, 'ajg_2024.json'),
    os.path.join(data_dir, 'zufe.json')
]

# 获取所有需要打包的资源文件
resource_files = [
    os.path.join(resources_dir, 'filter.ico'),
    os.path.join(resources_dir, 'scopus.ris')
]

# 构建打包命令
command = [
    'app.py',
    '--name=RIS文件处理器',
    '--windowed',  # 不显示终端窗口
    '--onefile',   # 生成单个可执行文件
    f'--icon={os.path.join(resources_dir, "filter.ico")}',  # 使用自定义图标
    '--clean',  # 清理临时文件
    '--noconfirm',  # 覆盖已存在的打包文件
]

# 添加所有数据文件到打包列表
for data_file in data_files:
    if os.path.exists(data_file):
        command.extend(['--add-data', f'{data_file};{data_dir}'])
    else:
        print(f"警告: 未找到数据文件 {data_file}")

# 添加所有资源文件到打包列表
for resource_file in resource_files:
    if os.path.exists(resource_file):
        command.extend(['--add-data', f'{resource_file};{resources_dir}'])
    else:
        print(f"警告: 未找到资源文件 {resource_file}")

# 运行打包命令
PyInstaller.__main__.run(command) 