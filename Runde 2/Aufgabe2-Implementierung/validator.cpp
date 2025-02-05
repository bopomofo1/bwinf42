#include <iostream>
#include <vector>
#include <fstream>
#include <sstream>


int main(int argc, char* argv[]) 
{
    using std::cout, std::string, std::vector;

    if (argc < 3) 
    {
        cout << "Nicht genügend Argumente.\n";
        return -1;
    }

    std::ifstream input {argv[1]};
    if (not input.is_open()) 
    {
        cout << "Input Datei konnte nicht geöffnet werden.\n";
        return -1;
    }
    string zeile;
    std::getline(input, zeile);
    std::istringstream iss(zeile);
    int anzahl_sorten, anzahl_stilrichtungen;
    iss >> anzahl_sorten >> anzahl_stilrichtungen;

    if (argc < 4)
    {
        cout << "Anzahl Sorten: " << anzahl_sorten << "\n";
        cout << "Anzahl Stilrichtungen: " << anzahl_stilrichtungen << "\n\n";

        std::cout << "Verbindungen:\n";
    }
    vector<vector<bool>> adjacency_matrix (anzahl_stilrichtungen, vector<bool>(anzahl_stilrichtungen));

    for (int x = 0; x < anzahl_stilrichtungen; x++) 
    {
        adjacency_matrix[x][x] = true;
    }

    while (std::getline(input, zeile) && not zeile.empty()) 
    {
        std::istringstream iss(zeile);
        int x, y;
        iss >> x >> y;
        if (argc < 4)
            cout << x << " - " << y << "\n";
        adjacency_matrix[x - 1][y - 1] = true;
        adjacency_matrix[y - 1][x - 1] = true;
    }

    if (argc < 4) 
    {
        cout << "\nKleidungsstücke:\n";
    }
    vector<vector<int>> kleidung_insgesamt (anzahl_sorten, vector<int> (anzahl_stilrichtungen));
    int anzahl_kleidung = 0;
    while (std::getline(input, zeile) && not zeile.empty()) 
    {
        std::istringstream iss(zeile);
        int sorte, stilrichtung, anzahl;
        iss >> sorte >> stilrichtung >> anzahl;
            
        if (argc < 4) 
        {
            cout << sorte << ", " << stilrichtung << ", " << anzahl << "\n";
        }
        kleidung_insgesamt[sorte - 1][stilrichtung - 1] = anzahl;
        anzahl_kleidung += anzahl;
    }
    input.close();

    std::ifstream answer {argv[2]};
    if (not answer.is_open()) 
    {
        cout << "Antwort Datei konnte nicht geöffnet werden.\n";
        return -1;
    }

    if (argc < 4) 
    {
        cout << "Zusammengestellte Boxen:\n";
    }
    int anzahl_boxen = 0;
    int anzahl_kleidung_benutzt = 0;
    vector<vector<int>> box;
    while (std::getline(answer, zeile)) 
    {
        if (zeile.empty()) 
        {   
            anzahl_boxen++;
            // Passen die Stilrichtungen zusammen?
            vector<int> inhalt (anzahl_sorten);
            for (int i = 0; i < box.size(); i++) 
            {
                inhalt[box[i][0]] += box[i][2];
                for (int j = i + 1; j < box.size(); j++) 
                {
                    if (adjacency_matrix[box[i][1]][box[j][1]] == false) 
                    {
                        cout << "X " << box[i][1] << " Y " << box[j][1] << "\n"; 
                        cout << "Kleidungsstücke passen nicht zusammen!\n";
                        return EXIT_FAILURE;
                    }
                }
            }

            int min = *std::min_element(inhalt.begin(), inhalt.end());
            int max = *std::max_element(inhalt.begin(), inhalt.end());

            if (max > 3) 
            {
                cout << "Größer 3!\n";
                return EXIT_FAILURE;
            }

            if (min == 0) 
            {
                cout << "Nicht genügend Platz in der Box!\n";
                return EXIT_FAILURE;
            }
            if (argc < 4)
                ;//cout << "\n";
            box.clear();
            continue;
        }

        std::istringstream iss(zeile);
        int sorte, stilrichtung, anzahl;
        iss >> sorte >> stilrichtung >> anzahl;
        if (argc < 4) 
        {
            ;//cout << sorte << " " << stilrichtung << " " << anzahl << "\n";
        }
        box.push_back({sorte - 1, stilrichtung - 1, anzahl});
        anzahl_kleidung_benutzt += anzahl;

        // Mehr benutzt als da ist?
        kleidung_insgesamt[sorte - 1][stilrichtung - 1] -= anzahl;
        if (kleidung_insgesamt[sorte - 1][stilrichtung - 1] < 0) 
        {
            cout << "Zu viele Kleidungsstücken benutzt!\n";
            return -1;
        }
    }
    if (argc < 4) 
    {
        cout << anzahl_boxen <<  " Boxen zusammengesellt\n";
        cout << anzahl_kleidung_benutzt << "/" << anzahl_kleidung << " Kleidungsstücken benutzt\n";
    }
    cout << anzahl_kleidung_benutzt << "/" << anzahl_kleidung;
    return 0;
}