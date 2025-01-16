from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import json
import os
from core.paper_processor import process_ris_file, selection_criteria
import sys

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

    def __init__(self, file_path, selected, output_path, trans_ti, trans_ab, token_missuo, token_linuxdo):
        super().__init__()
        self.file_path = file_path
        self.selected = selected
        self.output_path = output_path
        self.trans_ti = trans_ti
        self.trans_ab = trans_ab
        self.token_missuo = token_missuo
        self.token_linuxdo = token_linuxdo

    def run(self):
        try:
            result = process_ris_file(
                self.file_path, 
                self.selected, 
                self.output_path,
                trans_ti=self.trans_ti,
                trans_ab=self.trans_ab,
                tokenMissuo=self.token_missuo,
                tokenLinuxdo=self.token_linuxdo,
                progress_callback=self.progress.emit
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RIS文件处理器")
        self.setMinimumSize(1500, 500)  # 增加窗口宽度
        
        # 设置应用图标
        icon_path = get_resource_path(os.path.join("resources", "filter.ico"))
        icon = QIcon(icon_path)
        self.setWindowIcon(icon)
        
        # 获取应用程序的正确路径
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        else:
            application_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        # 配置文件路径
        self.config_file = os.path.join(application_path, 'config.json')
        
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
        
        # 添加标题
        title_label = QLabel("选择分类标准：")
        title_label.setStyleSheet("""
            QLabel {
                color: #333333;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        checkbox_layout.addWidget(title_label)
        
        # 添加分类标准复选框
        self.checkboxes = {}
        criteria_list = list(selection_criteria.keys())  # 从 selection_criteria 获取选项
        for criteria in criteria_list:
            checkbox = QCheckBox(criteria)
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
            self.checkboxes[criteria] = checkbox
            checkbox_layout.addWidget(checkbox)
        
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

        self.output_directory = None
        self.current_ris_file = None

        # 加载上次的配置
        self.load_config()
        
        # 如果有保存的输出目录，更新显示
        if self.output_directory:
            self.select_output_btn.setText(f"输出目录：{os.path.basename(self.output_directory)}")

    def select_output_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if directory:
            self.output_directory = directory
            self.select_output_btn.setText(f"输出目录：{os.path.basename(directory)}")
            self.save_config()

    def update_file_list(self):
        self.file_list.clear()
        subfolder_name = self.subfolder_input.text().strip()
        if self.output_directory and subfolder_name:
            full_path = os.path.join(self.output_directory, subfolder_name)
            if os.path.exists(full_path):
                files = [f for f in os.listdir(full_path) if f.endswith('.ris')]
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
                    except Exception as e:
                        print(f"读取文件出错：{str(e)}")
                        file_entries.append((file, 0))
                
                # 添加文件条目
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

    def load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.output_directory = config.get('output_directory')
                    # 加载翻译令牌
                    self.token_missuo_input.setText(config.get('token_missuo', ''))
                    self.token_linuxdo_input.setText(config.get('token_linuxdo', ''))
                    # 加载翻译选项
                    self.trans_ti_checkbox.setChecked(config.get('trans_ti', False))
                    self.trans_ab_checkbox.setChecked(config.get('trans_ab', False))
        except Exception as e:
            print(f"加载配置文件出错：{str(e)}")
            self.output_directory = None

    def save_config(self):
        """保存配置到文件"""
        try:
            config = {
                'output_directory': self.output_directory,
                'token_missuo': self.token_missuo_input.text(),
                'token_linuxdo': self.token_linuxdo_input.text(),
                'trans_ti': self.trans_ti_checkbox.isChecked(),
                'trans_ab': self.trans_ab_checkbox.isChecked()
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
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
            self.update_file_list()
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
        selected = [criteria for criteria, checkbox in self.checkboxes.items() if checkbox.isChecked()]
        if not selected:
            QMessageBox.warning(self, "警告", "请至少选择一个分类标准")
            return

        # 构建完整的输出路径
        full_output_path = os.path.join(self.output_directory, self.subfolder_input.text().strip())

        # 禁用生成按钮，显示进度条
        self.generate_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.show()

        # 创建并启动处理线程
        self.process_thread = ProcessThread(
            self.current_ris_file, 
            selected, 
            full_output_path,
            trans_ti,
            trans_ab,
            token_missuo,
            token_linuxdo
        )
        self.process_thread.progress.connect(self.update_progress)
        self.process_thread.finished.connect(self.process_finished)
        self.process_thread.error.connect(self.process_error)
        self.process_thread.start()

    def closeEvent(self, event):
        """窗口关闭时保存配置"""
        self.save_config()
        super().closeEvent(event) 