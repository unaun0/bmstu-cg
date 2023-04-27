import sys
from PyQt5.QtWidgets import QApplication
from control import MainWindow        

def my_function(window):
    window.update_signal.emit("New text for label")

def main():
    app = QApplication(sys.argv)
    window = MainWindow() 
    window.show()
    app.exec_()

if __name__ == '__main__': 
    main()