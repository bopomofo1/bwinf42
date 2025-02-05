from pulp import LpVariable, LpAffineExpression
import math

class Clique():
    def __init__(self, amount_categories, amount_styles, useable_styles, inventory, variable_type, id):
        self.amount_categories = amount_categories
        self.amount_styles = amount_styles
        
        self.variables = [[None 
                        for _ in range(amount_styles)] 
                        for _ in range(amount_categories)]
        
        # Als Praefix für die Namen der Variablen
        self.id = id

        self.useable_styles = useable_styles
        
        # LpVariablen erstellen
        for style in useable_styles:
            for category in range(amount_categories):
                if inventory[category][style] > 0:
                    name = str(id) + "_" + str(category) + "_" + str(style)
                    self.variables[category][style] = LpVariable(name=name, lowBound=0, cat=variable_type)

        min_max_type = "Integer"
        if variable_type == "Integer":
            min_max_type = "Continuous"
        
        # Werden zwar immer erstellt, jedoch bei ilp-squared nicht dem Modell hinzugefügt
        self.min_variable = LpVariable(name=str(id) + "_min", lowBound=0, cat=min_max_type)
        self.max_variable = LpVariable(name=str(id) + "_max", lowBound=0, cat=min_max_type)


    # Gibt zurück die Summe aller Variablen dieser Sorte
    def category_sum(self, category) -> LpAffineExpression:
        sum = 0
        for style in self.useable_styles:  
            if self.variables[category][style] is not None:
                sum += self.variables[category][style]
        return sum       
    
    # Gibt zurück für jede Sorte die Anzahl an Kleidungsstücken 
    def categories_total(self) -> list[int]:
        total = [0 for i in range(self.amount_categories)]
        for category in range(self.amount_categories):
            for style in self.useable_styles:
                if self.variables[category][style] is not None:
                    total[category] += self.variables[category][style].varValue
        return total
    
    def add_second_constraint_quadratic(self, model):
        cache = [self.category_sum(category) for category in range(self.amount_categories)]
        for constraint_category in range(self.amount_categories):
            for category in range(self.amount_categories):
                if category == constraint_category:
                    continue
                model += cache[constraint_category] <= 3 * cache[category]
    
    def add_second_constraint_linear(self, model):
        for category in range(self.amount_categories):
            sum = self.category_sum(category)
            model += self.min_variable <= sum
            model += self.max_variable >= sum
        model += self.max_variable <= 3 * self.min_variable

    def get_boxes(self, amount=None) -> list[list[list[int]]]:
        categories_total = self.categories_total()

        remaining_amount = min(categories_total) 
        if amount is not None:
            remaining_amount = amount
        
        boxes = []

        while remaining_amount > 0:
            box = []

            for category in range(self.amount_categories):

                # Soviel nehmen das wir danach noch remaing_amount-1 Boxen erstellen können
                take = min(categories_total[category] - (remaining_amount - 1), 3)
                for style in self.useable_styles:
                    if take == 0:
                        break
                    elif self.variables[category][style] is None:
                        continue
                    elif int(self.variables[category][style].varValue) == 0:
                        continue

                    took = int(min(self.variables[category][style].varValue, take))

                    take -= took
                    self.variables[category][style].varValue -= took
                    categories_total[category] -= took

                    #print(took)


                    box.append([category + 1, style + 1, took])

            boxes.append(box) 
            remaining_amount -= 1
        return boxes

    # Gibt zurück, ob alle relevanten LpVariablen ganzzahlig sein
    def is_integral(self) -> bool:
        for category in range(self.amount_categories):
            for style in self.useable_styles:
                if (self.variables[category][style] is not None):
                    if self.variables[category][style].varValue.is_integer() == False:
                        return False
        return True

def add_first_constraint(model, cliques, amount_categories, amount_styles, inventory):
    for category in range(amount_categories):
        for style in range(amount_styles):
            sum = 0
            for clique in cliques:
                if clique.variables[category][style] is not None:
                    sum += clique.variables[category][style]
            
            model += sum <= inventory[category][style]

def add_n_boxes_constraint(model, n, cliques):
    min_amount_boxes = 0
    max_amount_boxes = 0

    for clique in cliques:
        min_amount_boxes += clique.max_variable
        max_amount_boxes += clique.min_variable
    
    model += n >= min_amount_boxes / 3
    model += n <= max_amount_boxes 

def get_n_boxes(n, cliques):
    boxes = []
    
    cliques_min_amount = []
    cliques_max_amount = []
    for i in range(len(cliques)):
        categories_total = cliques[i].categories_total()
        cliques_min_amount.append(math.ceil(max(categories_total) / 3))
        cliques_max_amount.append(min(categories_total))

    # Wie viel insgesamt zusätzlich zur minimalen Anzahl an Boxen
    # genommen werden soll
    d = n - sum(cliques_min_amount)

    for i in range(len(cliques)):
        spielraum = cliques_max_amount[i] - cliques_min_amount[i]
        extra = min(d, spielraum)

        boxes = boxes + cliques[i].get_boxes(amount= extra + cliques_min_amount[i])
        d -= extra
        
    return boxes