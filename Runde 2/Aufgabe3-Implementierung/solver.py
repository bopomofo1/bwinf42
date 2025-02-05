import math
import matplotlib.pyplot as plt
import matplotlib.path as mpltPath
from bounding_box import BoundingBox
from pulp import LpMaximize, LpProblem, LpStatus, lpSum, LpVariable, PULP_CBC_CMD

class Solver():
    # Präzisionsungenauigkeit
    precision_error = 0.000000001

    # Wie nah Kantenpunkte zu bereits hinzugefügten Gitterpunkten sein dürfen
    too_close = 0.01 # min_dist = grid_size * too_close

    small_radius = 5
    big_radius = 10

    gz = None
    gz_radius = 85

    # Seitenlänge der Quadrate bei der räumlichen Liste
    spatial_length = gz_radius + 1

    def __init__(self, polygon) -> None:
        self.polygon = polygon
        self.polygon_path = mpltPath.Path(polygon) # für Punkt in Polygon
        self.bounding_box = BoundingBox(polygon)


        # Wie viele Quadrate, also Spalten und Zeilen die räumliche Liste hat
        self.horizontal_amount = int(math.ceil(self.bounding_box.width / self.spatial_length)) + 1 
        self.vertical_amount = int(math.ceil(self.bounding_box.height / self.spatial_length)) + 1

        # Räumliche Liste
        self.big_circles_spatial = [[[] for x in range(self.horizontal_amount)] for y in range(self.vertical_amount)]
        self.small_circles_spatial = [[[] for x in range(self.horizontal_amount)] for y in range(self.vertical_amount)]


    # Gibt amount viele Punkte auf dem Kreis mit Radius 
    # radius und Mittelpunkt point zurücl
    def generate_candidates(self, point, radius, amount) -> list[list[float]]:
        feasible_points = []
        step_size = (2 * math.pi) / amount
        curr = 0
        while curr <= 2 * math.pi:
            feasible_points.append(
                [point[0] + 2 * radius * math.cos(curr),
                 point[1] + 2 * radius * math.sin(curr)])
            curr += step_size 
        return feasible_points
    
    # Wählt aus der Liste candidates, den Punkt mit
    # der geringsten x-Koordinate und zweitrangig
    # geringsten y-Koordinate aus
    def select_candidate(self, candidates) -> list[float]:
        selected = candidates[0]
        for i in range(1, len(candidates)):
            # Soweit wie möglich links
            if candidates[i][0] < selected[0]: 
                selected = candidates[i]
            # Zweitrangig weit unten
            elif candidates[i][0] == selected[0] and \
            candidates[i][1] < selected[1]: 
                selected = candidates[i]
        return selected

    # Durchsucht die bounding_box im Abstand step_size
    # von unten nach oben und von links nach rechts
    # gibt den ersten Punkt, der point_ok erfüllt zurück
    def select_bottom_left_point(self, mode, bounding_box, circles_spatial, step_size) -> list[float]:
        bottom_left = None
        # Suche von unten nach oben und von links nach rechts
        y = bounding_box.bottom
        while y < bounding_box.top:
            x = bounding_box.left
            while x < bounding_box.right:
                index = self.point_to_index([x, y])
                # Der erste gültige Punkt ist der bottom_left_point
                if self.point_ok([x, y], index, self.bounding_box, mode):
                    bottom_left = [x, y]
                    circles_spatial[index[0]][index[1]].append(bottom_left)
                    break
                x += step_size
            y += step_size

            # bottom_left wurde gefunden, wir können aufhören
            if bottom_left is not None:
                break
        
        return bottom_left

    def marble_slap_solve(self, mode, bounding_box, amount=360, step_size = 1) -> None:
        circles_spatial, radius = self.mode_to_parameter(mode)

        bottom_left = self.select_bottom_left_point(mode, bounding_box,
                                                    circles_spatial, step_size)
        while bottom_left is not None:
        
            candidates = self.generate_candidates(bottom_left, radius, amount)
            while len(candidates) > 0:
                
                # Ungültige Kandidaten löschen
                candidates = [x for x in candidates 
                    if self.point_ok(x, self.point_to_index(x), bounding_box, mode)]

                if len(candidates) == 0:
                    break
                
                circle = self.select_candidate(candidates)
                index = self.point_to_index(circle)
                
                circles_spatial[index[0]][index[1]].append(circle)
                candidates = candidates + self.generate_candidates(circle, radius, amount)

            bottom_left = self.select_bottom_left_point(mode, bounding_box,
                                                    circles_spatial, step_size)
  
    def marble_slap(self, mode, divide=False, amount=360, step_size = 1, height=100):
        if divide:
            for bb in self.bounding_box.create_smaller_bounding_boxes(
                height=height, width=self.bounding_box.width):
                    self.marble_slap_solve(mode, bb, amount, step_size)
        else:
            self.marble_slap_solve(mode, self.bounding_box, amount, step_size)


    def hexagonal(self, mode) -> None:
        circles_spatial, radius = self.mode_to_parameter(mode)

        x_step_size = 1.5 * (radius / (math.sqrt(3) / 2))
        y_step_size = 2 * radius

        # Damit Spalten abwechselnd nach oben um radius
        # versetzt werden
        alternate = 0 

        x = self.bounding_box.left
        while x <= self.bounding_box.right:
            y = self.bounding_box.bottom + alternate * radius
            while y <= self.bounding_box.top:
                index = self.point_to_index([x, y])
                if self.point_ok([x, y], index, self.bounding_box, mode=mode):
                    circles_spatial[index[0]][index[1]].append([x, y])
                y += y_step_size
            x += x_step_size
            alternate = (alternate + 1) % 2

    def square(self, mode) -> None:
        circles_spatial, radius = self.mode_to_parameter(mode)

        x_step_size = 2 * radius
        y_step_size = 2 * radius

        x = self.bounding_box.left
        while x <= self.bounding_box.right:
            y = self.bounding_box.bottom 
            while y <= self.bounding_box.top:
                index = self.point_to_index([x, y])
                if self.point_ok([x, y], index, self.bounding_box, mode=mode):
                    circles_spatial[index[0]][index[1]].append([x, y])
                y += y_step_size
            x += x_step_size

    def create_edge_points(self, grid_size) -> list[list[float]]:
        edge_points = []

        for i in range(1, len(self.polygon)):
            
            # Die Kanten von i - 1 zu i wird in Punkt-Richtungsform dargestellt 
            dir_vec = [self.polygon[i][0] - self.polygon[i - 1][0], 
                       self.polygon[i][1] - self.polygon[i - 1][1]]
            length = math.dist([0, 0], dir_vec)
            # Richtungsvektor erhält Länge 1
            dir_vec = [dir_vec[0] / length, 
                       dir_vec[1] / length]

            # Wie viele Schritte mit Länge grid_size wir entlang des Richtungsvektors machen können
            # ohne die Kante zu verlassen
            steps = int(length / grid_size)
            for n in range(steps):
                new_point = [self.polygon[i - 1][0] + n * grid_size * dir_vec[0], 
                             self.polygon[i - 1][1] + n * grid_size * dir_vec[1]]
                edge_points.append(new_point)

        return edge_points

    def create_grid(self, grid_size, bounding_box, mode) -> list[list[float]]:    
        grid = []

        # Gitterpunkte erstellen
        y = bounding_box.bottom
        while y < bounding_box.top:
            x = bounding_box.left
            while x < bounding_box.right:
                index = self.point_to_index([x, y])
                if self.point_ok([x, y], index, bounding_box, mode=mode):
                    grid.append([x, y])

                x += grid_size
            y += grid_size

        # Kantenpunkte hinzufügen
        for x in self.create_edge_points(grid_size): 
            index = self.point_to_index(x)
            # Punkt muss gültig sein und
            # Einhaltung des Minimumabstandes zu bereits hinzugefügten Gitterpunkten
            if self.point_ok(x, index, bounding_box, mode=mode) and \
            self.min_distance(x, grid) + self.precision_error > grid_size * self.too_close:
                grid.append(x)

        return grid

    def ilp_solve(self, grid_size, bounding_box, divide, draw=False, mode="") -> None:
        grid = self.create_grid(grid_size, bounding_box, mode=mode)
        circles, radius = self.mode_to_parameter(mode)
        model = LpProblem(name="circle-packing", sense=LpMaximize)

        # binäre Variablen erstellen
        variables = [None] * len(grid)
        for i in range(len(grid)):
            variables[i] = LpVariable(str(i), cat="Binary")

        # Ungleichungen hinzufügen
        for i in range(len(grid)):
            sum_close_variables = 0
            amount_close_variables = 0
            for j in range(len(grid)):
                if i == j:
                    continue
                
                # Wenn sie überschneiden würden
                if math.dist(grid[i], grid[j]) + self.precision_error < 2 * radius:
                    sum_close_variables += variables[j]
                    amount_close_variables += 1

            if amount_close_variables == 0:
                continue

            model += variables[i] * amount_close_variables + sum_close_variables <= amount_close_variables

        cost_function = 0
        for i in range(len(variables)):
            if divide:
                scale_y = 2 * (bounding_box.height - (grid[i][1] - bounding_box.bottom))
                scale_x = 0#bounding_box.width - (grid[i][0] - bounding_box.left)
                cost_function += (1 + (scale_y + scale_x) * self.precision_error) *  variables[i]
            else:
                cost_function += variables[i]

        model += cost_function

        print("Wird gelöst.", "Anzahl an Variablen: ", len(variables))

        # Statusmeldung vllt. noch überprüfen
        status = model.solve(PULP_CBC_CMD(msg=False))  

        # platzierte Kreise der Liste hinzufügen
        for i in range(len(variables)):
            if variables[i].varValue == 1:
                index = self.point_to_index([grid[i][0], grid[i][1]])
                circles[index[0]][index[1]].append([grid[i][0], grid[i][1]])
        
        return model.objective.value()

    # Wrapper around ilp_solve
    def ilp(self, grid_size, mode="", divide=False, width=50, height=50) -> None:
        if divide == True:
            for bb in self.bounding_box.create_smaller_bounding_boxes(width, height):
                self.ilp_solve(grid_size, bb,divide=divide, mode=mode)
        else:
            self.ilp_solve(grid_size, self.bounding_box, divide=divide, mode=mode)

    # Gibt die Anzahl an Siedlungen zurück ein Gesundheitszentrum
    # bei gz_canidate beinhalten würde
    def gz_score(self, gz_candidate) -> int:
        index = self.point_to_index(gz_candidate)
        indices = self.index_to_neighbors(index)
        score = 0

        for index in indices:
            for circle in self.small_circles_spatial[index[0]][index[1]]:
                dist = math.dist(gz_candidate, circle)
                if dist <= self.gz_radius + self.precision_error:
                    score += 1
        return score

    # Gibt den Punkt mit dem besten gefundenen gz_score zurück
    def select_gz(self, step_size) -> None:
        gz = [-1, -1]
        best = 0

        y = self.bounding_box.bottom
        while y < self.bounding_box.top:
            x = self.bounding_box.left
            while x < self.bounding_box.right:
                if self.contains_point([x, y]):
                    result = self.gz_score([x, y])
                    if result >= best:
                        best = result
                        gz = [x, y]
                x += step_size
            y += step_size
        
        self.gz = gz

    # Gibt zurück, ob ein Punkt im Modus mode gültig ist
    def point_ok(self, point, index, bounding_box, mode=""):

        # Nicht innerhalb der Boundingbox?
        if bounding_box.contains_point(point) == False:
            return False

        # Nicht innerhalb des Polygon?
        if self.contains_point(point) == False:
            return False
        
        circles_spatial, radius = self.mode_to_parameter(mode)
        
        # Ist Minimumabstand zu gleichen Kreisen nicht  eingehalten?
        if self.min_distance_spatial(point, index, circles_spatial) \
            + self.precision_error < 2 * radius:
            return False
        

        if mode == "inside":
            # Ist innerhalb des Wirkungsbereich des Gesundheitszentrums
            if math.dist(point, self.gz) > self.gz_radius + self.precision_error:
                return False
        
        if mode == "outside":
            # Ist Minimumabstand zu bereits platzierten
            # kleinen Kreisen nicht eingehalten?
            if self.min_distance_spatial(point, index, self.small_circles_spatial) \
            + self.precision_error < 2 * self.small_radius:
                return False

        return True
    
    # Gibt zurück, ob point innerhalb des Polygon ist
    def contains_point(self, point) -> bool:
        return  self.polygon_path.contains_point(point, radius=self.precision_error) or \
                self.polygon_path.contains_point(point, radius=-self.precision_error)

    # Gibt den geringsten Abstand von point 
    # zu den Punkten aus point_list zurück
    def min_distance(self, point, point_list) -> float:        
        min_dist = 999999
        for i in range(len(point_list)):
            
            dist = math.dist(point, point_list[i])


            if dist is None:
                print("OMGGG")
                return

            if dist < min_dist:
                min_dist = dist
        return min_dist
    
    # Gibt den geringsten Abstand von point 
    # zu den Punkten aus points_spatial einer räumlichen Liste zurück
    def min_distance_spatial(self, point, index, points_spatial):

        # Beinhaltet die Indizes aller umliegenden Quadrate, 
        # sowie der des eigenen
        indices = self.index_to_neighbors(index)

        min_dist = 9999999
        for index in indices:
            min_dist = min(min_dist, self.min_distance(point, points_spatial[index[0]][index[1]]))
        return min_dist

    # Gibt die korrekte räumliche Liste und den Radius der 
    # zu benutzenden Kreise zurück, je nachdem in welchem Modus man ist
    def mode_to_parameter(self, mode) -> tuple[list, int]:
        radius = self.small_radius
        circles = self.small_circles_spatial
        if mode == "outside":
            radius = self.big_radius
            circles = self.big_circles_spatial
        
        return circles, radius
    
    # Gibt für einen Punkt, den Index (Zeile, Spalte) für
    # die räumliche Liste zurück
    def point_to_index(self, point) -> list[int]:
        # Punkt muss relativ zur Boundingbox vorliegen
        point_relative = [self.bounding_box.top - point[1],
                          self.bounding_box.right- point[0]]
        
        indices = [int(point_relative[1] / self.spatial_length),
                   int(point_relative[0] / self.spatial_length)]

        return indices

    # Gibt die Indizes aller umliegenden Quadrate, 
    # sowie den gegebenen Index in einer Liste zurück
    def index_to_neighbors(self, index) -> list[list[int]]:

        indices = [index]

        if index[0] > 0:
            # unten mitte
            indices.append([index[0] - 1, index[1]])
            if index[1] > 0:
                # unten links
                indices.append([index[0] - 1, index[1] - 1]) 
            if index[1] < self.horizontal_amount - 1:
                # unten rechts
                indices.append([index[0] - 1, index[1] + 1])

        if index[0] < self.vertical_amount - 1:
            # oben
            indices.append([index[0] + 1, index[1]])

            if index[1] > 0:
                # oben links
                indices.append([index[0] + 1, index[1] - 1])
            if index[1] < self.horizontal_amount - 1:
                # oben rechts
                indices.append([index[0] + 1, index[1] + 1])

        if index[1] > 0:
            # links
            indices.append([index[0], index[1] - 1])

        if index[1] < self.horizontal_amount - 1:
            # rechts
            indices.append([index[0], index[1] + 1])
        
        return indices