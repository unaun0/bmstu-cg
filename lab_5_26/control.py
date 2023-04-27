from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QColor, QPen, QPixmap, QPainter
from PyQt5.QtWidgets import QWidget, QMainWindow, QMessageBox, QColorDialog, QPushButton, QDialog
from PyQt5.QtCore import Qt

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
        #self.pushButton_clear.clicked.connect(self.clear_canvas) # clean
        #self.pushButton_back.clicked.connect(self.undo) # back
        self.pushButton_fadd_point.clicked.connect(self.add_point) # add point
        self.pushButton_ffill.clicked.connect(self.fill_poligon) # close figure
        self.pushButton_fclose.clicked.connect(self.close_figure) # fill figure

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
        self.scale = 1

        self.graphicsView.mousePressEvent = self.pointSelectEvent
        self.graphicsView.mouseMoveEvent = self.canvasMoveEvent
        self.graphicsView.wheelEvent = self.zoomWheelEvent

        self.init_color_settings()
        #self.update_stack()
    
    def init_color_settings(self):
        self.bg_color = QColor(255, 255, 255)
        self.fill_color = QColor(0, 0, 0)
    
    def scrollbar_refresh(self):
        self.graphicsView.horizontalScrollBar().setValue(int(self.canvas_center[0] - (self.view_size[0] // 2)))
        self.graphicsView.verticalScrollBar().setValue(int(self.canvas_center[1] - (self.view_size[1] // 2)))

    def push_point_in_table(self, point): 
        last_index_row = self.tableWidget_points.rowCount()
        self.tableWidget_points.insertRow(last_index_row)
        self.tableWidget_points.setItem(last_index_row, 0, QtWidgets.QTableWidgetItem("{:10}".format(point[0])))
        self.tableWidget_points.setItem(last_index_row, 1, QtWidgets.QTableWidgetItem("{:10}".format(point[1])))

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
                return
            elif Figure.count_point > 2:
                start_prev_edge = (float(self.tableWidget_points.item(last_index_row - 2 , 0).text()), \
                                    float(self.tableWidget_points.item(last_index_row - 2, 1).text()))
                if start_prev_edge == point_pres:
                    ErrorInput("Ребра фигуры не должны повторяться.")
                    self.tableWidget_points.removeRow(last_index_row)
                    return
            self.draw_line(point_prev, point_pres, self.fill_color)
    
    def add_point(self):
        point = (int(self.spinBox_fx.value()), int(self.spinBox_fy.value()))
        self.push_point_in_table(point)
        self.draw_edge()

    def close_figure(self):
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
            self.draw_line(point_start, point_end, self.fill_color)
        Poligon.edges = list(Poligon.edges.copy() + self.make_edges_list_from_table().copy())
        Poligon.eindex = Figure.eindex
        Figure.count_point = 0
        Figure.closed = True
        
    def fill_poligon(self):
        if not Figure.closed:
            ErrorInput("Необходимо замкнуть фигуру.")
            return
        if len(Poligon.edges) < 1:
            ErrorInput("Невозможно закрасить область.")
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
        lines, ranges = self.make_lines(Poligon.edges)
        self.fill_lines(lines, ranges, self.fill_color, pause)
        end = time.time_ns()
        if time_flag:
            result = (end - start) * 0.000001
            self.label_time_action.setText(str(round(result, 6)))

        Poligon.fill = True
        Poligon.edges = []
    
    def get_edge_top_y(self, edge):
        return min(edge[1], edge[3])
    
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

        sorted_edges = sorted(edges, key=self.get_edge_top_y)

        return sorted_edges

    def make_lines(self, edges):

        min_y = min([min(edge[1], edge[3]) for edge in edges])
        max_y = max([max(edge[1], edge[3]) for edge in edges])
        min_x = min([min(edge[0], edge[2]) for edge in edges])
        max_x = max([max(edge[0], edge[2]) for edge in edges])

        sorted_edges = sorted(edges, key=self.get_edge_top_y)

        lines = []
        for y in range(min_y, max_y + 1):
            intersections = []
            for edge in edges:
                x1, y1, x2, y2 = edge
                if y1 <= y < y2 or y2 <= y < y1:
                    x = (((y - y1) * (x2 - x1)) / (y2 - y1) + x1)
                    intersections.append(x)
            intersections.sort()
            lines.append([y, intersections.copy()])
        
        return lines, (min_y, max_y, min_x, max_x)
    
    def fill_lines(self, lines, ranges, color, pause):
        min_y, max_y, min_x, max_x = ranges
        for i in range(0, len(lines)):
            y = lines[i][0]
            _len = len(lines[i][1])
            for j in range(0, _len - 1, 2):
                x1 = max(min_x, ceil(lines[i][1][j]))
                x2 = min(max_x, floor(lines[i][1][j + 1]))
                for x in range(x1, x2 + 1):
                    self._draw_point((x + self.canvas_center[0], self.canvas_center[1] - y), color)
                if pause > 0:
                    time.sleep(pause // 1000)
                    print("hello")
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
    
    def update_scene(self):
        self.scene.addPixmap(self.pixmap)
        self.graphicsView.show()
    
    def update_stack(self):
        pixmap_copy = self.pixmap.copy()
        #self.state_stack.append([pixmap_copy.copy(), self.bg_color, self.pen_color])
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
                if not Poligon.fill:
                    ErrorInput("Невозможно изменить цвет области в процессе её создания.")
                    return
                self.set_fill_color(color)
 
    def set_bg_color(self, color):
        self.bg_color = color
        brush = QtGui.QBrush(QtGui.QColor(color))
        self.graphicsView.setBackgroundBrush(brush)
        color = tuple(QColor.getRgb(color))
        self.label_bcolor.setStyleSheet("background-color: rgba{:};".format(str(color)))

    def set_fill_color(self, color):
        self.fill_color = color
        color = tuple(QColor.getRgb(color))
        self.label_fcolor.setStyleSheet("background-color: rgba{:};".format(str(color)))

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
            point = [round(pos_scene.x() - (self.canvas_center[0])), 
                     -round(pos_scene.y() - (self.canvas_center[1]))]
            self.push_point_in_table(point)
            self.draw_edge()
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
