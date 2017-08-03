from PyQt4.QtGui import *
from PyQt4.QtCore import *


class GameControlWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.layout = QVBoxLayout(self)
        self.undo_button = QPushButton('Undo', parent)
        self.giveup_button = QPushButton('Give up', parent)
        self.escape_button = QPushButton('Escape', parent)
        self.layout.addWidget(self.undo_button)
        self.layout.addWidget(self.giveup_button)
        self.layout.addWidget(self.escape_button)