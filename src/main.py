import sys

from PyQt5.QtWidgets import QApplication

from user_interface import UI


def main():
    app = QApplication(sys.argv)
    ui = UI()
    ui.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()