import matplotlib.pyplot as plt

def PlotGrid(ax, grid_size, start=None, goal=None, path=None, obstacles=None, fixed_grid=None):
    ax.clear()  # Clear the current plot

    for x in range(grid_size + 1):
        ax.axhline(y=x, color='gray', linestyle='--', linewidth=0.5)
        ax.axvline(x=x, color='gray', linestyle='--', linewidth=0.5)

    for x in range(grid_size):
        ax.axhline(y=x + 0.5, color='lightgray', linestyle='-', linewidth=0.5)
        ax.axvline(x=x + 0.5, color='lightgray', linestyle='-', linewidth=0.5)

    for (x, y), connections in fixed_grid.items():
        for (cx, cy) in connections:
            if 0 <= cx <= grid_size and 0 <= cy <= grid_size:
                ax.plot([x, cx], [y, cy], 'ro-', markersize=5)

    if path:
        for i in range(len(path) - 1):
            x0, y0 = path[i]
            x1, y1 = path[i + 1]
            ax.plot([x0, x1], [y0, y1], 'g-', linewidth=2)

    if start:
        ax.plot(start[0], start[1], 'bo', markersize=10)
    if goal:
        ax.plot(goal[0], goal[1], 'mo', markersize=10)

    if obstacles:
        for obs in obstacles:
            ax.plot(obs[0], obs[1], 'ks', markersize=10)

    ax.set_xlim(-1, grid_size + 1)
    ax.set_ylim(-1, grid_size + 1)
    ax.set_xticks(range(grid_size + 1))
    ax.set_yticks(range(grid_size + 1))
    ax.set_xlabel('X')
    ax.set_ylabel('Y')

    ax.set_yticks(range(grid_size, -1, -1))
    ax.set_yticklabels(range(grid_size, -1, -1))

    ax.set_aspect('equal')
    ax.grid(True)
    plt.draw()
    plt.pause(0.001)
