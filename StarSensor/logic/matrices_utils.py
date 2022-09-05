import numpy as np
import math


#  Направляющие cos для теодолита:
def lmn(hz, v):
    #  hz, v в градусах
    hz = math.radians(hz)
    v = math.radians(90-v)
    return np.array([[math.cos(-hz) * math.cos(v)], [math.sin(-hz) * math.cos(v)], [math.sin(v)]]).reshape(3, 1)


#  Нормирование вектора
def vector_norm(vec):
    return vec/np.linalg.norm(vec)


#  определение матрицы поворота:
def find_Mper(xpr=0):
    mper3 = np.array([[-1], [0], [0]]).reshape(3, 1)
    mper1 = []
    if xpr == 1:
        mper1 = np.array([[0, 0], [0, 1], [1, 0]])
    if xpr == 0:
        mper1 = np.array([[0, 0], [0, -1], [-1, 0]])
    if xpr == 3:
        mper1 = np.array([[0, 0], [-1, 0], [0, 1]])
    if xpr == 2:
        mper1 = np.array([[0, 0], [1, 0], [0, -1]])
    return np.hstack((mper1, mper3))


#  матрица перехода от ВСК к СК ТЗ:
def vsk2sk_tz(ax, ay, az, mper, degree=True):
    if degree:
        ax = math.radians(ax)
        ay = math.radians(ay)
        az = math.radians(az)
    A1 = np.array([[1, 0, 0], [0, math.cos(ax), -math.sin(ax)], [0, math.sin(ax), math.cos(ax)]])
    A2 = np.array([[math.cos(ay), 0, math.sin(ay)], [0, 1, 0], [-math.sin(ay), 0, math.cos(ay)]])
    A3 = np.array([[math.cos(az), -math.sin(az), 0], [math.sin(az), math.cos(az), 0], [0, 0, 1]])
    B = A1.dot(A2)
    C = B.dot(A3)
    E1 = C.dot(mper)
    return E1


def X(ax, ay, az, ra, dec, f, mper):
    ra = math.radians(ra)
    dec = math.radians(dec)
    LMN = np.array([[math.cos(ra)*math.cos(dec)], [math.sin(ra)*math.cos(dec)], [math.sin(dec)]]).reshape(3, 1)
    LMNvsk_sktz = np.transpose(vsk2sk_tz(ax, ay, az, mper)).dot(LMN)
    return -(LMNvsk_sktz[0]/LMNvsk_sktz[2]) * f


def Y(ax, ay, az, ra, dec, f, mper):
    ra = math.radians(ra)
    dec = math.radians(dec)
    LMN = np.array([[math.cos(ra)*math.cos(dec)], [math.sin(ra)*math.cos(dec)], [math.sin(dec)]]).reshape(3, 1)
    LMNvsk_sktz = np.transpose(vsk2sk_tz(ax, ay, az, mper)).dot(LMN)
    return -(LMNvsk_sktz[1]/LMNvsk_sktz[2]) * f


def angle_M(matrix1, matrix2):
    rot = matrix1.dot(np.transpose(matrix2))
    beta = 0.5 * (rot[0][0] + rot[1][1] + rot[2][2] - 1)
    alpha = math.acos(beta)
    ax = alpha * (rot[2][1] - rot[1][2]) / (2 * math.sin(alpha))
    ay = alpha * (rot[0][2] - rot[2][0]) / (2 * math.sin(alpha))
    az = alpha * (rot[1][0] - rot[0][1]) / (2 * math.sin(alpha))
    return [math.degrees(ax), math.degrees(ay), math.degrees(az)]
