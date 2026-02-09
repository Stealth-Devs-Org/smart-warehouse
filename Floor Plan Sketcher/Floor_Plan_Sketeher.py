import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import filedialog

# Function to read the grid from an Excel file
def ReadGrid(file_path):
    def process_connected_nodes(connected_nodes_str):
        connected_nodes_str = connected_nodes_str.strip()[1:-1]
        node_pairs = connected_nodes_str.split('),(')
        return [tuple(map(int, pair.split(','))) for pair in node_pairs]
    
    df = pd.read_excel(file_path)
    fixed_grid = {}
    for index, row in df.iterrows():
        node = tuple(map(int, row['Node'].strip('()').split(',')))
        connected_nodes_list = process_connected_nodes(row['Connected Nodes'])
        fixed_grid[node] = connected_nodes_list

    return fixed_grid

# Function to plot the entire grid
def plot_entire_grid(grid, grid_size_x=32, grid_size_y=28):
    fig, ax = plt.subplots(figsize=(12, 15))

    # Plot main grid lines (dashed)
    for x in range(grid_size_x + 1):
        ax.axhline(y=x, color='gray', linestyle='--', linewidth=0.5)
        ax.axvline(x=x, color='gray', linestyle='--', linewidth=0.5)

    # Plot connections
    for (x, y), connections in grid.items():
        for (cx, cy) in connections:
            ax.plot([x, cx], [y, cy], 'ro-', markersize=5)  # Red lines with circle markers

    ax.set_xlim(-1, grid_size_x + 1)
    ax.set_ylim(-1, grid_size_y + 1)
    ax.set_xticks(range(grid_size_x + 1))
    ax.set_yticks(range(grid_size_y + 1))
    ax.set_xlabel('X')
    ax.set_ylabel('Y')

    # Set y-ticks to match the descending axis
    ax.set_yticks(range(grid_size_y, -1, -1))
    ax.set_yticklabels(range(grid_size_y, -1, -1))

    ax.set_aspect('equal')
    ax.grid(True)
    
    # Store the initial view limits
    ax.initial_xlim = (-1, grid_size_x + 1)
    ax.initial_ylim = (-1, grid_size_y + 1)
    
    return fig, ax

# Function to handle adding points
def add_point():
    global mode
    mode = 'add'
    print("Mode: Add Point")

# Function to handle erasing points
def erase_point():
    global mode
    mode = 'erase'
    print("Mode: Erase Point")

# Function to handle connecting points
def connect_points():
    global mode
    mode = 'connect'
    print("Mode: Connect Points")

# Function to handle saving the grid to an Excel file
def save_to_excel():
    # Prompt user to select file path and name
    file_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx")],
        title="Save As"
    )
    
    if file_path:
        # Ensure the file extension is .xlsx
        if not file_path.lower().endswith('.xlsx'):
            file_path += '.xlsx'
        
        # Prepare data for saving
        data = {'Node': [], 'Connected Nodes': []}
        for node, connections in grid.items():
            data['Node'].append(f"({node[0]},{node[1]})")
            connected_nodes_str = ','.join([f"({c[0]},{c[1]})" for c in connections])
            data['Connected Nodes'].append(connected_nodes_str)
        
        df = pd.DataFrame(data)
        
        try:
            # Use the openpyxl engine to handle .xlsx files
            df.to_excel(file_path, index=False, engine='openpyxl')
            print(f"Grid saved to {file_path}")
        except Exception as e:
            print(f"Error saving file: {e}")

# Function to handle mouse clicks for interaction
def on_click(event):
    global selected_points, mode, erased_points
    if event.inaxes is None:  # Ignore clicks outside the plot area
        return

    x, y = int(round(event.xdata)), int(round(event.ydata))
    
    if mode == 'add':
        # Add a new point
        if (x, y) not in grid:
            grid[(x, y)] = []
            ax.plot(x, y, 'bo', markersize=10)  # Blue point
            print(f"Added point: ({x}, {y})")
    
    elif mode == 'erase':
        # Erase a point and its connections
        if (x, y) in grid:
            # Get the connections of the point to be erased
            connections = grid.pop((x, y))
            for conn in connections:
                if (x, y) in grid.get(conn, []):  # Check if conn is a key before accessing it
                    grid[conn].remove((x, y))
            # Mark the point and lines as black
            ax.plot(x, y, 'ko', markersize=10)  # Black point
            for conn in connections:
                ax.plot([x, conn[0]], [y, conn[1]], 'k--', markersize=5)  # Black dashed line
            plt.draw()
            print(f"Removed point: ({x}, {y})")
    
    elif mode == 'connect':
        # Connect two points
        selected_points.append((x, y))
        if len(selected_points) == 2:
            p1, p2 = selected_points
            if p1 in grid and p2 in grid:
                if p2 not in grid[p1]:
                    grid[p1].append(p2)
                if p1 not in grid[p2]:
                    grid[p2].append(p1)
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'go-', markersize=5)  # Green line
                print(f"Connected points: {p1} and {p2}")
            selected_points.clear()
    
    plt.draw()

# Function to handle moving existing points
def on_motion(event):
    global mode, move_point
    if event.inaxes is None or mode != 'move' or move_point is None:
        return

    x, y = int(round(event.xdata)), int(round(event.ydata))
    old_x, old_y = move_point

    if (old_x, old_y) in grid:
        # Update the grid
        connections = grid.pop((old_x, old_y))
        for conn in connections:
            grid[conn].remove((old_x, old_y))
        
        if (x, y) not in grid:
            grid[(x, y)] = []
        
        for conn in connections:
            grid[(x, y)].append(conn)
            if conn not in grid[conn]:
                grid[conn].append((x, y))
        
        # Redraw the grid
        ax.clear()
        plot_entire_grid(grid, grid_size)
        move_point = (x, y)
    
    plt.draw()

# Function to handle selecting and moving existing points
def on_press(event):
    global move_point
    if event.inaxes is None:
        return

    x, y = int(round(event.xdata)), int(round(event.ydata))
    if (x, y) in grid:
        move_point = (x, y)
        print(f"Selected point for moving: ({x}, {y})")

# Main execution
file_path = 'Floor Plan Sketcher\grid.xlsx'  # Path to your input Excel file
grid = ReadGrid(file_path)
selected_points = []
mode = None  # Current mode: add, erase, connect, or move
move_point = None  # The point being moved
erased_points = set()  # To track erased points
grid_size_x = 40  # Size of the grid in the x direction
grid_size_y = 30  # Size of the grid in the y direction

# Create the main window
root = tk.Tk()
root.title("Grid Editor")

# Create a frame for the plot
plot_frame = tk.Frame(root)
plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Create a frame for the buttons
button_frame = tk.Frame(root, padx=10, pady=10)
button_frame.pack(side=tk.RIGHT, fill=tk.Y)

# Plot the initial grid
fig, ax = plot_entire_grid(grid, grid_size_x, grid_size_y)

# Create a canvas for the plot and add it to the Tkinter window
canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Add buttons to the button frame
btn_add = tk.Button(button_frame, text="Add Point", command=add_point)
btn_add.pack(pady=5)

btn_erase = tk.Button(button_frame, text="Erase Point", command=erase_point)
btn_erase.pack(pady=5)

btn_connect = tk.Button(button_frame, text="Connect Points", command=connect_points)
btn_connect.pack(pady=5)

btn_save = tk.Button(button_frame, text="Save to Excel", command=save_to_excel)
btn_save.pack(pady=5)

# Connect the click and motion event handlers
fig.canvas.mpl_connect('button_press_event', on_click)
fig.canvas.mpl_connect('motion_notify_event', on_motion)
fig.canvas.mpl_connect('button_press_event', on_press)

# Start the Tkinter main loop
root.mainloop()
