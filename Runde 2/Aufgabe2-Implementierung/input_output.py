
def read_input(filename):
    with open(filename) as f:
        content = f.readlines()

    anzahl_sorten, anzahl_stilrichtungen = list(map(int, content[0].split()))

    # Einlesen der Kompatibilitäten bis zur nächsten leeren Zeile.
    edges = []
    index = 1
    while index < len(content):
        if (content[index].strip() == ''):
            break

        x, y = list(map(int, content[index].split()))
        edges.append([x - 1, y - 1])
        index += 1

    index += 1 # Schleife hat bei einer leeren Zeile aufgehört

    # Erstellt eine 2d Liste in der Form Sorten(Stilrichtungen) 
    # die für alle Kleidungsstücke deren gegebene Anzahl speichert. 
    vorrat = [[0 for x in range(anzahl_stilrichtungen)] for y in range(anzahl_sorten)] 

    # Einlesen der verfügbaren Kleidungsstücken
    while index < len(content):
        if (content[index].strip() == ''):
            break

        sorte, stilrichtung, anzahl = list(map(int, content[index].split()))
        vorrat[sorte - 1][stilrichtung - 1] = anzahl
        index += 1 
    
    return (anzahl_sorten, anzahl_stilrichtungen, edges, vorrat)

def write_output(filename, boxes):
    output = open(filename, "w")

    # Boxen in Output Datei schreiben
    for box in boxes:
        for [typ, style, amount] in box: 
            output.write(str(typ) + " " + str(style) + " " + str(amount) + "\n")
            print(str(typ) + " " + str(style) + " " + str(amount))
        print("")
        output.write("\n")

    output.close()