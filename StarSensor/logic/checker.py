import numpy as np
import warnings


def check_vector(vector):
    if not (1 - np.linalg.norm(vector) <= 1e-15):
        warnings.warn("Вектор не удовлетворяет необходимым условиям\n", stacklevel=5)


def check_matrix(matrix, state):
    check_statement1 = 1 - np.linalg.det(matrix) <= 1e-15
    check_statement2 = 1 - np.linalg.det(np.dot(matrix, matrix.transpose())) <= 1e-15
    check_statement3 = np.linalg.det(np.subtract(np.linalg.inv(matrix), matrix.transpose())) <= 1e-30
    if not(check_statement1 and check_statement2 and check_statement3):
        warnings.warn("Матрица ({}) не удовлетворяет необходимым условиям\n".format(state), stacklevel=6)


def check_angle(angle, maximum):
    if np.abs(angle) > maximum:
        warnings.warn("Угол не удовлетворяет необходимым условиям\n", stacklevel=5)
