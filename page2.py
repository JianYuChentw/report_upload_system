import glob
import re
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QRadioButton, QButtonGroup, QGroupBox, QScrollArea, 
    QSizePolicy, QPushButton, QMessageBox, QLineEdit, QDialog, QFormLayout, QProgressDialog,QCheckBox, QGraphicsView,
    QGraphicsScene, QGraphicsPixmapItem, QComboBox, QTextEdit, QSpacerItem
)
from PyQt6.QtGui import QPixmap, QWheelEvent, QPainter, QTextOption, QFont, QIcon
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QThread, QEvent

from simulation_spider import batch_processing_spider
from utils import  save_informants, load_informants, process_json_data, add_law_number, delete_law_number, filter_successful_cases, move_matching_files, resource_path



class WorkerThread(QThread):
    finished = pyqtSignal(bool)
    result_signal = pyqtSignal(list)

    def __init__(self, executor, account, password, report_data):
        super().__init__()
        self.executor = executor
        self.account = account
        self.password = password
        self.report_data = report_data

    def run(self):
        try:
            loginData={
                'InformantName':self.executor,
                'MemberID': self.account,
                'MemberPW': self.password
            }
            
            results = batch_processing_spider(loginData, self.report_data)
        
                   
            case_numbers = filter_successful_cases(results)
            current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            rulingImgPath = os.path.join(current_path, 'rulingImg')
        
            directory = os.path.join(rulingImgPath, 'close_case')


            move_matching_files(case_numbers, directory)
            self.finished.emit(True)
            self.result_signal.emit(results)
        except Exception as e:
            self.finished.emit(False)
            self.result_signal.emit([{"caseNumber": "Error", "report": False, "operation": "error", "說明": str(e)}])


class ZoomableGraphicsView(QGraphicsView):
    def __init__(self, pixmap):
        super().__init__()
        self.setScene(QGraphicsScene(self))
        self.pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene().addItem(self.pixmap_item)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.scale_factor = 1.0

        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.fitInView(self.pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            old_pos = self.mapToScene(event.position().toPoint())
            if event.angleDelta().y() > 0:
                factor = 1.25
            else:
                factor = 0.8

            self.scale(factor, factor)
            self.scale_factor *= factor
            new_pos = self.mapToScene(event.position().toPoint())
            delta = new_pos - old_pos
            self.translate(delta.x(), delta.y())

    def reset_zoom(self):
        self.resetTransform()
        self.scale_factor = 1.0


class WheelEventFilter(QObject):
   def eventFilter(self, obj, event):
       if event.type() == QEvent.Type.Wheel:
           return True  # 阻止滾輪事件
       return super().eventFilter(obj, event)



class Page2(QWidget):
    switch_to_page3 = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.revise_adjustLaw_button = QPushButton('條文編號編輯', self)

            # 設置按鈕樣式 #0618
        self.revise_adjustLaw_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                padding: 5px 10px;
                background-color: #157EFA;
                color: black;
                border: 1px solid black;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
            QPushButton:pressed {
                background-color: #D2E9FF;
            }
        """)
        
        # 添加處理案件數量的標籤 #0618
        self.count_label = QLabel("處理案件數量: 0", self)
        self.count_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.count_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 5px 0 0 0;")

        # 設置按鈕對齊方式
        button_layout = QHBoxLayout()
        button_layout.addStretch(0)

        button_layout.addWidget(self.count_label)
        button_layout.addWidget(self.revise_adjustLaw_button)
        button_layout.addStretch(0)

        # 創建一個新的頂部佈局來包含按鈕佈局
        top_layout = QVBoxLayout()
        top_layout.addLayout(button_layout)


        self.page2_layout = QVBoxLayout()
        self.page2_scroll_area = QScrollArea()
        self.page2_scroll_area.setWidgetResizable(True)
        self.page2_widget = QWidget()
        self.page2_widget.setLayout(self.page2_layout)
        self.page2_scroll_area.setWidget(self.page2_widget)
        self.loginData ={}

        # 創建主佈局
        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)  # 將頂部佈局添加到主佈局中
        main_layout.addWidget(self.page2_scroll_area)
        self.setLayout(main_layout)

        self.car_number_inputs = {}  # 初始化字典用來保存所有 QLineEdit 


        # 初始化返回按鈕和送出按鈕
        self.return_page_button = QPushButton('回到前頁', self)
        self.return_page_button.setStyleSheet(
            """QPushButton {
            font-size: 20px; 
            padding: 10px 20px; 
            border: 1px solid black; 
            border-radius: 5px
            }
            QPushButton:hover {
                background-color: #E0E0E0 ;
            }
            QPushButton:pressed {
                background-color: #D2E9FF; /* 按下時的顏色 */
            }
            """)
        self.submit_button = QPushButton('送出', self)
        self.submit_button.setStyleSheet(
            """QPushButton {
                font-size: 20px;
                padding: 10px 20px; 
                border: 1px solid black; 
                border-radius: 5px
            }
            QPushButton:hover {
                background-color: #E0E0E0 ;
            }
            QPushButton:pressed {
                background-color: #D2E9FF; /* 按下時的顏色 */
            }
            """)
        self.submit_button.clicked.connect(self.show_input_dialog)

        self.add_bottom_buttons()

        # 綁定條文編號編輯按鈕的點擊事件
        self.revise_adjustLaw_button.clicked.connect(self.show_law_edit_dialog)

    def update_content(self, input_contents):
        self.loginData = input_contents['loginData']
        while self.page2_layout.count() > 0:
            item = self.page2_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.case_entries = []
        self.car_number_inputs = {}

        self.count_label.setText(f"處理案件數量: {len(input_contents['data'])}")


        if input_contents['data']:
            for content in input_contents['data']:
                group_box = QGroupBox()
                group_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                group_box.setStyleSheet("font-size: 16px;")
                
                # 使用 QVBoxLayout 來放置頂部區域和主要內容
                vbox = QVBoxLayout()
                vbox.setSpacing(1)
                vbox.setContentsMargins(10, 10, 10, 10)
                group_box.setLayout(vbox)

                # 頂部區域用來放置 case_label
                case_label = QLabel(f"案件編號: {content['caseNumber']}", self)
                case_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                case_label.setStyleSheet("font-size: 18px; color: black; font-weight:bold; background-color: gray; border-radius: 3px; padding: 2px 5px;")
                vbox.addWidget(case_label)

                # 在 case_label 和 hbox 之間添加間隔
                vbox.addSpacing(1)  # 這裡可以調整間隔大小
                

                hbox = QHBoxLayout()
                hbox.setSpacing(10)
                hbox.setContentsMargins(0, 0, 0, 0)
                vbox.addLayout(hbox)  # 將 hbox 添加到 vbox

                left_side_widget = QWidget()
                left_side_layout = QVBoxLayout(left_side_widget)
                left_side_widget.setFixedWidth(200)
                left_side_widget.setFixedHeight(275)
                left_side_layout.setSpacing(3)
                left_side_layout.setContentsMargins(0, 0, 0, 0)

                car_number_layout = QHBoxLayout()

                if content['carNumber'] == '無對應車牌':
                    # 創建 QLabel
                    car_number_label = QLabel("車牌編號:", self)
                    car_number_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                    car_number_label.setStyleSheet("font-size: 16px;")

                    # 創建 QLineEdit，並將預設值設為 content['carNumber']
                    car_number_input = QLineEdit(self)
                    car_number_input.setFixedHeight(20)  # 設置固定高度
                    car_number_input.setText(content['carNumber'])
                    car_number_input.setFont(QFont("Arial", 12))
                    car_number_input.setReadOnly(True)  # 設置為只讀
                    car_number_input.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 設置文字垂直置中
                    car_number_input.setStyleSheet("""
                        QLineEdit {
                            height: 20px;
                            qproperty-alignment: AlignCenter;
                        }
                    """)

                    car_number_layout.addWidget(car_number_label)
                    car_number_layout.addWidget(car_number_input)
                else:
                    # 創建 QLabel
                    car_number_label = QLabel("車牌編號:", self)
                    car_number_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                    car_number_label.setStyleSheet("font-size: 16px;")

                    # 創建 QLineEdit，並將預設值設為 content['carNumber']
                    car_number_input = QLineEdit(self)
                    car_number_input.setText(content['carNumber'])
                    car_number_input.setFont(QFont("Arial", 16))

                    # 保存 car_number_input，使用 caseNumber 作為鍵
                    self.car_number_inputs[content['caseNumber']] = (car_number_input, content['carNumber'])

                    # 創建重置按鈕並添加到佈局中
                    reset_button = QPushButton(self)
                    resetImg = resource_path('resources/sysImg/reset.png')
                    reset_button.setIcon(QIcon(resetImg))  # 設置按鈕圖標
                    reset_button.setFixedWidth(40)
                    # 使用 lambda 將 caseNumber 傳遞給 reset_car_number 函數
                    reset_button.clicked.connect(lambda checked, case_number=content['caseNumber']: self.reset_car_number(case_number))

                    # 將 QLabel 和 QLineEdit 添加到佈局中
                    car_number_layout.addWidget(car_number_label)
                    car_number_layout.addWidget(car_number_input)
                    car_number_layout.addWidget(reset_button)


                car_type_and_inspection_layout = QVBoxLayout()
                car_type_and_inspection_layout.setSpacing(3)

                car_type_label = QLabel("車型:")
                car_type_label.setStyleSheet("font-size: 14px; margin-left:0; margin-top: 0px; margin-bottom: 0px;")
                car_type_label.setMinimumWidth(20)
                car_type_label.setMaximumWidth(50)

                car_type_space1 = QLabel("")
                car_type_space1.setMinimumWidth(20)
                car_type_space1.setMaximumWidth(50)

                car_type_spinbox = QComboBox(self)
                car_type_spinbox.addItems(["1", "2", "3", "4", "5", "6", "7"])
                car_type_spinbox.setMaximumWidth(60)
                car_type_spinbox.setEnabled(False)

                car_type_space2 = QLabel("")
                car_type_space2.setMinimumWidth(20)
                car_type_space2.setMaximumWidth(50)


                car_type_layout = QVBoxLayout()
                car_type_layout.setSpacing(1)
                

                label_and_spinbox_layout = QHBoxLayout()

                label_and_spinbox_layout.addWidget(car_type_label)
                label_and_spinbox_layout.addWidget(car_type_spinbox)
                label_and_spinbox_layout.addWidget(car_type_space2)
                label_and_spinbox_layout.addWidget(car_type_space2)
                

                # car_type_layout.addWidget(car_number_label)
                car_type_layout.addLayout(car_number_layout)
                car_type_layout.addLayout(label_and_spinbox_layout)
                
                left_side_layout.addLayout(car_type_layout)

                remark_label = QLabel("1汽車/2拖車/3重機/4輕機\n5動力機械/6臨時車牌/7試車牌", self)
                remark_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                remark_label.setStyleSheet("font-size: 14px; color: gray; margin-top: 0px; margin-bottom: 2px;")
                remark_label.setMinimumWidth(200)
                # car_type_and_inspection_layout.addWidget(remark_label)
                car_type_layout.addWidget(remark_label)


                now_adjustLaw_label = QLabel(f"法條一編號: {content['adjustLaw']}", self)
                now_adjustLaw_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                now_adjustLaw_label.setStyleSheet("font-size: 14px;")
                # left_side_layout.addWidget(now_adjustLaw_label)
                car_type_layout.addWidget(now_adjustLaw_label)

                now_adjustLaw_content_label = QLabel(f" {content.get('adjustLawcontent', '無法條內容')}", self)
                now_adjustLaw_content_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                now_adjustLaw_content_label.setStyleSheet("font-size: 14px; color:red; font-weight:bold;")
                now_adjustLaw_content_label.setWordWrap(True)
                # left_side_layout.addWidget(now_adjustLaw_content_label)
                car_type_layout.addWidget(now_adjustLaw_content_label)



                inspection_layout = QHBoxLayout()
                
                inspection_group = QButtonGroup(self)
                inspection_radio1 = QRadioButton("檢舉")
                inspection_radio1.setStyleSheet("font-size: 16px;")
                inspection_radio2 = QRadioButton("不檢舉")
                inspection_radio2.setStyleSheet("font-size: 16px;")

                if content['carNumber'] == '無對應車牌':
                    inspection_radio1.setEnabled(False)
                    inspection_radio2.setEnabled(False)

                inspection_group.addButton(inspection_radio1)
                inspection_group.addButton(inspection_radio2)
                inspection_layout.addWidget(inspection_radio1)
                inspection_layout.addWidget(inspection_radio2)
                inspection_layout.addWidget(car_type_space1)


                inspection_radio1.toggled.connect(lambda checked, combobox=car_type_spinbox: combobox.setEnabled(checked))

                law_checkbox = QCheckBox("修正法條一編號:")
                law_combobox1 = QComboBox()
                law_combobox1.setEditable(False)
                law_combobox1.addItems(process_json_data("resources/articleNumber.json"))
                law_combobox1.setFixedWidth(150)
                law_combobox1.setMaxVisibleItems(5)

                law_combobox1.setEnabled(False)
                law_checkbox.setEnabled(False)

                def toggle_law_controls(enabled, law_checkbox=law_checkbox, law_combobox1=law_combobox1):
                    law_checkbox.setEnabled(enabled)
                    law_combobox1.setEnabled(enabled and law_checkbox.isChecked())

                def law_checkbox_toggled(checked, law_combobox1):
                    if checked:
                        law_combobox1.clear()
                        law_combobox1.addItems(process_json_data("resources/articleNumber.json"))
                    law_combobox1.setEnabled(checked)

                inspection_radio1.toggled.connect(lambda checked, spinbox=car_type_spinbox, checkbox=law_checkbox, combobox=law_combobox1: toggle_law_controls(checked, checkbox, combobox))
                law_checkbox.toggled.connect(lambda checked, combobox=law_combobox1: law_checkbox_toggled(checked, combobox))

                current_law_label = QLabel("選擇條文編號：")
                current_law_label.setStyleSheet("font-size: 14px;")
                law_layout = QVBoxLayout()
                law_layout.addWidget(current_law_label)
                law_layout.addWidget(law_combobox1)

                car_type_and_inspection_layout.addWidget(law_checkbox)
                car_type_and_inspection_layout.addLayout(law_layout)
                car_type_and_inspection_layout.addLayout(inspection_layout)

                left_side_layout.addLayout(car_type_and_inspection_layout)

                
                hbox.addWidget(left_side_widget)

                no_image_widget = QWidget()
                no_image_widget.setFixedHeight(280)
                no_image_layout = QVBoxLayout(no_image_widget)
                
                no_image_layout.setSpacing(1)
                no_image_layout.setContentsMargins(5, 5, 5, 5)

                # 創建下拉選單
                dropdown = QComboBox()
                dropdown.addItems(["重複檢舉", "超過舉發時效", "相片無法辨識", "違規事實變造", "非本轄案件", "已另案舉發", "已建檔", "其他"])
                no_image_layout.addWidget(dropdown)

                # 創建支持自動換行的輸入框
                input_field = QTextEdit()
                input_field.setPlaceholderText("輸入內容")
                input_field.setFixedHeight(265)  # 設置固定高度
                input_field.setFixedWidth(650)  # 設置固定寬度
                input_field.setWordWrapMode(QTextOption.WrapMode.WordWrap)  # 設置自動換行   
                no_image_layout.addWidget(input_field)

                no_image_layout.addStretch()

                no_image_widget.setVisible(False)  # 默認隱藏
                hbox.addWidget(no_image_widget)



                image_layout = QHBoxLayout()

                current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                directory = os.path.join(current_path, "rulingImg")
                pattern = re.compile(f"^{re.escape(content['caseNumber'])}.*\.jpe?g$")
                search_pattern_jpg = os.path.join(directory, "*.jpg")
                search_pattern_jpeg = os.path.join(directory, "*.jpeg")

                all_image_paths = glob.glob(search_pattern_jpg) + glob.glob(search_pattern_jpeg)
                image_paths = [path for path in all_image_paths if pattern.match(os.path.basename(path))]
                image_paths = [path.replace("\\", "/") for path in image_paths]

                if image_paths:
                    image_label1 = ZoomableGraphicsView(QPixmap(image_paths[0]))
                    image_label1.setFixedHeight(260)
                else:
                    image_label1 = QLabel("無對應圖片", self)
                    image_label1.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    image_label1.setStyleSheet('border: 1px solid black; text-align: center;')
                    image_label1.setFixedHeight(260)

                image_label1.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                image_layout.addStretch()
                image_layout.addWidget(image_label1)
                image_layout.addStretch()

                if len(image_paths) > 1:
                    image_label2 = ZoomableGraphicsView(QPixmap(image_paths[1]))
                    image_label2.setFixedHeight(260)
                else:
                    image_label2 = QLabel("無對應圖片", self)
                    image_label2.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    image_label2.setStyleSheet('border: 1px solid black; text-align: center;')
                    image_label2.setFixedHeight(260)

                image_label2.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                image_layout.addStretch()
                image_layout.addWidget(image_label2)
                image_layout.addStretch()

                image_widget = QWidget()
                image_widget.setLayout(image_layout)
                hbox.addWidget(image_widget)
                hbox.addStretch()

                
                
                # 切換顯示內容的函數
                def toggle_content(radio2, image_widget, no_image_widget):
                    if radio2.isChecked():
                        image_widget.setVisible(False)
                        no_image_widget.setVisible(True)
                    else:
                        image_widget.setVisible(True)
                        no_image_widget.setVisible(False)

                # 在迴圈中設定連接
                inspection_radio2.toggled.connect(lambda checked, 
                    radio2=inspection_radio2, image_widget=image_widget, 
                    no_image_widget=no_image_widget: toggle_content(radio2, 
                    image_widget, no_image_widget))

               
                self.page2_layout.addWidget(group_box)
                
                # 送出該案選擇內容
                self.case_entries.append((content, car_number_input,inspection_radio1, inspection_radio2, car_type_spinbox, law_checkbox, law_combobox1, dropdown, input_field))

        self.add_bottom_buttons()

    def add_bottom_buttons(self):
        # 創建一個水平佈局來放置返回按鈕和提交按鈕
        bottom_layout = QHBoxLayout()


        # 設置按鈕的固定寬度
        self.submit_button.setFixedWidth(150)
        self.return_page_button.setFixedWidth(150)


        # 添加彈性空間和按鈕
        bottom_layout.addStretch()  # 添加彈性空間，使按鈕靠右
        bottom_layout.addWidget(self.return_page_button)
        bottom_layout.addSpacing(20)  # 添加固定間距
        bottom_layout.addWidget(self.submit_button)
        bottom_layout.addStretch()  # 添加彈性空間，使按鈕靠左


        # 將這個水平佈局添加到頁面2的佈局中
        self.page2_layout.addLayout(bottom_layout)

    # 智慧系統資訊輸入
    def show_input_dialog(self):
        
        if self.check_all_reports_selected():
            dialog = QDialog(self)
            dialog.setWindowTitle("智慧系統檢舉人資訊")

            form_layout = QFormLayout(dialog)

            # 舉發人下拉選單
            executor_input = QComboBox(dialog)
            executor_input.setEditable(True)  # 允許輸入新的名稱
            informants = load_informants()
            executor_input.addItems(informants)

            form_layout.addRow("舉發人:", executor_input)

            # 按鈕布局
            buttons_layout = QHBoxLayout()
            submit_button = QPushButton("確定", dialog)
            delete_button = QPushButton("刪除選定舉發人", dialog)
            cancel_button = QPushButton("取消", dialog)

            buttons_layout.addWidget(submit_button)
            buttons_layout.addWidget(delete_button)
            buttons_layout.addWidget(cancel_button)

            form_layout.addRow(buttons_layout)

            # 登入系統位置
            account_input = self.loginData['account']
            password_input = self.loginData['password']

            submit_button.clicked.connect(lambda: self.handle_dialog_submission(dialog, executor_input, account_input, password_input))
            delete_button.clicked.connect(lambda: self.delete_informant(executor_input))
            
            cancel_button.clicked.connect(dialog.reject)
            dialog.setLayout(form_layout)
            dialog.exec()
        else:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle('輸入錯誤')
            msg_box.setText('檢舉選項為必選，且不檢舉說明為必填！')
            msg_box.setStyleSheet("QMessageBox { font-size: 16px; }")
            
            # 計算主窗口的中心位置
            main_window_rect = self.geometry()
            main_window_center_x = main_window_rect.center().x()
            main_window_center_y = main_window_rect.center().y()

            # 設置警告對話框的位置，使其顯示在主窗口的中心
            msg_box.move(main_window_center_x - msg_box.width() // 2, main_window_center_y - msg_box.height() // 2)
            
            msg_box.show()
            msg_box.exec()

    # 車牌號碼初始化
    def reset_car_number(self, case_number):
            # 根據 caseNumber 在 input_contents 中查找對應的 carNumber，並重設 QLineEdit 的值
            if case_number in self.car_number_inputs:
                car_number_input, initial_value = self.car_number_inputs[case_number]
                car_number_input.setText(initial_value)

    # 刪除舉發人
    def delete_informant(self, executor_input):
        current_text = executor_input.currentText()  # 獲取當前選中的文本
        informants = load_informants()  # 從文件加載舉發人列表
        if current_text in informants:  # 檢查當前文本是否在列表中
            informants.remove(current_text)  # 如果是，則從列表中移除
            save_informants(informants)  # 保存更新後的列表到文件
            executor_input.removeItem(executor_input.currentIndex())  # 從下拉列表中移除選項

    # 檢查必選
    def check_all_reports_selected(self):
        for content, car_number_input, radio1, radio2, combobox, law_checkbox, law_combobox1, dropdown, input_field in self.case_entries:
            print('檢查',radio2.isChecked(), len(input_field.toPlainText()))
            if content['carNumber'] == '無對應車牌':
                continue
            if not radio1.isChecked() and not radio2.isChecked():
                return False
            if  radio2.isChecked() and len(input_field.toPlainText()) == 0:
                return False
        return True
    
    # 檢查智慧系統輸入格必填
    def handle_dialog_submission(self, dialog, executor_input, account_input, password_input):
        informant = executor_input.currentText()
        account = account_input
        password = password_input

        if informant:
            informants = load_informants()
            if informant not in informants:
                informants.append(informant)
                save_informants(informants)


            report_data = self.collect_report_data()
            # print('handle_dialog_submission', report_data)
            self.run_background_process(informant, account, password, report_data)
            dialog.accept()
        else:
            QMessageBox.warning(self, '輸入錯誤', '請輸入所有欄位')
    
    # 條文編號異動
    def show_law_edit_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("條文編號編輯")

        form_layout = QFormLayout(dialog)

        # 條文編號下拉選項框
        law_input = QComboBox(dialog)
        law_input.setEditable(True)  # 允許輸入新的條文編號
        law_input.setMaxVisibleItems(5)  # 設置最大可見條目數為5
        laws = process_json_data('resources/articleNumber.json')
        law_input.addItems(laws)
        form_layout.addRow("條文編號:", law_input)

        # 按鈕布局
        buttons_layout = QHBoxLayout()
        add_button = QPushButton("新增", dialog)
        delete_button = QPushButton("刪除", dialog)
        cancel_button = QPushButton("取消", dialog)

        buttons_layout.addWidget(add_button)
        buttons_layout.addWidget(delete_button)
        buttons_layout.addWidget(cancel_button)

        form_layout.addRow(buttons_layout)

        add_button.clicked.connect(lambda: self.handle_law_addition(dialog, law_input))
        delete_button.clicked.connect(lambda: self.handle_law_deletion(dialog, law_input))
        cancel_button.clicked.connect(dialog.reject)

        dialog.setLayout(form_layout)
        dialog.exec()
    # 新增法條
    def handle_law_addition(self, dialog, law_input):
        new_law_number = law_input.currentText()
        add_law_number(new_law_number)
        if new_law_number not in [law_input.itemText(i) for i in range(law_input.count())]:
            law_input.addItem(new_law_number)
        dialog.accept()

    # 刪除法條 
    def handle_law_deletion(self, dialog, law_input):
        law_number_to_delete = law_input.currentText()
        delete_law_number(law_number_to_delete)
        index_to_delete = law_input.currentIndex()
        if index_to_delete != -1:
            law_input.removeItem(index_to_delete)
        dialog.accept()

      
    # 蒐集表單資料
    def collect_report_data(self):
        report_data = []
        for content, car_number_input, radio1, radio2, combobox, law_checkbox, law_combobox1, dropdown, input_field in self.case_entries:
        # for content, radio1, radio2, spinbox in self.case_entries:
            print(car_number_input.text())
            # 檢查車牌號是否為'無對應車牌'，如果是，則略過該案件
            if content['carNumber'] == '無對應車牌':
                continue
            
            # 如果車牌號有效，檢查是否選擇了檢舉
            if radio1.isChecked():
                entry = {
                    "caseNumber": content['caseNumber'],
                    "carNumber":car_number_input.text(),
                    "report": True,  # 已選擇檢舉
                    "carType": combobox.currentText(), # 收集車型資訊
                    "adjustLaw": law_checkbox.isChecked(),  # 是否調整法條
                    "lawOption1": law_combobox1.currentText() if law_checkbox.isChecked() else None,  # 第一段下拉選項
                }
            else:
                entry = {
                    "caseNumber": content['caseNumber'],
                    "carNumber":car_number_input.text(),
                    "report": False,  # 選擇不檢舉
                    "carType": None,  # 不收集車型資訊
                    "adjustLaw": False,  # 不調整法條
                    "lawOption1": dropdown.currentText() ,  # 無下拉選項
                    "reason": input_field.toPlainText(),  # 事由
                }
            
            report_data.append(entry)
        print(report_data)
        return report_data

    # 發送帳號及表單資料運行爬蟲
    def run_background_process(self, executor, account, password, report_data):
        # print('發送帳號及表單資料運行爬蟲',executor, account, password,report_data)
        if len(report_data) < 1:
            QMessageBox.warning(self, '輸入錯誤', '尚無可執行案件!')
            return
        # print('發送帳號及表單資料運行爬蟲',executor, account, password, report_data)
        self.progress_dialog = QProgressDialog("處理中，請稍候...", None, 0, 0, self)
        self.progress_dialog.setWindowTitle('運行中')
        self.progress_dialog.setModal(True)
        self.progress_dialog.show()

        self.worker = WorkerThread(executor, account, password, report_data)
        self.worker.finished.connect(self.on_task_finished)
        self.worker.result_signal.connect(self.process_results)
        self.worker.start()
    
    # 回傳結果格式調整
    def process_results(self, result):
        # print('回傳結果格式調整',result)


        # 新增判斷
        if result[0]['caseNumber'] == 400:
            QMessageBox.warning(self, '登入失敗', result[0]['description'])
            return

        if isinstance(result, list):
            try:
                result_dict = {item['caseNumber']: {'report': item['report'], 'operation': item['operation'], 'description': item['description']} for item in result}
            except (TypeError, KeyError) as e:
                print(f"Error converting list to dict: {e}")
                result_dict = {}
        else:
            result_dict = result

        self.switch_to_page3.emit(result_dict)
    

    # 進度隱藏顯示
    def on_task_finished(self, success):
        self.progress_dialog.hide()
        if not success:
            QMessageBox.warning(self, '錯誤', '處理過程中發生錯誤')

