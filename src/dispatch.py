import numpy as np
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QPushButton

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

INF = 9999


class Dispatcher(object):
    def __init__(self, elevator):
        self.elevator = elevator  # 绑定电梯对象
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)
        self.state = [RUNNING_UP] * 5
        # 消息队列
        self.messages_forward = [[] for _ in range(5)]
        self.messages_reverse = [[] for _ in range(5)]
        self.messages_other = [[] for _ in range(5)]

    def external_dispatch(self, floor, command):
        available_elevator = []
        for i in range(5):
            if self.elevator.elev_enabled[i]:
                available_elevator.append(i)

        dist = [INF] * 5
        for index in available_elevator:
            # 往上顺路
            if self.state[index] == RUNNING_UP and command == GO_UP and floor >= self.elevator.elev_floor[index]:
                dist[index] = floor - self.elevator.elev_floor[index] + 2 * len(
                    [x for x in self.messages_forward[index] if x < floor])

            # 往下顺路
            elif self.state[index] == RUNNING_DOWN and command == GO_DOWN and floor <= self.elevator.elev_floor[index]:
                dist[index] = self.elevator.elev_floor[index] - floor + 2 * len(
                    [x for x in self.messages_forward[index] if x > floor])

            # 电梯往上,用户往下
            elif self.state[index] == RUNNING_UP and command == GO_DOWN:
                max_floor = max(floor, self.elevator.elev_floor[index])
                max_floor = max(max_floor, max(self.messages_forward[index] if self.messages_forward[index] != [] else [0]))
                max_floor = max(max_floor,
                                max(self.messages_reverse[index] if self.messages_reverse[index] != [] else [0]))
                dist[index] = 2 * max_floor - floor - self.elevator.elev_floor[index]

                dist[index] += 2 * len(self.messages_forward[index]) + 2 * len(
                    [x for x in self.messages_reverse[index] if x > floor])

            # 电梯往下️,用户往上
            elif self.state[index] == RUNNING_DOWN and command == GO_UP:
                min_floor = min(floor, self.elevator.elev_floor[index])
                min_floor = min(min_floor, min(self.messages_forward[index] if self.messages_forward[index] != [] else [20]))
                min_floor = min(min_floor,
                                min(self.messages_reverse[index] if self.messages_reverse[index] != [] else [20]))
                dist[index] = floor + self.elevator.elev_floor[index] - 2 * min_floor

                dist[index] += 2 * len(self.messages_forward[index]) + 2 * len(
                    [x for x in self.messages_reverse[index] if x < floor])

            # 都往上,但不顺路
            elif self.state[index] == RUNNING_UP and command == GO_UP and floor < self.elevator.elev_floor[index]:
                max_floor = max(self.messages_forward[index]) if self.messages_forward[index] != [] else self.elevator.elev_floor[index]
                max_floor = max(max_floor,
                                max(self.messages_reverse[index] if self.messages_reverse[index] != [] else [0]))
                min_floor = min(self.messages_other[index]) if self.messages_other[index] != [] else floor
                min_floor = min(min_floor,
                                min(self.messages_reverse[index] if self.messages_reverse[index] != [] else [20]))
                dist[index] = 2 * max_floor - self.elevator.elev_floor[index] + floor - 2 * min_floor

                dist[index] += 2 * len(self.messages_forward[index]) + 2 * len(self.messages_reverse[index]) + 2 * len(
                    [x for x in self.messages_other[index] if x < floor])

            # 都往下,但不顺路
            elif self.state[index] == RUNNING_DOWN and command == GO_DOWN and floor > self.elevator.elev_floor[index]:
                min_floor = min(self.messages_forward[index]) if self.messages_forward[index] != [] else self.elevator.elev_floor[index]
                min_floor = min(min_floor,
                                min(self.messages_reverse[index] if self.messages_reverse[index] != [] else [20]))
                max_floor = max(self.messages_other[index]) if self.messages_other[index] != [] else floor
                max_floor = max(max_floor,
                                max(self.messages_reverse[index] if self.messages_reverse[index] != [] else [0]))
                dist[index] = 2 * max_floor - floor + self.elevator.elev_floor[index] - 2 * min_floor

                dist[index] += 2 * len(self.messages_forward[index]) + 2 * len(self.messages_reverse[index]) + 2 * len(
                    [x for x in self.messages_other[index] if x > floor])

        best = dist.index(min(dist))

        if dist[best] == 0:
            if self.elevator.door_state[best] != OPEN:
                self.elevator.door_state[best] = OPEN
                self.open_door(best)
            if command == GO_DOWN:
                outbutton = self.elevator.findChild(QPushButton,
                                                 "downbutton {}".format(floor - 1))
                outbutton.setStyleSheet("QPushButton{border-image: url(../resources/down_normal.png)}"
                                     "QPushButton:hover{border-image: url(../resources/down_normal.png)}"
                                     "QPushButton:pressed{border-image: url(../resources/down_active.png)}")
                outbutton.setEnabled(True)
            else:
                outbutton = self.elevator.findChild(QPushButton,
                                                 "upbutton {}".format(floor - 1))
                outbutton.setStyleSheet("QPushButton{border-image: url(../resources/up_normal.png)}"
                                     "QPushButton:hover{border-image: url(../resources/up_normal.png)}"
                                     "QPushButton:pressed{border-image: url(../resources/up_active.png)}")
                outbutton.setEnabled(True)

        else:
            if self.state[best] == RUNNING_UP and command == GO_UP and floor >= self.elevator.elev_floor[best]:
                self.messages_forward[best].append(floor)
                self.messages_forward[best] = list(set(self.messages_forward[best]))
                self.messages_forward[best].sort()
            elif self.state[best] == RUNNING_UP and command == GO_UP and floor < self.elevator.elev_floor[best]:
                self.messages_other[best].append(floor)
            elif self.state[best] == RUNNING_UP and command == GO_DOWN:
                self.messages_reverse[best].append(floor)
            elif self.state[best] == RUNNING_DOWN and command == GO_DOWN and floor <= self.elevator.elev_floor[best]:
                self.messages_forward[best].append(floor)
                self.messages_forward[best] = list(set(self.messages_forward[best]))
                self.messages_forward[best].sort()
                self.messages_forward[best].reverse()
            elif self.state[best] == RUNNING_DOWN and command == GO_DOWN and floor > self.elevator.elev_floor[best]:
                self.messages_other[best].append(floor)
            elif self.state[best] == RUNNING_DOWN and command == GO_UP:
                self.messages_reverse[best].append(floor)

    def internal_dispatch(self, elevator_index, target_floor):
        current_floor = self.elevator.elev_floor[elevator_index]

        if current_floor < target_floor:  # 当前层低于目标层
            if self.state[elevator_index] == RUNNING_UP:
                self.messages_forward[elevator_index].append(target_floor)
                self.messages_forward[elevator_index] = list(set(self.messages_forward[elevator_index]))
                self.messages_forward[elevator_index].sort()
            else:
                self.messages_reverse[elevator_index].append(target_floor)

        elif current_floor > target_floor:  # 当前层高于目标层
            if self.state[elevator_index] == RUNNING_UP:
                self.messages_reverse[elevator_index].append(target_floor)
            else:
                self.messages_forward[elevator_index].append(target_floor)
                self.messages_forward[elevator_index] = list(set(self.messages_forward[elevator_index]))
                self.messages_forward[elevator_index].sort()
                self.messages_forward[elevator_index].reverse()

        else:
            if self.elevator.elev_state[elevator_index] == STILL:
                if self.elevator.door_state[elevator_index] != OPEN:
                    self.elevator.door_state[elevator_index] = OPEN
                    self.open_door(elevator_index)

            floor_button = self.elevator.findChild(QPushButton,
                                                   "floorbutton {} {}".format(elevator_index, current_floor))
            floor_button.setStyleSheet("border-radius: 11px")
            floor_button.setEnabled(True)

    # 电梯状态更新
    def update(self):
        for i in range(len(self.messages_forward)):
            if not self.elevator.elev_enabled[i]:
                continue

            if len(self.messages_forward[i]) != 0:
                if self.elevator.elev_state[i] == STILL:
                    if self.elevator.door_state[i] != OPEN:
                        self.elevator.door_state[i] = OPEN
                        self.open_door(i)
                        self.elevator.state[i].setStyleSheet("QGraphicsView{border-image: url(../resources/state.png)}")

                    if self.elevator.elev_floor[i] < self.messages_forward[i][0]:
                        self.elevator.elev_state[i] = RUNNING_UP
                        if self.elevator.door_state[i] != CLOSE:
                            self.elevator.door_state[i] = CLOSE
                            self.close_door(i)

                    elif self.elevator.elev_floor[i] > self.messages_forward[i][0]:
                        self.elevator.elev_state[i] = RUNNING_DOWN
                        if self.elevator.door_state[i] != CLOSE:
                            self.elevator.door_state[i] = CLOSE
                            self.close_door(i)
                    else:
                        self.messages_forward[i].pop(0)
                        floor_button = self.elevator.findChild(QPushButton,
                                                               "floorbutton {} {}".format(i, self.elevator.elev_floor[i]))
                        floor_button.setStyleSheet("border-radius: 11px")
                        floor_button.setEnabled(True)

                        if self.state[i] == RUNNING_DOWN:
                            out_button = self.elevator.findChild(QPushButton,
                                                                 "downbutton {}".format(self.elevator.elev_floor[i] - 1))
                            out_button.setStyleSheet("QPushButton{border-image: url(../resources/down_normal.png)}"
                                                     "QPushButton:hover{border-image: url("
                                                     "../resources/down_normal.png)} "
                                                     "QPushButton:pressed{border-image: url("
                                                     "../resources/down_active.png)}")
                            out_button.setEnabled(True)
                        else:
                            out_button = self.elevator.findChild(QPushButton,
                                                                 "upbutton {}".format(self.elevator.elev_floor[i] - 1))
                            out_button.setStyleSheet("QPushButton{border-image: url(../resources/up_normal.png)}"
                                                     "QPushButton:hover{border-image: url(../resources/up_normal.png)}"
                                                     "QPushButton:pressed{border-image: url("
                                                     "../resources/up_active.png)}")
                            out_button.setEnabled(True)

                        if self.elevator.door_state[i] != OPEN:
                            self.elevator.door_state[i] = OPEN
                            self.open_door(i)
                else:
                    floor = self.messages_forward[i][0]
                    if self.elevator.elev_floor[i] < floor:  # 向上运动
                        self.elevator.elev_state[i] = RUNNING_UP
                        self.elevator.elev_floor[i] += 1
                        self.elevator.led[i].setProperty("value", self.elevator.elev_floor[i])
                        self.elevator.state[i].setStyleSheet(
                            "QGraphicsView{border-image: url(../resources/state_up.png)}")

                    elif self.elevator.elev_floor[i] > floor:  # 向下运动
                        self.elevator.elev_state[i] = RUNNING_DOWN
                        self.elevator.elev_floor[i] -= 1
                        self.elevator.led[i].setProperty("value", self.elevator.elev_floor[i])
                        self.elevator.state[i].setStyleSheet(
                            "QGraphicsView{border-image: url(../resources/state_down.png)}")

                    else:  # 电梯到目的地
                        self.open_door(i)
                        self.elevator.door_state[i] = OPEN
                        self.elevator.elev_state[i] = STILL
                        self.messages_forward[i].pop(0)

                        self.elevator.state[i].setStyleSheet("QGraphicsView{border-image: url(../resources/state.png)}")

                        floor_button = self.elevator.findChild(QPushButton,
                                                               "floorbutton {} {}".format(i, self.elevator.elev_floor[i]))
                        floor_button.setStyleSheet("border-radius: 11px")
                        floor_button.setEnabled(True)

                        if self.state[i] == RUNNING_DOWN:
                            out_button = self.elevator.findChild(QPushButton,
                                                                 "downbutton {}".format(self.elevator.elev_floor[i] - 1))
                            out_button.setStyleSheet("QPushButton{border-image: url(../resources/down_normal.png)}"
                                                     "QPushButton:hover{border-image: url("
                                                     "../resources/down_normal.png)} "
                                                     "QPushButton:pressed{border-image: url("
                                                     "../resources/down_active.png)}")
                            out_button.setEnabled(True)
                        else:
                            out_button = self.elevator.findChild(QPushButton,
                                                                 "upbutton {}".format(self.elevator.elev_floor[i] - 1))
                            out_button.setStyleSheet("QPushButton{border-image: url(../resources/up_normal.png)}"
                                                     "QPushButton:hover{border-image: url(../resources/up_normal.png)}"
                                                     "QPushButton:pressed{border-image: url("
                                                     "../resources/up_active.png)}")
                            out_button.setEnabled(True)

            elif len(self.messages_reverse[i]):

                if self.state[i] == RUNNING_UP and self.elevator.elev_floor[i] < max(self.messages_reverse[i]):
                    self.messages_forward[i].append(max(self.messages_reverse[i]))
                elif self.state[i] == RUNNING_DOWN and self.elevator.elev_floor[i] > min(self.messages_reverse[i]):
                    self.messages_forward[i].append(min(self.messages_reverse[i]))

                else:
                    # 换方向
                    self.state[i] = RUNNING_DOWN if self.state[i] == RUNNING_UP else RUNNING_UP
                    self.messages_forward[i] = self.messages_reverse[i].copy()
                    self.messages_reverse[i].clear()
                    self.messages_reverse[i] = self.messages_other[i].copy()
                    self.messages_other[i].clear()

                    self.messages_forward[i] = list(set(self.messages_forward[i]))
                    self.messages_forward[i].sort()
                    if self.state[i] == RUNNING_DOWN:
                        self.messages_forward[i].reverse()

            elif len(self.messages_other[i]):
                if self.state[i] == RUNNING_UP:
                    self.messages_reverse[i].append(min(self.messages_other[i]))
                else:
                    self.messages_reverse[i].append(max(self.messages_other[i]))

            else:
                if self.elevator.door_state[i] != CLOSE:
                    self.close_door(i)
                    self.elevator.door_state[i] = CLOSE

    def warn_control(self, index):
        self.elevator.elev_enabled[index] = False  # 禁用电梯
        self.elevator.led[index].setEnabled(False)  # 禁用LED显示灯
        self.elevator.alarm_button[index].setEnabled(False)  # 禁用报警器
        self.elevator.grid_layout_widget[index].setEnabled(False)  # 禁用楼层按键
        self.elevator.open_button[index].setEnabled(False)  # 禁用开门键
        self.elevator.close_button[index].setEnabled(False)  # 禁用关门键
        self.elevator.state[index].setEnabled(False)  # 禁言状态显示

        self.messages_forward[index].clear()
        self.messages_reverse[index].clear()
        self.messages_other[index].clear()

        for i in range(20):
            floor_button = self.elevator.findChild(QPushButton,
                                                   "floorbutton {} {}".format(index, i + 1))
            floor_button.setStyleSheet("border-radius: 11px")
        self.break_down(index)

        if (np.array(self.elevator.elev_enabled) == False).all():
            for i in range(20):
                self.elevator.up_button[i].setEnabled(False)
                self.elevator.down_button[i].setEnabled(False)

    def switch_door(self, index, command):
        if command == OPEN:
            # 如果门是关着的且电梯是静止的
            if self.elevator.door_state[index] == CLOSE and self.elevator.elev_state[index] == STILL:
                self.elevator.door_state[index] = OPEN  # 设置门的状态为开
                self.open_door(index)
        else:
            if self.elevator.door_state[index] == OPEN and self.elevator.elev_state[index] == STILL:
                self.elevator.door_state[index] = CLOSE  # 设置门的状态为关
                self.close_door(index)

    def open_door(self, index):
        self.elevator.door[index].setStyleSheet("QGraphicsView{border-image: url(../resources/open.png)}")

    def close_door(self, index):
        self.elevator.door[index].setStyleSheet("QGraphicsView{border-image: url(../resources/close.png)}")

    def break_down(self, index):
        self.elevator.door[index].setStyleSheet("QGraphicsView{border-image: url(../resources/broken.png)}")
