import sys
from input_output import read_input, write_output
from graph import Graph
from clique import Clique, add_first_constraint, add_n_boxes_constraint, get_n_boxes
from pulp import LpMaximize, LpProblem, LpStatus, lpSum, LpVariable
from pulp import PULP_CBC_CMD
from timeit import default_timer as timer

start = timer()

modes = ["ilp-quadratic", "ilp-linear", "milp"]
mode = sys.argv[1]
if mode not in modes:
    print("Verfügbare Modi sind:", modes)
    exit()

variable_type = "Integer"
if mode == modes[2]:
    variable_type = "Continuous"

amount_categories, amount_styles, edges, inventory = read_input(sys.argv[2])

# Stilgraphen erstellen
graph = Graph(amount_styles)
for edge in edges:
    graph.add_edge(edge[0], edge[1])
    graph.add_edge(edge[1], edge[0])

# maximale Cliquen finden
maximal_cliques = list(graph.bron_kerbosch(P=set([node for node in range(amount_styles)])))

model = LpProblem(name="Do-something", sense=LpMaximize)

# Cliquenobjekte erstellen
cliques = []
for id, clique_styles in enumerate(maximal_cliques):
    cliques.append(Clique(amount_categories, amount_styles, clique_styles, inventory, variable_type, id))

# Kostenfunktion hinzufügen
cost_expression = 0
for clique in cliques:
    for category in range(amount_categories):
        for style in range(amount_styles):
            if clique.variables[category][style] is not None:
                cost_expression += clique.variables[category][style] 
model += cost_expression


# Constraint (1) hinzufügen
add_first_constraint(model, cliques, amount_categories, amount_styles, inventory)

# Constraint(2) hinzufügen
for clique in cliques:
    if mode == modes[0]:
        clique.add_second_constraint_quadratic(model)
    else:
        clique.add_second_constraint_linear(model)

# N Boxen Constraint hinzufügen
#n = 50
#add_n_boxes_constraint(model, n, cliques)

status = model.solve(PULP_CBC_CMD(msg=True))

print("Modus:", mode)

if model.status == -1:
    print("konnte nicht gelöst werden")
    exit()

for clique in cliques:
    if clique.is_integral() == False:
        print("Alarmstufe Rot, ALARMSTUFE ROT")
        exit(1)

print(f"status: {model.status}, {LpStatus[model.status]}")

print("benutzte Kleidungsstücke:",model.objective.value())

# (Falls N) genau N Boxen erstellen
#boxes =get_n_boxes(n, cliques)
boxes = []
for clique in cliques:
    boxes = boxes + clique.get_boxes()


print("erstellte Boxen:", len(boxes))

write_output(sys.argv[3], boxes)

end = timer()
print("Dauer:",round(end - start, 5), "s")
