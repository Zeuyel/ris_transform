from msilib.schema import Icon
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QLabel, QFileDialog, QMessageBox, 
                           QDialog, QDialogButtonBox, QTabWidget, QTableWidget,
                           QTableWidgetItem, QHeaderView, QCheckBox, QFrame,
                           QProgressBar, QListWidget, QListWidgetItem, QLineEdit,
                           QGroupBox, QGridLayout)
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import json
import os
import sys
import shutil

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from core.paper_processor import process_ris_file
from core.data_manager import DataManager
from core.data_types import RatingSystem

def get_resource_path(relative_path):
    """获取资源的绝对路径"""
    if getattr(sys, 'frozen', False):
        # 如果是打包后的 exe
        base_path = sys._MEIPASS
    else:
        # 如果是直接运行 python 脚本
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# 自定义样式的按钮
class StyledButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #7F7FD5;
                color: white;
                border-radius: 10px;
                padding: 10px;
                font-family: "Microsoft YaHei UI";
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #6B6BD5;
            }
            QPushButton:pressed {
                background-color: #5959D5;
            }
        """)

# 自定义样式的拖放区域
class DropArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        
        layout = QVBoxLayout()
        self.label = QLabel("将RIS文件拖放到这里或者点击选择")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                color: #7F7FD5;
                font-family: "Microsoft YaHei UI";
                font-size: 16px;
                font-weight: 600;
                background-color: #F0F0F7;
                border: 2px dashed #7F7FD5;
                border-radius: 15px;
                padding: 20px;
            }
        """)
        layout.addWidget(self.label)
        self.setLayout(layout)
        
        # 设置鼠标指针样式
        self.setCursor(Qt.PointingHandCursor)
        self.label.setCursor(Qt.PointingHandCursor)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 获取主窗口引用
            main_window = self.window()
            # 调用选择文件方法
            main_window.select_file()
            
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            self.label.setStyleSheet("""
                QLabel {
                    color: #6B6BD5;
                    font-size: 16px;
                    font-weight: bold;
                    background-color: #E6E6F5;
                    border: 2px dashed #6B6BD5;
                    border-radius: 15px;
                    padding: 20px;
                }
            """)
            event.accept()
        else:
            event.ignore()
            
    def dragLeaveEvent(self, event):
        self.label.setStyleSheet("""
            QLabel {
                color: #7F7FD5;
                font-size: 16px;
                font-weight: bold;
                background-color: #F0F0F7;
                border: 2px dashed #7F7FD5;
                border-radius: 15px;
                padding: 20px;
            }
        """)

    def dropEvent(self, event):
        files = event.mimeData().urls()
        for url in files:
            file_path = url.toLocalFile()
            if file_path.lower().endswith('.ris'):
                # 更新显示的文件名
                file_name = os.path.basename(file_path)
                self.label.setText(f"当前文件：{file_name}")
                # 获取主窗口引用
                main_window = self.window()
                # 只保存文件路径，不自动处理
                main_window.current_ris_file = file_path

    def update_file_name(self, file_path):
        """更新显示的文件名（供外部调用）"""
        if file_path:
            file_name = os.path.basename(file_path)
            self.label.setText(f"当前文件：{file_name}")
        else:
            self.label.setText("将RIS文件拖放到这里或者点击选择")

class ProcessThread(QThread):
    """处理RIS文件的线程"""
    progress = pyqtSignal(int, int)  # 发送进度信号
    finished = pyqtSignal(bool)  # 发送完成信号
    error = pyqtSignal(str)  # 发送错误信号

    def __init__(self, file_path, selected, selection_profile, path_rating_file,
                 json_attribute_title, json_attribute_rating, output_path,
                 trans_ti, trans_ab, token_missuo, token_linuxdo):
        super().__init__()
        self.file_path = file_path
        self.selected = selected
        self.selection_profile = selection_profile
        self.path_rating_file = path_rating_file
        self.json_attribute_title = json_attribute_title
        self.json_attribute_rating = json_attribute_rating
        self.output_path = output_path
        self.trans_ti = trans_ti
        self.trans_ab = trans_ab
        self.token_missuo = token_missuo
        self.token_linuxdo = token_linuxdo

    def run(self):
        try:
            result = process_ris_file(
                file_path=self.file_path,
                selection_criteria=self.selected,
                selection_profile=self.selection_profile,
                path_rating_file=self.path_rating_file,
                json_attribute_title=self.json_attribute_title,
                json_attribute_rating=self.json_attribute_rating,
                output_directory=self.output_path,
                trans_ti=self.trans_ti,
                trans_ab=self.trans_ab,
                tokenMissuo=self.token_missuo,
                tokenLinuxdo=self.token_linuxdo,
                progress_callback=self.progress.emit
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class RatingSystemDialog(QDialog):
    def __init__(self, system_id="", name="", description="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("评级系统设置")
        self.setMinimumWidth(500)
        
        self.system_id = system_id
        self.file_path = None  # 保存选择的文件路径
        self.setup_ui(system_id, name, description)
        
    def setup_ui(self, system_id, name, description):
        layout = QVBoxLayout(self)
        
        # 基本信息组
        basic_group = QGroupBox("基本信息")
        basic_layout = QVBoxLayout(basic_group)
        
        # 系统ID输入框
        id_layout = QHBoxLayout()
        id_label = QLabel("系统ID:")
        self.id_input = QLineEdit(system_id)
        if system_id:  # 如果是编辑模式，ID不可修改
            self.id_input.setEnabled(False)
        id_layout.addWidget(id_label)
        id_layout.addWidget(self.id_input)
        basic_layout.addLayout(id_layout)
        
        # 名称输入框
        name_layout = QHBoxLayout()
        name_label = QLabel("名称:")
        self.name_input = QLineEdit(name)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        basic_layout.addLayout(name_layout)
        
        # 描述输入框
        desc_layout = QHBoxLayout()
        desc_label = QLabel("描述:")
        self.desc_input = QLineEdit(description)
        desc_layout.addWidget(desc_label)
        desc_layout.addWidget(self.desc_input)
        basic_layout.addLayout(desc_layout)
        
        layout.addWidget(basic_group)
        
        # 数据文件组
        file_group = QGroupBox("数据文件")
        file_layout = QVBoxLayout(file_group)
        
        # 文件选择按钮和显示
        file_select_layout = QHBoxLayout()
        self.file_label = QLabel("未选择文件")
        self.file_label.setStyleSheet("color: #666666;")
        self.file_btn = QPushButton("选择文件")
        self.file_btn.clicked.connect(self.select_file)
        file_select_layout.addWidget(self.file_label)
        file_select_layout.addWidget(self.file_btn)
        file_layout.addLayout(file_select_layout)
        
        # 属性映射组
        mapping_group = QWidget()
        mapping_layout = QVBoxLayout(mapping_group)
        mapping_layout.setContentsMargins(0, 0, 0, 0)
        
        # 论文名称属性
        name_mapping_layout = QHBoxLayout()
        name_mapping_label = QLabel("论文名称字段:")
        self.name_mapping_input = QLineEdit()
        self.name_mapping_input.setPlaceholderText("例如：Paper_name 或 fullname")
        name_mapping_layout.addWidget(name_mapping_label)
        name_mapping_layout.addWidget(self.name_mapping_input)
        mapping_layout.addLayout(name_mapping_layout)
        
        # 等级属性
        level_mapping_layout = QHBoxLayout()
        level_mapping_label = QLabel("等级字段:")
        self.level_mapping_input = QLineEdit()
        self.level_mapping_input.setPlaceholderText("例如：Level 或 rank")
        level_mapping_layout.addWidget(level_mapping_label)
        level_mapping_layout.addWidget(self.level_mapping_input)
        mapping_layout.addLayout(level_mapping_layout)
        
        # 类型属性（可选）
        type_mapping_layout = QHBoxLayout()
        type_mapping_label = QLabel("类型字段:")
        self.type_mapping_input = QLineEdit()
        self.type_mapping_input.setPlaceholderText("例如：type（可选）")
        type_mapping_layout.addWidget(type_mapping_label)
        type_mapping_layout.addWidget(self.type_mapping_input)
        mapping_layout.addLayout(type_mapping_layout)
        
        file_layout.addWidget(mapping_group)
        layout.addWidget(file_group)
        
        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def select_file(self):
        """选择数据文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择评级数据文件", "", "JSON文件 (*.json)"
        )
        if file_path:
            self.file_path = file_path
            self.file_label.setText(os.path.basename(file_path))
            self.file_label.setStyleSheet("color: #000000;")
        
    def validate_and_accept(self):
        """验证输入并接受对话框"""
        if not self.id_input.text().strip():
            QMessageBox.warning(self, "警告", "系统ID不能为空")
            return
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "警告", "名称不能为空")
            return
        if not self.desc_input.text().strip():
            QMessageBox.warning(self, "警告", "描述不能为空")
            return
        if not self.file_path:
            QMessageBox.warning(self, "警告", "请选择数据文件")
            return
        if not self.name_mapping_input.text().strip():
            QMessageBox.warning(self, "警告", "论文名称字段不能为空")
            return
        if not self.level_mapping_input.text().strip():
            QMessageBox.warning(self, "警告", "等级字段不能为空")
            return
        self.accept()
        
    def get_data(self):
        """获取对话框数据"""
        mapping = {
            "paper_name": self.name_mapping_input.text().strip(),
            "level": self.level_mapping_input.text().strip()
        }
        
        # 如果有类型字段，添加到映射中
        type_field = self.type_mapping_input.text().strip()
        if type_field:
            mapping["type"] = type_field
        
        return {
            "system_id": self.id_input.text().strip(),
            "name": self.name_input.text().strip(),
            "description": self.desc_input.text().strip(),
            "file_path": self.file_path,
            "mapping": mapping
        }

class AttributeMappingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置属性映射")
        self.setMinimumWidth(400)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 论文名称属性
        name_layout = QHBoxLayout()
        name_label = QLabel("论文名称字段:")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("例如：Paper_name 或 fullname")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # 等级属性
        level_layout = QHBoxLayout()
        level_label = QLabel("等级字段:")
        self.level_input = QLineEdit()
        self.level_input.setPlaceholderText("例如：Level 或 rank")
        level_layout.addWidget(level_label)
        level_layout.addWidget(self.level_input)
        layout.addLayout(level_layout)
        
        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def validate_and_accept(self):
        """验证输入并接受对话框"""
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "警告", "论文名称字段不能为空")
            return
        if not self.level_input.text().strip():
            QMessageBox.warning(self, "警告", "等级字段不能为空")
            return
        self.accept()
        
    def get_data(self):
        """获取对话框数据"""
        return {
            "paper_name": self.name_input.text().strip(),
            "level": self.level_input.text().strip()
        }

class SettingsDialog(QDialog):
    def __init__(self, data_manager: DataManager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.setWindowTitle("设置")
        self.setMinimumWidth(1050)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 创建选项卡
        tab_widget = QTabWidget()
        
        # 评级系统设置
        rating_tab = QWidget()
        rating_layout = QVBoxLayout(rating_tab)
        
        # 评级系统表格
        self.rating_table = QTableWidget()
        self.rating_table.setColumnCount(5)
        self.rating_table.setHorizontalHeaderLabels(["系统ID", "名称", "描述", "数据文件", "操作"])
        self.rating_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        rating_layout.addWidget(self.rating_table)
        
        # 添加评级系统按钮
        add_rating_btn = QPushButton("添加评级系统")
        add_rating_btn.clicked.connect(self.add_rating_system)
        rating_layout.addWidget(add_rating_btn)
        
        # 分类标准设置
        criteria_tab = QWidget()
        criteria_layout = QVBoxLayout(criteria_tab)
        
        # 分类标准表格
        self.criteria_table = QTableWidget()
        self.criteria_table.setColumnCount(3)
        self.criteria_table.setHorizontalHeaderLabels(["标准名称", "包含系统", "操作"])
        self.criteria_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        criteria_layout.addWidget(self.criteria_table)
        
        # 添加分类标准按钮
        add_criteria_btn = QPushButton("添加分类标准")
        add_criteria_btn.clicked.connect(self.add_criteria)
        criteria_layout.addWidget(add_criteria_btn)
        
        # 组合标准设置
        profile_tab = QWidget()
        profile_layout = QVBoxLayout(profile_tab)
        
        # 组合标准表格
        self.profile_table = QTableWidget()
        self.profile_table.setColumnCount(3)
        self.profile_table.setHorizontalHeaderLabels(["标准名称", "包含集合", "操作"])
        self.profile_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        profile_layout.addWidget(self.profile_table)
        
        # 添加组合标准按钮
        add_profile_btn = QPushButton("添加组合标准")
        add_profile_btn.clicked.connect(self.add_profile)
        profile_layout.addWidget(add_profile_btn)
        
        # 添加选项卡
        tab_widget.addTab(rating_tab, "评级系统")
        tab_widget.addTab(criteria_tab, "分类标准")
        tab_widget.addTab(profile_tab, "组合标准")
        
        layout.addWidget(tab_widget)
        
        # 在底部按钮之前添加刷新按钮
        refresh_btn = QPushButton("刷新数据")
        refresh_btn.clicked.connect(self.refresh_data)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #7F7FD5;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6B6BD5;
            }
        """)
        layout.addWidget(refresh_btn)
        
        # 底部按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # 加载数据
        self.load_data()
        
    def load_data(self):
        """加载所有数据到表格"""
        # 加载评级系统数据
        self.load_rating_systems()
        # 加载分类标准数据
        self.load_criteria()
        # 加载组合标准数据
        self.load_profiles()
        
    def load_rating_systems(self):
        """加载评级系统数据到表格"""
        self.rating_table.setRowCount(0)
        rating_systems = self.data_manager.get_rating_systems()
        
        for row, (system_id, info) in enumerate(rating_systems.items()):
            self.rating_table.insertRow(row)
            
            # 系统ID
            self.rating_table.setItem(row, 0, QTableWidgetItem(system_id))
            # 名称
            self.rating_table.setItem(row, 1, QTableWidgetItem(info['name']))
            # 描述
            self.rating_table.setItem(row, 2, QTableWidgetItem(info['description']))
            
            # 数据文件
            file_info = self.data_manager.get_rating_file_info(system_id)
            if file_info and file_info['file_path']:
                file_path = os.path.join(self.data_manager.base_path, file_info['file_path'])
                if os.path.exists(file_path):
                    file_text = file_info['file_path']
                    file_color = "#000000"  # 黑色
                else:
                    file_text = f"{file_info['file_path']} (文件不存在)"
                    file_color = "#FF0000"  # 红色
            else:
                file_text = "未设置"
                file_color = "#FF0000"  # 红色
            
            file_item = QTableWidgetItem(file_text)
            file_item.setForeground(QBrush(QColor(file_color)))
            self.rating_table.setItem(row, 3, file_item)
            
            # 操作按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = QPushButton("编辑")
            edit_btn.clicked.connect(lambda checked, s=system_id: self.edit_rating_system(s))
            
            delete_btn = QPushButton("删除")
            delete_btn.clicked.connect(lambda checked, s=system_id: self.delete_rating_system(s))
            
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)
            
            self.rating_table.setCellWidget(row, 4, btn_widget)
            
    def load_criteria(self):
        """加载分类标准数据到表格"""
        self.criteria_table.setRowCount(0)
        criteria_dict = self.data_manager.get_selection_criteria()
        
        for row, (name, criteria) in enumerate(criteria_dict.items()):
            self.criteria_table.insertRow(row)
            
            # 标准名称
            self.criteria_table.setItem(row, 0, QTableWidgetItem(name))
            
            # 包含系统
            systems = ", ".join(criteria.keys())
            self.criteria_table.setItem(row, 1, QTableWidgetItem(systems))
            
            # 操作按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = QPushButton("编辑")
            edit_btn.clicked.connect(lambda checked, n=name: self.edit_criteria(n))
            
            delete_btn = QPushButton("删除")
            delete_btn.clicked.connect(lambda checked, n=name: self.delete_criteria(n))
            
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)
            
            self.criteria_table.setCellWidget(row, 2, btn_widget)
            
    def load_profiles(self):
        """加载组合标准数据到表格"""
        self.profile_table.setRowCount(0)
        profiles = self.data_manager.get_selection_profiles()
        
        for row, (name, profile) in enumerate(profiles.items()):
            self.profile_table.insertRow(row)
            
            # 标准名称
            self.profile_table.setItem(row, 0, QTableWidgetItem(name))
            
            # 包含集合
            sets = ", ".join(profile.keys())
            self.profile_table.setItem(row, 1, QTableWidgetItem(sets))
            
            # 操作按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = QPushButton("编辑")
            edit_btn.clicked.connect(lambda checked, n=name: self.edit_profile(n))
            
            delete_btn = QPushButton("删除")
            delete_btn.clicked.connect(lambda checked, n=name: self.delete_profile(n))
            
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)
            
            self.profile_table.setCellWidget(row, 2, btn_widget)
    
    # 评级系统相关方法
    def add_rating_system(self):
        """添加新的评级系统"""
        dialog = RatingSystemDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                # 检查系统ID是否已存在
                if data["system_id"] in self.data_manager.get_rating_systems():
                    QMessageBox.warning(self, "警告", "系统ID已存在")
                    return
                    
                # 获取文件名
                file_name = os.path.basename(data["file_path"])
                
                # 构建目标路径（ratings目录下）
                ratings_dir = os.path.join(self.data_manager.base_path, "ratings")
                os.makedirs(ratings_dir, exist_ok=True)
                
                # 构建新的文件名（使用系统ID作为前缀，避免文件名冲突）
                new_file_name = f"{data['system_id'].lower()}_{file_name}"
                target_path = os.path.join(ratings_dir, new_file_name)
                
                # 复制文件到ratings目录
                import shutil
                shutil.copy2(data["file_path"], target_path)
                
                # 使用统一的相对路径格式（使用正斜杠）
                relative_path = "ratings/" + new_file_name
                
                # 添加新的评级系统
                self.data_manager.add_rating_system(
                    system_id=data["system_id"],
                    name=data["name"],
                    description=data["description"]
                )
                
                # 添加评级文件和属性映射
                self.data_manager.add_rating_file(
                    system_id=data["system_id"],
                    file_path=relative_path,
                    json_attribute_mapping=data["mapping"]
                )
                
                # 刷新表格
                self.load_rating_systems()
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"添加评级系统失败：{str(e)}")
                # 如果复制失败，清理可能已创建的文件
                if 'target_path' in locals() and os.path.exists(target_path):
                    try:
                        os.remove(target_path)
                    except:
                        pass
                
    def edit_rating_system(self, system_id: str):
        """编辑评级系统"""
        # 获取当前系统信息
        rating_systems = self.data_manager.get_rating_systems()
        if system_id not in rating_systems:
            QMessageBox.warning(self, "警告", "系统不存在")
            return
        
        current_system = rating_systems[system_id]
        dialog = RatingSystemDialog(
            system_id=system_id,
            name=current_system["name"],
            description=current_system["description"],
            parent=self
        )
        
        # 加载现有的文件和映射信息
        file_info = self.data_manager.get_rating_file_info(system_id)
        if file_info and file_info['file_path']:
            file_path = os.path.join(self.data_manager.base_path, file_info['file_path'])
            if os.path.exists(file_path):
                dialog.file_path = file_path
                dialog.file_label.setText(os.path.basename(file_path))
                dialog.file_label.setStyleSheet("color: #000000;")
                
                # 设置映射信息
                mapping = file_info['mapping']
                if mapping:
                    dialog.name_mapping_input.setText(mapping.get('paper_name', ''))
                    dialog.level_mapping_input.setText(mapping.get('level', ''))
                    if 'type' in mapping:
                        dialog.type_mapping_input.setText(mapping['type'])
        
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                # 更新评级系统基本信息
                self.data_manager.update_rating_system(
                    system_id=data["system_id"],
                    name=data["name"],
                    description=data["description"]
                )
                
                # 如果选择了新文件，更新文件和映射信息
                if data["file_path"]:
                    # 获取文件名
                    file_name = os.path.basename(data["file_path"])
                    
                    # 构建目标路径（ratings目录下）
                    ratings_dir = os.path.join(self.data_manager.base_path, "ratings")
                    os.makedirs(ratings_dir, exist_ok=True)
                    
                    # 构建新的文件名（使用系统ID作为前缀，避免文件名冲突）
                    new_file_name = f"{data['system_id'].lower()}_{file_name}"
                    target_path = os.path.join(ratings_dir, new_file_name)
                    
                    # 复制文件到ratings目录
                    import shutil
                    shutil.copy2(data["file_path"], target_path)
                    
                    # 使用统一的相对路径格式（使用正斜杠）
                    relative_path = "ratings/" + new_file_name
                    
                    # 更新评级文件和属性映射
                    self.data_manager.add_rating_file(
                        system_id=data["system_id"],
                        file_path=relative_path,
                        json_attribute_mapping=data["mapping"]
                    )
                
                # 刷新表格
                self.load_rating_systems()
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"更新评级系统失败：{str(e)}")
                # 如果复制失败，清理可能已创建的文件
                if 'target_path' in locals() and os.path.exists(target_path):
                    try:
                        os.remove(target_path)
                    except:
                        pass
    
    def select_rating_file(self, system_id: str):
        """选择评级系统的数据文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择评级数据文件", "", "JSON文件 (*.json)"
        )
        
        if file_path:
            try:
                # 弹出属性映射设置对话框
                mapping_dialog = AttributeMappingDialog(self)
                if mapping_dialog.exec_() != QDialog.Accepted:
                    return
                
                mapping_data = mapping_dialog.get_data()
                
                # 获取文件名
                file_name = os.path.basename(file_path)
                
                # 构建目标路径（ratings目录下）
                ratings_dir = os.path.join(self.data_manager.base_path, "ratings")
                os.makedirs(ratings_dir, exist_ok=True)
                
                # 构建新的文件名（使用系统ID作为前缀，避免文件名冲突）
                new_file_name = f"{system_id.lower()}_{file_name}"
                target_path = os.path.join(ratings_dir, new_file_name)
                
                # 复制文件到ratings目录
                import shutil
                shutil.copy2(file_path, target_path)
                
                # 更新配置文件中的路径（使用相对路径）和属性映射
                relative_path = os.path.join("ratings", new_file_name).replace("\\", "/")  # 使用正斜杠
                
                # 更新评级文件路径和属性映射
                self.data_manager.add_rating_file(
                    system_id=system_id,
                    file_path=relative_path,
                    json_attribute_mapping=mapping_data
                )
                
                # 刷新表格
                self.load_rating_systems()
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"添加评级文件失败：{str(e)}")
                # 如果复制失败，清理可能已创建的文件
                if 'target_path' in locals() and os.path.exists(target_path):
                    try:
                        os.remove(target_path)
                    except:
                        pass
                
    def delete_rating_system(self, system_id: str):
        """删除评级系统"""
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除评级系统 {system_id} 吗？\n这将同时删除相关的评级文件和配置。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # 删除评级系统
                self.data_manager.remove_rating_system(system_id)
                
                # 刷新表格
                self.load_rating_systems()
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除评级系统失败：{str(e)}")
    
    # 分类标准相关方法
    def add_criteria(self):
        """添加新的分类标准"""
        dialog = CriteriaDialog(self.data_manager, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                # 检查名称是否已存在
                if data["name"] in self.data_manager.get_selection_criteria():
                    QMessageBox.warning(self, "警告", "标准名称已存在")
                    return
                    
                # 保存分类标准
                self.data_manager.save_criteria(data["name"], data["criteria"])
                
                # 刷新表格
                self.load_criteria()
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"添加分类标准失败：{str(e)}")
            
    def edit_criteria(self, name: str):
        """编辑分类标准"""
        # 获取当前标准数据
        criteria_dict = self.data_manager.get_selection_criteria()
        if name not in criteria_dict:
            QMessageBox.warning(self, "警告", "标准不存在")
            return
        
        current_criteria = criteria_dict[name]
        dialog = CriteriaDialog(
            self.data_manager,
            name=name,
            criteria=current_criteria,
            parent=self
        )
        
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                # 保存分类标准
                self.data_manager.save_criteria(data["name"], data["criteria"])
                
                # 刷新表格
                self.load_criteria()
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"更新分类标准失败：{str(e)}")
            
    def delete_criteria(self, name: str):
        """删除分类标准"""
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除分类标准 {name} 吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # 删除分类标准
                self.data_manager.remove_criteria(name)
                
                # 刷新表格
                self.load_criteria()
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除分类标准失败：{str(e)}")
    
    # 组合标准相关方法
    def add_profile(self):
        """添加新的组合标准"""
        dialog = ProfileDialog(self.data_manager, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                # 检查名称是否已存在
                if data["name"] in self.data_manager.get_selection_profiles():
                    QMessageBox.warning(self, "警告", "组合标准名称已存在")
                    return
                    
                # 保存组合标准
                self.data_manager.save_profile(data["name"], data["criteria_sets"])
                
                # 刷新表格
                self.load_profiles()
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"添加组合标准失败：{str(e)}")
    
    def edit_profile(self, name: str):
        """编辑组合标准"""
        # 获取当前标准数据
        profile_dict = self.data_manager.get_selection_profiles()
        if name not in profile_dict:
            QMessageBox.warning(self, "警告", "组合标准不存在")
            return
        
        current_profile = profile_dict[name]
        dialog = ProfileDialog(
            self.data_manager,
            name=name,
            profile=current_profile,
            parent=self
        )
        
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                # 保存组合标准
                self.data_manager.save_profile(data["name"], data["criteria_sets"])
                
                # 刷新表格
                self.load_profiles()
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"更新组合标准失败：{str(e)}")
    
    def delete_profile(self, name: str):
        """删除组合标准"""
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除组合标准 {name} 吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # 删除组合标准
                self.data_manager.remove_profile(name)
                
                # 刷新表格
                self.load_profiles()
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除组合标准失败：{str(e)}")

    def refresh_data(self):
        """刷新所有数据"""
        try:
            self.data_manager.reload_config()
            self.load_data()
            QMessageBox.information(self, "成功", "数据已刷新")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"刷新数据失败：{str(e)}")

class CriteriaDialog(QDialog):
    def __init__(self, data_manager: DataManager, name="", criteria=None, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.setWindowTitle("分类标准设置")
        self.setMinimumWidth(600)
        self.setup_ui(name, criteria)
    
    def setup_ui(self, name, criteria):
        layout = QVBoxLayout(self)
        
        # 标准名称
        name_layout = QHBoxLayout()
        name_label = QLabel("标准名称:")
        self.name_input = QLineEdit(name)
        if name:  # 如果是编辑模式，名称不可修改
            self.name_input.setEnabled(False)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # 评级系统选择
        systems_group = QGroupBox("评级系统选择")
        systems_layout = QVBoxLayout(systems_group)
        
        # 获取所有可用的评级系统
        self.system_widgets = {}
        rating_systems = self.data_manager.get_rating_systems()
        
        for system_id, info in rating_systems.items():
            # 创建系统组
            system_group = QGroupBox(info['name'])
            system_layout = QVBoxLayout(system_group)
            
            # 从数据文件中获取可用的等级和类型
            file_info = self.data_manager.get_rating_file_info(system_id)
            available_levels = set()
            available_types = set()
            
            if file_info and file_info['file_path']:
                try:
                    file_path = os.path.join(self.data_manager.base_path, file_info['file_path'])
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        level_field = file_info['mapping']['level']
                        # 过滤掉None值并转换为字符串
                        available_levels = {str(item[level_field]) 
                                         for item in data 
                                         if level_field in item and item[level_field] is not None}
                        
                        # 如果有类型字段，获取可用的类型
                        if 'type' in file_info['mapping']:
                            type_field = file_info['mapping']['type']
                            available_types = {str(item[type_field])
                                            for item in data
                                            if type_field in item and item[type_field] is not None}
                except Exception as e:
                    print(f"读取文件 {file_path} 时出错: {str(e)}")
                    continue
            
            # 创建等级和类型的复选框
            system_data = {'group': system_group}
            
            if available_types:
                # 如果有类型字段，为每个类型创建独立的等级选择区域
                type_level_groups = {}
                for type_val in sorted(available_types):
                    type_group = QGroupBox(f"类型：{type_val}")
                    type_layout = QVBoxLayout(type_group)
                    
                    # 为该类型创建等级选择
                    level_checkboxes = {}
                    # 将等级值转换为字符串并排序
                    sorted_levels = sorted(available_levels, key=lambda x: (
                        float(x) if x.replace('.', '', 1).isdigit() else float('inf'),
                        x
                    ))
                    
                    # 创建等级复选框的网格布局
                    level_grid = QGridLayout()
                    for i, level in enumerate(sorted_levels):
                        combined_value = f"{level}{type_val}"
                        checkbox = QCheckBox(str(level))
                        if criteria and system_id in criteria and combined_value in criteria[system_id]:
                            checkbox.setChecked(True)
                        level_checkboxes[combined_value] = checkbox
                        level_grid.addWidget(checkbox, i // 4, i % 4)  # 每行4个复选框
                    
                    type_layout.addLayout(level_grid)
                    system_layout.addWidget(type_group)
                    type_level_groups[str(type_val)] = {
                        'group': type_group,
                        'levels': level_checkboxes
                    }
                
                system_data['type_groups'] = type_level_groups
            else:
                # 如果没有类型字段，创建单一的等级选择区域
                level_group = QGroupBox("等级选择")
                level_layout = QVBoxLayout(level_group)
                
                level_checkboxes = {}
                # 将等级值转换为字符串并排序
                sorted_levels = sorted(available_levels, key=lambda x: (
                    float(x) if x.replace('.', '', 1).isdigit() else float('inf'),
                    x
                ))
                
                # 创建等级复选框的网格布局
                level_grid = QGridLayout()
                for i, level in enumerate(sorted_levels):
                    checkbox = QCheckBox(str(level))
                    if criteria and system_id in criteria and str(level) in [str(l) for l in criteria[system_id]]:
                        checkbox.setChecked(True)
                    level_checkboxes[str(level)] = checkbox
                    level_grid.addWidget(checkbox, i // 4, i % 4)  # 每行4个复选框
                
                level_layout.addLayout(level_grid)
                system_layout.addWidget(level_group)
                system_data['levels'] = level_checkboxes
            
            if 'type_groups' in system_data or 'levels' in system_data:
                self.system_widgets[system_id] = system_data
                systems_layout.addWidget(system_group)
        
        layout.addWidget(systems_group)
        
        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def validate_and_accept(self):
        """验证输入并接受对话框"""
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "警告", "标准名称不能为空")
            return
            
        # 检查是否至少选择了一个等级
        has_selection = False
        for system_data in self.system_widgets.values():
            if 'type_groups' in system_data:
                # 检查每个类型组中是否有选中的等级
                for type_group_data in system_data['type_groups'].values():
                    if any(checkbox.isChecked() for checkbox in type_group_data['levels'].values()):
                        has_selection = True
                        break
            else:
                if any(checkbox.isChecked() for checkbox in system_data['levels'].values()):
                    has_selection = True
                    break
                
        if not has_selection:
            QMessageBox.warning(self, "警告", "请至少选择一个等级")
            return
            
        self.accept()
    
    def get_data(self):
        """获取对话框数据"""
        criteria_data = {}
        for system_id, system_data in self.system_widgets.items():
            selected_levels = []
            
            if 'type_groups' in system_data:
                # 处理带有类型的系统
                for type_val, type_group_data in system_data['type_groups'].items():
                    for level, checkbox in type_group_data['levels'].items():
                        if checkbox.isChecked():
                            selected_levels.append(level)  # level 已经是组合值了
            else:
                # 处理没有类型的系统
                for level, checkbox in system_data['levels'].items():
                    if checkbox.isChecked():
                        try:
                            if level.isdigit():
                                level = int(level)
                            elif level.replace('.', '', 1).isdigit():
                                level = float(level)
                        except ValueError:
                            pass  # 如果转换失败，保持原始字符串
                        selected_levels.append(level)
            
            if selected_levels:
                criteria_data[system_id] = selected_levels
        
        return {
            'name': self.name_input.text().strip(),
            'criteria': criteria_data
        }

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        print("初始化主窗口...")
        try:
            self.setWindowTitle("RIS文件处理器")
            self.setMinimumSize(1500, 700)
            
            # 获取基础路径（用于静态资源）
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
                print(f"运行在打包环境中，基础路径: {base_path}")
            else:
                base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                print(f"运行在开发环境中，基础路径: {base_path}")
            
            # 设置应用图标
            icon_path = os.path.join(base_path, "resources", "filter.ico")
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
            
            # 获取数据目录
            data_path = self.get_app_data_dir()
            print(f"数据目录路径: {data_path}")
            
            # 确保目录结构存在
            os.makedirs(os.path.join(data_path, "ratings"), exist_ok=True)
            os.makedirs(os.path.join(data_path, "criteria"), exist_ok=True)
            os.makedirs(os.path.join(data_path, "profiles"), exist_ok=True)
            
            # 初始化数据管理器
            config_path = os.path.join(data_path, "config.json")
            
            # 如果配置文件不存在，创建默认配置
            if not os.path.exists(config_path):
                print("创建默认配置文件...")
                default_config = {
                    "rating_systems": {
                        "CCF": {"name": "CCF期刊/会议分类", "description": "中国计算机学会推荐期刊会议目录"},
                        "FMS": {"name": "FMS期刊分类", "description": "金融管理科学期刊目录"},
                        "AJG": {"name": "AJG期刊分类", "description": "Academic Journal Guide"},
                        "ZUFE": {"name": "ZUFE期刊分类", "description": "浙江财经大学期刊目录"}
                    },
                    "rating_file_paths": {
                        "CCF": "ratings/ccf_data.json",
                        "FMS": "ratings/FMS.json",
                        "AJG": "ratings/ajg_2024.json",
                        "ZUFE": "ratings/zufe.json"
                    },
                    "json_attribute_mapping": {
                        "CCF": {"paper_name": "fullname", "level": "rank", "type": "type"},
                        "FMS": {"paper_name": "Paper_name", "level": "Level"},
                        "AJG": {"paper_name": "Paper_name", "level": "Level"},
                        "ZUFE": {"paper_name": "Paper_name", "level": "Level"}
                    },
                    "token_missuo": "",
                    "token_linuxdo": "",
                    "output_directory": "",
                    "subfolder": ""
                }
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, ensure_ascii=False, indent=4)
            
            # 初始化数据管理器，传入正确的参数
            self.data_manager = DataManager(base_path=data_path, config_path=config_path)
            print("数据管理器初始化完成")
            
            # 获取分类标准列表
            self.criteria_list = self.data_manager.get_selection_criteria()
            print(f"加载了 {len(self.criteria_list)} 个分类标准")
            
            # 初始化变量
            self.current_ris_file = None
            self.output_directory = None
            self.process_thread = None
            
            self.init_ui()
            print("界面初始化完成")
            
        except Exception as e:
            print(f"初始化过程中发生错误: {str(e)}")
            raise

    def get_app_data_dir(self):
        """获取应用数据目录"""
        print("正在获取应用数据目录...")
        try:
            if getattr(sys, 'frozen', False):
                # 获取exe所在目录
                exe_dir = os.path.dirname(sys.executable)
                print(f"exe所在目录: {exe_dir}")
                
                # 在exe目录下创建_internal目录
                app_data_dir = os.path.join(exe_dir, "_internal")
                print(f"应用数据目录: {app_data_dir}")
                
                if not os.path.exists(app_data_dir):
                    print("创建_internal目录...")
                    os.makedirs(app_data_dir)
                    
                    # 从临时目录复制数据文件
                    temp_data_dir = os.path.join(sys._MEIPASS, "data")
                    if os.path.exists(temp_data_dir):
                        print(f"从临时目录复制数据文件: {temp_data_dir} -> {app_data_dir}")
                        for item in os.listdir(temp_data_dir):
                            s = os.path.join(temp_data_dir, item)
                            d = os.path.join(app_data_dir, item)
                            if os.path.isdir(s):
                                shutil.copytree(s, d, dirs_exist_ok=True)
                            else:
                                shutil.copy2(s, d)
                
                return app_data_dir
            else:
                # 开发环境下使用项目目录
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                data_dir = os.path.join(base_dir, "data")
                print(f"开发环境数据目录: {data_dir}")
                return data_dir
        except Exception as e:
            print(f"获取应用数据目录时出错: {str(e)}")
            raise

    def init_ui(self):
        """初始化UI界面"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #FFFFFF;
                font-family: "Microsoft YaHei UI";
            }
            QLabel {
                color: #333333;
                font-size: 14px;
                font-weight: 400;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                background-color: #F8F8F8;
                font-size: 14px;
                font-family: "Microsoft YaHei UI";
            }
            QLineEdit:focus {
                border: 2px solid #7F7FD5;
                background-color: white;
            }
            QListWidget {
                border: none;
                border-radius: 0;
                padding: 0;
                background-color: #F8F8F8;
                font-family: "Microsoft YaHei UI";
                font-size: 13px;
            }
            QListWidget::item {
                padding: 0;
                margin: 4px 8px;
                border-radius: 5px;
                border: 1px solid #E0E0E0;
            }
            QListWidget::item:selected {
                border: 2px solid #7F7FD5;
                background-color: transparent;
            }
            QListWidget::item:hover {
                border: 1px solid #7F7FD5;
            }
            QScrollBar:vertical {
                border: none;
                background: #F0F0F0;
                width: 8px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #C0C0C0;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            QFrame.InfoFrame {
                background-color: #F8F8F8;
                border: 2px dashed #E0E0E0;
                border-radius: 10px;
                padding: 15px;
            }
            QLabel.InfoLabel {
                color: #333333;
                font-size: 14px;
                font-weight: 500;
                padding: 5px 0;
            }
        """)
        
        # 创建主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 左侧布局
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(10)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # 拖放区域
        self.drop_area = DropArea()
        left_layout.addWidget(self.drop_area)
        main_layout.addWidget(left_widget)

        # 中间布局
        middle_widget = QWidget()
        middle_layout = QVBoxLayout(middle_widget)
        middle_layout.setSpacing(10)
        middle_layout.setContentsMargins(20, 0, 20, 0)
        
        # 添加弹性空间使箭头垂直居中
        middle_layout.addStretch()
        
        # 添加箭头线容器（使用QWidget确保宽度）
        arrow_container = QWidget()
        arrow_container.setMinimumWidth(200)  # 设置较大的宽度
        arrow_layout = QHBoxLayout(arrow_container)
        arrow_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加箭头线
        arrow_label = QLabel("⟶")  # 使用Unicode箭头字符
        arrow_label.setAlignment(Qt.AlignCenter)
        arrow_label.setStyleSheet("""
            QLabel {
                font-size: 48px;
                color: #7F7FD5;
                font-family: "Segoe UI Symbol";
                padding: 10px;
            }
        """)
        arrow_layout.addWidget(arrow_label)
        middle_layout.addWidget(arrow_container)
        
        # 添加分类标准选择框
        checkbox_container = QWidget()
        checkbox_layout = QVBoxLayout(checkbox_container)
        checkbox_layout.setContentsMargins(10, 10, 10, 10)
        checkbox_layout.setSpacing(5)
        
        # 创建水平布局来放置两组复选框
        criteria_profile_layout = QHBoxLayout()
        
        # 左侧 Criteria 部分
        criteria_widget = QWidget()
        criteria_layout = QVBoxLayout(criteria_widget)
        criteria_layout.setContentsMargins(0, 0, 10, 0)
        criteria_layout.setSpacing(5)
        
        # 添加Criteria标题
        criteria_title = QLabel("选择分类标准：")
        criteria_title.setStyleSheet("""
            QLabel {
                color: #333333;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        criteria_layout.addWidget(criteria_title)
        
        # 添加Criteria复选框
        self.checkboxes = {}
        for criteria in self.criteria_list:
            checkbox = QCheckBox(criteria)
            checkbox.setStyleSheet("""
                QCheckBox {
                    color: #333333;
                    font-size: 13px;
                    padding: 5px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                }
                QCheckBox::indicator:unchecked {
                    border: 2px solid #E0E0E0;
                    border-radius: 4px;
                    background-color: white;
                }
                QCheckBox::indicator:checked {
                    border: 2px solid #7F7FD5;
                    border-radius: 4px;
                    background-color: #7F7FD5;
                    image: url(check.png);
                }
                QCheckBox::indicator:hover {
                    border-color: #7F7FD5;
                }
            """)
            self.checkboxes[criteria] = checkbox
            criteria_layout.addWidget(checkbox)
            
        # 右侧 Profile 部分
        profile_widget = QWidget()
        profile_layout = QVBoxLayout(profile_widget)
        profile_layout.setContentsMargins(10, 0, 0, 0)
        profile_layout.setSpacing(5)
        
        # 添加Profile标题
        profile_title = QLabel("选择组合标准：")
        profile_title.setStyleSheet("""
            QLabel {
                color: #333333;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        profile_layout.addWidget(profile_title)
        
        # 添加Profile复选框
        self.profile_checkboxes = {}
        profiles = self.data_manager.get_selection_profiles()
        for profile_name in profiles.keys():
            checkbox = QCheckBox(profile_name)
            checkbox.setStyleSheet("""
                QCheckBox {
                    color: #333333;
                    font-size: 13px;
                    padding: 5px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                }
                QCheckBox::indicator:unchecked {
                    border: 2px solid #E0E0E0;
                    border-radius: 4px;
                    background-color: white;
                }
                QCheckBox::indicator:checked {
                    border: 2px solid #7F7FD5;
                    border-radius: 4px;
                    background-color: #7F7FD5;
                    image: url(check.png);
                }
                QCheckBox::indicator:hover {
                    border-color: #7F7FD5;
                }
            """)
            self.profile_checkboxes[profile_name] = checkbox
            profile_layout.addWidget(checkbox)
            
        # 将两个部分添加到水平布局
        criteria_profile_layout.addWidget(criteria_widget)
        criteria_profile_layout.addWidget(profile_widget)
        
        # 将水平布局添加到主布局
        checkbox_layout.addLayout(criteria_profile_layout)
        
        # 添加分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #E0E0E0;")
        checkbox_layout.addWidget(line)
        
        # 添加翻译选项标题
        trans_title = QLabel("翻译选项：")
        trans_title.setStyleSheet("""
            QLabel {
                color: #333333;
                font-size: 14px;
                font-weight: bold;
                margin-top: 10px;
            }
        """)
        checkbox_layout.addWidget(trans_title)
        
        # 添加翻译选项复选框
        self.trans_ti_checkbox = QCheckBox("翻译标题")
        self.trans_ab_checkbox = QCheckBox("翻译摘要")
        for checkbox in [self.trans_ti_checkbox, self.trans_ab_checkbox]:
            checkbox.setStyleSheet("""
                QCheckBox {
                    font-size: 14px;
                    padding: 3px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                }
                QCheckBox::indicator:unchecked {
                    border: 2px solid #E0E0E0;
                    border-radius: 4px;
                    background-color: white;
                }
                QCheckBox::indicator:checked {
                    border: 2px solid #7F7FD5;
                    border-radius: 4px;
                    background-color: #7F7FD5;
                }
            """)
            checkbox_layout.addWidget(checkbox)
        
        # 添加令牌输入框标题
        token_title = QLabel("翻译服务令牌：")
        token_title.setStyleSheet("""
            QLabel {
                color: #333333;
                font-size: 14px;
                font-weight: bold;
                margin-top: 10px;
            }
        """)
        checkbox_layout.addWidget(token_title)
        
        # 添加令牌输入框
        self.token_missuo_input = QLineEdit()
        self.token_missuo_input.setPlaceholderText("Missuo令牌（可选）")
        self.token_linuxdo_input = QLineEdit()
        self.token_linuxdo_input.setPlaceholderText("Linuxdo令牌（可选）")
        
        for input_field in [self.token_missuo_input, self.token_linuxdo_input]:
            input_field.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    border: 2px solid #E0E0E0;
                    border-radius: 8px;
                    background-color: white;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border: 2px solid #7F7FD5;
                }
            """)
            checkbox_layout.addWidget(input_field)
        
        middle_layout.addWidget(checkbox_container)
        
        # 生成按钮容器
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(50, 0, 50, 0)  # 通过边距控制按钮宽度
        
        # 生成按钮
        self.generate_btn = StyledButton("生成")
        self.generate_btn.clicked.connect(self.manual_generate)
        self.generate_btn.setMinimumHeight(40)
        button_layout.addWidget(self.generate_btn)
        
        # 添加进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #E0E0E0;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #7F7FD5;
                border-radius: 3px;
            }
        """)
        self.progress_bar.hide()  # 初始时隐藏进度条
        
        # 将进度条添加到布局中（在生成按钮下方）
        button_layout.addWidget(self.progress_bar)
        
        middle_layout.addWidget(button_container)
        
        # 添加弹性空间
        middle_layout.addStretch()
        main_layout.addWidget(middle_widget)

        # 右侧布局
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(10)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # 信息显示框
        info_frame = QFrame()
        info_frame.setObjectName("InfoFrame")
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(10)
        
        # 输出目录选择按钮
        self.select_output_btn = StyledButton("选择输出目录")
        self.select_output_btn.clicked.connect(self.select_output_directory)
        info_layout.addWidget(self.select_output_btn)
        
        # 子文件夹名称输入框
        subfolder_layout = QHBoxLayout()
        subfolder_label = QLabel("子文件夹名称：")
        self.subfolder_input = QLineEdit()
        self.subfolder_input.setPlaceholderText("检索式")
        subfolder_layout.addWidget(subfolder_label)
        subfolder_layout.addWidget(self.subfolder_input)
        info_layout.addLayout(subfolder_layout)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #E0E0E0;")
        info_layout.addWidget(line)
        
        # 创建文件列表容器
        list_container = QWidget()
        list_layout = QVBoxLayout(list_container)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(0)
        
        # 文件列表
        self.file_list = QListWidget()
        self.file_list.itemDoubleClicked.connect(self.open_file)
        list_layout.addWidget(self.file_list)
        
        # 总计行
        self.total_widget = QWidget()
        self.total_widget.setFixedHeight(50)
        self.total_widget.setStyleSheet("""
            QWidget {
                background-color: #F8F8F8;
                border-top: 1px solid #E0E0E0;
            }
        """)
        
        total_layout = QHBoxLayout(self.total_widget)
        total_layout.setContentsMargins(15, 0, 15, 0)
        total_layout.setAlignment(Qt.AlignVCenter)
        
        self.total_label = QLabel("共计")
        self.count_label = QLabel("0条目")
        self.total_label.setStyleSheet("""
            color: #7F7FD5;
            font-weight: bold;
            font-size: 14px;
        """)
        self.count_label.setStyleSheet("""
            color: #7F7FD5;
            font-weight: bold;
            font-size: 14px;
        """)
        
        total_layout.addWidget(self.total_label)
        total_layout.addStretch()
        total_layout.addWidget(self.count_label)
        
        list_layout.addWidget(self.total_widget)
        
        info_layout.addWidget(list_container)
        right_layout.addWidget(info_frame)
        main_layout.addWidget(right_widget)
        
        # 设置三栏比例为3:4:3
        main_layout.setStretch(0, 3)
        main_layout.setStretch(1, 4)
        main_layout.setStretch(2, 3)

        # 加载上次的配置
        self.load_config()
        
        # 如果有保存的输出目录，更新显示
        if self.output_directory:
            self.select_output_btn.setText(f"输出目录：{os.path.basename(self.output_directory)}")

        # 添加设置按钮到工具栏
        self.toolbar = self.addToolBar('工具栏')
        settings_action = self.toolbar.addAction('设置')
        settings_action.triggered.connect(self.open_settings)

    def select_output_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if directory:
            self.output_directory = directory
            self.select_output_btn.setText(f"输出目录：{os.path.basename(directory)}")
            self.save_config()

    def update_file_list(self):
        """更新文件列表显示"""
        try:
            self.file_list.clear()
            subfolder_name = self.subfolder_input.text().strip()
            if self.output_directory and subfolder_name:
                full_path = os.path.join(self.output_directory, subfolder_name)
                print(f"正在扫描目录: {full_path}")
                
                if not os.path.exists(full_path):
                    print(f"输出目录不存在: {full_path}")
                    return
                    
                files = [f for f in os.listdir(full_path) if f.endswith('.ris')]
                print(f"找到 {len(files)} 个RIS文件")
                
                total_entries = 0
                file_entries = []
                
                # 首先计算总条目数
                for file in files:
                    file_path = os.path.join(full_path, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8-sig') as f:
                            content = f.read()
                            entry_count = content.count('ER  -')
                            total_entries += entry_count
                            file_entries.append((file, entry_count))
                            print(f"文件 {file}: {entry_count} 条目")
                    except Exception as e:
                        print(f"读取文件 {file} 出错：{str(e)}")
                        file_entries.append((file, 0))
                
                # 添加文件条目到列表
                for file, entry_count in file_entries:
                    if total_entries > 0:
                        percentage = (entry_count / total_entries) * 100
                        item = QListWidgetItem()
                        
                        # 创建主容器widget
                        container = QWidget()
                        container.setFixedHeight(40)
                        container_layout = QVBoxLayout(container)
                        container_layout.setContentsMargins(4, 4, 4, 4)
                        container_layout.setSpacing(0)
                        
                        # 创建内容容器
                        content_container = QWidget()
                        content_layout = QHBoxLayout(content_container)
                        content_layout.setContentsMargins(15, 0, 15, 0)
                        
                        # 文件名和条目数
                        name_label = QLabel(file)
                        name_label.setStyleSheet("""
                            background: transparent;
                            font-size: 14px;
                        """)
                        count_label = QLabel(f"{entry_count}条目")
                        count_label.setStyleSheet("""
                            color: #666666;
                            background: transparent;
                            font-size: 14px;
                        """)
                        
                        content_layout.addWidget(name_label)
                        content_layout.addStretch()
                        content_layout.addWidget(count_label)
                        
                        # 设置背景和进度条
                        content_container.setStyleSheet(f"""
                            QWidget {{
                                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                    stop:0 #E6E6F5,
                                    stop:{percentage/100} #E6E6F5,
                                    stop:{percentage/100} #F8F8F8,
                                    stop:1 #F8F8F8);
                                border-radius: 5px;
                            }}
                        """)
                        
                        container_layout.addWidget(content_container)
                        
                        item.setSizeHint(QSize(container.sizeHint().width(), 40))
                        self.file_list.addItem(item)
                        self.file_list.setItemWidget(item, container)
                
                # 更新总计行
                self.count_label.setText(f"{total_entries}条目")
                print(f"总计: {total_entries} 条目")
                
        except Exception as e:
            print(f"更新文件列表时出错: {str(e)}")
            QMessageBox.warning(self, "警告", f"更新文件列表时出错: {str(e)}")

    def load_config(self):
        """加载配置"""
        try:
            # 从data_manager获取配置
            config = self.data_manager.config
            self.token_missuo_input.setText(config.token_missuo)
            self.token_linuxdo_input.setText(config.token_linuxdo)
            self.output_directory = config.output_directory
            self.subfolder_input.setText(config.subfolder)
            
            if self.output_directory:
                self.select_output_btn.setText(f"输出目录：{os.path.basename(self.output_directory)}")
        except Exception as e:
            print(f"加载配置文件出错：{str(e)}")

    def save_config(self):
        """保存配置"""
        try:
            # 更新data_manager中的配置
            self.data_manager.update_config(
                token_missuo=self.token_missuo_input.text(),
                token_linuxdo=self.token_linuxdo_input.text(),
                output_directory=self.output_directory or '',
                subfolder=self.subfolder_input.text()
            )
            
            # 保存配置
            self.data_manager.save_config()
        except Exception as e:
            print(f"保存配置文件出错：{str(e)}")

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择RIS文件", "", "RIS文件 (*.ris)")
        if file_path:
            # 更新拖放区域显示的文件名
            self.drop_area.update_file_name(file_path)
            # 只保存文件路径，不自动处理
            self.current_ris_file = file_path

    def process_file(self, file_path):
        """处理RIS文件"""
        self.current_ris_file = file_path  # 保存当前文件路径
        
        if not self.output_directory:
            self.output_directory = os.path.join(os.path.dirname(file_path), 'out_ris')
            self.select_output_btn.setText(f"输出目录：{os.path.basename(self.output_directory)}")

        # 不再自动设置子文件夹名称
        if not self.subfolder_input.text().strip():
            return

        # 获取选中的分类标准
        selected = [criteria for criteria, checkbox in self.checkboxes.items() if checkbox.isChecked()]
        if not selected:
            QMessageBox.warning(self, "警告", "请至少选择一个分类标准")
            return

        # 构建完整的输出路径
        full_output_path = os.path.join(self.output_directory, self.subfolder_input.text().strip())

        try:
            process_ris_file(file_path, selected, full_output_path)
            self.update_file_list()
            QMessageBox.information(self, "成功", "文件处理完成！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"处理文件时出错：{str(e)}")

    def open_file(self, item):
        # 获取当前显示的子文件夹名称
        subfolder_name = self.subfolder_input.text().strip()
        
        # 获取实际的文件名
        widget = self.file_list.itemWidget(item)
        if widget:
            # 获取内容容器
            content_container = widget.layout().itemAt(0).widget()
            # 获取文件名标签
            name_label = content_container.layout().itemAt(0).widget()
            file_name = name_label.text()
        else:
            # 如果是普通项，直接使用item的文本
            file_name = item.text()
        
        file_path = os.path.join(self.output_directory, subfolder_name, file_name)
        if os.path.exists(file_path):
            import platform
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                os.system(f'open "{file_path}"')
            else:  # Linux
                os.system(f'xdg-open "{file_path}"')

    def update_progress(self, current, total):
        """更新进度条"""
        percentage = int((current / total) * 100)
        self.progress_bar.setValue(percentage)
        self.progress_bar.setFormat(f'处理中... {percentage}% ({current}/{total})')

    def process_finished(self, success):
        """处理完成的回调"""
        self.progress_bar.hide()
        self.generate_btn.setEnabled(True)
        if success:
            try:
                self.update_file_list()
                # 获取处理后的文件统计
                subfolder_name = self.subfolder_input.text().strip()
                full_path = os.path.join(self.output_directory, subfolder_name)
                if os.path.exists(full_path):
                    files = [f for f in os.listdir(full_path) if f.endswith('.ris')]
                    QMessageBox.information(
                        self, 
                        "成功", 
                        f"文件处理完成！\n生成了 {len(files)} 个分类文件。"
                    )
            except Exception as e:
                print(f"处理完成后更新界面时出错: {str(e)}")
                QMessageBox.information(self, "成功", "文件处理完成！")

    def process_error(self, error_msg):
        """处理错误的回调"""
        self.progress_bar.hide()
        self.generate_btn.setEnabled(True)
        QMessageBox.critical(self, "错误", f"处理文件时出错：{error_msg}")

    def manual_generate(self):
        """生成处理结果"""
        if not self.current_ris_file:
            QMessageBox.warning(self, "警告", "请先选择或拖入RIS文件")
            return
            
        if not self.output_directory:
            QMessageBox.warning(self, "警告", "请选择输出目录")
            return
            
        if not self.subfolder_input.text().strip():
            QMessageBox.warning(self, "警告", "请输入子文件夹名称")
            return

        # 构建完整的输出路径
        full_output_path = os.path.join(self.output_directory, self.subfolder_input.text().strip())
        print(f"输出路径: {full_output_path}")
        
        # 确保输出目录存在
        os.makedirs(full_output_path, exist_ok=True)
        
        # 获取翻译选项状态
        trans_ti = self.trans_ti_checkbox.isChecked()
        trans_ab = self.trans_ab_checkbox.isChecked()
        
        # 获取令牌（如果有）
        token_missuo = self.token_missuo_input.text().strip() or None
        token_linuxdo = self.token_linuxdo_input.text().strip() or None
        
        # 如果需要翻译但没有提供任何令牌，显示提示信息
        if (trans_ti or trans_ab) and not (token_missuo or token_linuxdo):
            QMessageBox.information(
                self, 
                "提示", 
                "未提供翻译服务令牌，将使用免费翻译服务（速度可能较慢）"
            )
        
        # 获取选中的分类标准
        selected_criteria = {}
        for criteria, checkbox in self.checkboxes.items():
            if checkbox.isChecked():
                criteria_data = self.data_manager.get_criteria(criteria)
                if criteria_data:
                    selected_criteria[criteria] = criteria_data  # 直接使用criteria_data，不需要转换

        # 获取选中的组合标准
        selected_profiles = {}
        for profile_name, checkbox in self.profile_checkboxes.items():
            if checkbox.isChecked():
                profile_data = self.data_manager.get_profile(profile_name)
                if profile_data:
                    selected_profiles[profile_name] = profile_data  # 直接使用profile_data，不需要转换

        if not selected_criteria and not selected_profiles:
            QMessageBox.warning(self, "警告", "请至少选择一个分类标准或组合标准")
            return

        # 检查数据文件
        missing_files = self.check_rating_files(selected_criteria)
        if missing_files:
            msg = "以下评级系统缺少数据文件：\n" + "\n".join(missing_files)
            msg += "\n\n是否继续处理？"
            reply = QMessageBox.question(
                self,
                "警告",
                msg,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        # 获取基础路径
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # 获取评级数据文件路径（使用绝对路径）
        path_rating_file = {
            system: os.path.join(base_path, path)
            for system, path in self.data_manager.config.rating_file_paths.items()
        }
        
        # 获取JSON属性映射
        json_attribute_mapping = self.data_manager.config.json_attribute_mapping
        json_attribute_title = {
            system: mapping['paper_name']
            for system, mapping in json_attribute_mapping.items()
        }
        json_attribute_rating = {
            system: mapping['level']
            for system, mapping in json_attribute_mapping.items()
        }

        # 构建完整的输出路径
        full_output_path = os.path.join(self.output_directory, self.subfolder_input.text().strip())

        # 禁用生成按钮，显示进度条
        self.generate_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.show()

        # 创建并启动处理线程
        self.process_thread = ProcessThread(
            file_path=self.current_ris_file,
            selected=selected_criteria,
            selection_profile=selected_profiles,
            path_rating_file=path_rating_file,
            json_attribute_title=json_attribute_title,
            json_attribute_rating=json_attribute_rating,
            output_path=full_output_path,
            trans_ti=trans_ti,
            trans_ab=trans_ab,
            token_missuo=token_missuo,
            token_linuxdo=token_linuxdo
        )
        self.process_thread.progress.connect(self.update_progress)
        self.process_thread.finished.connect(self.process_finished)
        self.process_thread.error.connect(self.process_error)
        self.process_thread.start()

    def check_rating_files(self, selected_criteria):
        """检查选中的评级系统是否都有对应的数据文件"""
        missing_files = []
        
        # 收集所有使用到的系统
        used_systems = set()
        for criteria_data in selected_criteria.values():
            used_systems.update(criteria_data.keys())
        
        # 检查每个系统的数据文件
        for system_id in used_systems:
            file_info = self.data_manager.get_rating_file_info(system_id)
            if not file_info or not file_info['file_path']:
                missing_files.append(f"{system_id} (未设置文件)")
                continue
            
            file_path = os.path.join(self.data_manager.base_path, file_info['file_path'])
            if not os.path.exists(file_path):
                missing_files.append(f"{system_id} (文件不存在: {file_info['file_path']})")
        
        return missing_files

    def closeEvent(self, event):
        """窗口关闭时保存配置"""
        self.save_config()
        super().closeEvent(event) 

    def open_settings(self):
        """打开设置对话框"""
        dialog = SettingsDialog(self.data_manager, self)
        if dialog.exec_() == QDialog.Accepted:
            # 如果用户点击了确定，重新加载数据
            self._load_all_data()

    def _load_all_data(self):
        # 实现重新加载所有数据的逻辑
        pass 

class ProfileDialog(QDialog):
    def __init__(self, data_manager: DataManager, name="", profile=None, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.setWindowTitle("组合标准设置")
        self.setMinimumWidth(800)
        self.setup_ui(name, profile)
    
    def setup_ui(self, name, profile):
        layout = QVBoxLayout(self)
        
        # 标准名称
        name_layout = QHBoxLayout()
        name_label = QLabel("标准名称:")
        self.name_input = QLineEdit(name)
        if name:  # 如果是编辑模式，名称不可修改
            self.name_input.setEnabled(False)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # 创建分组标准设置区域
        self.criteria_sets_group = QGroupBox("分组标准设置")
        criteria_sets_layout = QVBoxLayout(self.criteria_sets_group)
        
        # 添加分组的按钮
        add_set_btn = QPushButton("添加分组")
        add_set_btn.clicked.connect(self.add_criteria_set)
        criteria_sets_layout.addWidget(add_set_btn)
        
        # 分组列表
        self.sets_list = QListWidget()
        self.sets_list.currentItemChanged.connect(self.on_set_selected)
        criteria_sets_layout.addWidget(self.sets_list)
        
        # 分组编辑区域
        self.set_edit_group = QGroupBox("分组编辑")
        set_edit_layout = QVBoxLayout(self.set_edit_group)
        
        # 分组名称
        set_name_layout = QHBoxLayout()
        set_name_label = QLabel("分组名称:")
        self.set_name_input = QLineEdit()
        set_name_layout.addWidget(set_name_label)
        set_name_layout.addWidget(self.set_name_input)
        set_edit_layout.addLayout(set_name_layout)
        
        # 评级系统选择
        self.system_widgets = {}
        rating_systems = self.data_manager.get_rating_systems()
        
        for system_id, info in rating_systems.items():
            # 创建系统组
            system_group = QGroupBox(info['name'])
            system_layout = QVBoxLayout(system_group)
            
            # 从数据文件中获取可用的等级和类型
            file_info = self.data_manager.get_rating_file_info(system_id)
            available_levels = set()
            available_types = set()
            
            if file_info and file_info['file_path']:
                try:
                    file_path = os.path.join(self.data_manager.base_path, file_info['file_path'])
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        level_field = file_info['mapping']['level']
                        # 过滤掉None值并转换为字符串
                        available_levels = {str(item[level_field]) 
                                         for item in data 
                                         if level_field in item and item[level_field] is not None}
                        
                        # 如果有类型字段，获取可用的类型
                        if 'type' in file_info['mapping']:
                            type_field = file_info['mapping']['type']
                            available_types = {str(item[type_field])
                                            for item in data
                                            if type_field in item and item[type_field] is not None}
                except Exception as e:
                    print(f"读取文件 {file_path} 时出错: {str(e)}")
                    continue
            
            # 创建等级和类型的复选框
            system_data = {'group': system_group}
            
            if available_types:
                # 如果有类型字段，为每个类型创建独立的等级选择区域
                type_level_groups = {}
                for type_val in sorted(available_types):
                    type_group = QGroupBox(f"类型：{type_val}")
                    type_layout = QVBoxLayout(type_group)
                    
                    # 为该类型创建等级选择
                    level_checkboxes = {}
                    # 将等级值转换为字符串并排序
                    sorted_levels = sorted(available_levels, key=lambda x: (
                        float(x) if x.replace('.', '', 1).isdigit() else float('inf'),
                        x
                    ))
                    
                    # 创建等级复选框的网格布局
                    level_grid = QGridLayout()
                    for i, level in enumerate(sorted_levels):
                        checkbox = QCheckBox(str(level))
                        level_checkboxes[str(level)] = checkbox
                        level_grid.addWidget(checkbox, i // 4, i % 4)  # 每行4个复选框
                    
                    type_layout.addLayout(level_grid)
                    system_layout.addWidget(type_group)
                    type_level_groups[str(type_val)] = {
                        'group': type_group,
                        'levels': level_checkboxes
                    }
                
                system_data['type_groups'] = type_level_groups
            else:
                # 如果没有类型字段，创建单一的等级选择区域
                level_group = QGroupBox("等级选择")
                level_layout = QVBoxLayout(level_group)
                
                level_checkboxes = {}
                # 将等级值转换为字符串并排序
                sorted_levels = sorted(available_levels, key=lambda x: (
                    float(x) if x.replace('.', '', 1).isdigit() else float('inf'),
                    x
                ))
                
                # 创建等级复选框的网格布局
                level_grid = QGridLayout()
                for i, level in enumerate(sorted_levels):
                    checkbox = QCheckBox(str(level))
                    level_checkboxes[str(level)] = checkbox
                    level_grid.addWidget(checkbox, i // 4, i % 4)  # 每行4个复选框
                
                level_layout.addLayout(level_grid)
                system_layout.addWidget(level_group)
                system_data['levels'] = level_checkboxes
            
            if 'type_groups' in system_data or 'levels' in system_data:
                self.system_widgets[system_id] = system_data
                set_edit_layout.addWidget(system_group)
        
        # 分组操作按钮
        set_buttons_layout = QHBoxLayout()
        save_set_btn = QPushButton("保存分组")
        save_set_btn.clicked.connect(self.save_current_set)
        delete_set_btn = QPushButton("删除分组")
        delete_set_btn.clicked.connect(self.delete_current_set)
        set_buttons_layout.addWidget(save_set_btn)
        set_buttons_layout.addWidget(delete_set_btn)
        set_edit_layout.addLayout(set_buttons_layout)
        
        # 添加分组编辑区域
        criteria_sets_layout.addWidget(self.set_edit_group)
        
        # 添加分组标准设置区域到主布局
        layout.addWidget(self.criteria_sets_group)
        
        # 对话框按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # 初始化数据
        self.criteria_sets = {}
        if profile:
            for set_name, criteria in profile.items():
                self.criteria_sets[set_name] = criteria
                self.sets_list.addItem(set_name)
    
    def on_set_selected(self, current, previous):
        """当选择的分组改变时"""
        if current:
            set_name = current.text()
            self.set_name_input.setText(set_name)
            
            # 更新复选框状态
            criteria = self.criteria_sets.get(set_name, {})
            print(f"Loading criteria for set {set_name}: {criteria}")  # 调试输出
            
            for system_id, system_data in self.system_widgets.items():
                if 'type_groups' in system_data:
                    # 获取系统的标准数据
                    system_levels = criteria.get(system_id, [])
                    print(f"System {system_id} - Levels: {system_levels}")  # 调试输出
                    
                    for type_val, type_group_data in system_data['type_groups'].items():
                        for level, checkbox in type_group_data['levels'].items():
                            # 组合等级和类型
                            combined_value = f"{level}{type_val}"
                            is_checked = system_id in criteria and combined_value in criteria[system_id]
                            print(f"  Combined {combined_value}: {is_checked}")  # 调试输出
                            checkbox.setChecked(is_checked)
                else:
                    # 获取系统的标准数据
                    system_levels = criteria.get(system_id, [])
                    print(f"System {system_id} - Levels: {system_levels}")  # 调试输出
                    
                    for level, checkbox in system_data['levels'].items():
                        is_checked = system_id in criteria and str(level) in [str(l) for l in system_levels]
                        print(f"  Level {level}: {is_checked}")  # 调试输出
                        checkbox.setChecked(is_checked)
    
    def add_criteria_set(self):
        """添加新的分组"""
        # 生成默认名称
        base_name = "新分组"
        name = base_name
        counter = 1
        while name in self.criteria_sets:
            name = f"{base_name}{counter}"
            counter += 1
        
        # 添加到列表和数据中
        self.criteria_sets[name] = {}
        self.sets_list.addItem(name)
        self.sets_list.setCurrentRow(self.sets_list.count() - 1)
    
    def save_current_set(self):
        """保存当前分组的更改"""
        current_item = self.sets_list.currentItem()
        if not current_item:
            return
        
        old_name = current_item.text()
        new_name = self.set_name_input.text().strip()
        
        if not new_name:
            QMessageBox.warning(self, "警告", "分组名称不能为空")
            return
        
        if new_name != old_name and new_name in self.criteria_sets:
            QMessageBox.warning(self, "警告", "分组名称已存在")
            return
        
        # 收集选中的等级
        criteria = {}
        for system_id, system_data in self.system_widgets.items():
            if 'type_groups' in system_data:
                # 处理带有类型的系统
                selected_levels = []
                for type_val, type_group_data in system_data['type_groups'].items():
                    for level, checkbox in type_group_data['levels'].items():
                        if checkbox.isChecked():
                            # 组合等级和类型
                            combined_value = f"{level}{type_val}"
                            selected_levels.append(combined_value)
                
                if selected_levels:
                    criteria[system_id] = selected_levels
            else:
                # 处理没有类型的系统
                selected_levels = []
                for level, checkbox in system_data['levels'].items():
                    if checkbox.isChecked():
                        try:
                            if level.isdigit():
                                level = int(level)
                            elif level.replace('.', '', 1).isdigit():
                                level = float(level)
                        except ValueError:
                            pass  # 如果转换失败，保持原始字符串
                        selected_levels.append(level)
                
                if selected_levels:
                    criteria[system_id] = selected_levels
        
        # 更新数据
        if old_name in self.criteria_sets:
            del self.criteria_sets[old_name]
        self.criteria_sets[new_name] = criteria
        
        # 更新列表项
        current_item.setText(new_name)
        QMessageBox.information(self, "成功", "分组保存成功")
    
    def delete_current_set(self):
        """删除当前分组"""
        current_item = self.sets_list.currentItem()
        if not current_item:
            return
        
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除分组 {current_item.text()} 吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            set_name = current_item.text()
            if set_name in self.criteria_sets:
                del self.criteria_sets[set_name]
            self.sets_list.takeItem(self.sets_list.row(current_item))
    
    def validate_and_accept(self):
        """验证输入并接受对话框"""
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "警告", "标准名称不能为空")
            return
        
        if not self.criteria_sets:
            QMessageBox.warning(self, "警告", "请至少添加一个分组")
            return
        
        self.accept()
    
    def get_data(self):
        """获取对话框数据"""
        return {
            'name': self.name_input.text().strip(),
            'criteria_sets': self.criteria_sets
        }