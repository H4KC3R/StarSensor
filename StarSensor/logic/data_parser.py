import csv


def get_main_data(file_stars, gamma):
    x, y, RA, Dec = [], [], [], []
    with open(file_stars, "r") as read_file:
        data = csv.reader(read_file, delimiter='\t')
        next(data)
        for elem in data:
            x.append(float(elem[1]))
            y.append(float(elem[2]))
        # координаты от теодолита
            RA.append(-float(elem[3]) - gamma + 180)
            Dec.append(90 - float(elem[4]))
    return x, y, RA, Dec


def get_cube_data(file_spin):
    combo = []
    with open(file_spin, "r") as read_file:
        data = csv.reader(read_file, delimiter='\t')
        for elem in data:
            combo.append(elem)
    return combo


def get_ruler(file_ruler):
    ruler = []
    with open(file_ruler, "r") as read_file:
        data = csv.reader(read_file, delimiter='\t')
        for elem in data:
            ruler.append(elem)
    return ruler


def get_mirror(file_mirror):
    mirror = []
    with open(file_mirror, "r") as read_file:
        data = csv.reader(read_file, delimiter='\t')
        for elem in data:
            mirror.append(elem)
    return mirror
