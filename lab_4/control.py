from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QColor, QPen, QPixmap, QPainter
from PyQt5.QtWidgets import QWidget, QMainWindow, QMessageBox, QColorDialog, QDialog
from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsPixmapItem, QGraphicsScene
from PyQt5.QtCore import Qt, QRect, pyqtSignal

from main_window import Ui_MainWindow
from task_popup import Ui_TaskPopup
from errors import ErrorInput

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self): 
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.init_stack()
        self.init_canvas()
        self.bindActions()
        self.bindButtons()
        self.set_options()
        self.scrollbar_refresh()

    def bindActions(self):
        self.comboBox_figure.currentIndexChanged.connect(self.set_options) # change settings 
        self.actionExit.triggered.connect(self.closeEvent) # close app
        self.actionAuthors.triggered.connect(self.show_info) #  info about app 

    def bindButtons(self):
        self.pushButton_color.clicked.connect(self.set_color)  # set new color
        self.pushButton_draw_figure.clicked.connect(self.build_figure) # draw circle
        self.pushButton_draw_range.clicked.connect(self.build_range) # draw range
        self.pushButton_clear.clicked.connect(self.clear_canvas) # clean
        self.pushButton_back.clicked.connect(self.undo) # back

    def init_stack(self):
        self.state_stack = []
        self.stack_size = 10

    def init_canvas(self):
        self.canvas_init = True
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

        self.update_stack()
    
    def scrollbar_refresh(self):
        self.graphicsView.horizontalScrollBar().setValue(self.canvas_center[0] - (self.view_size[0] / 2))
        self.graphicsView.verticalScrollBar().setValue(self.canvas_center[1] - (self.view_size[1] / 2)) 

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

        self.bg_color = QColor(255, 255, 255)
        self.pen_color = QColor(0, 0, 0)

        self.set_bg_color(self.bg_color)
        self.set_pen_color(self.pen_color)

        self.scrollbar_refresh()

    def build_figure(self):
        center = ((float(self.doubleSpinBox_xc.value())), -(float(self.doubleSpinBox_yc.value())))
        radius_x = float(self.doubleSpinBox_rx.value())
        radius_y = float(self.doubleSpinBox_ry.value())
        if radius_x == 0:
            ErrorInput("Невозможно построить фигуру. Радиус Rx должен быть больше нуля.")
            return
        action = self.comboBox_figure.currentIndex()
        if action == 0:
            radius_y = radius_x
        elif radius_y == 0:
            ErrorInput("Невозможно построить фигуру. Радиус Ry должен быть больше нуля.")
            return
        radius = (radius_x, radius_y)
        if self.check_size_figure(center, radius):
            ErrorInput("Невозможно построить фигуру. Превышен максимальный размер холста.")
        else:
            self.update_stack()
            color = QColor(self.pen_color)
            self.draw_figure(center, radius, color)
            self.update_scene()

    def check_size_figure(self, center, radius):
        if abs(center[0] + radius[0]) > 2500 or abs(center[0] - radius[0]) > 2500:
            return True
        if abs(center[1] + radius[1]) > 2500 or abs(center[1] - radius[1]) > 2500:
            return True
        return False
    
    def check_size_range(self, center, radius, count, param, param_value):
        if self.check_size_figure(center, radius):
            return True
        elif param == 0 and self.check_size_figure(center, param_value):
            return True
        else:
            radius_end = (param_value[0] * count, param_value[1] * count)
            if self.check_size_figure(center, radius_end):
                return True
        return False

    def build_range(self):
        center = ((float(self.doubleSpinBox_xc.value())), -(float(self.doubleSpinBox_yc.value())))
        radius_x = float(self.doubleSpinBox_xstart_3.value())
        radius_y = float(self.doubleSpinBox_ystart_3.value())
        if radius_x <= 0 or radius_y <= 0:
            ErrorInput("Невозможно построить спектр. Радиус Rx / Ry должен быть больше нуля.")
            return
        radius_start = (radius_x, radius_y)

        count = (int(self.spinBox_count.value()))
        if count <= 0:
            ErrorInput("Невозможно построить спектр. Количество фигур должно быть больше нуля.")
            return
        
        action = self.comboBox_param.currentIndex()
        param = ((float(self.doubleSpinBox_deltax.value())), 
                 (float(self.doubleSpinBox_deltay.value())))
        if param[0] <= 0 or param[1] <= 0:
            ErrorInput("Невозможно построить спектр. Конечный радиус / шаг должен быть больше нуля.")
            return
        if action == 0:
            if param[0] < radius_start[0] or param[1] < radius_start[1]:
                ErrorInput("Невозможно построить спектр. Конечный радиус должен быть больше начального.")
                return
            
        if self.check_size_range(center, radius_start, count, action, param):
            ErrorInput("Невозможно построить спектр. Превышен максимальный размер холста.")
        else:
            self.update_stack()
            color = QColor(self.pen_color)
            self.draw_range(center, radius_start, count, action, param, color)
            self.update_scene()
        
    def draw_range(self, center, radius_start, count, action, param, color):
        if action == 0:
            step_x = (param[0] - radius_start[0]) / (count - 1)
            step_y = (param[1] - radius_start[1]) / (count - 1)
            radius_end = (param[0], param[1])
        else:
            step_x = param[0]
            step_y = param[1]
            radius_end = (param[0] * count, param[1] * count)
        radius_start = list(radius_start)
        for i in range(count):
            if radius_start[0] >= radius_end[0] or radius_start[1] >= radius_end[1]:
                self.draw_figure(center, radius_end, color)
                break
            self.draw_figure(center, radius_start, color)
            radius_start[0] += step_x
            radius_start[1] += step_y

    def draw_figure(self, center, radius, color):
        action = self.comboBox_alg.currentIndex()
        center = list(center)
        center[0] += self.canvas_center[0]
        center[1] += self.canvas_center[1]
        print(center)
        if action == 0:
            self.draw_ellipse(center, radius, color)

    def draw_ellipse(self, center, radius, color):
        painter = QPainter(self.pixmap)
        painter.setPen(QColor(color))
        painter.drawEllipse(center[0] - radius[0], center[1] - radius[1], radius[0] * 2, radius[1] * 2)
        painter.end()

    def show_info(self):
        self.sub_window = Info()
        self.sub_window.show()
    
    def set_options(self):
        action = self.comboBox_figure.currentIndex()
        if not action:
            self.doubleSpinBox_ry.setEnabled(False)
        else:
            self.doubleSpinBox_ry.setEnabled(True)

    def set_color(self):
        self.update_stack()
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