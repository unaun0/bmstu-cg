from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QColor, QPen, QPixmap, QPainter
from PyQt5.QtWidgets import QWidget, QMainWindow, QMessageBox, QColorDialog, QPushButton
from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsPixmapItem, QGraphicsScene
from PyQt5.QtCore import Qt, QRect, pyqtSignal

from main_window import Ui_MainWindow
from task_popup import Ui_TaskPopup
from errors import ErrorInput

from geometry import *
from math import ceil
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
        self.pushButton_analyse.clicked.connect(self.time_analyse) # analyse time

    def set_value(self):
        self.doubleSpinBox_xc.setValue(0.0)
        self.doubleSpinBox_yc.setValue(0.0)
        self.spinBox_count.setValue(1)
        self.doubleSpinBox_rx.setValue(50)
        self.doubleSpinBox_ry.setValue(50)
        self.doubleSpinBox_xstart_3.setValue(1)
        self.doubleSpinBox_ystart_3.setValue(1)
        self.doubleSpinBox_deltax.setValue(25)
        self.doubleSpinBox_deltay.setValue(25)

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
    
    def scrollbar_refresh(self):
        self.graphicsView.horizontalScrollBar().setValue(int(self.canvas_center[0] - (self.view_size[0] // 2)))
        self.graphicsView.verticalScrollBar().setValue(int(self.canvas_center[1] - (self.view_size[1] // 2)))

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

        self.bg_color = QColor(255, 255, 255)
        self.pen_color = QColor(0, 0, 0)
        self.scale = 1

        self.set_bg_color(self.bg_color)
        self.set_pen_color(self.pen_color)

        self.set_value()
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
        
        if radius_x < 0.5:
            radius_x = 0.5
        if radius_y < 0.5:
            radius_y = 0.5
        radius = (radius_x, radius_y)

        if self.check_size_figure(center, radius):
            ErrorInput("Невозможно построить фигуру. Превышен максимальный размер холста.")
        else:
            self.update_stack()
            color = QColor(self.pen_color)
            self.draw_figure(center, radius, color, False)
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
        elif param == 1:
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
        if radius_x < 0.5:
            radius_x = 0.5
        if radius_y < 0.5:
            radius_y = 0.5
        radius_start = (radius_x, radius_y)

        count = (int(self.spinBox_count.value()))
        if count <= 0:
            ErrorInput("Невозможно построить спектр. Количество фигур должно быть больше нуля.")
            return
        
        action = self.comboBox_param.currentIndex()
        param = ((float(self.doubleSpinBox_deltax.value())), 
                 (float(self.doubleSpinBox_deltay.value())))
        if action == 0:
            if param[0] < radius_start[0] or param[1] < radius_start[1]:
                ErrorInput("Невозможно построить спектр. Конечный радиус должен быть больше начального.")
                return 
        if self.check_size_range(center, radius_start, count, action, param):
            ErrorInput("Невозможно построить спектр. Превышен максимальный размер холста.")
        else:
            self.update_stack()
            color = QColor(self.pen_color)
            self.draw_range(center, radius_start, count, action, param, color, False)
            self.update_scene()
        
    def draw_range(self, center, radius_start, count, action, param, color, timer):
        if action == 0:
            if count > 1:
                step_x = abs(param[0] - radius_start[0]) / (count - 1)
                step_y = abs(param[1] - radius_start[1]) / (count - 1)
            else:
                step_x = abs(param[0] - radius_start[0])
                step_y = abs(param[1] - radius_start[1])
            radius_end = (param[0], param[1])
        else:
            step_x = param[0]
            step_y = param[1]
            radius_x = step_x * count
            radius_y = step_y * count
            if radius_x == 0:
                radius_x = radius_start[0]
            if radius_y == 0:
                radius_y = radius_start[1]
            radius_end = (radius_x, radius_y)
        radius_start = list(radius_start)
        for i in range(count):
            self.draw_figure(center, radius_start, color, timer)
            radius_start[0] += step_x
            radius_start[1] += step_y

    def draw_figure(self, center, radius, color, timer):
        action = self.comboBox_alg.currentIndex()

        center = list(center)
        center[0] += self.canvas_center[0]
        center[1] += self.canvas_center[1]

        if action == 0:
            self.draw_ellipse(center, radius, color)
        elif action == 1:
            self.draw_ellipse_canonical(center, radius, color, timer)
        elif action == 2:
            self.draw_ellipse_parametric(center, radius, color, timer)
        elif action == 3:
            self.draw_ellipse_mid_point(center, radius, color, timer)
        elif action == 4:
            self.draw_ellipse_bresenham(center, radius, color, timer)
        else:
            return False
        return True

    def draw_ellipse(self, center, radius, color):
        painter = QPainter(self.pixmap)
        painter.setPen(QColor(color))   
        painter.drawEllipse(round(center[0] - radius[0]), round(center[1] - radius[1]), round(radius[0] * 2), round(radius[1] * 2))
        painter.end()

    def draw_point(self, point, color):
        painter = QPainter(self.pixmap)
        painter.setPen(QColor(color))
        painter.drawPoint(round(point[0]), round(point[1]))
        painter.end()

    def draw_ellipse_canonical(self, center, radius, color, timer):
        points = ellipse_canonical(center[0], center[1], radius[0], radius[1])
        if not timer:
            for point in points:
                self.draw_point(point, color)

    def draw_ellipse_parametric(self, center, radius, color, timer):
        points = ellipse_parametric(center[0], center[1], radius[0], radius[1])
        if not timer:
            for point in points:
                self.draw_point(point, color)

    def draw_ellipse_bresenham(self, center, radius, color, timer):
        points = ellipse_bresenham(center[0], center[1], radius[0], radius[1])
        if not timer:
            for point in points:
                self.draw_point(point, color)

    def draw_ellipse_mid_point(self, center, radius, color, timer):
        points = ellipse_mid_point(center[0], center[1], radius[0], radius[1])
        if not timer:
            for point in points:
                self.draw_point(point, color)

    def time_analyse(self):
        msgBox = QMessageBox()
        msgBox.setText("Выберите фигуру для анализа по времени:")
        msgBox.setWindowTitle("Анализ")

        ok_button = QPushButton('Окружность', msgBox)
        ellipse_button = QPushButton('Эллипс', msgBox)

        msgBox.addButton(ok_button, QMessageBox.AcceptRole)
        msgBox.addButton(ellipse_button, QMessageBox.RejectRole)

        result = msgBox.exec_()
        if result == QMessageBox.AcceptRole:
            self.time_analyse_circle()
        elif result == QMessageBox.RejectRole:
            self.time_analyse_ellipse()
    
    def time_analyse_circle(self):
        last_index = self.comboBox_alg.currentIndex()

        sizes = [1]
        for i in range(100, 10001, 100):
            sizes.append(i)

        time_alg = []
        for method in range(4):
            self.comboBox_alg.setCurrentIndex(method + 1)
            time_size = [] * 9
            for size in sizes:
                average_time = 0
                for count in range(5):
                    time_start = time.time_ns()
                    self.draw_figure([0, 0], [size, size], None, True)
                    time_end = time.time_ns()
                    average_time += (time_end - time_start)
                average_time /= 5
                time_size.append(average_time)
            time_alg.append(time_size.copy())
        
        self.comboBox_alg.setCurrentIndex(last_index)

        plt.figure(figsize=(14, 5))
        plt.title("Анализ времени для различных алгоритмов пострения окружности\nКоличество итераций: 5\n")
        plt.ylabel("время(ns)")
        plt.xlabel("радиус")
        plt.plot(sizes, time_alg[0], label="канонич. ур-е")
        plt.plot(sizes, time_alg[1], linestyle = '--', label="парам. ур-е")
        plt.plot(sizes, time_alg[2], linestyle = '-.', label="алг-м средней точки")
        plt.plot(sizes, time_alg[3], linestyle = ':', label="алг-м Брезенхема")
        ticks = [1]
        for i in range(1000, 10001, 1000):
            ticks.append(i)
        plt.xticks(ticks)
        plt.legend()
        plt.show()

    def time_analyse_ellipse(self):
        self.time_analyse_ellipse_ry()
        self.time_analyse_ellipse_rx()

    def time_analyse_ellipse_ry(self):
        last_index = self.comboBox_alg.currentIndex()
        rx = 5
        sizes = []
        for i in range(1, 21):
            new_size = [rx, (rx * rx)]
            sizes.append(new_size)
            rx += 5
        time_alg = []
        for method in range(4):
            self.comboBox_alg.setCurrentIndex(method + 1)
            time_size = []
            for size in sizes:
                average_time = 0
                for count in range(5):
                    time_start = time.time_ns()
                    self.draw_figure([0, 0], [size[0], size[1]], None, True)
                    time_end = time.time_ns()
                    average_time += (time_end - time_start)
                average_time /= 5
                time_size.append(average_time)
            time_alg.append(time_size.copy())
        self.comboBox_alg.setCurrentIndex(last_index)

        ticks_list = []
        for i in range(20):
            ticks_list.append(sizes[i][1] / sizes[i][0])

        plt.figure(figsize=(14, 5))
        plt.title("Анализ времени для различных алгоритмов пострения эллипса\nКоличество итераций: 5\n")
        plt.ylabel("время(ns)")
        plt.xlabel("отношение Ry / Rx")
        plt.plot(ticks_list, time_alg[0], label="канонич. ур-е")
        plt.plot(ticks_list, time_alg[1], linestyle = '--', label="парам. ур-е")
        plt.plot(ticks_list, time_alg[2], linestyle = '-.', label="алг-м средней точки")
        plt.plot(ticks_list, time_alg[3], linestyle = ':', label="алг-м Брезенхема")
        plt.xticks(ticks_list)
        plt.legend()
        plt.show()

    def time_analyse_ellipse_rx(self):
        last_index = self.comboBox_alg.currentIndex()
        rx = 5
        sizes = []
        for i in range(1, 21):
            new_size = [rx, (rx * rx)]
            sizes.append(new_size)
            rx += 5
        time_alg = []
        for method in range(4):
            self.comboBox_alg.setCurrentIndex(method + 1)
            time_size = []
            for size in sizes:
                average_time = 0
                for count in range(5):
                    time_start = time.time_ns()
                    self.draw_figure([0, 0], [size[1], size[0]], None, True)
                    time_end = time.time_ns()
                    average_time += (time_end - time_start)
                average_time /= 5
                time_size.append(average_time)
            time_alg.append(time_size.copy())
        self.comboBox_alg.setCurrentIndex(last_index)

        ticks_list = []
        for i in range(20):
            ticks_list.append(sizes[i][1] / sizes[i][0])

        plt.figure(figsize=(14, 5))
        plt.title("Анализ времени для различных алгоритмов пострения эллипса\nКоличество итераций: 5\n")
        plt.ylabel("время(ns)")
        plt.xlabel("отношение Rx / Ry")
        plt.plot(ticks_list, time_alg[0], label="канонич. ур-е")
        plt.plot(ticks_list, time_alg[1], linestyle = '--', label="парам. ур-е")
        plt.plot(ticks_list, time_alg[2], linestyle = '-.', label="алг-м средней точки")
        plt.plot(ticks_list, time_alg[3], linestyle = ':', label="алг-м Брезенхема")
        plt.xticks(ticks_list)
        plt.legend()
        plt.show()

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
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_0:
            self.graphicsView.resetTransform()
            self.scale = 1
        elif event.key() == Qt.Key_Plus or event.key() == Qt.Key_Equal:
            self.scale_plus()
        elif event.key() == Qt.Key_Minus:
            self.scale_minus()
        elif event.key() == Qt.Key_Escape:
            buttonReply = QMessageBox.question(self, 'Завершение работы', \
                                           "Вы хотите завершить программу?", \
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if buttonReply == QMessageBox.Yes:
                QtWidgets.QApplication.quit()
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
        elif event.key() == Qt.Key_A:
            currentIndex = self.comboBox_alg.currentIndex()
            count = self.comboBox_alg.count()
            nextIndex = (currentIndex + 1) % count
            self.comboBox_alg.setCurrentIndex(nextIndex)
        elif event.key() == Qt.Key_F:
            self.build_figure()
        elif event.key() == Qt.Key_S:
            self.build_range()
        elif event.key() == Qt.Key_S:
            self.build_range()
    
    def showEvent(self, event):
        self.scrollbar_refresh()

    def zoomWheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.scale_plus()
        else:
            self.scale_minus()

    def pointSelectEvent(self, event):
        print(event.button())
        if event.button() == Qt.LeftButton:
            pos_scene = self.graphicsView.mapToScene(event.pos())
            point = [pos_scene.x() - (self.canvas_center[0]), 
                     -(pos_scene.y() - (self.canvas_center[1]))]
            self.doubleSpinBox_xc.setValue(float(point[0]))
            self.doubleSpinBox_yc.setValue(float(point[1]))
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
