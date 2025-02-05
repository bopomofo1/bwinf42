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

struct cuboid
{
	int x;
	int y;
	int z;
};

std::array<int, 3> readCuboid(std::ifstream& input)
{
	std::array<int, 3> c;
	input >> c[0];
	input >> c[1];
	input >> c[2];
	return c;
}

std::vector<cuboid> generate_orientations(const std::array<int, 3>& c)
{
	if ((c[0] == c[1]) && (c[0] == c[2])) 
	{
		std::vector<cuboid> orientations
		{
			{c[0], c[1], c[2]},
		};
		return orientations;
	}

	else if ((c[0] == c[1]) && (c[0] != c[2])) 
	{
		std::vector<cuboid> orientations
		{
			{c[0], c[1], c[2]},
			{c[0], c[2], c[1]},
			{c[2], c[1], c[0]},
		};
		return orientations;
	}
	
	else if ((c[0] == c[2]) && (c[0] != c[1])) 
	{
		std::vector<cuboid> orientations
		{
			{c[0], c[1], c[2]},
			{c[0], c[2], c[1]},
			{c[1], c[0], c[2]},
		};
		return orientations;
	}

	else if ((c[1] == c[2]) && (c[1]) != c[0])
	{
		std::vector<cuboid> orientations
		{
			{c[0], c[1], c[2]},
			{c[1], c[0], c[2]},
			{c[2], c[1], c[0]},
		};
		return orientations;
	}

	else
	{
		std::vector<cuboid> orientations
		{
			{c[0], c[1], c[2]},
			{c[1], c[0], c[2]},

			{c[0], c[2], c[1]},
			{c[2], c[0], c[1]},

			{c[2], c[1], c[0]},
			{c[1], c[2], c[0]},

		};
		return orientations;
	}
}

int iteration = 0;
int found = false;


void backtracking_box(std::vector<std::vector<std::vector<int>>> box, int x, int y, int z, 
	std::vector<std::vector<int>> cuboidGroupedIndices, const std::vector<std::array<int, 3>>& cuboids, int mid, int size)
{

	if (found) 
	{
		return;
	}

	iteration++;
	//if (iteration % 1000000 == 1)
	//	std::cout << "epoch " << iteration  << " groups " << cuboidGroupedIndices.size() << "\n";

	if (x >= size) 
	{
		x = 0;
		y += 1;
	}
	if (y >= size) 
	{
		y = 0;
		z += 1;
	}

	if (z >= size) 
	{
		std::cout << "Found solution in " << iteration << " steps\n";
		for (int zView = 0; zView < size; zView++) 
		{
			std::cout << "Ebene " << zView << "\n";
			for (int xView = 0; xView < size; xView++)
			{
				for (int yView = 0; yView < size; yView++)
				{
					int value = box[xView][yView][zView];
					if (value == 10000)
						std::cout << std::setw(5) << std::setfill(' ') << "G";
					else
						std::cout << std::setw(5) << std::setfill(' ') << value;
				}
				std::cout << "\n";
			}
			std::cout << "\n";
		}
		found = true;
	}

	if (box[x][y][z] > 0) 
	{
		backtracking_box(box, x + 1, y, z, cuboidGroupedIndices, cuboids, mid, size);
	}
	
	for (int groupIndex = 0; groupIndex < cuboidGroupedIndices.size(); groupIndex++)
	{
		if (cuboidGroupedIndices[groupIndex].size() == 0)
		{
			continue;
		}
		std::vector<cuboid> orientations = generate_orientations(cuboids[cuboidGroupedIndices[groupIndex][0]]);
		for (const auto& o : orientations)
		{
			if (x + o.x > size || y + o.y > size || z + o.z > size) 
			{
				//std::cout << "1\n";
				continue;
			}

			if ((x <= mid && mid <= x + o.x - 1) &&
				(y <= mid && mid <= y + o.y - 1) &&
				(z <= mid && mid <= z + o.z - 1)) 
			{ 
				continue;
			}

			bool canPlace = true;
			for (int xScout = 0; xScout < o.x; xScout++) 
			{
				
					if (box[x + xScout][y][z] > 0)
					{
						canPlace = false;
					}
			
			}

			if (canPlace) 
			{
				auto boxCopy(box);
				for (int xScout = 0; xScout < o.x; xScout++)
				{
					for (int yScout = 0; yScout < o.y; yScout++)
					{
						for (int zScout = 0; zScout < o.z; zScout++) 
						{
							boxCopy[x + xScout][y + yScout][z + zScout] = cuboidGroupedIndices[groupIndex].back() + 1;
						}
					}
				}

				auto cuboidGroupedIndicesCopy(cuboidGroupedIndices);
				cuboidGroupedIndicesCopy[groupIndex].pop_back();

				backtracking_box(boxCopy, x + 1, y, z, cuboidGroupedIndicesCopy, cuboids, mid, size);
			}

		}
	}
}

int main() 
{
	std::ifstream example;
	example.open("raetsel1.txt");

	std::locale dt("de_DE.utf-8");
	std::locale::global(dt);
	SetConsoleOutputCP(65001);

	if (!example.is_open())
	{
		std::cout << "couldn't open file\n";
		return -1;
	}


	
	int size = readCuboid(example)[0];
	int mid = size / 2;
	int k;
	example >> k;

	std::vector<std::array<int, 3>> cuboids(k);
	for (int i = 0; i < k; i++) 
	{
		cuboids[i] = readCuboid(example);
	}

	std::vector<std::vector<int>> cuboidsGrouped;
	std::vector<std::vector<std::vector<int>>> groupMapping(size, std::vector<std::vector<int>>(size, std::vector<int>(size, -1)));
	
	for (int i = 0; i < cuboids.size(); i++) 
	{
		std::sort(cuboids[i].begin(), cuboids[i].end());
		std::cout << " x " << cuboids[i][0] << " y " << cuboids[i][1] << " z " << cuboids[i][2] << "\n";

		if (groupMapping[cuboids[i][0] - 1][cuboids[i][1] - 1][cuboids[i][2] - 1] > - 1)
		{
			cuboidsGrouped[groupMapping[cuboids[i][0] - 1][cuboids[i][1] - 1][cuboids[i][2] - 1]].push_back(i);
		}
		else 
		{
			cuboidsGrouped.push_back(std::vector<int>{{i}});
			groupMapping[cuboids[i][0] - 1][cuboids[i][1] - 1][cuboids[i][2] - 1] = cuboidsGrouped.size() - 1;
		}

	}

	std::cout << "size: " << size << "\n";
	std::cout << "mid: " << mid << "\n";

	
	std::vector<std::vector<std::vector<int>>> box(size, std::vector<std::vector<int>>(size, std::vector<int>(size, 0)));

	box[mid][mid][mid] = 10000;
	std::vector<int> cuboidIndices(cuboids.size());
	for (int i = 0; i < cuboidsGrouped.size(); i++) 
	{
		for (auto c : cuboidsGrouped[i]) 
		{
			std::cout << "i: " << c + 1 << " | " << cuboids[c][0] << " " << cuboids[c][1] << " " << cuboids[c][2] << " " << "\n";
		}
		
	}

	

	backtracking_box(box, 0, 0, 0, cuboidsGrouped, cuboids, mid, size);
	if (found == false ) 
	{
		std::cout << "keine Loesung gefunen\n";
	}

}