#include <iostream>
#include <fstream>
#include <string>
#include <Windows.h>
#include <vector>
#include <sstream>
#include <unordered_map>

struct tourpoint 
{
	std::string name;
	int year;
	bool essential;
	int culminated;
};

struct tour 
{
	int start;
	int end;
	int distance;
};

int iteration = 0;
void generate_combinations(const std::vector<tour>& tours, std::vector<std::vector<tour>>& combinations, std::vector<tour> curr, int i)
{
	//std::cout << tours.size() << " size\n";
	//std::cout << "epoch: " << iteration << "\n";
	iteration++;

	if (i >= tours.size())
	{
		if (curr.size() > 0)
		{
			combinations.push_back(curr);
		}
		return;
	}

	// take it or leave it
	generate_combinations(tours, combinations, curr, i + 1);
	
	if (curr.size() > 0)
	{
		// no intersection 
		if (tours[i].start >= curr[curr.size()-1].end) 
		{
			curr.push_back(tours[i]);
		}
	}
	else 
	{
		curr.push_back(tours[i]);
	}
	generate_combinations(tours, combinations, curr, i + 1);
}

int main() 
{
	std::ifstream example;
	example.open("tour5.txt");

	std::locale dt("de_DE.utf-8");
	std::locale::global(dt);
	SetConsoleOutputCP(65001);

	if (!example.is_open()) 
	{
		std::cout << "couldn't open file\n";
		return -1;
	}

	std::string line;
	std::getline(example, line);
	std::getline(example, line);
	int n = std::stoi(line);
	std::cout << "n " << n << "\n";

	std::vector<tourpoint> tourpoints;
	tourpoints.resize(n);

	std::unordered_map<std::string, int> tourMap;
	std::vector<tour> tours;


	// input, split and teiltour classification
	int last_essential = -1;
	for (int i = 0; i < n; i++)
	{
		
		std::getline(example, line);
		std::vector<std::string> split;
		std::stringstream ss(line);
		while (ss.good()) {
			std::string substr;
			std::getline(ss, substr, ',');
			split.push_back(substr);
		}

		tourpoints[i] = { split[0], std::stoi(split[1]), split[2] == "X", std::stoi(split[3]) };


		if (!tourMap.contains(tourpoints[i].name)) 
		{
			tourMap[tourpoints[i].name] = i;
		}
		else 
		{
			int start = tourMap[tourpoints[i].name];
			int end = i;
			tourMap[tourpoints[i].name] = end;
			if (last_essential <= start || last_essential > end)
			{	
				tours.push_back({ start, end, tourpoints[end].culminated - tourpoints[start].culminated });
			}	
		}

		if (tourpoints[i].essential) 
		{
			last_essential = i;
		}
	}
	example.close();

	std::vector<std::vector<tour>> combinations;
	std::vector<tour> curr{};
	generate_combinations(tours, combinations, curr, 0);

	



	int max_index = 0;
	int max = 0;
	for (int c = 0; c < combinations.size(); c++) 
	{
		int curr{};
		for (auto x : combinations[c])
		{
			curr += x.distance;
		}
		if (curr > max) 
		{
			max = curr;
			max_index = c;
		}
	}


	std::cout << "(";
	for (auto x : combinations[max_index])
	{
		std::cout << tourpoints[x.start].name << ", ";
		tourpoints[x.start].culminated = -2;
		tourpoints[x.end].culminated = -2;
		for (auto i = x.start+1; i < x.end; i++) 
		{
			tourpoints[i].culminated = -1;
		}
	}
	std::cout << ")\n";

	// graphics
	for (auto x : tours)
	{
		std::cout << x.distance << " ";
		for (int i = 0; i < x.start; i++)
		{
			std::cout << " ";
		}
		
		if (tourpoints[x.start].culminated == -2) 
		{
			std::cout << "\x1B[31m" << tourpoints[x.start].name[0] << "\033[0m";
		}
		else
		{
			std::cout << tourpoints[x.start].name[0];
		}
		

		for (int i = x.start + 1; i < x.end; i++)
		{
			std::cout << " ";
		}

		if (tourpoints[x.end].culminated == -2)
		{
			std::cout << "\x1B[31m" << tourpoints[x.end].name[0] << "\033[0m\n";
		}
		else
		{
			std::cout << tourpoints[x.end].name[0] << "\n";
		}
	}


	for (const auto& point : tourpoints) 
	{
		if (point.culminated == -1) 
		{
			std::cout << "(" << point.name << " " << point.year << ")\n";
			continue;
		}
		std::cout << point.name << " " << point.year << "\n";
	}



}