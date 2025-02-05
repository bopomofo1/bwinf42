#include <iostream>
#include <fstream>
#include <string>
#include <Windows.h>
#include <vector>
#include <sstream>
#include <unordered_map>
#include <map>
#include <array>
#include<algorithm>
#include <iomanip>

// Z geht von 1 (Stockwerk 1), 2 (Decke), 3(Decke), 4 (Stockwerk2)
struct Punkt 
{
	int x, y, z;
};

std::vector<std::string> stockwerk_einlesen(std::ifstream& datei, int hoehe)
{
	std::vector<std::string> stockwerk(hoehe);
	std::string zeile;
	for (int i = 0; i < hoehe; i++)
	{
		std::getline(datei, zeile);
		stockwerk[i] = zeile;
	}
	std::getline(datei, zeile);
	return stockwerk;
}

void stockwerk_anzeigen(const std::vector<std::string>& stockwerk) 
{
	for (auto zeile : stockwerk) 
	{
		std::cout << zeile << "\n";
	}
}

Punkt start_finden(const std::vector<std::vector<std::string>>& bugwarts) 
{
	for (int z = 0; z < bugwarts.size(); z++) 
	{
		for (int y = 0; y < bugwarts[z].size(); y++) 
		{
			for (int x = 0; x < bugwarts[z][y].length(); x++) 
			{
				if (bugwarts[z][y][x] == 'A')
					return Punkt{ x, y, z };
			}
		}
	}
}

int main()
{
	std::ifstream datei;
	datei.open("zauberschule0.txt");

	std::locale dt("de_DE.utf-8");
	std::locale::global(dt);
	SetConsoleOutputCP(65001);

	if (!datei.is_open())
	{
		std::cout << "couldn't open file\n";
		return -1;
	}
	int hoehe, breite;
	datei >> hoehe >> breite;

	std::cout << "hoehe: " << hoehe << "\nbreite: " << breite << "\n";

	std::string tmp;
	std::getline(datei, tmp);
	auto stockwerk1 = stockwerk_einlesen(datei, hoehe);
	std::cout << "\nStockwerk1:\n";
	stockwerk_anzeigen(stockwerk1);
	auto stockwerk2 = stockwerk_einlesen(datei, hoehe);
	std::cout << "\nStockwerk2:\n";
	stockwerk_anzeigen(stockwerk2);

	Punkt A = start_finden({ stockwerk1, stockwerk2 });
	std::cout << "Start bei: " << A.x << " " << A.y << " " << A.z << " ";

}