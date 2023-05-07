from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QColor, QPixmap, QPainter
from PyQt5.QtWidgets import QWidget, QMessageBox, QColorDialog, QDialog, QGraphicsEllipseItem
from PyQt5.QtCore import Qt

from main_window import Ui_MainWindow
from task_popup import Ui_TaskPopup
from errors import ErrorInput
from clipper import *

class Line:
    spoint = None
    epoint = None

    _list = []

    proc = False

    _res_list = []

class Clip:
    spoint = None
    tpoint = None
    epoint = None

    proc = False
    closed = True

    items = []
    points = []

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self): 
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.stack_init()
        self.color_init()
        self.canvas_init()
        self.bindActions()
        self.bindButtons()

    def bindActions(self):
        self.radioButton_clip.toggled.connect(self.draw_mode_change_clip) # change mode
        self.radioButton_line.toggled.connect(self.draw_mode_change_line) # change mode
        self.actionExit.triggered.connect(self.closeEvent) # close app
        self.actionAuthors.triggered.connect(self.show_info) #  info about app

    def bindButtons(self):
        self.pushButton_ladd.clicked.connect(self.action_add_line) # add line
        self.pushButton_cadd.clicked.connect(self.action_add_clip) # add clipper
        self.pushButton_color.clicked.connect(self.set_color)  # set new color
        self.pushButton_clear.clicked.connect(self.canvas_clear) # clear
        self.pushButton_back.clicked.connect(self.undo) # back
        self.pushButton_close.clicked.connect(self.clipper_close) # close clipper
        self.pushButton_clip.clicked.connect(self.clipper_line) # clip lines

    def stack_init(self):
        self.state_stack = []
        self.stack_size = 20
    
    def scene_clear(self):
        for item in self.scene.items():
            if item != self.pixmap:
                item.hide()

    def stack_update(self):
        visible_items = []
        for item in self.scene.items():
            if item.isVisible():
                visible_items.append(item)
        self.state_stack.append([self.bg_color,
                                 self.line_color,
                                 self.clip_color,
                                 self.result_color,
                                 [Line.spoint, Line.epoint, Line._list.copy(), Line.proc, Line._res_list.copy()],
                                 [Clip.spoint, Clip.tpoint, Clip.epoint, Clip.proc, Clip.closed, Clip.items.copy(), Clip.points.copy()],
                                 visible_items.copy()
                                ])
        if len(self.state_stack) > self.stack_size:
            items = self.state_stack[0][6]
            for item in items:
                if item.isVisible():
                    continue
                if item != self.line and item != self.point and item != self.pixmap:
                    self.scene.removeItem(item)
            self.state_stack.pop(0)
    
    def undo(self):
        index = (len(self.state_stack) - 1)
        if index < 0:
            return ErrorInput("Невозможно отменить действие.")

        self.scene_clear()

        self.tableWidget_line.clearContents()
        self.tableWidget_line.setRowCount(0)

        self.tableWidget_clip.clearContents()
        self.tableWidget_clip.setRowCount(0)

        """ Color options """
        self.bg_color = self.state_stack[index][0]
        self.line_color = self.state_stack[index][1]
        self.clip_color = self.state_stack[index][2]
        self.result_color = self.state_stack[index][3]

        self.color_start_set()

        print("Color options: successfully canceled")

        """ Line options """
        lineOptions = self.state_stack[index][4].copy()

        Line.spoint, Line.epoint = lineOptions[0], lineOptions[1]

        Line._list = lineOptions[2]

        for line in Line._list:
            self.table_push_line((line[0], line[1]), (line[2], line[3]))

        Line.proc = lineOptions[3]

        Line._res_list = lineOptions[4]

        print("Line options: successfully canceled")

        """ Clip options """
        clipOptions = self.state_stack[index][5].copy()

        Clip.spoint, Clip.tpoint, Clip.epoint = clipOptions[0], clipOptions[1], clipOptions[2]

        Clip.proc, Clip.closed = clipOptions[3], clipOptions[4]

        Clip.items = clipOptions[5].copy()

        Clip.points = clipOptions[6].copy()

        for point in Clip.points:
            self.table_push_clip(point)

        print("Clip options: successfully canceled")
        
        """ Scene items """
        sceneItems = self.state_stack[index][6].copy()

        for item_ in sceneItems:
            item_.show()
        
        print("Scene options: successfully canceled")
        
        self.canvas_update()

        self.state_stack.pop(index)
        
    def canvas_init(self):
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
        self.graphicsView.mouseReleaseEvent = self.canvasReleaseEvent

        self.dashline_init()
        self.dashrect_point()

        self.stack_update()
    
    def canvas_scrollbar_refresh(self):
        self.graphicsView.horizontalScrollBar().setValue(int(self.canvas_center[0] - (self.view_size[0] // 2)))
        self.graphicsView.verticalScrollBar().setValue(int(self.canvas_center[1] - (self.view_size[1] // 2)))

    def canvas_update(self):
        self.scene.update()

    def canvas_clear(self):
        self.stack_update()

        self.canvas_size = (5002, 5002)
        self.view_size = (self.graphicsView.width(), self.graphicsView.height())
        self.canvas_center = (self.canvas_size[0] / 2, self.canvas_size[1] / 2)

        self.graphicsView.resetTransform()
        self.scene_clear()

        self.dashline_init()
        self.dashrect_point()

        self.canvas_update()
        self.canvas_scrollbar_refresh()

        self.tableWidget_line.clearContents()
        self.tableWidget_line.setRowCount(0)

        self.tableWidget_clip.clearContents()
        self.tableWidget_clip.setRowCount(0)
        
        self.scale = 1
        
        Line.spoint = None
        Line.epoint = None
        Line._list = []
        Line.proc = False
        Line._res_list = []

        Clip.spoint, Clip.tpoint, Clip.epoint = None, None, None
        Clip.proc, Clip.closed = False, True

        Clip.items = []
        Clip.points = []
        
        self.color_init()
        self.color_start_set()

    def table_push_line(self, point_a, point_b):
        last_index_row = self.tableWidget_line.rowCount()
        self.tableWidget_line.insertRow(last_index_row)
        self.tableWidget_line.setItem(last_index_row, 0, QtWidgets.QTableWidgetItem("{:10}".format(point_a[0])))
        self.tableWidget_line.setItem(last_index_row, 1, QtWidgets.QTableWidgetItem("{:10}".format(point_a[1])))
        self.tableWidget_line.setItem(last_index_row, 2, QtWidgets.QTableWidgetItem("{:10}".format(point_b[0])))
        self.tableWidget_line.setItem(last_index_row, 3, QtWidgets.QTableWidgetItem("{:10}".format(point_b[1])))
        self.table_fill(self.tableWidget_line, self.line_color)

    def table_push_clip(self, point_a):
        last_index_row = self.tableWidget_clip.rowCount()
        self.tableWidget_clip.insertRow(last_index_row)
        self.tableWidget_clip.setItem(last_index_row, 0, QtWidgets.QTableWidgetItem("{:10}".format(point_a[0])))
        self.tableWidget_clip.setItem(last_index_row, 1, QtWidgets.QTableWidgetItem("{:10}".format(point_a[1])))
        self.table_fill(self.tableWidget_clip, self.clip_color)

    def table_fill(self, table, color_):
        color = color_
        old_alpha = color.alpha()
        color.setAlpha(120)

        last_index_row = table.rowCount() - 1
        if last_index_row > 0:
            last_color = table.item(last_index_row - 1, 0).background().color()
            if color == last_color:
                color.setAlpha(90)
        for i in range(table.columnCount()):
            table.item(last_index_row, i).setBackground(QtGui.QBrush(QtGui.QColor(color)))
        
        color.setAlpha(old_alpha)
    
    def action_add_line(self):
        Line.proc = False
        Line.spoint = (self.spinBox_xs.value(), self.spinBox_ys.value())
        Line.epoint = (self.spinBox_xe.value(), self.spinBox_ye.value())
        self.add_line()
        
    def action_add_clip(self):
        Line.proc = False
        point = (self.spinBox_xos.value(), self.spinBox_yos.value())
        if Clip.closed:
            self.clip_refresh()
            Clip.spoint = point
            Clip.epoint = Clip.spoint
            Clip.tpoint = Clip.spoint
            Clip.points.append(Clip.epoint)
            self.table_push_clip(Clip.epoint)
            Clip.closed = False
        else:
            Clip.proc = False
            Clip.epoint = point
            self.add_clip()
            Clip.tpoint = Clip.epoint
    
    def clip_refresh(self):
        for item in Clip.items:
            item.hide()

        Clip.items = []
        Clip.points = []

        self.tableWidget_clip.clearContents()
        self.tableWidget_clip.setRowCount(0)

    def clip_update(self):
        for item in Clip.items:
            item.setZValue(1)

    def result_refresh(self):
        for item in Line._res_list:
            item.hide()
        Line._res_list = []

    def add_clip(self):
        if Clip.epoint == Clip.tpoint:
            ErrorInput("Длина ребра отсекателя должна быть больше нуля.")
        else:
            self.stack_update()
            Clip.items.append(self.draw_line(Clip.tpoint, Clip.epoint, self.clip_color))
            Clip.points.append(Clip.epoint)
            self.table_push_clip(Clip.epoint)

    def add_line(self):
        if Line.epoint == Line.spoint:
            ErrorInput("Длина отрезка должна быть больше нуля.")
        else:
            self.stack_update()
            Line._list.append((Line.spoint[0], Line.spoint[1], Line.epoint[0], Line.epoint[1]))
            self.draw_line(Line.spoint, Line.epoint, self.line_color)
            self.table_push_line(Line.spoint, Line.epoint)

    def add_line_mouse(self, point):
        if not Line.proc:
            Line.proc = True
            Line.spoint = tuple(point)
        else:
            Line.proc = False
            Line.epoint = tuple(point)
            self.add_line()

    def add_clip_mouse(self, point):
        Line.proc = False
        if Clip.closed:
            self.clip_refresh()
            Clip.spoint = tuple(point)
            Clip.epoint = Clip.spoint
            Clip.tpoint = Clip.spoint
            Clip.points.append(Clip.epoint)
            self.table_push_clip(Clip.epoint)
            Clip.closed = False
        else:
            Clip.proc = False
            Clip.epoint = tuple(point)
            self.add_clip()
            Clip.tpoint = Clip.epoint

    def draw_mode_set(self):
        self.radioButton_line.setChecked(True)
        self.radioButton_clip.setChecked(False)

    def draw_mode_change_line(self):
        if self.radioButton_line.isChecked():
            self.radioButton_clip.setChecked(False)
        else:
            self.radioButton_clip.setChecked(True)

    def draw_mode_change_clip(self):
        if self.radioButton_clip.isChecked():
            self.radioButton_line.setChecked(False)
        else:
            self.radioButton_line.setChecked(True)

    def draw_mode_change(self):
        if self.radioButton_clip.isChecked():
            self.radioButton_clip.setChecked(False)
            self.radioButton_line.setChecked(True)
        else:
            self.radioButton_clip.setChecked(True)
            self.radioButton_line.setChecked(False)
        
    def draw_clip(self, point_a, point_b, color):
        pass
        point = (round(point[0] + self.canvas_center[0]), round(self.canvas_center[1] - point[1]))
        self.canvas_update()

    def draw_line(self, point_a, point_b, color):
        point_a = (round(point_a[0] + self.canvas_center[0]), round(self.canvas_center[1] - point_a[1]))
        point_b = (round(point_b[0] + self.canvas_center[0]), round(self.canvas_center[1] - point_b[1]))
        line = self._draw_line(self.scene, point_a, point_b, color, 1)
        self.canvas_update()

        return line

    def _draw_line(self, scene, point_a, point_b, color, size):
        pen = QtGui.QPen(Qt.SolidLine)
        pen.setWidth(size)
        pen.setColor(QColor(color))
        line = scene.addLine(point_a[0], point_a[1], point_b[0], point_b[1], pen)
        
        return line

    def clipper_close(self):
        if len(Clip.points) < 3:
            ErrorInput("Количество вершин отсекателя должно быть больше двух.") 
        else:
            self.stack_update()
            if Clip.tpoint != Clip.spoint:
                Clip.items.append(self.draw_line(Clip.tpoint, Clip.spoint, self.clip_color))
            Clip.closed, Clip.proc = True, False
            Clip.spoint, Clip.epoint, Clip.tpoint  = None, None, None
            self.point.setVisible(False)
    
    def clipper_line(self):
        if len(Clip.points) < 3 or not Clip.closed:
            return ErrorInput("Необходимо задать и замкнуть отсекатель.")
        elif len(Line._list) < 1:
            return ErrorInput("Необходимо задать отрезки.")
        elif not check_convexity(Clip.points):
            return ErrorInput("Отсекатель должен быть выпуклым многоугольником.")
        elif polygon_area(Clip.points) < 1:
            return ErrorInput("Площадь отсекателя должна быть больше нуля.")
        else:
            self.stack_update()
            self.result_refresh()

        edges = poly_to_edges(Clip.points)
    
        for line in Line._list:
            new_line = CyrusBeckClipper((line[0], line[1]), (line[2], line[3]), edges)
            if new_line != None and len(new_line) == 2:
                Line._res_list.append(self._draw_line(self.scene, 
                               (new_line[0][0] + self.canvas_center[0], self.canvas_center[1] - new_line[0][1]),
                               (new_line[1][0] + self.canvas_center[0], self.canvas_center[1] - new_line[1][1]),
                               self.result_color, 1))
        self.clip_update()
        self.canvas_update()

    def show_info(self):
        self.sub_window = Info()
        self.sub_window.show()

    def color_init(self):
        self.bg_color = QColor(255, 255, 255)
        self.line_color = QColor(0, 0, 0)
        self.clip_color = QColor(255, 0, 0)
        self.result_color = QColor(0, 255, 0)

    def color_start_set(self):
        self.set_bg_color(self.bg_color)
        self.set_line_color(self.line_color)
        self.set_clip_color(self.clip_color)
        self.set_result_color(self.result_color)
    
    def set_color(self):
        color_dialog = QColorDialog()
        if color_dialog.exec_() == QDialog.Accepted:
            color = color_dialog.selectedColor()
            action = self.comboBox_color.currentIndex()
            self.stack_update()
            if action == 0:
                self.set_bg_color(color)
            elif action == 1:
                self.set_line_color(color)
            elif action == 2:
                self.set_clip_color(color)
            elif action == 3:
                self.set_result_color(color)
                
    def set_bg_color(self, color):
        self.bg_color = color
        brush = QtGui.QBrush(QtGui.QColor(color))
        self.graphicsView.setBackgroundBrush(brush)

    def set_line_color(self, color):
        self.line_color = color
        color = tuple(QColor.getRgb(color))
        self.label_lcolor.setStyleSheet("background-color: rgba{:};".format(str(color)))
    
    def set_clip_color(self, color):
        self.clip_color = color
        color = tuple(QColor.getRgb(color))
        self.label_ocolor.setStyleSheet("background-color: rgba{:};".format(str(color)))

    def set_result_color(self, color):
        self.result_color = color
        color = tuple(QColor.getRgb(color))
        self.label_rcolor.setStyleSheet("background-color: rgba{:};".format(str(color)))

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
        elif event.key() == Qt.Key_Plus or event.key() == Qt.Key_Equal:
            self.scale_plus()
        elif event.key() == Qt.Key_Minus:
            self.scale_minus()
        elif event.key() == Qt.Key_Escape:
            self.close_app()
        elif event.key() == Qt.Key_V:
            self.draw_mode_change()
        elif event.key() == Qt.Key_Q:
            self.canvas_clear()
        elif event.key() == Qt.Key_B:
            self.undo()
        elif event.key() == Qt.Key_C:
            self.set_color()
        elif event.key() == Qt.Key_X:
            currentIndex = self.comboBox_color.currentIndex()
            count = self.comboBox_color.count()
            nextIndex = (currentIndex + 1) % count
            self.comboBox_color.setCurrentIndex(nextIndex)

    def showEvent(self, event):
        self.color_start_set()
        self.draw_mode_set()
        self.canvas_scrollbar_refresh()

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
            if self.radioButton_line.isChecked():
                self.line.setLine(pos_scene.x(), pos_scene.y(), pos_scene.x(), pos_scene.y())
                self.line.setVisible(True)
                self.add_line_mouse(point)
            elif self.radioButton_clip.isChecked():
                self.point.setRect(pos_scene.x() - 1, pos_scene.y() - 1, 2, 2)
                self.point.setVisible(True)
                self.add_clip_mouse(point)
        elif event.button() == Qt.RightButton or event.button() == Qt.MiddleButton:
            self._last_mouse_pos = self.graphicsView.mapToScene(event.pos())
            
    def canvasMoveEvent(self, event):
        pos_scene = self.graphicsView.mapToScene(event.pos())
        if self.line.isVisible():
            self.line.setLine(self.line.line().x1(), self.line.line().y1(), pos_scene.x(), pos_scene.y())
        if event.buttons() == Qt.RightButton or event.buttons() == Qt.MiddleButton:
            x_diff = int((pos_scene.x() - self._last_mouse_pos.x()) * self.scale)
            y_diff = int((pos_scene.y() - self._last_mouse_pos.y()) * self.scale)

            x_val = self.graphicsView.horizontalScrollBar().value()
            y_val = self.graphicsView.verticalScrollBar().value()
            
            self.graphicsView.horizontalScrollBar().setValue(x_val - x_diff)
            self.graphicsView.verticalScrollBar().setValue(y_val - y_diff)

            self._last_mouse_pos =  self.graphicsView.mapToScene(event.pos())

    def canvasReleaseEvent(self, event):
        pos_scene = self.graphicsView.mapToScene(event.pos())
        point = [(round(pos_scene.x()) - (self.canvas_center[0])), 
                    -(round(pos_scene.y()) - (self.canvas_center[1]))]
        if event.button() == Qt.LeftButton:
            if self.radioButton_line.isChecked():
                self.line.setVisible(False)
                self.add_line_mouse(point)

    def close_app(self):
        buttonReply = QMessageBox.question(self, 'Завершение работы', 
                                           "Вы хотите завершить программу?", 
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            QtWidgets.QApplication.quit()

    def closeEvent(self, event):
        self.close_app()

    def dashline_init(self):
        pen = QtGui.QPen(Qt.DashLine)
        pen.setWidth(1)
        pen.setColor(Qt.lightGray)

        self.line = self.scene.addLine(0, 0, 0, 0, pen)
        self.line.setVisible(False)
    
    def dashrect_point(self):
        pen = QtGui.QPen(Qt.SolidLine)

        pen.setWidth(1)
        pen.setColor(Qt.magenta)
        brush = QtGui.QBrush(Qt.magenta)
        self.point = QGraphicsEllipseItem(0, 0, 0, 0)
        self.point.setPen(pen)
        self.point.setBrush(brush)
        self.scene.addItem(self.point)
        self.point.setVisible(False)

class Info(QWidget, Ui_TaskPopup):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.okBtn.clicked.connect(self.close)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            self.close()
