class Graph():
    def __init__(self, amount_nodes):
        self.adj_list = [[] for _ in range(amount_nodes)]
        
    def add_edge(self, start, end):
        self.adj_list[start].append(end)
    
    def bron_kerbosch(self, P, R=set(), X=set()):

        # Ist P und X leer haben wir eine maximale Clique gefunden
        if not P and not X:
            yield R

        # Pivot Element auswählen
        best = 0
        pivot = -1
        for v in P.union(X):
            if len(self.adj_list[v]) >= best:
                pivot = v
                best = len(self.adj_list)

        # Über alle Knoten in P, 
        # die nicht Nachbarn vom Pivotelement sind iterieren
        for v in P.difference(self.adj_list[pivot]):
            # Rekursiver Aufruf
            yield from self.bron_kerbosch(
                    R=R.union([v]), 
                    P=P.intersection(self.adj_list[v]), 
                    X=X.intersection(self.adj_list[v]))
            
            P.remove(v)
            X.add(v)