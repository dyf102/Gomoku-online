from PyQt4.QtGui import *
from PyQt4.QtCore import *
from controller.user_controller import UserController


class RankList(QListView):
    def __init__(self, parent=None):
        QListView.__init__(self, parent)
        self.setStyleSheet(
            '''
            border-image: url(:btn_bg);
            background-repeat: no-repeat;
            ''')

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

        self.connect(UserController(), SIGNAL("add_rank_item(QString, int)"), self.add_rank_item)
        self.connect(UserController(), SIGNAL("clear"), self.clear)

    def add_rank_item(self, username, point):
        text = unicode(username) + ': ' + str(point)
        item = QStandardItem(text)
        item.setTextAlignment(Qt.AlignCenter)
        self.model.appendRow(item)

    def clear(self):
        self.model.clear()

    '''
        def refresh(self):
        self.model.clear()
        rank = 0
        for user in [{'uid': 123, 'point': 12}]:
            if 'uid' in user and 'point' in user:
                text = user['uid'] + ' : ' + str(user['point'])
                item = QStandardItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                item.setFont(QFont(50))
                if rank == 0:
                    item.setForeground(QBrush(QColor(255, 0, 0)))
                if rank == 1:
                    item.setForeground(QBrush(QColor(200, 0, 0)))
                if rank == 2:
                    item.setForeground(QBrush(QColor(150, 0, 0)))
                self.model.appendRow(item)
                rank += 1
    '''

