import numpy as np


#  перевод пикселей в миллиметры:
def px2mm(px, mat_size, pix_size):
    matrix_size = mat_size  # размер матрицы
    pixel_size = pix_size  # размер пискселя
    mm = (px - matrix_size / 2) * pixel_size
    return mm


def lmn2V(lmn):
    return 90 - np.degrees(np.arcsin(lmn[2][0]))


def lmn2Hz(lmn):
    return np.degrees(-np.arctan2(lmn[1][0],lmn[0][0]))


def deg2dms(dd):
    is_positive = dd >= 0
    dd = abs(dd)
    minutes, seconds = divmod(dd*3600, 60)
    degrees, minutes = divmod(minutes, 60)
    return [degrees, minutes, seconds] if is_positive else [-degrees, -minutes, -seconds]
