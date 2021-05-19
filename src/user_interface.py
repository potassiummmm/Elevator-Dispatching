from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDesktopWidget, QGraphicsView, \
    QGridLayout, QLabel, QLCDNumber, QMessageBox, \
    QPushButton, QWidget

from dispatch import Dispatcher

# 电梯门状态
OPEN = 0
CLOSE = 1

# 运行状态
STILL = 0
RUNNING_UP = 1
RUNNING_DOWN = 2

# 用户选择
GO_UP = 0
GO_DOWN = 1


class UI(QWidget):
    def __init__(self):
        super().__init__()
        self.dispatcher = Dispatcher(self)
        self.elev_enabled = [True] * 5  # 电梯状态（可使用/禁用）
        self.elev_state = [STILL] * 5  # 电梯运行状态（上/下/静止）
        self.elev_floor = [1] * 5  # 电梯所在的楼层
        self.door_state = [CLOSE] * 5  # 电梯门状态（开/关）
        self.door = []  # 电梯门状态显示
        self.floor_label = []  # 外电梯label
        self.up_button = []  # 外电梯上升按钮
        self.down_button = []  # 外电梯下降按钮
        self.label = []  # 电梯序号label
        self.led = []  # LED灯
        self.state = []  # 电梯状态显示器
        self.alarm_button = []  # 报警器
        self.grid_layout_widget = []  # 楼层按键
        self.grid_layout = []
        self.open_button = []  # 电梯门开关
        self.close_button = []
        self.init_ui()

    def init_ui(self):
        self.resize(1280, 720)
        self.center()

        # 电梯状态
        elev_pos = [30, 280, 530, 780, 1030]
        for i in range(5):
            self.door.append(QGraphicsView(self))
            self.door[i].setGeometry(elev_pos[i] + 5, 490, 120, 120)
            self.door[i].setStyleSheet("QGraphicsView{border-image: url(../resources/close.png)}")
            self.door[i].setObjectName("door" + str(i))

        # 电梯序号
        label_pos = [75, 325, 575, 835, 1075]
        for i in range(5):
            self.label.append(QLabel(str(i + 1) + '号电梯', self))
            self.label[i].setGeometry(label_pos[i], 600, 100, 100)
            self.label[i].setObjectName("label" + str(i))

        # 电梯楼层数码管
        led_pos = [50, 300, 550, 800, 1050]
        for i in range(5):
            self.led.append(QLCDNumber(self))
            self.led[i].setGeometry(led_pos[i] + 20, 440, 51, 41)
            self.led[i].setDigitCount(2)
            self.led[i].setProperty("value", 1.0)
            self.led[i].setObjectName("led" + str(i))

            self.state.append(QGraphicsView(self))
            self.state[i].setGeometry(led_pos[i] + 10, 350, 71, 61)
            self.state[i].setStyleSheet("QGraphicsView{border-image: url(../resources/state.png)}")
            self.state[i].setObjectName("stateshow" + str(i))

        # 报警器
        alarm_pos = [190, 440, 690, 940, 1190]
        for i in range(5):
            self.alarm_button.append(QPushButton(self))
            self.alarm_button[i].setGeometry(alarm_pos[i] + 12, 640, 50, 50)
            self.alarm_button[i].setObjectName("alarmButton" + str(i))
            self.alarm_button[i].setStyleSheet("QPushButton{border-image: url(../resources/alarm.png)}")
            self.alarm_button[i].clicked.connect(self.slot_warn_button)

        grid_pos = [190, 440, 690, 940, 1190]
        for i in range(5):
            self.grid_layout_widget.append(QWidget(self))
            self.grid_layout_widget[i].setGeometry(grid_pos[i], 140, 81, 451)
            self.grid_layout_widget[i].setObjectName(
                "grid_layout_widget" + str(i))
            self.grid_layout.append(QGridLayout(self.grid_layout_widget[i]))
            self.grid_layout[i].setObjectName("grid_layout" + str(i))

        # 电梯内按钮
        floor_name = ['19', '20', '17', '18', '15', '16', '13', '14', '11', '12', '9', '10',
                      '7', '8', '5', '6', '3', '4', '1', '2']
        positions = [(i, j) for i in range(10) for j in range(2)]
        for i in range(len(grid_pos)):
            for position, name in zip(positions, floor_name):
                button = QPushButton(name)
                button.setStyleSheet("border-radius: 11px")
                button.setObjectName("floorbutton " + str(i) + ' ' + name)
                button.clicked.connect(self.slot_internal_button)
                self.grid_layout[i].addWidget(button, *position)

        # 电梯外按钮
        for i in range(20):
            # 上行按钮
            self.up_button.append(QPushButton(self))
            self.up_button[i].setGeometry(80 + 120 * (i % 10), 60 if i < 10 else 120, 24, 24)
            self.up_button[i].setStyleSheet("QPushButton{border-image: url(../resources/up_normal.png)}"
                                        "QPushButton:hover{border-image: url(../resources/up_normal.png)}"
                                        "QPushButton:pressed{border-image: url(../resources/up_active.png)}")
            self.up_button[i].setObjectName("upbutton " + str(i))
            self.up_button[i].clicked.connect(self.slot_external_button)

            # 下行按钮
            self.down_button.append(QPushButton(self))
            self.down_button[i].setGeometry(110 + 120 * (i % 10), 60 if i < 10 else 120, 24, 24)
            self.down_button[i].setStyleSheet("QPushButton{border-image: url(../resources/down_normal.png)}"
                                          "QPushButton:hover{border-image: url(../resources/down_normal.png)}"
                                          "QPushButton:pressed{border-image: url(../resources/down_active.png)}")
            self.down_button[i].setObjectName("downbutton " + str(i))
            self.down_button[i].clicked.connect(self.slot_external_button)

            # 楼层
            self.floor_label.append(
                QLabel("0" + str(i + 1) if i < 9 else str(i + 1), self))
            self.floor_label[i].setGeometry(50 + 120 * (i % 10), 60 if i < 10 else 120, 24, 24)
            self.floor_label[i].setObjectName("label" + str(i))
            self.floor_label[i].setAlignment(Qt.AlignCenter)

        self.up_button[19].setEnabled(False)
        self.up_button[19].setVisible(False)
        self.down_button[0].setEnabled(False)
        self.down_button[0].setVisible(False)
        # 电梯门开关
        open_button_pos = [190, 440, 690, 940, 1190]
        close_button_pos = [240, 490, 740, 990, 1240]
        for i in range(5):
            self.open_button.append(QPushButton(self))
            self.open_button[i].setGeometry(open_button_pos[i] + 10, 590, 27, 27)
            self.open_button[i].setObjectName("openbutton" + str(i))
            self.open_button[i].setStyleSheet(
                "QPushButton{background: black;color:#fff;border-style: outset;border-radius: 11px}"
                "QPushButton:hover{background-color: #49afcd;border-color: #5599ff}"
                "QPushButton:pressed{border-radius:11px;background-color:red}"
            )
            self.open_button[i].setText("开")
            self.open_button[i].clicked.connect(self.slot_switch_button)
            self.close_button.append(QPushButton(self))
            self.close_button[i].setGeometry(close_button_pos[i] - 7, 590, 27, 27)
            self.close_button[i].setObjectName("closebutton" + str(i))
            self.close_button[i].setStyleSheet(
                "QPushButton{background: black;color:#fff;border-style: outset;border-radius: 11px}"
                "QPushButton:hover{background-color: #49afcd;border-color: #5599ff}"
                "QPushButton:pressed{border-radius: 11px;background-color:red}"
            )
            self.close_button[i].setText("关")
            self.close_button[i].clicked.connect(self.slot_switch_button)

    # 警报器
    def slot_warn_button(self):
        sender = self.sender()
        index = int(sender.objectName()[-1])
        QMessageBox.information(
            self.alarm_button[index], "警告!", "第" + str(index + 1) + "号电梯已损坏")
        self.dispatcher.warn_control(index)

    # 开关
    def slot_switch_button(self):
        sender = self.sender()
        index = int(sender.objectName()[-1])
        command = OPEN if sender.objectName()[0] == 'o' else CLOSE
        self.dispatcher.switch_door(index, command)

    # 电梯内按钮
    def slot_internal_button(self):
        sender = self.sender()
        indices = [int(s) for s in sender.objectName().split() if s.isdigit()]
        elev_index = indices[0]
        floor_index = indices[1]
        sender.setStyleSheet("border-radius: 11px;background-color:red")
        sender.setEnabled(False)
        self.dispatcher.internal_dispatch(elev_index, floor_index)

    # 电梯外按钮
    def slot_external_button(self):
        sender = self.sender()

        floor = [int(s) for s in sender.objectName().split() if s.isdigit()]
        floor = floor[0]
        button = sender.objectName()
        if button[0] == 'd':
            self.down_button[floor].setStyleSheet(
                "QPushButton{border-image: url(../resources/down_active.png)}")
            self.down_button[floor].setEnabled(False)
            choice = GO_DOWN
        else:
            self.up_button[floor].setStyleSheet(
                "QPushButton{border-image: url(../resources/up_active.png)}")
            self.up_button[floor].setEnabled(False)
            choice = GO_UP
        self.dispatcher.external_dispatch(floor + 1, choice)

    # 居中
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())