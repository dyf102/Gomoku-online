import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from view.gamelist_widget import GameListWidget
from controller.game_controller import GameController


app = QApplication(sys.argv)
game_controller = GameController()
widget = GameListWidget()
widget.show()
widget.game_controller.get_game_list_callback(data={'code': 200, 'list': [{'host_name': 'a', 'guest_name': 'b'}]})
sys.exit(app.exec_())
