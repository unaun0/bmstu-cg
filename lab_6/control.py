from PyQt5 import QtWidgets, QtGui, QtTest
from PyQt5.QtGui import QColor, QPen, QPixmap, QPainter
from PyQt5.QtWidgets import QWidget, QMainWindow, QMessageBox, QColorDialog, QPushButton, QDialog
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal

from main_window import Ui_MainWindow
from task_popup import Ui_TaskPopup
from errors import ErrorInput

import matplotlib.pyplot as plt
import time
from math import ceil, floor

class Poligon():
    sindex = 0
    eindex = 0
    edges = []
    fill = True

class Figure():
    sindex = 0
    eindex = 0
    count_point = 0
    closed = True

class SeedPoint():
    point = None

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self): 
        super(MainWindow, self).__init__()
        self.setupUi(self)
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
        self.pushButton_clear.clicked.connect(self.clear_canvas) # clear
        self.pushButton_back.clicked.connect(self.undo) # back
        self.pushButton_fadd_point.clicked.connect(self.add_point) # add point
        self.pushButton_ffill.clicked.connect(self.fill_poligon) # close figure
        self.pushButton_fclose.clicked.connect(self.close_figure) # fill figure

    def init_stack(self):
        self.state_stack = []
        self.stack_size = 10
        self.points = []

    def init_canvas(self):
        self.scene = QtWidgets.QGraphicsScene(self)
        self.graphicsView.setScene(self.scene)
        self.graphicsView.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.canvas_size = (5002, 5002)
        self.view_size = (self.graphicsView.width(), self.graphicsView.height())
        self.canvas_center = (self.canvas_size[0] / 2, self.canvas_size[1] / 2)

        self.pixmap = QPixmap(5002, 5002)
        self.pixmap.fill(Qt.white)

        self.scene.addPixmap(self.pixmap)
        self.scale = 1

        self.graphicsView.mousePressEvent = self.pointSelectEvent
        self.graphicsView.mouseMoveEvent = self.canvasMoveEvent
        self.graphicsView.wheelEvent = self.zoomWheelEvent

        self.init_color_settings()
        self.update_stack()
    
    def init_color_settings(self):
        self.bg_color = QColor(255, 255, 255)
        self.fill_color = QColor(0, 0, 0)
        self.edge_color = QColor(0, 0, 0)
    
    def scrollbar_refresh(self):
        self.graphicsView.horizontalScrollBar().setValue(int(self.canvas_center[0] - (self.view_size[0] // 2)))
        self.graphicsView.verticalScrollBar().setValue(int(self.canvas_center[1] - (self.view_size[1] // 2)))

    def update_table(self, point):
        last_index_row = self.tableWidget_points.rowCount()
        self.tableWidget_points.insertRow(last_index_row)
        self.tableWidget_points.setItem(last_index_row, 0, QtWidgets.QTableWidgetItem("{:10}".format(point[0])))
        self.tableWidget_points.setItem(last_index_row, 1, QtWidgets.QTableWidgetItem("{:10}".format(point[1])))

    def push_point_in_table(self, point): 
        self.points.append(point)
        self.update_table(point)

    def fill_table(self):
        color = self.fill_color
        old_alpha = color.alpha()
        color.setAlpha(120)
        if Poligon.sindex:
            last_color = self.tableWidget_points.item(Poligon.sindex - 1, 0).background().color()
            if color == last_color:
                color.setAlpha(100)
        for i in range(Poligon.sindex, Poligon.eindex + 1):
            self.tableWidget_points.item(i, 0).setBackground(QtGui.QBrush(QtGui.QColor(color)))
            self.tableWidget_points.item(i, 1).setBackground(QtGui.QBrush(QtGui.QColor(color)))
        color.setAlpha(old_alpha)
    
    def draw_edge(self):
        last_index_row = self.tableWidget_points.rowCount() - 1
        if Figure.closed:
            if Poligon.fill:
                Poligon.fill = False
                Poligon.sindex = last_index_row
                self.pixmap.fill(Qt.white)
            Figure.closed = False
            Figure.sindex = last_index_row
            Figure.count_point = 1
        else:
            Figure.count_point += 1
            point_prev = (float(self.tableWidget_points.item(last_index_row - 1 , 0).text()), \
                        float(self.tableWidget_points.item(last_index_row - 1, 1).text()))
            point_pres = (float(self.tableWidget_points.item(last_index_row, 0).text()), \
                        float(self.tableWidget_points.item(last_index_row, 1).text()))
            if point_pres == point_prev:
                ErrorInput("Длина ребра фигуры должна быть больше нуля.")
                self.tableWidget_points.removeRow(last_index_row)
                self.points = self.points[:-1]
                return
            elif Figure.count_point > 2:
                start_prev_edge = (float(self.tableWidget_points.item(last_index_row - 2 , 0).text()), \
                                    float(self.tableWidget_points.item(last_index_row - 2, 1).text()))
                if start_prev_edge == point_pres:
                    ErrorInput("Ребра фигуры не должны повторяться.")
                    self.tableWidget_points.removeRow(last_index_row)
                    self.points = self.points[:-1]
                    return
            self.draw_line(point_prev, point_pres, self.edge_color)
     
    def add_point(self):
        self.update_stack()
        point = (int(self.spinBox_fx.value()), int(self.spinBox_fy.value()))
        if self.radioButton.isChecked():
            self.push_point_in_table(point)
            self.draw_edge()
        elif self.radioButton_2.isChecked():
            self.add_seed_point(point)

    def close_figure(self):
        self.update_stack()
        Figure.eindex = self.tableWidget_points.rowCount() - 1
        count = Figure.eindex - Figure.sindex
        if count < 2:
            ErrorInput("Недостаточно точек, чтобы замкнуть фигуру (>= 3).")
            return
        point_start = (float(self.tableWidget_points.item(Figure.sindex , 0).text()), \
                      float(self.tableWidget_points.item(Figure.sindex, 1).text()))
        point_end = (float(self.tableWidget_points.item(Figure.eindex, 0).text()), \
                      float(self.tableWidget_points.item(Figure.eindex, 1).text()))
        if point_end != point_start:
            self.draw_line(point_start, point_end, self.edge_color)
        Poligon.edges = list(Poligon.edges.copy() + self.make_edges_list_from_table().copy())
        Poligon.eindex = Figure.eindex
        Figure.count_point = 0
        Figure.closed = True
        
    def fill_poligon(self):
        self.update_stack()
        if not Figure.closed:
            ErrorInput("Необходимо замкнуть фигуру.")
            return
        if len(Poligon.edges) < 3:
            ErrorInput("Невозможно закрасить область.")
            return
        if SeedPoint.point == None:
            ErrorInput("Отсутствует затравочная точка.")
            return
        if not self.is_inside(SeedPoint.point, Poligon.edges):
            ErrorInput("Затравочная точка вне области.")
            return
        self.fill_table()

        pause = 0
        time_flag = False
        if self.tab_index != None:
            if self.tab_index == 0:
                pause = int(self.spinBox_pause_time.value())
            elif self.tab_index == 1:
                time_flag = True

        start = time.time_ns()

        self.fill_lines(SeedPoint.point, self.fill_color, pause)
    
        end = time.time_ns()

        if time_flag:
            result = (end - start) * 0.000001
            self.label_time_action.setText(str(round(result, 6)))

        Poligon.fill = True
        Poligon.edges = []
    
    def make_edges_list_from_table(self):
        edges = []
        for i in range(Figure.sindex, Figure.eindex):
            edge = (int(float(self.tableWidget_points.item(i, 0).text().strip())), \
                    int(float(self.tableWidget_points.item(i, 1).text().strip())), \
                    int(float(self.tableWidget_points.item(i + 1, 0).text().strip())), \
                    int(float(self.tableWidget_points.item(i + 1, 1).text().strip())))
            edges.append(edge)
        edge = (int(float(self.tableWidget_points.item(Figure.eindex, 0).text().strip())), \
                int(float(self.tableWidget_points.item(Figure.eindex, 1).text().strip())), \
                int(float(self.tableWidget_points.item(Figure.sindex, 0).text().strip())), \
                int(float(self.tableWidget_points.item(Figure.sindex, 1).text().strip())))
        edges.append(edge)

        return edges

    def is_inside(self, point, edges):
        x, y = point
        count = 0
        for edge in edges:
            x1, y1, x2, y2 = edge
            if (y1 < y and y2 >= y) or (y2 < y and y1 >= y):
                if x1 + (y - y1) / (y2 - y1) * (x2 - x1) < x:
                    count += 1
        return count % 2 == 1

    def is_edge(self, point):
        point = (round(point[0] + self.canvas_center[0]), round(self.canvas_center[1] - point[1]))
        pixel_color = QColor(self.pixmap.toImage().pixel(point[0], point[1]))
        if pixel_color == self.edge_color:
            return True
        return False

    def is_bg(self, point):
        point = (round(point[0] + self.canvas_center[0]), round(self.canvas_center[1] - point[1]))
        pixel_color = QColor(self.pixmap.toImage().pixel(point[0], point[1]))
        if pixel_color == self.bg_color:
            return True
        return False
    
    def is_fill(self, point):
        point = (round(point[0] + self.canvas_center[0]), round(self.canvas_center[1] - point[1]))
        pixel_color = QColor(self.pixmap.toImage().pixel(point[0], point[1]))
        if pixel_color == self.fill_color:
            return True
        return False
        
    def fill_lines(self, seedpoint, color, pause):
        stack = []
        stack.append(seedpoint)
        while len(stack) > 0:
            x, y = stack.pop()

            self._draw_point((x + self.canvas_center[0], 
                              self.canvas_center[1] - y), 
                              color)
            
            tmp_x = x
            tmp_y = y

            x += 1
            while (self.is_edge((x, y)) == False) and (self.is_fill((x, y)) == False):
                self._draw_point((x + self.canvas_center[0], 
                                  self.canvas_center[1] - y), 
                                  color)
                x += 1
            x_right = x - 1

            x = tmp_x - 1
            while (self.is_edge((x, y)) == False) and (self.is_fill((x, y)) == False):
                self._draw_point((x + self.canvas_center[0], 
                                  self.canvas_center[1] - y), 
                                  color)
                x -= 1
            x_left = x + 1

            for cur_y in [y + 1, y - 1]:
                x = x_left
                while x <= x_right:
                    flag = False
                    while (self.is_edge((x, cur_y)) == False) and (self.is_fill((x, cur_y)) == False) and (x <= x_right):
                        flag = True
                        x += 1
                    if flag == True:
                        if (x == x_right) and (self.is_edge((x, cur_y)) == False) and (not self.is_fill((x, cur_y)) == False):
                            stack.append((x, cur_y))
                        else:
                            stack.append((x - 1, cur_y))
                        flag = False
                    x_cur = x
                    while (self.is_edge((x, cur_y)) == True or self.is_fill((x, cur_y)) == True) and (x < x_right):
                        x += 1
                    if x == x_cur:
                        x += 1
            if pause > 0:
                QtTest.QTest.qWait(pause)
                self.update_scene()
        self.update_scene()
    
    def draw_line(self, point_a, point_b, color):
        point_a = (round(point_a[0] + self.canvas_center[0]), round(self.canvas_center[1] - point_a[1]))
        point_b = (round(point_b[0] + self.canvas_center[0]), round(self.canvas_center[1] - point_b[1]))
        self._draw_line(point_a, point_b, color)
        self.update_scene()

    def _draw_point(self, point, color):
        painter = QPainter(self.pixmap)
        painter.setPen(QColor(color))
        painter.drawPoint(round(point[0]), round(point[1]))
        painter.end()

    def _draw_line(self, point_a, point_b, color):
        painter = QPainter(self.pixmap)
        painter.setPen(QColor(color))   
        painter.drawLine(round(point_a[0]), round(point_a[1]), round(point_b[0]), round(point_b[1]))
        painter.end()
    
    def draw_point(self, point, color):
        point = (round(point[0] + self.canvas_center[0]), round(self.canvas_center[1] - point[1]))
        self._draw_point(point, color)
        self.update_scene()

    def add_seed_point(self, point):
        SeedPoint.point = (point[0], point[1])
        self.lineEdit_pointX.setText(str(round(point[0])))
        self.lineEdit_pointY.setText(str(round(point[1])))

    def update_scene(self):
        self.scene.clear()
        self.scene.addPixmap(self.pixmap)
        self.scene.update()
    
    def update_stack(self):
        pixmap_copy = self.pixmap.copy()
        self.state_stack.append([self.points.copy(), 
                                 pixmap_copy.copy(), 
                                 [Poligon.sindex, Poligon.eindex, Poligon.edges, Poligon.fill],
                                 [Figure.sindex, Figure.eindex, Figure.count_point, Figure.closed],
                                 SeedPoint.point,
                                 self.bg_color, 
                                 self.edge_color,
                                 self.fill_color])
        if len(self.state_stack) > self.stack_size:
            self.state_stack.pop(0)

    def undo(self):
        index = (len(self.state_stack) - 1)
        if index < 0:
            ErrorInput("Невозможно отменить действие.")
        else:
            self.points = (self.state_stack[index][0]).copy()
            self.tableWidget_points.setRowCount(0)
            for point in  self.points:
                self.update_table(point)
            self.pixmap = self.state_stack[index][1]
            self.set_bg_color(self.state_stack[index][5])
            self.set_edge_color(self.state_stack[index][6])
            self.set_fill_color(self.state_stack[index][7])

            poligon = self.state_stack[index][2]

            Poligon.sindex = poligon[0]
            Poligon.eindex = poligon[1]
            Poligon.edges = poligon[2].copy()
            Poligon.fill = poligon[3]

            figure = self.state_stack[index][3]

            Figure.sindex = figure[0]
            Figure.eindex = figure[1]
            Figure.count_point = figure[2]
            Figure.closed = figure[3]

            SeedPoint.point = self.state_stack[index][4]
            if SeedPoint.point != None:
                self.add_seed_point(SeedPoint.point)
            else:
                self.lineEdit_pointX.setText("")
                self.lineEdit_pointY.setText("")

            self.state_stack.pop(index)
            self.update_scene()

    def clear_canvas(self):
        self.canvas_size = (5002, 5002)
        self.view_size = (self.graphicsView.width(), self.graphicsView.height())
        self.canvas_center = (self.canvas_size[0] / 2, self.canvas_size[1] / 2)

        self.scene.clear()
        self.update_stack()

        self.pixmap = QPixmap(5002, 5002)
        self.pixmap.fill(Qt.white)

        self.scene.addPixmap(self.pixmap)
        self.graphicsView.resetTransform()

        self.tableWidget_points.clearContents()
        self.tableWidget_points.setRowCount(0)

        self.lineEdit_pointX.setText("")
        self.lineEdit_pointY.setText("")
        
        self.points.clear()

        self.scale = 1

        Poligon.sindex = 0
        Poligon.eindex = 0
        Poligon.edges = []
        Poligon.fill = True

        Figure.sindex = 0
        Figure.eindex = 0
        Figure.count_point = 0
        Figure.closed = True

        SeedPoint.point = None

        self.set_start_color()

        self.scrollbar_refresh()

    def set_start_color(self):
        self.init_color_settings()
        self.set_bg_color(self.bg_color)
        self.set_edge_color(self.edge_color)
        self.set_fill_color(self.fill_color)

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
            if action == 0:
                if not Poligon.fill:
                    ErrorInput("Невозможно изменить цвет ребра в процессе создания области.")
                    return
                self.update_stack()
                self.set_edge_color(color)
            elif action == 1:
                self.update_stack()
                self.set_fill_color(color)
                
    def set_bg_color(self, color):
        self.bg_color = color
        brush = QtGui.QBrush(QtGui.QColor(color))
        self.graphicsView.setBackgroundBrush(brush)

    def set_fill_color(self, color):
        self.fill_color = color
        Poligon.color = color
        color = tuple(QColor.getRgb(color))
        self.label_fcolor.setStyleSheet("background-color: rgba{:};".format(str(color)))
    
    def set_edge_color(self, color):
        self.edge_color = color
        Poligon.color = color
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
            point = [(round(pos_scene.x()) - (self.canvas_center[0])), 
                    -(round(pos_scene.y()) - (self.canvas_center[1]))]
            if self.radioButton.isChecked():
                self.update_stack()
                self.push_point_in_table(point)
                self.draw_edge()
            elif self.radioButton_2.isChecked():
                self.update_stack()
                self.add_seed_point(point)
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
