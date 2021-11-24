import tkinter as tk
from tkinter import messagebox

from game_main import GameMain


class GameLobbyUI:
    def __init__(self):
        # Class Variable Init
        self.network_control_handler = None
        self.game_list = []
        self.id = ""

        self.game_start_signal = False

        # UI Component Init
        self.root = tk.Tk()
        self.root.title("Real-time Chess Client Program")

        self.root.geometry("340x480")
        self.root.resizable(width=False, height=False)

        self.main_frame = tk.Frame(self.root, width=100)
        self.main_frame.grid(row=0, column=0)

        self.top_label = tk.Label(self.main_frame, text="")
        self.top_label.grid(row=0, column=0)

        self.user_id_frame = tk.Frame(self.main_frame)
        self.user_id_frame.grid(row=1, column=0, sticky="e", padx=5)

        self.user_id_label = tk.Label(self.user_id_frame, text="USER ID: ")
        self.user_id_label.grid(row=0, column=0, sticky="e")

        self.user_id_var = tk.StringVar()
        self.user_id_entry = tk.Entry(self.user_id_frame, textvariable=self.user_id_var)
        self.user_id_entry.grid(row=0, column=1, sticky="e")

        self.game_list_frame = tk.Frame(self.main_frame)
        self.game_list_frame.grid(row=2, column=0, padx=(10, 10))

        self.game_list_listbox = tk.Listbox(self.game_list_frame, height=14, width=33, font=('Times', 14))
        self.game_list_listbox.grid(row=0, column=0, pady=20)

        self.game_list_scrollbar = tk.Scrollbar(self.game_list_frame, orient="vertical")
        self.game_list_scrollbar.config(command=self.game_list_listbox.yview)
        self.game_list_scrollbar.grid(row=0, column=1, pady=20, sticky='ns')

        self.game_list_listbox.config(yscrollcommand=self.game_list_scrollbar.set)

        self.buttons_frame = tk.Frame(self.main_frame)
        self.buttons_frame.grid(row=4, column=0, sticky='nsew')

        self.host_button = tk.Button(self.buttons_frame, text="Create Game", command=self.host_button, height=2, width=15)
        self.host_button.grid(row=0, column=0, sticky='nsew', padx=5)

        self.client_button = tk.Button(self.buttons_frame, text="Join Game", command=self.client_button, height=2, width=15)
        self.client_button.grid(row=0, column=1, sticky='nsew', padx=5)

        self.refresh_button = tk.Button(self.buttons_frame, text="\u21BA", command=self.refresh_game_list, height=2, font=('Times', 14))
        self.refresh_button.grid(row=0, column=2, sticky='nsew', padx=5)

        self.buttons_frame.grid_columnconfigure(0, weight=2)
        self.buttons_frame.grid_columnconfigure(1, weight=2)
        self.buttons_frame.grid_columnconfigure(2, weight=1)

        self.bottom_label = tk.Label(self.main_frame, text="")
        self.bottom_label.grid(row=5, column=0)

        self.root.pack_propagate(0)

    def set_network_control_handler(self, n_c):
        self.network_control_handler = n_c
        self.id = self.network_control_handler.my_id
        self.user_id_var.set(self.id)

    def block_ui(self, exception=None):
        self.game_list_listbox.config(self.game_list_listbox.config(bg='light grey', state='disabled'))
        self.host_button.config(state='disabled')
        self.client_button.config(state='disabled')
        self.user_id_entry.config(state='disabled')
        self.refresh_button.config(state='disabled')
        if exception is not None:
            temp = exception['text']
            exception.config(text=temp+"...", relief=tk.SUNKEN, state='normal')

    def unblock_ui(self, exception=None):
        self.game_list_listbox.config(self.game_list_listbox.config(bg='white', state='normal'))
        self.host_button.config(state='normal')
        self.client_button.config(state='normal')
        self.user_id_entry.config(state='normal')
        self.refresh_button.config(state='normal')
        if exception is not None:
            temp = exception['text']
            temp = temp.removesuffix("...")
            exception.config(text=temp, relief=tk.RAISED)

    def host_button(self):
        self.update_user_id()
        if self.host_button['relief'] != tk.SUNKEN:
            self.network_control_handler.new_request_message("start_host")
            self.block_ui(self.host_button)
        else:
            self.network_control_handler.new_request_message("cancel_host")
            self.unblock_ui(self.host_button)

    def client_button(self):
        self.update_user_id()
        if self.client_button['relief'] != tk.SUNKEN:
            selected_host = self.game_list_listbox.curselection()
            if len(selected_host) <= 0:
                tk.messagebox.showerror(title="Need to select a valid game host", message="No game host was selected.\n\n"
                                                                   "Please select a valid game host and try again.")
            else:
                self.network_control_handler.new_request_message("start_client", self.game_list_listbox.get(selected_host[0]))
                self.network_control_handler.opponent_id = self.game_list_listbox.get(selected_host[0])
                self.block_ui(self.client_button)
        else:
            self.unblock_ui(self.client_button)

    def refresh_game_list(self):
        self.network_control_handler.new_request_message("fetch_available_hosts")

    def update_game_list(self, games):
        for each in self.game_list:
            if each not in games:
                index_number = self.game_list_listbox.get(0, tk.END).index(each)
                self.game_list_listbox.delete(index_number)
        for each in games:
            if each not in self.game_list:
                self.game_list_listbox.insert(tk.END, each)
        self.game_list = games

    def update_user_id(self):
        new_id = self.user_id_entry.get()
        if new_id != self.id:
            print("ID CHANGED: ", new_id)
        self.network_control_handler.update_user_id(new_id)
        self.id = new_id

    def start_game(self):
        self.game_start_signal = True
        self.root.quit()

    def run(self):
        self.refresh_game_list()
        self.root.mainloop()

        if self.game_start_signal:
            game_main = GameMain(self.network_control_handler)
            game_main.run()

        self.root.destroy()

