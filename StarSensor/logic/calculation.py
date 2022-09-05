import numpy as np
import matplotlib.pyplot as plt
from logic import distortion, functions as func, data_parser, output_pdf, checker, matrices_utils as util
from scipy.optimize import least_squares


def calculate(files, initial_param, output_param, xpr=0):
    focus = float(initial_param[0])  # фокус прибора
    X0, Y0 = float(initial_param[1]), float(initial_param[2])  # Главная точка
    matrix_size = float(initial_param[3])  # размер матрицы
    pixel_size = float(initial_param[4])   # размер пискселя

    # --------------   Данные для кубика -------------- #
    COMBO = data_parser.get_cube_data(files[1])
    gamma = float(COMBO[6][4])
    T1_k1 = np.array([[0], [float(COMBO[2][5])]]).reshape(2, 1)
    T2_k2 = np.array([[0], [float(COMBO[3][5])]]).reshape(2, 1)
    T1_T2 = np.array([[float(COMBO[4][4])], [float(COMBO[4][5])]]).reshape(2, 1)
    T2_T1 = np.array([[float(COMBO[5][4])], [float(COMBO[5][5])]]).reshape(2, 1)

    # --------------  Определение матрицы поворота  -------------- #
    Mper = util.find_Mper(xpr)
    # --------------  Формулы ВСК - ТБ -------------- #
    x, y, RA, Dec = data_parser.get_main_data(files[0], gamma)
    # Подготовка:
    points = len(x)
    # Координаты измеренные на матрице прибора:
    x = [func.px2mm(elem, matrix_size, pixel_size) for elem in x]
    y = [func.px2mm(elem, matrix_size, pixel_size) for elem in y]
    # Учет дисторсий:
    if files[4] is not None:
        dist = distortion.Distortion(files[4])
        for i in range(points):
            x[i] = x[i] - dist.dx(x[i], y[i])
            y[i] = y[i] - dist.dy(x[i], y[i])

    # --------------  Уравнивание -------------- #
    # Первые приближения:
    ax, ay, az = 1, 1, 1
    f = focus

    # Уравнивание:
    def Resid(solution):
        funcs = np.zeros(points)
        for j in range(points):
            x1 = util.X(solution[0], solution[1], solution[2], RA[j], Dec[j], solution[3], Mper)
            y1 = util.Y(solution[0], solution[1], solution[2], RA[j], Dec[j], solution[3], Mper)
            resid = np.sqrt((x1 - x[j])**2 + (y1 - y[j])**2)
            funcs[j] = resid
        return funcs

    # Уравнивание фокуса:
    x0 = np.array([ax, ay, az, f])
    sol = least_squares(Resid, x0)
    [ax, ay, az] = sol.x[0], sol.x[1], sol.x[2]
    f = sol.x[3]
    Mvsk_tb = util.vsk2sk_tz(ax, ay, az, Mper, degree=True)
    res = sol.fun
    fig2 = plt.figure(figsize=(6, 2))
    plt.plot(range(points), res * 1000, "ro-", color='red', linewidth=1, markersize=2)
    plt.xlabel('i')
    plt.ylabel('Res_i, µm')
    plt.grid(color='g')
    # save the figure
    plt.savefig('{}/residuals.png'.format(files[5]), dpi=300, bbox_inches='tight')
    fig1, (axes1, axes2) = plt.subplots(nrows=1, ncols=2, figsize=(6, 3), dpi=80)

    axes1.plot(x, y, 'o', color='red')
    axes1.set_title('Точки на матрице')
    axes1.set_xlabel('x(i), mm')
    axes1.set_ylabel('y(i), mm')
    axes1.grid(color='g')

    axes2.plot(RA, Dec, 'd', color='red')
    axes2.set_title('Углы теодолита')
    axes2.set_xlabel('Dec(i), deg')
    axes2.set_ylabel('RA(i), deg')
    axes2.grid(color='g')
    fig1.tight_layout(pad=3.0)

    plt.savefig('{}/points and degrees.png'.format(files[5]), dpi=500, bbox_inches='tight')
    errors = [points, round(max(res)*1000, 5), round(np.sqrt(np.var(res))*1000, 5), round(float(np.mean(res))*1000, 5)]

    # --------------   Формулы ВСК - КУБ -------------- #
    T1_k2 = np.array([[T1_T2[0][0]-T2_T1[0][0] - 180], [T2_k2[1][0]]]).reshape(2, 1)
    T1_Xk_lmn = util.vector_norm(util.lmn(T1_k1[0][0], T1_k1[1][0]))
    T1_Yk_lmn = util.vector_norm(np.cross(util.lmn(T1_k2[0][0], T1_k2[1][0]), T1_Xk_lmn, axis=0))
    T1_Zk_lmn = util.vector_norm(np.cross(T1_Xk_lmn, T1_Yk_lmn, axis=0))
    checker.check_vector(T1_Xk_lmn)
    checker.check_vector(T1_Yk_lmn)
    checker.check_vector(T1_Zk_lmn)
    Mcube_tb = np.array([[T1_Xk_lmn[0][0], T1_Yk_lmn[0][0], T1_Zk_lmn[0][0]],
                         [T1_Xk_lmn[1][0], T1_Yk_lmn[1][0], T1_Zk_lmn[1][0]],
                        [T1_Xk_lmn[2][0], T1_Yk_lmn[2][0], T1_Zk_lmn[2][0]]])
    Mvsk_cube = np.transpose(Mcube_tb).dot(Mvsk_tb)
    #  Проверка ГУ и ВУ с теодолитов (не должен быть более 10 угл):
    checker.check_angle((90-T1_T2[1] + (90 - T2_T1[1])), 0.002777778)
    angle = np.radians(T1_T2[0] - T2_T1[0] + 270)
    checker.check_angle(np.degrees(np.arcsin(np.sin(angle))), 0.002777778)

    checker.check_matrix(Mvsk_tb, "Мвск_тб")
    checker.check_matrix(Mcube_tb, "Мкуб_тб")
    checker.check_matrix(Mvsk_cube, "Мвск_куб")

    # --------------   Данные для калибровачной матрицы(ЛИНЕЙКА) -------------- #
    #  Данные граней кубика:
    ruler = data_parser.get_ruler(files[2])
    #  Измерение граней кубика:
    T1_k1_L = np.array([[float(ruler[0][5])], [float(ruler[0][6])]]).reshape(2, 1)
    T2_k2_L = np.array([[float(ruler[1][5])], [float(ruler[1][6])]]).reshape(2, 1)
    #  Измерение труба в трубу:
    T1_T2_L = np.array([[float(ruler[5][5])], [float(ruler[5][6])]]).reshape(2, 1)
    T2_T1_L = np.array([[float(ruler[6][5])], [float(ruler[6][6])]]).reshape(2, 1)
    #  Зеркало на линейке:
    T1_mir_L = np.array([[float(ruler[2][5])], [float(ruler[2][6])]]).reshape(2, 1)

    # -------------- ЛИНЕЙКА формулы -------------- #
    checker.check_angle((90 - T1_T2_L[1] + (90 - T2_T1_L[1])), 0.004166667)
    angle = np.radians(T1_T2_L[0] - T2_T1_L[0] + 270)
    checker.check_angle(np.degrees(np.arcsin(np.sin(angle))), 0.005555556)

    T1_k2_L = np.array([[T1_T2_L[0][0]-T2_T1_L[0][0] - 180], [T2_k2_L[1][0]]]).reshape(2, 1)

    T1_Xk_lmn = util.vector_norm(util.lmn(T1_k1_L[0][0], T1_k1_L[1][0]))
    T1_Yk_lmn = util.vector_norm(np.cross(util.lmn(T1_k2_L[0][0], T1_k2_L[1][0]), T1_Xk_lmn, axis=0))
    T1_Zk_lmn = util.vector_norm(np.cross(T1_Xk_lmn, T1_Yk_lmn, axis=0))
    #  Ориентация куба в СК T1(добавлен поворот вокруг оси OY T1, т.к кронштейн положили)
    if xpr == 1:
        Mcube_tb_L = (np.array([[T1_Xk_lmn[0][0], T1_Yk_lmn[0][0], T1_Zk_lmn[0][0]],
                               [T1_Xk_lmn[1][0], T1_Yk_lmn[1][0], T1_Zk_lmn[1][0]],
                               [T1_Xk_lmn[2][0], T1_Yk_lmn[2][0], T1_Zk_lmn[2][0]]]).
                      dot(util.vsk2sk_tz(0, 90, 0, Mper))).dot(util.vsk2sk_tz(180, 0, 0, Mper))
    else:
        Mcube_tb_L = (np.array([[T1_Xk_lmn[0][0], T1_Yk_lmn[0][0], T1_Zk_lmn[0][0]],
                                [T1_Xk_lmn[1][0], T1_Yk_lmn[1][0], T1_Zk_lmn[1][0]],
                                [T1_Xk_lmn[2][0], T1_Yk_lmn[2][0], T1_Zk_lmn[2][0]]]).dot(
            util.vsk2sk_tz(0, 90, 0, Mper)))
    T1_Xk_L = util.lmn(T1_mir_L[0][0], T1_mir_L[1][0])
    #  Нормаль зеркала линейки в кубике:
    mir_k_L = np.transpose(Mcube_tb_L).dot(T1_Xk_L)

    # --------------   Данные для калибровочной матрицы(ЗЕРКАЛО) -------------- #
    mirror = data_parser.get_mirror(files[3])
    # ЗЕРКАЛО измерение граней кубика
    T1_k1_M = np.array([[0], [float(mirror[2][6])]]).reshape(2, 1)
    T2_k2_M = np.array([[0], [float(mirror[3][6])]]).reshape(2, 1)
    # Измерение труба в трубу
    T1_T2_M = np.array([[float(mirror[4][5])], [float(mirror[4][6])]]).reshape(2, 1)
    T2_T1_M = np.array([[float(mirror[5][5])], [float(mirror[5][6])]]).reshape(2, 1)
    # ЗЕРКАЛО перестановка теодолитов
    T2_mir_M1 = np.array([[0], [float(mirror[8][6])]]).reshape(2, 1)
    T2_mir_M2 = np.array([[float(mirror[9][5])], [float(mirror[9][6])]]).reshape(2, 1)
    T2_mir_M3 = np.array([[float(mirror[10][5])], [float(mirror[10][6])]]).reshape(2, 1)
    T2_mir_M4 = np.array([[float(mirror[11][5])], [float(mirror[11][6])]]).reshape(2, 1)
    # Измерение трубу в трубу, после перестановки ТИ
    T1_T2_M_2 = np.array([[float(mirror[12][5])], [float(mirror[12][6])]]).reshape(2, 1)
    T2_T1_M_2 = np.array([[float(mirror[13][5])], [float(mirror[13][6])]]).reshape(2, 1)

    T2_mir_M1 = util.lmn(T2_mir_M1[0][0], T2_mir_M1[1][0])
    T2_mir_M2 = util.lmn(T2_mir_M2[0][0], T2_mir_M2[1][0])
    T2_mir_M3 = util.lmn(T2_mir_M3[0][0], T2_mir_M3[1][0])
    T2_mir_M4 = util.lmn(T2_mir_M4[0][0], T2_mir_M4[1][0])
    T2_mir_M_1 = util.vector_norm(T2_mir_M1 + T2_mir_M2 + T2_mir_M3 + T2_mir_M4)
    Hz = func.lmn2Hz(T2_mir_M_1)
    V = func.lmn2V(T2_mir_M_1)
    T2_mir_M = np.array([[Hz], [V]]).reshape(2, 1)
    # -------------- ЗЕРКАЛО формулы -------------- #
    checker.check_angle((90 - T1_T2_M[1]) + (90 - T2_T1_M[1]), 0.002777778)
    angle = np.radians(T1_T2_M[0] - T2_T1_M[0] + 270)
    checker.check_angle(np.degrees(np.arcsin(np.sin(angle))), 0.005555556)

    T1_k2_M = np.array([[T1_T2_M[0][0] - T2_T1_M[0][0] - 180], [T2_k2_M[1][0]]]).reshape(2, 1)
    T1_Xk_lmn = util.vector_norm(util.lmn(T1_k1_M[0][0], T1_k1_M[1][0]))
    T1_Yk_lmn = util.vector_norm(np.cross(util.lmn(T1_k2_M[0][0], T1_k2_M[1][0]), T1_Xk_lmn, axis=0))
    T1_Zk_lmn = util.vector_norm(np.cross(T1_Xk_lmn, T1_Yk_lmn, axis=0))
    #  Ориентация куба в СК T1:
    Mcube_tb_M = np.array([[T1_Xk_lmn[0][0], T1_Yk_lmn[0][0], T1_Zk_lmn[0][0]],
                           [T1_Xk_lmn[1][0], T1_Yk_lmn[1][0], T1_Zk_lmn[1][0]],
                           [T1_Xk_lmn[2][0], T1_Yk_lmn[2][0], T1_Zk_lmn[2][0]]])
    # Измеряем нормаль зерекала через перестановку 2го теодолита:
    T1_mir_M = np.array([[T1_T2_M_2[0][0] - T2_T1_M_2[0][0] + 180 + T2_mir_M[0][0]],
                         [T2_mir_M[1][0]]]).reshape(2, 1)
    # Нормаль зеркала в ТБ:
    T1_Xk_M = util.lmn(T1_mir_M[0][0], T1_mir_M[1][0])
    # Нормаль зеркала в кубике:
    mirP_r = np.transpose(Mcube_tb_M).dot(T1_Xk_M)

    # -------------- Формулы ВСК - ПСК -------------- #
    Zpsk = util.vector_norm(-mirP_r)
    Xpsk = util.vector_norm(np.cross(mir_k_L, Zpsk, axis=0))
    Ypsk = util.vector_norm(np.cross(Zpsk, Xpsk, axis=0))
    Mpsk_cube = np.array([[Xpsk[0][0], Ypsk[0][0], Zpsk[0][0]], [Xpsk[1][0], Ypsk[1][0], Zpsk[1][0]],
                          [Xpsk[2][0], Ypsk[2][0], Zpsk[2][0]]])
    Mvsk_psk = np.transpose(Mpsk_cube).dot(Mvsk_cube)
    angles = util.angle_M(Mvsk_psk, np.eye(3))
    ax1, ay1, az1 = func.deg2dms(angles[0]), func.deg2dms(angles[1]), func.deg2dms(angles[2])
    transition_params = [["ax1", round(ax1[0], 4), round(ax1[1], 4), round(ax1[2], 4)],
                         ["ay1", round(ay1[0], 4), round(ay1[1], 4), round(ay1[2], 4)],
                         ["az1", round(az1[0], 4), round(az1[1], 4), round(az1[2], 4)]]

    output_pdf.create_pdf(output_param, round(f, 4), X0, Y0, Mvsk_psk, files[4], errors, transition_params, files[5])
    # -------------- Проверка компенсаторов -------------- #
    s10 = 10 / 3600
    # В начале:

    checker.check_angle(float(COMBO[0][4]), s10)
    checker.check_angle(float(COMBO[0][5]), s10)
    checker.check_angle(float(COMBO[1][4]), s10)
    checker.check_angle(float(COMBO[1][5]), s10)
    # В конце:
    checker.check_angle(float(COMBO[14][4]), s10)
    checker.check_angle(float(COMBO[14][5]), s10)
    checker.check_angle(float(COMBO[15][4]), s10)
    checker.check_angle(float(COMBO[15][5]), s10)
    # -------------- Проверка углов -------------- #
    s5 = 5 / 3600
    checker.check_angle(float(COMBO[2][5]) - float(COMBO[12][5]), s5)
    checker.check_angle(float(COMBO[3][5]) - float(COMBO[13][5]), s5)

    checker.check_angle(float(COMBO[4][4]) - float(COMBO[10][4]), s5)
    checker.check_angle(float(COMBO[4][5]) + float(COMBO[5][5]) - 180, s5)
    checker.check_angle(float(COMBO[5][4]) - float(COMBO[11][4]), s5)
    checker.check_angle(float(COMBO[10][5]) + float(COMBO[11][5]) - 180, s5)

    checker.check_angle(float(COMBO[6][4]) - float(COMBO[9][4]), s5)
    checker.check_angle(float(COMBO[6][5]) - float(COMBO[9][5]), s5)
