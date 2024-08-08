import os
import platform
import subprocess
from PyQt6.QtWidgets import QWidget, QFileDialog, QVBoxLayout, QHBoxLayout, QLabel,QScrollArea, QLineEdit,QCheckBox ,QPushButton, QMessageBox, QDialog, QFormLayout, QDialogButtonBox, QProgressDialog
from PyQt6.QtCore import Qt, QTimer, QMetaObject, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon
from simulation_spider import run_vehicle_information_spider  # 導入爬蟲函數
from utils import load_credentials, save_credentials, get_sorted_filenames, resource_path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('智慧系統登入')

        layout = QFormLayout(self)
        self.resize(300, 100)

        self.remind = QLabel('※智慧型交通執法管理系統帳號密碼', self)
        self.remind.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.remind.setStyleSheet("font-size: 16px; color:red")
        layout.addRow(self.remind)

        self.username_input = QLineEdit(self)
        self.username_input.setStyleSheet("font-size: 16px; height: 20px; ")
        self.password_input = QLineEdit(self)
        self.password_input.setStyleSheet("font-size: 16px; height: 20px; ")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        layout.addRow("<span style='font-size: 16px;'>使用者帳號</span>:", self.username_input)
        layout.addRow("<span style='font-size: 16px;'>密碼</span>:", self.password_input)

        # 加入顯示/隱藏密碼的複選框
        self.show_password_checkbox = QCheckBox('顯示密碼')
        self.show_password_checkbox.toggled.connect(self.toggle_password_visibility)
        layout.addRow(self.show_password_checkbox)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        layout.addWidget(self.buttons)

        # 讀取並填充帳號密碼
        self.load_saved_credentials()

    def toggle_password_visibility(self, checked):
        if checked:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

    def get_credentials(self):
        return self.username_input.text(), self.password_input.text()
    
    def load_saved_credentials(self):
       username, password = load_credentials()
    #    print(username, password)    
       if username and password:
           self.username_input.setText(username)
           self.password_input.setText(password)

class SpiderThread(QThread):
    result_ready = pyqtSignal(dict)

    def __init__(self, inputs, username, password):
        super().__init__()
        self.inputs = inputs
        self.username = username
        self.password = password

    def run(self):
        result = run_vehicle_information_spider(self.inputs, self.username, self.password)
        self.result_ready.emit(result)

class DirectoryWatcher(QThread):
    file_changed = pyqtSignal()

    def __init__(self, directory):
        super().__init__()
        self.directory = directory
        self.observer = Observer()

    def run(self):
        event_handler = FileSystemEventHandler()
        event_handler.on_any_event = self.on_any_event
        self.observer.schedule(event_handler, self.directory, recursive=False)
        self.observer.start()
        self.exec()

    def on_any_event(self, event):
        if event.event_type in ('created', 'deleted', 'modified'):
            self.file_changed.emit()

    def stop(self):
        self.observer.stop()
        self.observer.join()

class Page1(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        # self.setStyleSheet("background-color: lightblue;")
        # 初始化勾選狀態的字典
        self.selected_cases = {}

        # 設置第一頁的佈局
        layout = QVBoxLayout()

        # 標題
        self.title = QLabel('智能上傳系統', self)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("font-size: 24px; font-weight: bold;")

        # 顯示已選擇案件數量的標籤
        self.selected_count_label = QLabel('已選擇案件數量：0/10', self)
        self.selected_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.selected_count_label.setStyleSheet("font-size: 18px;")

        # 全選勾選匡
        self.select_all_checkbox = QCheckBox("全選", self)
        self.select_all_checkbox.setChecked(True)  # 初始設置為選中狀態
        self.select_all_checkbox.setStyleSheet("font-size: 18px;")  # 設置字體大小
        self.select_all_checkbox.stateChanged.connect(self.toggle_select_all)

        select_all_checkbox_layout = QHBoxLayout()
        select_all_checkbox_layout.addStretch()
        select_all_checkbox_layout.addWidget(self.select_all_checkbox)  # 加入全選勾選匡

        # ----------------------------------------------------------------    
        # 沒有檔案的標籤
        self.no_content_label = QWidget(self)
        self.no_content_label.setMaximumHeight(400)

        # 標題
        self.no_file_title = QLabel('智能上傳系統', self.no_content_label)
        self.no_file_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_file_title.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.no_file_title.setFixedSize(400, 30)

        # 創建一個垂直佈局來包含圖片和文字
        no_content_layout = QVBoxLayout(self.no_content_label)
        no_content_layout.setSpacing(0)
        no_content_layout.setContentsMargins(0, 0, 0, 0)

        # 圖片標籤
        image_label = QLabel(self.no_content_label)
        notFileImg = resource_path('resources/sysImg/Group.png')
        pixmap = QPixmap(notFileImg)

        image_label.setFixedSize(400, 200)
        image_label.setPixmap(pixmap.scaled(image_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 文字標籤
        combined_text = (
            '<span style="font-size: 16px; font-weight: bold; color: #157EFA;">'
            '尚無資料，請將欲上傳案件照片放入資料夾<br>'
            '<span"></span><br>'
            '<span style="color: red; margin-top:5px;">*請注意，案件照片須要兩張才能被讀取</span>'
            '</span>'
        )

        text_label = QLabel(combined_text, self.no_content_label)
        text_label.setFixedSize(400, 60)
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setStyleSheet("font-size: 16px; font-weight: bold; color:#157EFA")
        

        # 添加圖片和文字到佈局
        no_content_layout.addWidget(image_label)
        no_content_layout.addWidget(text_label)

        self.no_content_label.setLayout(no_content_layout)
        self.no_content_label.hide()  # 初始隱藏
        # ----------------------------------------------------------------

        # 在主目錄下找到rulingImg路徑
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        caseImg = os.path.join(current_path, "rulingImg")
        print('圖片儲存路徑:', caseImg)

        # 獲取檔案列
        self.case_files = get_sorted_filenames(caseImg)
        print(self.case_files)
        # print('圖片檔案列:', caseImg)

        self.items_per_page = 10
        self.current_page = 1
        self.total_pages = (len(self.case_files) - 1) // self.items_per_page + 1

        # 初始勾選前10個案件編號

        for case_file in self.case_files[:10]:
            self.selected_cases[case_file] = True
            
        # 初始化頁數標籤，頁數控制按鈕
        self.page_label = QLabel(f'頁數：{self.current_page}/{self.total_pages}', self)
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_label.setStyleSheet("font-size:16px;")

        self.prev_button = QPushButton('<', self)
        self.prev_button.setStyleSheet("""
            QPushButton {
                background-color:white ;
                color: black;
                font-size: 12px;
                border: 1px solid #6C6C6C;
                border-radius: 5px;
                padding: 1px 5px;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
            QPushButton:pressed {
                background-color: #D2E9FF;
            }
        """)
        self.next_button = QPushButton('>', self)
        self.next_button.setStyleSheet("""
            QPushButton {
                background-color:white ;
                color: black;
                font-size: 12px;
                border: 1px solid #6C6C6C;
                border-radius: 5px;
                padding: 1px 5px;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
            QPushButton:pressed {
                background-color: #D2E9FF;
            }
        """)
        self.prev_button.clicked.connect(self.prev_page)
        self.next_button.clicked.connect(self.next_page)

        # 頁數顯示和控制
        page_control_layout = QHBoxLayout()
        page_control_layout.addStretch(1)
        page_control_layout.addStretch()
        page_control_layout.addWidget(self.page_label)
        page_control_layout.addWidget(self.prev_button)
        page_control_layout.addWidget(self.next_button)
        # page_control_layout.addStretch()
        select_all_checkbox_layout.addLayout(page_control_layout)  # 加入全選勾選匡

        # 用 QVBoxLayout 包裝標題和已選擇數量標籤，並設置水平居中
        header_layout = QVBoxLayout()
        header_layout.addWidget(self.title)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addLayout(select_all_checkbox_layout)
        header_layout.addWidget(self.selected_count_label)

        layout.addLayout(header_layout)

        # 用 QScrollArea 包裝勾選框列表，讓它們可以滾動
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: none;
                width: 0px;
            }
            QScrollBar:horizontal {
                border: none;
                background: none;
                height: 0px;
            }
        """)
        self.scroll_area.setFixedWidth(250)
        self.scroll_area.setFixedHeight(380)
        self.scroll_widget = QWidget()
        self.scroll_layout = QFormLayout(self.scroll_widget)
        self.scroll_widget.setLayout(self.scroll_layout)

        self.checkboxes = []

        # 添加勾選框到滾動區域
        self.update_checkbox_list()

        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_widget)

        # 用 QHBoxLayout 包裝 QScrollArea，並設置水平居中
        scroll_area_layout = QHBoxLayout()
        scroll_area_layout.addStretch()
        scroll_area_layout.addWidget(self.scroll_area)
        scroll_area_layout.addWidget(self.no_content_label)
        scroll_area_layout.addStretch()

        layout.addLayout(scroll_area_layout)

        # 說明文字
        self.description = QLabel('選擇案件編號後，會於指定資料夾中檢索對應照片兩張。', self)
        self.description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.description.setStyleSheet("font-size: 18px;")

        # 用 QHBoxLayout 包裝說明文字，並設置水平居中
        description_layout = QHBoxLayout()
        description_layout.addStretch()
        description_layout.addWidget(self.description)
        description_layout.addStretch()

        layout.addLayout(description_layout)

        folderImg = resource_path('resources/sysImg/folder.png')
        self.open_folder_button = QPushButton('開啟資料夾', self)
        self.open_folder_button.setIcon(QIcon(folderImg))  # 設置圖示
        self.open_folder_button.setStyleSheet("""
            QPushButton {
                background-color:white ;
                color: #157EFA;
                font-size: 18px;
                border: 1px solid #6C6C6C;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
            QPushButton:pressed {
                background-color: #D2E9FF;
            }
        """)
        # 連接按鈕的點擊事件到相應的方法
        self.open_folder_button.clicked.connect(self.open_folder)


        # 按鈕
        self.search_button = QPushButton('開始檢索', self)
        self.search_button.setStyleSheet("""
            QPushButton {
                background-color: #157EFA ;
                color: white;
                font-size: 18px;
                border: 1px solid #6C6C6C;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
            QPushButton:pressed {
                background-color: #D2E9FF;
            }
        """)

        # 用 QHBoxLayout 包裝按鈕，並設置水平居中
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)  # 添加左側彈性空間
        button_layout.addWidget(self.open_folder_button)
        button_layout.addWidget(self.search_button)
        button_layout.addStretch()
        button_layout.addStretch()
        button_layout.addStretch(1)  # 添加右側彈性空間

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # 連接按鈕的點擊事件到相應的方法
        self.search_button.clicked.connect(self.show_login_dialog)

        self.checked_count = 0
        
        # 檢查 case_files 長度並設置 scroll_area 的可見性
        self.update_visibility()

        # 初始化並啟動目錄監視器
        self.directory_watcher = DirectoryWatcher(caseImg)
        self.directory_watcher.file_changed.connect(self.reload_case_files)
        self.directory_watcher.start()

    def update_visibility(self):
        if len(self.case_files) == 0:
            self.title.show()
            self.scroll_area.hide()
            self.no_content_label.show()
            self.search_button.hide()
            self.page_label.hide()
            self.prev_button.hide()
            self.next_button.hide()
            self.selected_count_label.hide()
            self.title.hide()
            self.description.hide()
            self.select_all_checkbox.hide()
        else:
            self.title.hide()
            self.scroll_area.show()
            self.no_content_label.hide()
            self.search_button.show()
            self.page_label.show()
            self.prev_button.show()
            self.next_button.show()
            self.selected_count_label.show()
            self.description.show()
            self.select_all_checkbox.show()

    def clear_inputs(self):
        for checkbox in self.checkboxes:
            checkbox.setChecked(False)
        self.selected_cases.clear()
        self.update_checked_count()

    def update_checked_count(self):
        for checkbox in self.checkboxes:
            self.selected_cases[checkbox.text()] = checkbox.isChecked()

        self.checked_count = sum(self.selected_cases.values())
        self.all_checked_count = all(self.selected_cases.values())

        self.selected_count_label.setText(f'已選擇案件數量：{self.checked_count}/10')

        if self.all_checked_count:
            self.select_all_checkbox.setChecked(True)
        else:
            # 斷開信號連接
            self.select_all_checkbox.blockSignals(True)
            # 改變狀態
            self.select_all_checkbox.setChecked(False)
            # 重新連接信號
            self.select_all_checkbox.blockSignals(False)

        if self.checked_count > 10:
            QMessageBox.warning(self, '警告', '最多只能選擇10個案件編號')
            sender = self.sender()
            if isinstance(sender, QCheckBox):
                sender.setChecked(False)
                self.selected_cases[sender.text()] = False
                self.checked_count -= 1
                self.selected_count_label.setText(f'已選擇案件數量：{self.checked_count}/10')

    def show_login_dialog(self):
        login_dialog = LoginDialog()
        if login_dialog.exec() == QDialog.DialogCode.Accepted:
            username, password = login_dialog.get_credentials()
            self.start_search(username, password)
        else:
            pass
    
    def open_folder(self):
        # 獲取當前腳本的路徑並構建目標資料夾的路徑
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        folder_path = os.path.join(current_path, "rulingImg")
        
        # 確認資料夾是否存在
        if os.path.isdir(folder_path):
            try:
                if platform.system() == "Windows":
                    os.startfile(folder_path)
                elif platform.system() == "Darwin":  # macOS
                    subprocess.Popen(["open", folder_path])
                else:  # Linux
                    subprocess.Popen(["xdg-open", folder_path])
            except Exception as e:
                QMessageBox.critical(self, "錯誤", f"無法打開資料夾: {e}")
        else:
            QMessageBox.warning(self, "警告", "目標資料夾不存在")

    def start_search(self, username, password):
        inputs = [case for case, checked in self.selected_cases.items() if checked]

        if not inputs:
            QMessageBox.warning(self, '警告', '必須選擇至少一個案件編號')
            return

        save_credentials(username, password)
        self.progress_dialog = QProgressDialog("正在檢索資料，請稍候...", None, 0, 0, self)
        self.progress_dialog.setWindowTitle('請稍候')
        self.progress_dialog.setModal(True)
        self.progress_dialog.show()

        self.thread = SpiderThread(inputs, username, password)
        self.thread.result_ready.connect(self.handle_result)
        self.thread.start()

    def handle_result(self, result):
        self.progress_dialog.hide()

        if not result['status']:
            self.show_login_failed_message(result['message'])
        else:
            self.parent_window.complete_search(result)

    def show_login_failed_message(self, message="帳號或密碼錯誤，請重試。"):
        QMessageBox.warning(self, '登入失敗', message)

    def update_checkbox_list(self):
        for i in reversed(range(self.scroll_layout.count())):
            self.scroll_layout.removeRow(i)

        start_index = (self.current_page - 1) * self.items_per_page
        end_index = start_index + self.items_per_page
        current_files = self.case_files[start_index:end_index]

        self.checkboxes = []
        for i, case_file in enumerate(current_files):
            checkbox = QCheckBox(case_file, self)
    
            checkbox.setStyleSheet("""
                QCheckBox {
                width: 150px;
                font-size: 20px;
                color: #157EFA;
                border-radius: 3px;
                background-color: white;
                padding: 2px 5px;
                }
                QCheckBox:hover {
                    background-color: lightgray;
                }
            """)
            checkbox.stateChanged.connect(self.update_checked_count)
            self.checkboxes.append(checkbox)

            if case_file in self.selected_cases:
                checkbox.setChecked(self.selected_cases[case_file])

            checkbox_layout = QHBoxLayout()
            checkbox_layout.addStretch()
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.addStretch()

            self.scroll_layout.addRow(checkbox_layout)

        self.page_label.setText(f'頁數：{self.current_page}/{self.total_pages}')
        self.update_checked_count()

    def toggle_select_all(self, state):
  
        if state == 2:
            for checkbox in self.checkboxes[:10]:
                checkbox.setChecked(True)
        else:
            self.clear_inputs()

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.update_checkbox_list()

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.update_checkbox_list()

    def reload_case_files(self):
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        directory = os.path.join(current_path, "rulingImg")
        self.case_files = get_sorted_filenames(directory)
        self.total_pages = (len(self.case_files) - 1) // self.items_per_page + 1
        self.current_page = 1

        self.selected_cases = {case_file: True for case_file in self.case_files[:10]}
        self.update_visibility()
        self.update_checkbox_list()
        self.update_checked_count()

    def closeEvent(self, event):
        self.directory_watcher.stop()
        event.accept()
