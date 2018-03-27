import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel
from PyQt5.QtCore import QSize


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setMinimumSize(QSize(400, 200))
        self.setWindowTitle('ARSO Lidar Downloader')

        btn_workspace = QPushButton('Set workspace!', self)
        btn_workspace.resize(100, 20)
        btn_workspace.move(50, 50)

        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec_())


