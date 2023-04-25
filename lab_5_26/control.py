from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QColor, QPen, QPixmap, QPainter
from PyQt5.QtWidgets import QWidget, QMainWindow, QMessageBox, QColorDialog, QPushButton, QDialog
from PyQt5.QtCore import Qt

from main_window import Ui_MainWindow
from task_popup import Ui_TaskPopup
from errors import ErrorInput

import matplotlib.pyplot as plt
import time

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self): 
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.set_value()
        self.init_stack()
        self.init_canvas()
        self.bindActions()
        self.bindButtons()
        self.set_options()

    def bindActions(self):
        self.tabWidget_time.currentChanged.connect(self.set_tab)
        self.radioButton_time.toggled.connect(self.set_options)
        self.actionExit.triggered.connect(self.closeEvent) # close app
        self.actionAuthors.triggered.connect(self.show_info) #  info about app 

    def bindButtons(self):
        self.pushButton_color.clicked.connect(self.set_color)  # set new color
        self.pushButton_clear.clicked.connect(self.clear_canvas) # clean
        self.pushButton_back.clicked.connect(self.undo) # back
        self.pushButton_fadd_point.clicked.connect(self.add_point) # add point

    def set_value(self):
        pass

    def init_stack(self):
        self.state_stack = []
        self.stack_size = 10

    def init_canvas(self):
        self.scene = QtWidgets.QGraphicsScene(self)
        self.graphicsView.setScene(self.scene)
        self.graphicsView.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.canvas_size = (5002, 5002)
        self.view_size = (self.graphicsView.width(), self.graphicsView.height())
        self.canvas_center = (self.canvas_size[0] / 2, self.canvas_size[1] / 2)

        self.pixmap = QPixmap(5002, 5002)
        self.pixmap.fill(Qt.transparent)

        self.scene.addPixmap(self.pixmap)

        self.bg_color = QColor(255, 255, 255)
        self.pen_color = QColor(0, 0, 0)
        self.scale = 1

        self.graphicsView.mousePressEvent = self.pointSelectEvent
        self.graphicsView.mouseMoveEvent = self.canvasMoveEvent
        self.graphicsView.wheelEvent = self.zoomWheelEvent
        self.update_stack()
    
    def init_color_settings(self):
        self.bg_color = QColor(255, 255, 255)
        self.border_color = QColor(0, 0, 0)
        self.edge_color = QColor(255, 0, 0)
        self.fill_color = QColor(0, 0, 0)
    
    def scrollbar_refresh(self):
        self.graphicsView.horizontalScrollBar().setValue(int(self.canvas_center[0] - (self.view_size[0] // 2)))
        self.graphicsView.verticalScrollBar().setValue(int(self.canvas_center[1] - (self.view_size[1] // 2)))

    def push_point_in_table(self, point):
        last_index_row = self.tableWidget_points.rowCount()
        self.tableWidget_points.insertRow(last_index_row)
        self.tableWidget_points.setItem(last_index_row, 0, QtWidgets.QTableWidgetItem("{:10.6f}".format(point[0])))
        self.tableWidget_points.setItem(last_index_row, 1, QtWidgets.QTableWidgetItem("{:10.6f}".format(point[1])))

    def add_point(self):
        point = (float(self.spinBox_fx.value()), float(self.spinBox_fy.value()))
        self.push_point_in_table(point)

    def draw_line(self, point_a, point_b):
        pass
    
    def update_scene(self):
        self.scene.addPixmap(self.pixmap)
        self.graphicsView.show()
    
    def update_stack(self):
        pixmap_copy = self.pixmap.copy()
        self.state_stack.append([pixmap_copy.copy(), self.bg_color, self.pen_color])
        if len(self.state_stack) > self.stack_size:
            self.state_stack[0] = None
            self.state_stack.pop(0)

    def undo(self):
        index = (len(self.state_stack) - 1)
        if index < 0:
            ErrorInput("Невозможно отменить действие.")
        else:
            self.pixmap = None

            self.pixmap = self.state_stack[index][0]
            self.set_bg_color(self.state_stack[index][1])
            self.set_pen_color(self.state_stack[index][2])

            self.state_stack.pop(index)
            self.scene.clear()
            self.scene.addPixmap(self.pixmap)

    def clear_canvas(self):
        self.canvas_size = (5002, 5002)
        self.view_size = (self.graphicsView.width(), self.graphicsView.height())
        self.canvas_center = (self.canvas_size[0] / 2, self.canvas_size[1] / 2)

        self.scene.clear()
        self.update_stack()

        self.pixmap = QPixmap(5002, 5002)
        self.pixmap.fill(Qt.transparent)

        self.scene.addPixmap(self.pixmap)
        self.graphicsView.resetTransform()

        self.scale = 1

        self.set_start_color()

        self.set_bg_color(self.bg_color)
        self.set_pen_color(self.pen_color)

        self.set_value()
        self.scrollbar_refresh()

    def set_start_color(self):
        self.init_color_settings()

        self.set_bg_color(self.bg_color)
        self.set_border_color(self.pen_color)
        self.set_edge_color(self.pen_color)
        self.set_fill_color(self.pen_color)

    def show_info(self):
        self.sub_window = Info()
        self.sub_window.show()
    
    def set_options(self):
        self.tab_index = None
        if self.radioButton_time.isChecked():
            self.tabWidget_time.setEnabled(True)
            self.set_tab()
        else:
            self.tabWidget_time.setEnabled(False)

    def set_tab(self):
        self.tab_index = self.tabWidget_time.currentIndex()

    def set_color(self):
        color_dialog = QColorDialog()
        if color_dialog.exec_() == QDialog.Accepted:
            color = color_dialog.selectedColor()
            action = self.comboBox_color.currentIndex()
            self.update_stack()
            if action == 0:
                self.set_bg_color(color)
            elif action == 1:
                self.set_border_color(color)
            elif action == 2:
                self.set_fill_color(color)
            elif action == 3:
                self.set_edge_color(color)
 
    def set_bg_color(self, color):
        self.bg_color = color
        brush = QtGui.QBrush(QtGui.QColor(color))
        self.graphicsView.setBackgroundBrush(brush)

    def set_border_color(self, color):
        self.pen_color = color
        color = tuple(QColor.getRgb(color))
        self.label_bcolor.setStyleSheet("background-color: rgba{:};".format(str(color)))
    
    def set_fill_color(self, color):
        self.pen_color = color
        color = tuple(QColor.getRgb(color))
        self.label_fcolor.setStyleSheet("background-color: rgba{:};".format(str(color)))
    
    def set_edge_color(self, color):
        self.pen_color = color
        color = tuple(QColor.getRgb(color))
        self.label_ecolor.setStyleSheet("background-color: rgba{:};".format(str(color)))

    def scale_plus(self):
        sub_scale = self.scale * 1.1
        if sub_scale >= 200:
            ErrorInput("Достигнут максимальный масштаб.")
        else:
            self.scale = sub_scale
            self.graphicsView.scale(1.1, 1.1)

    def scale_minus(self):
        sub_scale = self.scale * 0.9
        if sub_scale <= 0.3:
            ErrorInput("Достигнут минимальный масштаб.")
        else:
            self.scale = sub_scale
            self.graphicsView.scale(0.9, 0.9)
    
    def close(self):
        buttonReply = QMessageBox.question(self, 'Завершение работы', 
                                           "Вы хотите завершить программу?", 
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            QtWidgets.QApplication.quit()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_0:
            self.graphicsView.resetTransform()
        elif event.key() == Qt.Key_Plus or event.key() == Qt.Key_Equal:
            self.scale_plus()
        elif event.key() == Qt.Key_Minus:
            self.scale_minus()
        elif event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_Q:
            self.clear_canvas()
        elif event.key() == Qt.Key_B:
            self.undo()
        elif event.key() == Qt.Key_C:
            self.set_color()
        elif event.key() == Qt.Key_V:
            currentIndex = self.comboBox_color.currentIndex()
            count = self.comboBox_color.count()
            nextIndex = (currentIndex + 1) % count
            self.comboBox_color.setCurrentIndex(nextIndex)
    
    def showEvent(self, event):
        self.set_options()
        self.scrollbar_refresh()

    def zoomWheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.scale_plus()
        else:
            self.scale_minus()

    def pointSelectEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos_scene = self.graphicsView.mapToScene(event.pos())
            point = [pos_scene.x() - (self.canvas_center[0]), 
                     -(pos_scene.y() - (self.canvas_center[1]))]
            self.push_point_in_table(point)
        elif event.button() == Qt.RightButton or event.button() == Qt.MiddleButton:
            self._last_mouse_pos = self.graphicsView.mapToScene(event.pos())
            
    def canvasMoveEvent(self, event):
        if event.buttons() == Qt.RightButton or event.buttons() == Qt.MiddleButton:
            pos_scene = self.graphicsView.mapToScene(event.pos())

            x_diff = int((pos_scene.x() - self._last_mouse_pos.x()) * self.scale)
            y_diff = int((pos_scene.y() - self._last_mouse_pos.y()) * self.scale)

            x_val = self.graphicsView.horizontalScrollBar().value()
            y_val = self.graphicsView.verticalScrollBar().value()
            
            self.graphicsView.horizontalScrollBar().setValue(x_val - x_diff)
            self.graphicsView.verticalScrollBar().setValue(y_val - y_diff)

            self._last_mouse_pos =  self.graphicsView.mapToScene(event.pos())
        super().mouseMoveEvent(event)

    def closeEvent(self, event):
        self.close()

class Info(QWidget, Ui_TaskPopup):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.okBtn.clicked.connect(self.close)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            self.close()
