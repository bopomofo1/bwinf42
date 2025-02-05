import matplotlib.pyplot as plt
import math
import sys
from timeit import default_timer as timer
from polygon import load_polygon, draw_polygon
from solver import Solver

start = timer()

polygon = load_polygon(sys.argv[1])

solver = Solver(polygon)

print("Polygon wird mit kleinen Kreisen befüllt")

print(sys.argv[3])

if (sys.argv[3] == 'm'):
    solver.marble_slap("")
elif (sys.argv[3] == 'md'):
    solver.marble_slap("", divide=True, amount=360)  
elif (sys.argv[3] == 'h'):
    solver.hexagonal("")
elif (sys.argv[3] == 's'):
    solver.square("")
elif (sys.argv[3] == 'i'):
    solver.ilp(grid_size=5)
elif (sys.argv[3] == 'd'):
    solver.ilp(grid_size=5, divide=True, width=100, height=100)   

print("Gesundheitszentrum wird ausgewählt")

# Timeit
gz_start = timer()
solver.select_gz(1)
gz_time = timer() - gz_start

print("Gesundheitszentrum wird befüllt")

keep = "--keep" in sys.argv
if keep:
    # Kreise außerhalb des Gesundheitszentrums löschen
    solver.small_circles_spatial = \
    [[[c for c in solver.small_circles_spatial[y][x] 
       if math.dist(c, solver.gz) + solver.precision_error <= solver.gz_radius
       ]
       for x in range(solver.horizontal_amount)] 
       for y in range(solver.vertical_amount)]
else:
    solver.small_circles_spatial = [[[] for x in range(solver.horizontal_amount)] 
                                    for y in range(solver.vertical_amount)]
    if (sys.argv[4] == 'm'):
        solver.marble_slap("inside")
    elif (sys.argv[3] == 'md'):
        solver.marble_slap("inside", divide=True, amount=360)  
    elif (sys.argv[4] == 'h'):
        solver.hexagonal("inside")
    elif (sys.argv[4] == 's'):
        solver.square("inside")
    elif (sys.argv[4] == 'i'):
        solver.ilp(grid_size=5, mode="inside")
    elif (sys.argv[4] == 'd'):
        solver.ilp(grid_size=5, mode="inside", divide=True, 
                   width=100, height=100) 


print("Der Rest wird befüllt")

if (sys.argv[5 - keep] == 'm'):
    solver.marble_slap("outside")
elif (sys.argv[3] == 'md'):
        solver.marble_slap("outside", divide=True, amount=360)   
elif (sys.argv[5 - keep] == 'h'):
    solver.hexagonal("outside")
elif (sys.argv[5 - keep] == 's'):
    solver.square("outside")
elif (sys.argv[5 - keep] == 'i'):
    solver.ilp(grid_size=5, mode="outside")
elif (sys.argv[5] == 'd'):
    solver.ilp(grid_size=5, mode="outside", divide=True, width=100, height=100) 

print("Fertig")

end = timer()

# GZ Kreis zeichnen
plt.subplot(1, 1, 1).add_patch(plt.Circle(solver.gz, 1, color='r', fill=True))
plt.subplot(1, 1, 1).add_patch(plt.Circle(solver.gz, solver.gz_radius, color='r', fill=False))


placed_circles = 0
for y in range(solver.vertical_amount):
    for x in range(solver.horizontal_amount):
        # Kreise innerhalb GZ zeichen
        for circle in solver.small_circles_spatial[y][x]:
            placed_circles += 1
            # Mittelpunkt
            plt.subplot(1, 1, 1).add_patch(
                plt.Circle(circle, 0.25, color='g', fill=True)) 
            # Kreis
            plt.subplot(1, 1, 1).add_patch(
                plt.Circle(circle, solver.small_radius, color='k', fill=False))
            
        # Kreise außerhalb GZ zeichnen
        for circle in solver.big_circles_spatial[y][x]:
            placed_circles += 1
            # Mittelpunkt
            plt.subplot(1, 1, 1).add_patch(
                plt.Circle(circle, 1, color='g', fill=True))
            # Kreis
            plt.subplot(1, 1, 1).add_patch(
                plt.Circle(circle, solver.big_radius, color='k', fill=False))


print(placed_circles, " Kreise platziert.")



#Lösung speichern
# Format GZ Standort, kleinen Kreise, große Kreise
output = open(sys.argv[2] + ".txt", "w")

output.write(str(solver.gz[0]) + " " + str(solver.gz[1]) + "\n\n")
for y in range(solver.vertical_amount):
    for x in range(solver.horizontal_amount):
        for circle in solver.small_circles_spatial[y][x]:
            output.write(str(circle[0]) + " " + str(circle[1]) + "\n")

output.write("\n")

output.write(str(solver.gz[0]) + " " + str(solver.gz[1]) + "\n\n")
for y in range(solver.vertical_amount):
    for x in range(solver.horizontal_amount):
        for circle in solver.big_circles_spatial[y][x]:
            output.write(str(circle[0]) + " " + str(circle[1]) + "\n")

output.close()

# Lösung zeichnen und speichern

draw_polygon(polygon)
plt.subplot(1, 1, 1).axis('equal')
plt.subplot(1, 1, 1).set_title(str(placed_circles) + " Siedlungen in \
                               " + str(int(round(end-start, 0))) + "s platziert")
plt.legend(loc='best')

plt.tight_layout()
plt.savefig(sys.argv[2] + ".png", dpi=800)
#plt.show()


