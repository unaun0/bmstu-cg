from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QColor, QPixmap, QImage
from PyQt5.QtWidgets import QWidget, QMessageBox, QColorDialog, QDialog
from PyQt5.QtCore import Qt

from main_window import Ui_MainWindow
from task_popup import Ui_TaskPopup
from errors import ErrorInput

import numpy as np
from functions import *
from floating_horizont import *
import pyqtgraph as pg  # для цветов на рисунке
global w

from copy import deepcopy

WCANVAS = 2000
HCANVAS = 2000

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self): 
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.stack_init()
        self.canvas_init()
        self.bindActions()
        self.bindButtons()
        self.morf_param_init()

    def bindActions(self):
        self.actionExit.triggered.connect(self.closeEvent) # close app
        self.actionAbout.triggered.connect(self.show_info) #  info about app

    def bindButtons(self):
        self.pushButton_build.clicked.connect(self.build_figure) # build
        self.pushButton_scale.clicked.connect(self.scale_figure) # scale
        self.pushButton_rotate.clicked.connect(self.rotate_figure) # rotate
        self.pushButton_bgcolor.clicked.connect(self.set_bg_color) # bg color
        self.pushButton_fcolor.clicked.connect(self.set_edge_color) # edge color
        self.pushButton_back.clicked.connect(self.undo) # back
        self.pushButton_clear.clicked.connect(self.canvas_clear) # clear

    def add_function(self):
        pass

    def stack_init(self):
        self.state_stack = []
        self.stack_size = 20
    
    def canvas_clear(self):
        self.stack_update()
        self.color_init()
        self.color_start_set()
        self.morf_param_init()
        self.scene_clear()

    def scene_clear(self):
        self.image.fill(QColor(self.bg_color[0], self.bg_color[1], self.bg_color[2], self.bg_color[3]))
        self.pix.convertFromImage(self.image)
        self.scene.clear()
        self.scene.addPixmap(self.pix)

    def stack_update(self):
        self.state_stack.append([self.x_min, self.x_max, self.x_step,
                                 self.z_min, self.z_max, self.z_step,
                                 self.xangle, self.yangle, self.zangle, self.coef,
                                 self.function, self.edge_color, self.bg_color
                                ])
        if len(self.state_stack) > self.stack_size:
            self.state_stack.pop(0)
    
    def undo(self):
        index = (len(self.state_stack) - 1)
        if index <= 0:
            return ErrorInput("Невозможно отменить действие.")
        print("undo")
        self.x_min, self.x_max, self.x_step = self.state_stack[index][0], self.state_stack[index][1], self.state_stack[index][2]
        self.z_min, self.z_max, self.z_step = self.state_stack[index][3], self.state_stack[index][4], self.state_stack[index][5]

        self.xangle, self.yangle, self.zangle = self.state_stack[index][6], self.state_stack[index][7], self.state_stack[index][8]
        self.coef = self.state_stack[index][9]

        self.function = self.state_stack[index][10]

        self.edge_color = self.state_stack[index][11]
        self.bg_color = self.state_stack[index][12]

        self.color = QColor(self.edge_color[0], self.edge_color[1], self.edge_color[2], self.edge_color[3])
        self.color = self.color.rgb()

        if self.function != None:
            self.draw_figure()
        else:
            self.scene_clear()


        self.state_stack.pop(index)

    def morf_param_init(self): 
        self.x_min, self.x_max, self.x_step = None, None, None
        self.z_min, self.z_max, self.z_step = None, None, None

        self.color = None
        self.function = None

        self.width_draw = 1
        self.xangle = 0
        self.yangle = 0
        self.zangle = 0
        self.coef = 1

    def canvas_init(self):
        self.scene = QtWidgets.QGraphicsScene(0, 0, WCANVAS, HCANVAS)
        self.scene.win = self
        self.graph.setScene(self.scene)
        self.image = QImage(WCANVAS, HCANVAS, QImage.Format_RGB32)
        self.image.fill(Qt.white)
        self.pix = QPixmap()
        self.pix.convertFromImage(self.image)
        self.scene.addPixmap(self.pix)

    def scale_figure(self):
        if self.function == None:
            return ErrorInput("Необходимо построить поверхность.")
        k_coef = self.doubleSpinBox_scale.value()
        if k_coef == 0:
            return ErrorInput("Значение коэф-та K должно быть больше нуля.")
        self.coef *= k_coef
        self.on_bt_draw_clicked()
    
    def rotate_figure(self):
        if self.function == None:
            return ErrorInput("Необходимо построить поверхность.")
        index = self.comboBox_axis.currentIndex()
        value = self.doubleSpinBox_rotate.value()
        if index == 0:
            self.xangle += value
        elif index == 1:
            self.yangle += value
        elif index == 2:
            self.zangle += value
        else:
            return
        self.on_bt_draw_clicked()

    def limits_take(self):
        self.x_min, self.x_max, self.x_step = self.doubleSpinBox_xmin.value(), self.doubleSpinBox_xmax.value(), self.doubleSpinBox_xstep.value()
        self.z_min, self.z_max, self.z_step = self.doubleSpinBox_ymin.value(), self.doubleSpinBox_ymax.value(), self.doubleSpinBox_ystep.value()
        rc = True
        if self.x_max <= self.x_min:
            ErrorInput("Максимальное значение X должно быть больше минимального.")
        elif (self.x_max - self.x_min) < self.x_step:
            ErrorInput("Максимальный шаг при Xmin = {:} и Xmax = {:} : {:} ".format(str(self.x_min), 
                                                                                    str(self.x_max), 
                                                                                    str(abs(self.x_max - self.x_min))))
        elif self.z_max <= self.z_min:
            return ErrorInput("Максимальное значение Z должно быть больше минимального.")
        elif (self.z_max - self.z_min) < self.z_step:
            ErrorInput("Максимальный шаг при Zmin = {:} и Zmax = {:} : {:} ".format(str(self.z_min), 
                                                                                         str(self.z_max), 
                                                                                         str(abs(self.z_max - self.z_min))))
        elif (self.x_step and self.z_step) == 0:
            ErrorInput("Шаг должен быть больше нуля.")
        else:
            self.color = QColor(self.edge_color[0], self.edge_color[1], self.edge_color[2], self.edge_color[3])
            self.color = self.color.rgb()
            self.function = funcs_list[self.comboBox.currentIndex()]
            return True
        self.x_min, self.x_max, self.x_step = None, None, None
        self.z_min, self.z_max, self.z_step = None, None, None
        return False
    
    def build_figure(self):
        self.morf_param_init()
        if not self.limits_take():
            return
        self.on_bt_draw_clicked()

    def on_bt_draw_clicked(self):
        self.stack_update()
        self.draw_figure()
    
    def draw_figure(self):
        self.image.fill(QColor(self.bg_color[0], self.bg_color[1], self.bg_color[2], self.bg_color[3]))
        self.image = float_horizon(self.scene.width(), self.scene.height(),
                                   self.x_min, self.x_max, self.x_step,
                                   self.z_min, self.z_max, self.z_step,
                                   self.xangle, self.yangle, self.zangle, self.coef,
                                   self.function, self.image, self.color)
        self.pix.convertFromImage(self.image)
        self.scene.clear()
        self.scene.addPixmap(self.pix)
        self.scene.update()

    def show_info(self):
        self.sub_window = Info()
        self.sub_window.show()

    def color_init(self):
        self.bg_color = (255, 255, 255, 255)
        self.edge_color = (0, 0, 0, 255)

    def color_start_set(self):
        self.pushButton_fcolor.setStyleSheet("background-color: rgba{:};".format("(0, 0, 0, 225)"))
        self.pushButton_bgcolor.setStyleSheet("background-color: rgba{:};".format("(255, 255, 255, 225)"))
    
    def set_color(self):
        color = None
        color_dialog = QColorDialog()
        if color_dialog.exec_() == QDialog.Accepted:
            color = color_dialog.selectedColor()
        return color
          
    def set_bg_color(self):
        color = self.set_color()
        if color == None:
            return
        self.bg_color = tuple(QColor.getRgb(color))
        self.pushButton_bgcolor.setStyleSheet("background-color: rgba{:};".format(str(self.bg_color)))
        #self.pushButton_bgcolor.setBackgroundBrush(brush)

    def set_edge_color(self, color):
        color = self.set_color()
        if color == None:
            return
        self.edge_color = tuple(QColor.getRgb(color))
        self.pushButton_fcolor.setStyleSheet("background-color: rgba{:};".format(str(self.edge_color)))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close_app()
        elif event.key() == Qt.Key_Q:
            self.canvas_clear()
        elif event.key() == Qt.Key_B:
            self.undo()

    def showEvent(self, event):
        self.color_start_set()
        self.color_init()
        self.morf_param_init()
        self.stack_update()
        
    def close_app(self):
        buttonReply = QMessageBox.question(self, 'Завершение работы', 
                                           "Вы хотите завершить программу?", 
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            QtWidgets.QApplication.quit()

    def closeEvent(self, event):
        self.close_app()

class Info(QWidget, Ui_TaskPopup):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.okBtn.clicked.connect(self.close)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            self.close()
