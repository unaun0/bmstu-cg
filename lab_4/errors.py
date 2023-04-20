from PyQt5.QtWidgets import QMessageBox


class ErrorInput(QMessageBox):
    def __init__(self, text: str):
        super().__init__(QMessageBox.Critical, "Ошибка", text)
        self.setStandardButtons(QMessageBox.Cancel)
        self.exec_()


