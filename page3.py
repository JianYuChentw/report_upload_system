from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea, QFrame, QHBoxLayout, QGroupBox
from PyQt6.QtCore import Qt

class Page3(QWidget):
    def __init__(self):
        super().__init__()

        # 主佈局
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # 標題
        self.title_label = QLabel("處理結果")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 50px;")
        self.layout.addWidget(self.title_label)

        # 標題下的標籤
        header_layout = QHBoxLayout()
        headers = ["案件編號", "判定", "操作", "說明"]
        for header in headers:
            label = QLabel(header)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 5px;")
            header_layout.addWidget(label)

        self.layout.addLayout(header_layout)

        # 滾動區域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")

        # 結果框架
        self.result_frame = QFrame()
        self.result_layout = QVBoxLayout(self.result_frame)
        self.result_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.result_layout.setSpacing(2)  # 設置垂直間距
        self.scroll_area.setWidget(self.result_frame)

        self.layout.addWidget(self.scroll_area)

        # 返回按鈕
        self.back_button = QPushButton("完成")
        self.back_button.setStyleSheet("""
            QPushButton {
                font-size: 20px; 
                padding: 15px;
                background-color: #007BFF; 
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #003f7f;
            }
        """)
        self.back_button.clicked.connect(self.go_back)
        self.layout.addWidget(self.back_button)
        self.layout.setAlignment(self.back_button, Qt.AlignmentFlag.AlignCenter)

    def display_results(self, report_data):
        # 清空現有的結果
        while self.result_layout.count():
            item = self.result_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        # print(report_data)
        # 顯示結果數據
        for case_number, data in report_data.items():
            report = data['report']
            report_status = "舉發" if report else "不舉發"
            operation = data.get('operation', '未知')
            description = data.get('description', '無描述')

            # 創建案件區域
            
            case_group = QGroupBox()
            case_group.setMaximumHeight(200)  # 將最大高度設定
            case_group.setMinimumHeight(80)  # 將最小高度設定 
            case_layout = QHBoxLayout()
            
            case_group.setLayout(case_layout)

            if operation == '成功':
                case_group.setStyleSheet("""
                    QGroupBox {
                        font-size: 20px;
                        background-color: white;
                        border-radius: 5px;
                        margin-bottom: 5px;
                    }
                """)
            else:
                case_group.setStyleSheet("""
                    QGroupBox {
                        font-size: 20px;
                        background-color: #FF9797;
                        border-radius: 5px;
                        margin-bottom: 5px;
                    }
                """)


            # 案件編號
            case_number_label = QLabel(f"{case_number}")
            case_number_label.setStyleSheet("font-size: 18px; color: black;")
            case_number_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            case_number_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            case_layout.addWidget(case_number_label)

            # 判定
            status_label = QLabel(f"{report_status}")
            status_label.setStyleSheet("font-size: 18px; color: black;")
            status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            case_layout.addWidget(status_label)

            # 操作
            operation_label = QLabel(f"{operation}")
            operation_label.setStyleSheet("font-size: 18px; color: black;")
            operation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            case_layout.addWidget(operation_label)

            # 說明
            description_label = QLabel(f"{description}")
            description_label.setStyleSheet("font-size: 18px; color: black; ")
            description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            description_label.setWordWrap(True)
            description_label.setFixedWidth(370)  # 設置固定寬度
            case_layout.addWidget(description_label)

            # 添加案件區域到結果佈局
            self.result_layout.addWidget(case_group)

    def go_back(self):
        main_window = self.window()  # 獲取 MainWindow 的實例
        main_window.page1.clear_inputs()  # 清空 Page1 的輸入框
        main_window.page1.reload_case_files()  # 重新讀取資料夾中的檔案
        main_window.switch_page(0)  # 切換回 Page1
