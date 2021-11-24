from network_control import NetworkControl
from game_lobby_ui import GameLobbyUI
from game_main import GameMain


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    network_control = NetworkControl()
    network_control.start()

    while True:
        game_lobby_ui = GameLobbyUI()
        game_lobby_ui.set_network_control_handler(network_control)
        network_control.set_game_lobby_ui_handler(game_lobby_ui)
        game_lobby_ui.run()

        # if True:
        #     main = GameMain(network_control)
        #     main.run()

