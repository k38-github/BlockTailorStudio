import tkinter as tk


class MenuBar:
    def __init__(self, root, app):

        self.root = root
        self.app = app

        menubar = tk.Menu(root)

        # ===== File =====
        file_menu = tk.Menu(menubar, tearoff=0)

        file_menu.add_command(label="New Skin", command=app.new_skin)
        file_menu.add_command(label="Load Skin", command=app.load_skin)
        file_menu.add_command(label="Save Skin", command=app.save_skin)

        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)

        menubar.add_cascade(label="File", menu=file_menu)

        # ===== Edit =====
        edit_menu = tk.Menu(menubar, tearoff=0)

        edit_menu.add_command(label="Undo", command=app.skin_controller.undo)
        edit_menu.add_command(label="Redo", command=app.skin_controller.redo)

        menubar.add_cascade(label="Edit", menu=edit_menu)

        root.config(menu=menubar)
