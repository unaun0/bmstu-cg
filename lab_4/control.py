from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QMainWindow, QMessageBox, QColorDialog, QDialog
from PyQt5.QtCore import Qt, QRect, pyqtSignal

from main_window import Ui_MainWindow
from task_popup import Ui_TaskPopup

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    resized = QtCore.pyqtSignal() 
    def __init__(self):
        super(MainWindow, self).__init__()
        #self.resized.connect(self.some_func) 
        self.setupUi(self)

        # color
        self.bg_color = (1, 1, 1)
        self.line_color = (0, 0, 0)

        # stack
        self.state_stack = []
        self.state_stack_max_size = 10

        '''
        self.height = self.gr.frameGeometry().height()
        self.width = self.gr.frameGeometry().width()
        '''
        self.init_scene()
        self.bindButtons()

    def bindButtons(self):
        self.actionAuthors.triggered.connect(self.show_info) #  info about app 
        self.actionExit.triggered.connect(self.closeEvent) # close app
        self.pushButton_color.clicked.connect(self.set_color)  # set new color
        #self.pushButton_back.clicked.connect(self.some_func) # back
        #self.pushButton_clear.clicked.connect(self.some_func) # cleans

    def init_scene(self):
        self.scene = QtWidgets.QGraphicsScene(self)
        self.graphicsView.setScene(self.scene)
        self.bg_color = (255, 225, 255, 255)
        self.pen_color = (0, 0, 0, 255)

    def show_info(self):
        self.sub_window = Info()
        self.sub_window.show()

    def set_color(self):
        color = QColorDialog.getColor()
        action = self.comboBox_color.currentIndex()
        if action:
            self.set_pen_color(color)
        else:
            self.set_bg_color(color)
 
    def set_bg_color(self, color):
        self.bg_color = tuple(QColor.getRgb(color))
        brush = QtGui.QBrush(QtGui.QColor(color))
        self.graphicsView.setBackgroundBrush(brush)

    def set_pen_color(self, color):
        self.pen_color = tuple(QColor.getRgb(color))
        self.label_color.setStyleSheet("background-color: rgba{:};".format(str(self.pen_color)))

    def resizeEvent(self, event):
        self.resized.emit()
        return super(MainWindow, self).resizeEvent(event)
    
    def closeEvent(self, event):
        buttonReply = QMessageBox.question(self, 'Завершение работы', 
                                           "Вы хотите завершить программу?", 
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            QtWidgets.QApplication.quit()

class Info(QWidget, Ui_TaskPopup):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.okBtn.clicked.connect(self.close)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            self.close()
    