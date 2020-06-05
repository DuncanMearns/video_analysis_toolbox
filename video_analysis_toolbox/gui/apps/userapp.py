from PyQt5 import QtWidgets, QtCore


class UserApplicationWindow(QtWidgets.QMainWindow):

    exit_signal = QtCore.pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set central widget
        self.setCentralWidget(QtWidgets.QWidget())
        self.centralWidget().setLayout(QtWidgets.QVBoxLayout())
        self.statusBar().showMessage('')
        # Buttons widget
        self.exit_flag = 0
        self.exit_signal.connect(self.close_window)
        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_widget.setLayout(QtWidgets.QHBoxLayout())
        self.buttons_widget.layout().setAlignment(QtCore.Qt.AlignLeft)
        self.buttons = {}
        self.add_button("Confirm", 1)
        self.add_button("Cancel", 0)
        self.add_button("Quit", -1)
        self.centralWidget().layout().addWidget(self.buttons_widget)

    def add_button(self, name: str, exit_flag: int):
        self.buttons[name] = QtWidgets.QPushButton(name)
        self.buttons[name].setFixedWidth(100)
        self.buttons[name].clicked.connect(lambda x: self.exit_signal.emit(exit_flag))
        self.buttons_widget.layout().addWidget(self.buttons[name])

    @property
    def output(self):
        return

    @QtCore.pyqtSlot(int)
    def close_window(self, i):
        self.exit_flag = i
        self.close()

    @classmethod
    def start(cls, *args, **kwargs) -> tuple:
        """Static method for running the app.

        Returns
        -------
        tuple:
            retval, selected videos, thresholds
        """
        app = QtWidgets.QApplication([])
        window = cls(*args, **kwargs)
        window.show()
        app.exec_()
        exit_flag = window.exit_flag
        output = window.output
        return exit_flag, output
