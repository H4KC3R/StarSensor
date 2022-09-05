import tkinter.ttk as ttk
from tkinter import *


def create_execution_window(root):
    progress_window = Toplevel(root)
    progress_window.grab_set()
    progress_window.resizable(False, False)
    window_width = 850
    window_height = 300
    progress_window.geometry(f'{window_width}x{window_height}')
    progress_window.protocol("WM_DELETE_WINDOW", root.destroy)
    # Получает половину ширины / высоты экрана и ширины / высоты окна
    center_x = int(progress_window.winfo_screenwidth() / 2 - window_width / 2)
    center_y = int(progress_window.winfo_screenheight() / 2 - window_height / 2)

    # Помещает окно в центр страницы
    progress_window.geometry("+{}+{}".format(center_x, center_y))
    bottomFrame = Frame(progress_window)

    # Tell the Frame to fill the whole window
    bottomFrame.pack()

    # Make all the buttons and save them in a dict

    start_btn = Button(bottomFrame, text="Начать")
    start_btn.grid(row=1, column=0)

    processing_bar = ttk.Progressbar(bottomFrame, orient='horizontal', length=850, mode='indeterminate')
    processing_bar.grid(row=0, column=0, columnspan=1, sticky='NEWS')

    textFrame = Frame(progress_window)
    textFrame.pack()
    text = Text(textFrame, width=850, height=200, font=15, state="disabled")
    text.pack()

    return processing_bar, start_btn, text
