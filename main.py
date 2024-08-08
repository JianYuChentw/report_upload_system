import sys
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QStackedWidget, QVBoxLayout, QWidget, QMessageBox
from page1 import Page1
from page2 import Page2
from page3 import Page3
from utils import ensure_ruling_img_folder

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        ensure_ruling_img_folder()

        # 設定視窗標題和大小
        self.setWindowTitle('智能上傳系統')
        screen = QApplication.primaryScreen()
        screen_size = screen.size()
        screen_width = screen_size.width()
        screen_height = screen_size.height()
        # print('寬度',screen_width)
        
        # 設定視窗大小為螢幕寬度的 80% 和高度的 50%
        window_width = int(screen_width * 0.7)
        window_height = int(screen_height * 0.7)
        
        # 設定視窗位置為螢幕中心
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 3
      
        self.setGeometry(x_position, y_position, window_width, window_height)

        # 建立 QStackedWidget
        self.stacked_widget = QStackedWidget()

        # 建立不同的頁面
        self.page1 = Page1(self)
        self.page2 = Page2()
        self.page3 = Page3()

        # 將頁面加入 QStackedWidget
        self.stacked_widget.addWidget(self.page1)
        self.stacked_widget.addWidget(self.page2)
        self.stacked_widget.addWidget(self.page3)

        # 主佈局
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stacked_widget)

        self.setLayout(main_layout)

        # 連接按鈕點擊事件
        self.page2.return_page_button.clicked.connect(lambda: self.switch_page(0))
        self.page2.switch_to_page3.connect(self.show_page3)

    def complete_search(self, result):
        if result['status'] == False:
            QMessageBox.warning(self, '登入失敗', result['message'])
        else:
            self.page2.update_content(result)
            self.switch_page(1)

    def switch_page(self, n):
        self.stacked_widget.setCurrentIndex(n)

    def show_page3(self, result_data):
        print(result_data)
        self.page3.display_results(result_data)  # 假設 Page3 有 display_results 方法
        self.switch_page(2)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # app.setStyleSheet("""
    # QWidget {
    #     background-color: #E6EEF6;
    #     color: black;
    # }
    # """)
    # 設定視窗 logo
    app.setWindowIcon(QIcon('sysImg\logo.png'))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
