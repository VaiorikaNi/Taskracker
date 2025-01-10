from PyQt5.QtWidgets import QApplication
from main_ui import TaskTracker

if __name__ == '__main__':
    app = QApplication([])
    tracker = TaskTracker()
    tracker.show()
    app.exec_()
