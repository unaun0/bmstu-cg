from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QColor, QPen, QPixmap, QPainter
from PyQt5.QtWidgets import QWidget, QMainWindow, QMessageBox, QColorDialog, QDialog
from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsPixmapItem, QGraphicsScene
from PyQt5.QtCore import Qt, QRect, pyqtSignal

from main_window import Ui_MainWindow
from task_popup import Ui_TaskPopup

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self): 
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.init_canvas()
        self.bindActions()
        self.bindButtons()
        self.set_options()
        self.init_stack()
        self.scrollbar_refresh()

    def bindActions(self):
        self.comboBox_figure.currentIndexChanged.connect(self.set_options) # change settings 
        self.actionExit.triggered.connect(self.closeEvent) # close app
        self.actionAuthors.triggered.connect(self.show_info) #  info about app 

    def bindButtons(self):
        self.pushButton_color.clicked.connect(self.set_color)  # set new color
        self.pushButton_draw_figure.clicked.connect(self.build_figure) # back
        #self.pushButton_clear.clicked.connect(self.some_func) # cleans

    def init_stack(self):
        self.state_stack = []
        self.state_stack_max_size = 10

    def init_canvas(self):
        self.canvas_init = True
        self.scene = QtWidgets.QGraphicsScene(self)
        self.graphicsView.setScene(self.scene)
        self.graphicsView.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.canvas_size = (5000, 5000)
        self.view_size = (self.graphicsView.width(), self.graphicsView.height())
        self.canvas_center = (self.canvas_size[0] / 2, self.canvas_size[1] / 2)

        self.pixmap = QPixmap(5000, 5000)
        self.pixmap.fill(Qt.transparent)

        self.scene.addPixmap(self.pixmap)

        self.bg_color = Qt.white
        self.pen_color = Qt.black
    
    def scrollbar_refresh(self):
        self.graphicsView.horizontalScrollBar().setValue(self.canvas_center[0] - (self.view_size[0] / 2))
        self.graphicsView.verticalScrollBar().setValue(self.canvas_center[1] - (self.view_size[1] / 2)) 

    def update_scene(self):
        self.scene.addPixmap(self.pixmap)
        self.graphicsView.show()

    def set_options(self):
        action = self.comboBox_figure.currentIndex()
        if not action:
            self.doubleSpinBox_ry.setEnabled(False)
        else:
            self.doubleSpinBox_ry.setEnabled(True)

    def build_figure(self):
        center = ((float(self.doubleSpinBox_xc.value())), -(float(self.doubleSpinBox_yc.value())))
        radius_x = float(self.doubleSpinBox_rx.value())
        radius_y = float(self.doubleSpinBox_ry.value())
        if radius_x == 0:
            print("Error")
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
        center = list(center)
        center[0] += self.canvas_center[0]
        center[1] += self.canvas_center[1]
        print(center)
        if action == 0:
            self.draw_ellipse(center, radius, color)
        self.update_scene()

    def draw_ellipse(self, center, radius, color):
        painter = QPainter(self.pixmap)
        painter.setPen(QColor(color))
        painter.drawEllipse(center[0] - radius[0], center[1] - radius[1], radius[0] * 2, radius[1] * 2)
        painter.end()

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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Plus or event.key() == Qt.Key_Equal:
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

    def mousePressEvent(self, event):
        if self.canvas_init:
            self.canvas_init = False
            self.scrollbar_refresh()
            return
        if event.button() == Qt.LeftButton:
            pos_window = event.pos()
            x_value, y_value = pos_window.x(), pos_window.y()
            if x_value < 413 or y_value < 13:
                return
            pos_scene = self.graphicsView.mapToScene(pos_window)
            point = [pos_scene.x() - (413 + self.canvas_center[0]), 
                     -(pos_scene.y() - (13 + self.canvas_center[1]))]

            self.doubleSpinBox_xc.setValue(float(point[0]))
            self.doubleSpinBox_yc.setValue(float(point[1]))

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