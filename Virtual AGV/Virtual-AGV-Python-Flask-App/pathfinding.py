import copy
from queue import PriorityQueue

import pandas as pd


def ReadGrid(file_path):
    def process_connected_nodes(connected_nodes_str):
        connected_nodes_str = connected_nodes_str.strip()[1:-1]
        node_pairs = connected_nodes_str.split("),(")
        return [tuple(map(int, pair.split(","))) for pair in node_pairs]

    df = pd.read_excel(file_path)
    fixed_grid = {}

    for index, row in df.iterrows():
        node = tuple(map(int, row["Node"].strip("()").split(",")))
        connected_nodes_list = process_connected_nodes(row["Connected Nodes"])
        fixed_grid[node] = connected_nodes_list

    return fixed_grid


def CalculatePath(start, goal, grid):
    print("Calculating path from", start, "to", goal)

    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    open_list = PriorityQueue()
    g_score = {node: float("inf") for node in grid.keys()}
    rhs = {node: float("inf") for node in grid.keys()}

    g_score[goal] = float("inf")
    rhs[goal] = 0
    open_list.put((heuristic(start, goal), goal))

    def calculate_key(node):
        return min(g_score[node], rhs[node]) + heuristic(start, node)

    came_from = {}

    while not open_list.empty():
        current = open_list.get()[1]

        if g_score[current] > rhs[current]:
            g_score[current] = rhs[current]
            for neighbor in grid.get(current, []):
                tentative_rhs = g_score[current] + 1
                if tentative_rhs < rhs.get(neighbor, float("inf")):
                    rhs[neighbor] = tentative_rhs
                    came_from[neighbor] = current
                    open_list.put((calculate_key(neighbor), neighbor))
        else:
            g_score[current] = float("inf")
            for neighbor in grid.get(current, []):
                if came_from.get(neighbor) == current:
                    rhs[neighbor] = min([g_score[n] + 1 for n in grid.get(neighbor, [])])
                    open_list.put((calculate_key(neighbor), neighbor))

    path = []
    node = start
    while node != goal:
        path.append(node)
        if node not in came_from:
            return []  # Return empty path if no valid path exists
        node = came_from[node]
    path.append(goal)
    print("Returning path")
    return path


def RecalculatePath(obstacles, current_node, goal, fixed_grid):
    grid = copy.deepcopy(fixed_grid)
    if obstacles:
        obstacles = [tuple(obstacle) for obstacle in obstacles]
        for obs in obstacles:
            grid.pop(obs, None)
            for node, connections in grid.items():
                if obs in connections:
                    grid[node].remove(obs)

    new_path = CalculatePath(current_node, goal, grid)
    return new_path
