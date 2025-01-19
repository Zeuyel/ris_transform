import PyInstaller.__main__
import os
import sys

def collect_data_files():
    """收集所有需要打包的数据文件"""
    data_files = []
    
    # 数据目录结构
    data_structure = {
        'data': [
            'config.json',
            'ratings/*.json',
            'criteria/*.json',
            'profiles/*.json'
        ],
        'resources': [
            'filter.ico',
            'scopus.ris'
        ]
    }
    
    # 遍历数据目录结构
    for base_dir, patterns in data_structure.items():
        for pattern in patterns:
            full_pattern = os.path.join(base_dir, pattern)
            
            # 如果是通配符模式
            if '*' in pattern:
                dir_path = os.path.dirname(full_pattern)
                if os.path.exists(dir_path):
                    for file_name in os.listdir(dir_path):
                        if file_name.endswith('.json'):
                            file_path = os.path.join(dir_path, file_name)
                            if os.path.exists(file_path):
                                data_files.append((file_path, dir_path))
            else:
                # 单个文件
                if os.path.exists(full_pattern):
                    data_files.append((full_pattern, base_dir))
                else:
                    print(f"警告: 未找到文件 {full_pattern}")
    
    return data_files

def main():
    """主函数：构建打包命令并执行"""
    # 基本命令
    command = [
        'app.py',
        '--name=RIS文件处理器',
        '--windowed',       # 不显示终端窗口
        '--onefile',        # 生成单个可执行文件
        '--clean',          # 清理临时文件
        '--noconfirm',      # 覆盖已存在的打包文件
    ]
    
    # 添加图标
    icon_path = os.path.join('resources', 'filter.ico')
    if os.path.exists(icon_path):
        command.extend(['--icon', icon_path])
    else:
        print(f"警告: 未找到图标文件 {icon_path}")
    
    # 添加数据文件
    data_files = collect_data_files()
    for file_path, target_dir in data_files:
        # 在Windows上使用分号，在其他平台上使用冒号
        separator = ';' if sys.platform == 'win32' else ':'
        command.extend(['--add-data', f'{file_path}{separator}{target_dir}'])
    
    # 添加隐藏导入（如果需要）
    hidden_imports = [
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'core',
        'core.data_manager',
        'core.data_types',
        'core.paper_processor',
        'gui',
        'gui.main_window',
        'utils',
        'utils.translator'
    ]
    for imp in hidden_imports:
        command.extend(['--hidden-import', imp])
    
    # 添加Python路径
    command.extend(['--paths', '.'])
    
    # 打印命令（用于调试）
    print("PyInstaller 命令:")
    print(" ".join(command))
    print("\n包含的数据文件:")
    for file_path, target_dir in data_files:
        print(f"- {file_path} -> {target_dir}")
    
    # 运行打包命令
    try:
        PyInstaller.__main__.run(command)
        print("\n打包完成!")
    except Exception as e:
        print(f"\n打包失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 