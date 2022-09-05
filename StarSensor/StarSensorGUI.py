import tkinter.filedialog as filedialog
from logic import calculation
from tkinter import *
from functools import partial
from PIL import Image, ImageTk
from threading import Thread
import warnings
import os
root = Tk()
root.resizable(False, False)


# -------------- Блок с функциями -------------- #
def start(files, initial_params, output_params, xpr, text):
    with warnings.catch_warnings(record=True) as w_list:
        warnings.simplefilter("always", UserWarning)
        calculation.calculate(files, initial_params, output_params, xpr=xpr)
        for w in w_list:
            text.config(state="normal")
            text.insert(END, w.message)
            text.config(state="disabled")


def show_and_run(func, btn):
    # Сохряняем текущий цвет кнопки и меняем на зеленый
    old_color = btn['bg']
    btn['bg'] = 'green'

    # Вызов функций
    func()

    # Восстановить исходный цвет кнопки
    btn['bg'] = old_color


def run_function(func, btn, processing_bar):
    # Отключить все кнопки
    btn.config(text="Ожидайте, идёт вычисление", state='disabled')

    processing_bar.start()
    show_and_run(func, btn)
    processing_bar.stop()

    # Включить все кнопки
    btn.config(text="Готово", state='normal', command=root.destroy)


def clicked(func, btn, processing_bar):
    Thread(target=run_function, args=(func, btn, processing_bar)).start()


def openfile(entry):
    input_path = filedialog.askopenfilename(filetypes=(('text files', '.txt'),))
    entry.delete(0, "end")
    entry.insert(1, input_path)


def openfolder(entry):
    path = filedialog.askdirectory()
    entry.delete(0, "end")
    entry.insert(1, path)


# -------------- Блок с функциями -------------- #
# -------------- Создание окна -------------- #
root.title("Калибровка звездного датчика")
app_width = 840
app_height = 500
root.geometry(f'{app_width}x{app_height}')

# Получает половину ширины / высоты экрана и ширины / высоты окна
positionRight = int(root.winfo_screenwidth() / 2 - app_width / 2)
positionDown = int(root.winfo_screenheight() / 2 - app_height / 2)

# Помещает окно в центр страницы
root.geometry("+{}+{}".format(positionRight, positionDown))
root.minsize(app_width, app_height)

frmSetup = Frame(root, bd=5)
frmSetup.pack()

# -------------- Создание окна -------------- #
# -------------- Ставим лого -------------- #
image = Image.open("Logo/logo.jpg")
photo = ImageTk.PhotoImage(image)

label = Label(frmSetup, image=photo, bg="white")
label.image = photo
label.pack(side=LEFT, anchor="e")

# -------------- Ставим лого -------------- #
# -------------- Выбор направления прибора -------------- #
frmChooseDir = Frame(frmSetup, bd=5)
frmChooseDir.pack(side=LEFT)
varRadio = IntVar()
r1 = Radiobutton(frmChooseDir, text="OX прибора вниз", variable=varRadio, value=0)
r1.grid(row=0, column=0)

r2 = Radiobutton(frmChooseDir, text="OX прибора вверх(ОГ-32P)", variable=varRadio, value=1)
r2.grid(row=0, column=1)

r3 = Radiobutton(frmChooseDir, text="OX прибора влево(БОКЗ-МР)", variable=varRadio, value=2)
r3.grid(row=0, column=2)

r4 = Radiobutton(frmChooseDir, text="OX прибора вправо(БОКЗ-МР, -M60. -M60/1000)", variable=varRadio, value=3)
r4.grid(row=1, column=0, columnspan=3)

# -------------- Выбор направления прибора -------------- #
# -------------- Параметры стенда -------------- #
sep = Frame(root, width=1, bd=5, bg='black')
sep.pack(fill=X, expand=1)
topFrame = Frame(root)
topFrame.pack()

lblDevice = Label(topFrame, text='Прибор:', width=25)
lblDevice.grid(row=0, column=0)
device_var = StringVar()
entDevice = Entry(topFrame, width=20, textvariable=device_var)
entDevice.grid(row=0, column=1)

lblNumber = Label(topFrame, text='№:', width=25)
lblNumber.grid(row=0, column=2)
number_var = StringVar()
entNumber = Entry(topFrame, width=20, textvariable=number_var)
entNumber.grid(row=0, column=3)

lblDate = Label(topFrame, text='Дата проведения измерений:', width=30)
lblDate.grid(row=1, column=0)
date_var = StringVar()
entDevice = Entry(topFrame, width=20, textvariable=date_var)
entDevice.grid(row=1, column=1)

lblOperator = Label(topFrame, text='Оператор:', width=25)
lblOperator.grid(row=1, column=2)
operator_var = StringVar()
entNumber = Entry(topFrame, width=20, textvariable=operator_var)
entNumber.grid(row=1, column=3)

lblFocus = Label(topFrame, text='Фокус(в мм):', width=25)
lblFocus.grid(row=2, column=0)
focus_var = StringVar()
entFocus = Entry(topFrame, width=20, textvariable=focus_var)
entFocus.grid(row=2, column=1)

lblMainPoint = Label(topFrame, text='Главная точка(x,y):', width=25)
lblMainPoint.grid(row=2, column=2)
x_var = StringVar()
y_var = StringVar()

main_pointFrame = Frame(topFrame)
main_pointFrame.grid(row=2, column=3)
entMainPointX = Entry(main_pointFrame, width=9, textvariable=x_var)
entMainPointX.grid(row=0, column=0, padx=5)
entMainPointY = Entry(main_pointFrame, width=9, textvariable=y_var)
entMainPointY.grid(row=0, column=1, padx=5)

lblMatrixSize = Label(topFrame, text='Размер матрицы:', width=30)
lblMatrixSize.grid(row=3, column=0)
matrix_size_var = StringVar()
entMatrixSize = Entry(topFrame, width=20, textvariable=matrix_size_var)
entMatrixSize.grid(row=3, column=1)

lblPixelSize = Label(topFrame, text='Размер пикселя(в мм):', width=30)
lblPixelSize.grid(row=3, column=2)
pixel_size_var = StringVar()
entPixelSize = Entry(topFrame, width=20, textvariable=pixel_size_var)
entPixelSize.grid(row=3, column=3)

# -------------- Параметры стенда -------------- #
# -------------- Подгрузка файлов  -------------- #
sep1 = Frame(root, width=1, bd=5, bg='black')
sep1.pack(fill=X, expand=1)
frmFiles = Frame(root, bd=5)
frmFiles.pack()

lblIn = Label(frmFiles, text='Файл с локализацией звезд', width=40).grid(row=0, column=0)
input_var = StringVar()
entIn = Entry(frmFiles, width=50, textvariable=input_var)
entIn.grid(row=0, column=1)
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)
btnIn = Button(frmFiles, text='Выбрать', command=partial(openfile, entIn)).grid(row=0, column=2)

lblSpn = Label(frmFiles, text='Файл с углами поворотов', width=25).grid(row=1, column=0, padx=59)
spn_var = StringVar()
entSpn = Entry(frmFiles, width=50, textvariable=spn_var)
entSpn.grid(row=1, column=1)
btnSpn = Button(frmFiles, text='Выбрать', command=partial(openfile, entSpn)).grid(row=1, column=2)

lblRuler = Label(frmFiles, text='Файл со значениями линейки', width=26).grid(row=2, column=0, padx=59)
ruler_var = StringVar()
entRuler = Entry(frmFiles, width=50, textvariable=ruler_var)
entRuler.grid(row=2, column=1)
btnRuler = Button(frmFiles, text='Выбрать', command=partial(openfile, entRuler)).grid(row=2, column=2)


lblMirror = Label(frmFiles, text='Файл со значениями зеркала', width=26).grid(row=3, column=0, padx=59)
mirror_var = StringVar()
entMirror = Entry(frmFiles, width=50, textvariable=mirror_var)
entMirror.grid(row=3, column=1)
btnMirror = Button(frmFiles, text='Выбрать', command=partial(openfile, entMirror)).grid(row=3, column=2)

lblOut = Label(frmFiles, text='Выходная папка', width=20).grid(row=4, column=0, padx=59)
output_var = StringVar()
entOut = Entry(frmFiles, width=50, textvariable=output_var)
entOut.grid(row=4, column=1)
btnOut = Button(frmFiles, text='Выбрать', command=partial(openfolder, entOut)).grid(row=4, column=2)

# -------------- Подгрузка файлов  -------------- #
# -------------- Учёт дисторсий -------------- #
sep2 = Frame(root, width=1, bd=5, bg='black')
sep2.pack(fill=X, expand=1)

frmDist = Frame(root, bd=5)
frmDist.pack()
value_check = IntVar()
chkDist = Checkbutton(frmDist, text='Учет дисторсий', variable=value_check, onvalue=1, offvalue=0)
chkDist.pack(side=LEFT)
dist_var = StringVar()
entDist = Entry(frmDist, width=60, state=DISABLED, textvariable=dist_var)
entDist.pack(side=LEFT)
btnDist = Button(frmDist, text='Выбрать', command=partial(openfile, entDist), state=DISABLED)
btnDist.pack(side=LEFT)


def enable_disable():
    if value_check.get() == 1:
        btnDist.config(state=NORMAL)
        entDist.config(state=NORMAL)
    elif value_check.get() == 0:
        btnDist.config(state=DISABLED)
        entDist.config(state=DISABLED)


chkDist.config(command=enable_disable)
# -------------- Учёт дисторсий -------------- #
# -------------- Вычисление -------------- #


def run():
    import StarSensorGUI_execution_window as StarExec
    distortion_file = dist_var.get() if value_check.get() == 1 else None
    xper = varRadio.get()
    files = [input_var.get(), spn_var.get(), ruler_var.get(), mirror_var.get(), distortion_file, output_var.get()]
    output_params = [device_var.get(), number_var.get(), date_var.get(), operator_var.get()]
    initial_params = [focus_var.get(), x_var.get(), y_var.get(), matrix_size_var.get(), pixel_size_var.get()]
    processing_bar, start_btn, text = StarExec.create_execution_window(root)
    start_calculation = partial(start, files, initial_params, output_params, xper, text)
    start_btn.config(command=lambda f=start_calculation, b=start_btn: clicked(f, b, processing_bar))


# -------------- Вычисление -------------- #
# -------------- Далее/Выход -------------- #
sep3 = Frame(root, width=1, bd=5, bg='black')
sep3.pack(fill=X, expand=1)
frmQuitNext = Frame(root, bd=5)
frmQuitNext.pack()
btnNext = Button(frmQuitNext, text='Далее', state=DISABLED, command=run)
btnNext.pack(side=RIGHT, anchor=SE)
btnQuit = Button(frmQuitNext, text='Выход', command=root.destroy)
btnQuit.pack(anchor=SW)

# -------------- Далее/Выход -------------- #
# -------------- Следим за тем что бы поля были заполнены -------------- #


def validate(*args):
    if value_check.get():
        if input_var.get() and spn_var.get() and mirror_var.get() and ruler_var.get() and output_var.get() \
                and dist_var.get():
            btnNext.config(state='normal')
        else:
            btnNext.config(state='disabled')
    else:
        if input_var.get() and spn_var.get() and mirror_var.get() and ruler_var.get() and output_var.get():
            btnNext.config(state='normal')
        else:
            btnNext.config(state='disabled')


device_var.trace("w", validate)
number_var.trace("w", validate)
date_var.trace("w", validate)
operator_var.trace("w", validate)
focus_var.trace("w", validate)
x_var.trace("w", validate)
y_var.trace("w", validate)
matrix_size_var.trace("w", validate)
pixel_size_var.trace("w", validate)
input_var.trace("w", validate)
spn_var.trace("w", validate)
mirror_var.trace("w", validate)
ruler_var.trace("w", validate)
output_var.trace("w", validate)
dist_var.trace("w", validate)
# -------------- Следим за тем что бы поля были заполнены -------------- #

root.mainloop()
