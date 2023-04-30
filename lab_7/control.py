from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QColor, QPixmap, QPainter
from PyQt5.QtWidgets import QWidget, QGraphicsView, QMessageBox, QColorDialog, QDialog
from PyQt5.QtCore import Qt

from main_window import Ui_MainWindow
from task_popup import Ui_TaskPopup
from errors import ErrorInput

from math import ceil, floor

class Line:
    spoint = None
    epoint = None
    _list = []
    proc = False

class Clip:
    spoint = None
    epoint = None
    proc = False

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
        self.radioButton_clip.toggled.connect(self.draw_mode_change_clip)
        self.radioButton_line.toggled.connect(self.draw_mode_change_line)
        self.actionExit.triggered.connect(self.closeEvent) # close app
        self.actionAuthors.triggered.connect(self.show_info) #  info about app

    def bindButtons(self):
        self.pushButton_ladd.clicked.connect(self.action_add_line)
        self.pushButton_oadd.clicked.connect(self.action_add_clip)
        self.pushButton_color.clicked.connect(self.set_color)  # set new color
        self.pushButton_clear.clicked.connect(self.canvas_clear) # clear
        self.pushButton_back.clicked.connect(self.undo) # back

    def stack_init(self):
        self.state_stack = []
        self.stack_size = 10
    
    def stack_update(self):
        pixmap_copy = self.pixmap.copy()
        pixmap_sub_copy = self.pixmap_sub.copy()
        self.state_stack.append([pixmap_copy.copy(),
                                 pixmap_sub_copy.copy(),
                                 [Line.spoint, Line.epoint, Line._list.copy(), Line.proc],
                                 [Clip.spoint, Clip.epoint, Clip.proc],
                                 self.bg_color,
                                 self.line_color, 
                                 self.clip_color,
                                 self.result_color])
        if len(self.state_stack) > self.stack_size:
            self.state_stack.pop(0)
    
    def undo(self):
        index = (len(self.state_stack) - 1)
        if index < 0:
            ErrorInput("Невозможно отменить действие.")
        else:
            self.pixmap = self.state_stack[index][0]
            self.pixmap_sub = self.state_stack[index][1]

            line_data = self.state_stack[index][2]

            Line.spoint = line_data[0]
            Line.epoint = line_data[1]
            Line._list = line_data[2].copy()
            Line.proc = line_data[3]

            self.tableWidget_points.clearContents()
            self.tableWidget_points.setRowCount(0)
            for line in Line._list:
                self.table_push_line(line[0], line[1])

            clip_data = self.state_stack[index][3]

            Clip.spoint = clip_data[0]
            Clip.epoint = clip_data[1]
            Clip.proc = clip_data[2]

            if Clip.spoint != None and Clip.epoint != None:
                self.clip_push(Clip.spoint, Clip.epoint)
            else:
                self.clip_push(("", ""), ("", ""))

            self.bg_color = self.state_stack[index][4]
            self.line_color = self.state_stack[index][5]
            self.clip_color = self.state_stack[index][6]
            self.result_color = self.state_stack[index][7]

            self.color_start_set()

            self.state_stack.pop(index)
            self.canvas_update()

    def canvas_init(self):
        self.scene = QtWidgets.QGraphicsScene(self)
        self.graphicsView.setScene(self.scene)
        self.graphicsView.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.canvas_size = (5002, 5002)
        self.view_size = (self.graphicsView.width(), self.graphicsView.height())
        self.canvas_center = (self.canvas_size[0] / 2, self.canvas_size[1] / 2)

        self.pixmap = QPixmap(5002, 5002)
        self.pixmap.fill(Qt.transparent)

        self.pixmap_sub = QPixmap(5002, 5002)
        self.pixmap_sub.fill(Qt.transparent)

        self.scene.addPixmap(self.pixmap)
        self.scene.addPixmap(self.pixmap_sub)

        self.scale = 1

        self.graphicsView.mousePressEvent = self.pointSelectEvent
        self.graphicsView.mouseMoveEvent = self.canvasMoveEvent
        self.graphicsView.wheelEvent = self.zoomWheelEvent

        self.isRubberBandOn = False

        self.stack_update()
    
    def canvas_scrollbar_refresh(self):
        self.graphicsView.horizontalScrollBar().setValue(int(self.canvas_center[0] - (self.view_size[0] // 2)))
        self.graphicsView.verticalScrollBar().setValue(int(self.canvas_center[1] - (self.view_size[1] // 2)))

    def canvas_update(self):
        self.scene.clear()
        self.scene.addPixmap(self.pixmap)
        self.scene.addPixmap(self.pixmap_sub)
        self.scene.update()

    def canvas_clear(self):
        self.stack_update()

        self.canvas_size = (5002, 5002)
        self.view_size = (self.graphicsView.width(), self.graphicsView.height())
        self.canvas_center = (self.canvas_size[0] / 2, self.canvas_size[1] / 2)

        self.scene.clear()

        self.pixmap = QPixmap(5002, 5002)
        self.pixmap.fill(Qt.transparent)

        self.pixmap_sub = QPixmap(5002, 5002)
        self.pixmap_sub.fill(Qt.transparent)

        self.scene.addPixmap(self.pixmap)
        self.scene.addPixmap(self.pixmap_sub)
        self.graphicsView.resetTransform()

        self.canvas_update()
        self.canvas_scrollbar_refresh()

        self.tableWidget_points.clearContents()
        self.tableWidget_points.setRowCount(0)
        self.clip_push(("", ""), ("", ""))

        self.scale = 1
        
        Line.spoint = None
        Line.epoint = None
        Line._list = []
        Line.proc = False

        Clip.spoint = None
        Clip.epoint = None
        Clip.proc = False
        
        self.color_init()
        self.color_start_set()

    def table_push_line(self, point_a, point_b):
        last_index_row = self.tableWidget_points.rowCount()
        self.tableWidget_points.insertRow(last_index_row)
        self.tableWidget_points.setItem(last_index_row, 0, QtWidgets.QTableWidgetItem("{:10}".format(point_a[0])))
        self.tableWidget_points.setItem(last_index_row, 1, QtWidgets.QTableWidgetItem("{:10}".format(point_a[1])))
        self.tableWidget_points.setItem(last_index_row, 2, QtWidgets.QTableWidgetItem("{:10}".format(point_b[0])))
        self.tableWidget_points.setItem(last_index_row, 3, QtWidgets.QTableWidgetItem("{:10}".format(point_b[1])))

    def clip_push(self, point_a, point_b):
        self.lineEdit_xn.setText(str(point_a[0]))
        self.lineEdit_yn.setText(str(point_a[1]))
        self.lineEdit_xok.setText(str(point_b[0]))
        self.lineEdit_yok.setText(str(point_b[1]))

    def table_fill(self):
        pass
        '''
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
        '''
    
    def action_add_line(self):
        Line.proc = False
        Line.spoint = (self.spinBox_xs.value(), self.spinBox_ys.value())
        Line.epoint = (self.spinBox_xe.value(), self.spinBox_ye.value())
        self.add_line()
    
    def action_add_clip(self):
        Clip.proc = False
        Clip.spoint = (self.spinBox_xos.value(), self.spinBox_yos.value())
        Clip.epoint = (self.spinBox_xoe.value(), self.spinBox_yoe.value())
        self.add_clip()
    
    def clip_refresh(self):
        self.pixmap_sub = QPixmap(5002, 5002)
        self.pixmap_sub.fill(Qt.transparent)
        self.scene.addPixmap(self.pixmap)

    def add_clip(self):
        if (abs(Clip.epoint[0] - Clip.spoint[0]) < 2) or (abs(Clip.epoint[1] - Clip.spoint[1]) < 2):
            ErrorInput("Площадь отсекателя должна быть больше нуля.")
        else:
            self.stack_update()
            if Clip.spoint and Clip.epoint:
                self.clip_refresh()
            self.draw_clip(Clip.spoint, Clip.epoint, self.clip_color)
            self.clip_push(Clip.spoint, Clip.epoint)

    def add_line(self):
        if Line.epoint == Line.spoint:
            ErrorInput("Длина отрезка должна быть больше нуля.")
        else:
            self.stack_update()
            Line._list.append((Line.spoint, Line.epoint))
            self.draw_line(Line.spoint, Line.epoint, self.line_color)
            self.table_push_line(Line.spoint, Line.epoint)

    def add_line_mouse(self, point):
        if not Line.proc:
            Clip.proc = False
            Line.proc = True
            Line.spoint = tuple(point)
        else:
            Line.proc = False
            Line.epoint = tuple(point)
            self.add_line()

    def add_clip_mouse(self, point):
        if not Clip.proc:
            Line.proc = False
            Clip.proc = True
            Clip.spoint = tuple(point)
        else:
            Clip.proc = False
            Clip.epoint = tuple(point)
            self.add_clip()

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

    def vert_clip(self, point_a, point_b):
        x1, y1 = point_a
        x2, y2 = point_b
        
        point = (min(x1, x2), max(y1, y2))
        w, h = round(max(x1, x2) - min(x1, x2)), round(max(y1, y2) - min(y1, y2))

        return point, w, h
        
    def draw_clip(self, point_a, point_b, color):
        point, width, height = self.vert_clip(point_a, point_b)
        point = (round(point[0] + self.canvas_center[0]), round(self.canvas_center[1] - point[1]))
        self._draw_rect(self.pixmap_sub, point, width, height, color)
        self.canvas_update()

    def draw_line(self, point_a, point_b, color):
        point_a = (round(point_a[0] + self.canvas_center[0]), round(self.canvas_center[1] - point_a[1]))
        point_b = (round(point_b[0] + self.canvas_center[0]), round(self.canvas_center[1] - point_b[1]))
        self._draw_line(self.pixmap, point_a, point_b, color)
        self.canvas_update()

    def _draw_rect(self, pixmap, point, width, height, color):
        painter = QPainter(pixmap)
        painter.setPen(QColor(color))
        painter.drawRect(point[0], point[1], width, height)
        painter.end()

    def _draw_point(self, pixmap, point, color):
        painter = QPainter(pixmap)
        painter.setPen(QColor(color))
        painter.drawPoint(round(point[0]), round(point[1]))
        painter.end()

    def _draw_line(self, pixmap, point_a, point_b, color):
        painter = QPainter(pixmap)
        painter.setPen(QColor(color))   
        painter.drawLine(round(point_a[0]), round(point_a[1]), round(point_b[0]), round(point_b[1]))
        painter.end()
    
    def draw_point(self, point, color):
        point = (round(point[0] + self.canvas_center[0]), round(self.canvas_center[1] - point[1]))
        self._draw_point(point, color)
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
        elif event.key() == Qt.Key_C:
            self.draw_mode_change()
        '''
         elif event.key() == Qt.Key_Q:
            self.canvas_c()
        elif event.key() == Qt.Key_B:
            self.undo()
        elif event.key() == Qt.Key_C:
            self.set_color()
        elif event.key() == Qt.Key_V:
            currentIndex = self.comboBox_color.currentIndex()
            count = self.comboBox_color.count()
            nextIndex = (currentIndex + 1) % count
            self.comboBox_color.setCurrentIndex(nextIndex)
        '''
   
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
                self.add_line_mouse(point)
            elif self.radioButton_clip.isChecked():
                self.add_clip_mouse(point)
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
