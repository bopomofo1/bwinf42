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

std::vector<std::string> readInput(std::ifstream& file, int height) 
{
	std::vector<std::string> inputMatrix;
	for (int i = 0; i < height; i++)
	{
		std::string line;	
		std::getline(file, line);
		line.erase(remove(line.begin(), line.end(), ' '), line.end());
		line.erase(remove(line.begin(), line.end(), 'Q'), line.end());
		line.erase(remove(line.begin(), line.end(), 'L'), line.end());
		inputMatrix.push_back(line);
	}
	return inputMatrix;
}

struct Field 
{
	int pos;
	bool active;
};

void generateInputStates(int amount, std::vector<std::vector<bool>>& states, std::vector<bool> currentState, int i)
{
	i++;
	if (i == amount)
	{
		states.push_back(currentState);
		return;
	}
	generateInputStates(amount, states, currentState, i);
	currentState[i] = true;
	generateInputStates(amount, states, currentState, i);
}

void calculateOutput(std::vector<std::string> inputMatrix, const std::vector<Field>& inputs, std::vector<Field>& outputs, int height, int width)
{
	std::vector<std::vector<bool>> zustand(height, std::vector<bool>(width));
	
	for (auto& input : inputs)
	{
		zustand[0][input.pos] = input.active;
	}

	for (int y = 1; y < height - 1; y++)
	{
		for (int x = 0; x < width; x++)
		{
			switch (inputMatrix[y][x])
			{
			case 'W':
				if (!(zustand[y - 1][x] && zustand[y - 1][x + 1]))
				{
					zustand[y][x] = true;
					zustand[y][x + 1] = true;
				}
				x += 1;
				break;

			case 'r':
				if (!zustand[y - 1][x + 1])
				{
					zustand[y][x] = true;
					zustand[y][x + 1] = true;
				}
				x += 1;
				break;

			case 'R':
				if (!zustand[y - 1][x])
				{
					zustand[y][x] = true;
					zustand[y][x + 1] = true;
				}
				x += 1;
				break;

			case 'B':
				if (zustand[y - 1][x])
				{
					zustand[y][x] = true;
				}
			}
		}
	}

	for (auto row : zustand) 
	{
		
		for (auto element : row)
		{
			//std::cout << element << " | ";
		}
		//std::cout << "\n";
		
	}


	for (auto& output : outputs)
	{
		output.active = zustand[height - 2][output.pos];
	}
}


int main()
{
	std::ifstream example;
	example.open("nandu1.txt");

	std::locale dt("de_DE.utf-8");
	std::locale::global(dt);
	SetConsoleOutputCP(65001);

	if (!example.is_open())
	{
		std::cout << "couldn't open file\n";
		return -1;
	}
	int width;
	int height;

	example >> width >> height;
	std::cout << "width: " << width << "\nheight: " << height << "\n";

	std::string tmp;
	std::getline(example, tmp);
	auto inputMatrix = readInput(example, height);
	std::vector<std::vector<bool>> zustand(height, std::vector<bool>(width));
	std::vector<Field> inputs;
	std::vector<Field> outputs;

	
	
	for (int x = 0; x < width; x++) 
	{
		if (inputMatrix[0][x] != 'X') 
		{
			inputs.push_back({ x, false });
		}
		if (inputMatrix[height-1][x] != 'X') 
		{
			outputs.push_back({ x, false });
		}
	}


	std::vector<std::vector<bool>> allInputStates;
	std::vector<bool> tmpCurrentState (inputs.size());
	generateInputStates(inputs.size(), allInputStates, tmpCurrentState, -1);

	std::cout << "generated " << allInputStates.size() << " inputStates\n";

	for (auto input : inputs) 
		std::cout << 'Q' << inputMatrix[0][input.pos] << " ";
	for (auto output : outputs)
		std::cout << 'L' << inputMatrix[height-1][output.pos] << " ";

	


	std::cout << "\n";

	for (auto inputState : allInputStates)
	{
		for (int x = 0; x < inputs.size(); x++)
		{
			inputs[x].active = inputState[x];
		}
		//std::cout << "\n";
		calculateOutput(inputMatrix, inputs, outputs, height, width);
		//std::cout << "\n";
		for (auto& input : inputs)
		{
			std::cout << input.active << "    ";
		}
		for (auto& output : outputs) 
		{	
			std::cout << output.active << "    ";
			output.active = false;
		}


		std::cout << "\n";
	}

}