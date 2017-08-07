# -*- encoding:utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from controller.chat_controller import ChatController
from controller.user_controller import UserController


class ChatWidget(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.input_box = ChatInput(self)
        self.chat_view = ChatView(self)
        # print(self.geometry())
        # self.chat_view.setGeometry(520, 10, 260, 250)
        # self.input_box.setGeometry(520, 260, 260, 40)
        self.chat_controller = ChatController()
        self.user_controller = UserController()
        self.cid = parent.rid  # room id
        uid = self.user_controller.current_user_id
        if uid:
            self.chat_controller.add_polling_msg_task(self.cid, uid)

    def send_text(self, txt):
        uid = self.user_controller.current_user_id
        username = self.user_controller.current_username
        self.chat_controller.send_msg(cid=self.cid, uid=uid, msg=unicode(txt), username=username)


class ChatInput(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.textEdit = QLineEdit(self)
        self.textEdit.setFocusPolicy(Qt.ClickFocus)
        self.sendBtn = QPushButton(self)
        self.sendBtn.setText(u'send')
        self.sendBtn.clicked.connect(self.send_text)
        self.sendBtn.setFocusPolicy(Qt.ClickFocus)
        self.hbox = QHBoxLayout(self)
        self.hbox.addWidget(self.textEdit)
        self.hbox.addWidget(self.sendBtn)
        # self.hbox.addStretch(1)

    def send_text(self):
        self.parent().send_text(str(self.textEdit.text()))
        self.textEdit.clear()


class ChatView(QListView):
    def __init__(self, parent=None):
        QListView.__init__(self, parent)

        self.model = QStandardItemModel()
        self.setModel(self.model)
        self.setWordWrap(True)
        self.setUniformItemSizes(True)
        self.setGridSize(QSize(self.rect().width(), 30))
        self.setFont(QFont("Microsoft YaHei", 10))
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setAcceptDrops(True)
        # self.updateLayout()

    def showText(self, text, r=0, g=0, b=0):
        color = QBrush(QColor(r, g, b))
        item = QStandardItem(text)
        item.setTextAlignment(Qt.AlignLeft)
        # item.setFont(QFont(50))
        item.setForeground(color)
        self.model.appendRow(item)
        self.scrollTo(self.model.indexFromItem(item),
                      QAbstractItemView.PositionAtCenter)

    def clear(self):
        self.model.clear()

