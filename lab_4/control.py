from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QColor, QPen
from PyQt5.QtWidgets import QWidget, QMainWindow, QMessageBox, QColorDialog, QDialog
from PyQt5.QtWidgets import QGraphicsEllipseItem
from PyQt5.QtCore import Qt, QRect, pyqtSignal

from main_window import Ui_MainWindow
from task_popup import Ui_TaskPopup

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        # color
        self.bg_color = (1, 1, 1)
        self.line_color = (0, 0, 0)

        # stack
        self.state_stack = []
        self.state_stack_max_size = 10

        self.init_scene()
        self.set_options()
        self.bindButtons()

    def bindButtons(self):
        self.comboBox_figure.currentIndexChanged.connect(self.set_options)
        self.actionExit.triggered.connect(self.closeEvent) # close app
        self.actionAuthors.triggered.connect(self.show_info) #  info about app 
        self.pushButton_color.clicked.connect(self.set_color)  # set new color
        self.pushButton_draw_figure.clicked.connect(self.build_figure) # back
        #self.pushButton_clear.clicked.connect(self.some_func) # cleans

    def init_scene(self):
        self.scene = QtWidgets.QGraphicsScene(self)
        self.graphicsView.setScene(self.scene)
        self.graphicsView.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        center = self.graphicsView.mapToScene(self.graphicsView.viewport().rect().center())
        scene_rect = self.scene.itemsBoundingRect()
        scene_rect.moveCenter(center)
        self.graphicsView.fitInView(self.scene.sceneRect(), QtCore.Qt.KeepAspectRatio)


        self.bg_color = Qt.white
        self.pen_color = Qt.black

        self.x_offset = 0
        self.y_offset = 0

    def update_scene(self):
        self.graphicsView.show()

    def keyPressEvent(self, event):
        step_y = 10
        step_x = 10
        if event.key() == Qt.Key_Up or event.key() == Qt.Key_W:
            self.y_offset += step_y
        elif event.key() == Qt.Key_Down or event.key() == Qt.Key_S:
            self.y_offset -= step_y
        elif event.key() == Qt.Key_Left or event.key() == Qt.Key_A:
            self.x_offset += step_x
        elif event.key() == Qt.Key_Right or event.key() == Qt.Key_D:
            self.x_offset -= step_x
        elif event.key() == Qt.Key_Plus or event.key() == Qt.Key_Equal:
            current_scale = self.graphicsView.transform().m11()
            new_scale = current_scale * 1.1
            view_center = self.graphicsView.viewport().rect().center()
            scene_center = self.graphicsView.mapToScene(view_center)
            print(view_center, scene_center)
            self.graphicsView.scale(new_scale, new_scale)
            scene_center = self.graphicsView.mapToScene(view_center)
            self.graphicsView.centerOn(scene_center)
        elif event.key() == Qt.Key_Minus:
            current_scale = self.graphicsView.transform().m11()
            new_scale = current_scale * 0.9
            view_center = self.graphicsView.viewport().rect().center()
            scene_center = self.graphicsView.mapToScene(view_center)
            print(view_center, scene_center)
            self.graphicsView.scale(new_scale, new_scale)
            scene_center = self.graphicsView.mapToScene(view_center)
            self.graphicsView.centerOn(scene_center)
        else:
            return
        self.scene.setSceneRect(self.x_offset, self.y_offset, self.width, self.height)
        #self.graphicsView.fitInView(self.scene.sceneRect(), QtCore.Qt.KeepAspectRatio)

    def set_options(self):
        action = self.comboBox_figure.currentIndex()
        if not action:
            self.doubleSpinBox_ry.setEnabled(False)
        else:
            self.doubleSpinBox_ry.setEnabled(True)
    
    def build_figure(self):
        center = (-(float(self.doubleSpinBox_xc.value())), -(float(self.doubleSpinBox_yc.value())))
        radius_x = float(self.doubleSpinBox_rx.value())
        radius_y = float(self.doubleSpinBox_ry.value())
        if radius_x == 0:
            print("error")
            return
        action = self.comboBox_figure.currentIndex()
        if action == 0:
            radius_y = radius_x
        elif radius_y == 0:
            print("Error")
            return
        radius = (radius_x, radius_y)
        self.draw_figure(center, radius)
    
    def draw_figure(self, center, radius):
        action = self.comboBox_alg.currentIndex()
        color = QColor(self.pen_color)
        if action == 0:
            self.draw_ellipse(center, radius, color)
        self.update_scene()

    def draw_ellipse(self, center, radius, color):
        ellipse = QGraphicsEllipseItem(center[0] - radius[0], center[1] - radius[1], radius[0] * 2, radius[1] * 2)
        ellipse.setPen(QtGui.QPen(QPen(color)))
        self.scene.addItem(ellipse)

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
        self.bg_color = color
        brush = QtGui.QBrush(QtGui.QColor(color))
        self.graphicsView.setBackgroundBrush(brush)

    def set_pen_color(self, color):
        self.pen_color = color
        color = tuple(QColor.getRgb(color))
        self.label_color.setStyleSheet("background-color: rgba{:};".format(str(color)))
    
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
    