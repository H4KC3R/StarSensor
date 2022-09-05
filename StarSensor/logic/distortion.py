import csv


# учет дисторсий
class Distortion:
    def __init__(self, distortion_file):
        self.ax = []
        self.ay = []
        with open(distortion_file, "r") as read_file:
            data = csv.reader(read_file, delimiter=' ')
            for elem in data:
                self.ax.append(float(elem[0]))
                self.ay.append(float(elem[1]))

    def dx(self, x, y):
        dx = self.ax[0] + self.ax[1] * x + self.ax[2] * y + (self.ax[3] * x**2 / 2) + (self.ax[4] * x * y / 2) \
             + (self.ax[5] * y**2 / 2) + (self.ax[6] * x**3 / 2) + (self.ax[7] * x**2 * y / 2) \
             + (self.ax[8] * x * y**2 / 2) + (self.ax[9] * y**3 / 2)
        return dx

    def dy(self, x, y):
        dy = self.ay[0] + self.ay[1] * x + self.ay[2] * y + (self.ay[3] * x**2 / 2) + (self.ay[4] * x * y / 2) \
             + (self.ay[5] * y**2 / 2) + (self.ay[6] * x**3 / 2) + (self.ay[7] * x**2 * y / 2) \
             + (self.ay[8] * x * y**2 / 2) + (self.ay[9] * y**3 / 2)
        return dy
