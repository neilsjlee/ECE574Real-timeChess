from network_control import NetworkControl
from game_lobby_ui import GameLobbyUI


if __name__ == '__main__':

    # This main.py file is the start point of the client program.
    # Please run this code if you want to start the client program.
    #       (e.g. python3 main.py)
    # (If you want to start the server program, please run "server.py" file.

    # Instantiates NetworkControl class and makes it start
    network_control = NetworkControl()
    network_control.start()

    # Instantiates GameLobbyUI class
    game_lobby_ui = GameLobbyUI()
    game_lobby_ui.set_network_control_handler(network_control)  # Passes the NetworkControl class's handler to GameLobbyUI class.
    network_control.set_game_lobby_ui_handler(game_lobby_ui)    # Passes the GameLobbyUI class's handler to NetworkControl class.
    game_lobby_ui.run()                                         # Starts the GameLobbyUI class

