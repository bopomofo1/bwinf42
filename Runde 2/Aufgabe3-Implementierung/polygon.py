import matplotlib.pyplot as plt
import json

# Gibt eine Liste an Polygon Punkten zurück
def load_polygon(path):
    file = open(path, 'r')
    lines = int(file.readline())
    
    polygon = []
    for _ in range(lines):
        polygon.append([float(x) for x in file.readline().split()])
    polygon.append(polygon[0])
    file.close()
    return polygon


def draw_polygon(polygon):
    xs, ys = zip(*polygon)
    plt.subplot(1, 1, 1).plot(xs, ys, 'k', linewidth=0.8)


