from PyQt5.QtCore import QPropertyAnimation, QRect, Qt, QCoreApplication
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QDesktopWidget, QGraphicsView, \
    QGridLayout, QLabel, QLCDNumber, QMessageBox, \
    QPushButton, QWidget
from dispatch import Dispatcher

BROKEN = -1
CLOSE = 0
OPEN = 1

STILL = 0
UP = 1
DOWN = 2


class ExternalPanel(QWidget):
    def __init__(self, label):
        super().__init__()
        self.up_button = QPushButton(self)
        self.down_button = QPushButton(self)
        self.label = label
    def init_ui(self, label):
        self.up_button.setGeometry(230 + 90 * (i % 10), 60 if i < 10 else 90, 24, 24)
        self.up_button.setStyleSheet("QPushButton{border-image: url(../resources/up.png)}"
                                        "QPushButton:hover{border-image: url(../resources/up_hover.png)}"
                                        "QPushButton:pressed{border-image: url(../resources/up_pressed.png)}")
        self.up_button.clicked.connect(self.outClick)


class Elevator(QWidget):
    def __init__(self):
        super().__init__()
        self.x_coord = 0
        self.y_coord = 0
        self.alarm_button = None
        self.up_button = None
        self.down_button = None
        self.label = None

    def init_ui(self):
        pass

    def set_position(self, x, y):
        self.x_coord = x
        self.y_coord = y


class UI(QWidget):
    def __init__(self):
        super().__init__()
        self.elevators = [Elevator()] * 5
        self.dispatcher = Dispatcher(self)
        self.elevator_state = [CLOSE] * 5
        self.elevator_action = [STILL] * 5
        self.internal_up_button = []
        self.internal_down_button = []
        self.external_up_button = []
        self.external_down_button = []
        self.alarm_button = []