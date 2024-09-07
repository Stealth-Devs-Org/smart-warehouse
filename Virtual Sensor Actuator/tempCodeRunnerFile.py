import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import math

class WarehouseSimulator(tk.Tk):
    def __init__(self):
        super().__init__()

        # Set window title
        self.title("Warehouse Temperature Simulator")

        # Get screen size
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Set canvas size to fit the screen
        self.canvas_width = screen_width - 100  # Adjust width to leave some space for controls
        self.canvas_height = screen_height - 100  # Adjust height to leave some space for controls

        self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack()

        # Placeholder for floor plan image
        self.floor_plan = None

        # Buttons for interaction
        self.upload_button = tk.Button(self, text="Upload Floor Plan", command=self.upload_floor_plan)
        self.upload_button.pack(side=tk.LEFT)

        self.add_heat_button = tk.Button(self, text="Add Heat Points", command=self.enable_heat_adding)
        self.add_heat_button.pack(side=tk.LEFT)

        self.clear_button = tk.Button(self, text="Clear Heat Points", command=self.clear_heat_points)
        self.clear_button.pack(side=tk.LEFT)

        self.measure_button = tk.Button(self, text="Measure Heat", command=self.enable_heat_measurement)
        self.measure_button.pack(side=tk.LEFT)

        # Sliders and input for heat point adjustment
        self.heat_value_label = tk.Label(self, text="Heat Value (°C):")
        self.heat_value_label.pack(side=tk.LEFT)
        self.heat_value_slider = tk.Scale(self, from_=50, to=500, orient=tk.HORIZONTAL)
        self.heat_value_slider.pack(side=tk.LEFT)

        self.heat_radius_label = tk.Label(self, text="Heat Radius:")
        self.heat_radius_label.pack(side=tk.LEFT)
        self.heat_radius_slider = tk.Scale(self, from_=10, to=200, orient=tk.HORIZONTAL)
        self.heat_radius_slider.pack(side=tk.LEFT)

        # Entry for environmental temperature
        self.env_temp_label = tk.Label(self, text="Environmental Temperature (°C):")
        self.env_temp_label.pack(side=tk.LEFT)
        self.env_temp_entry = tk.Entry(self)
        self.env_temp_entry.pack(side=tk.LEFT)
        self.env_temp_entry.insert(0, "30")  # Default environmental temperature

        # Store heat points
        self.heat_points = []

        # Bind left click to handle clicks only if in the right mode
        self.canvas.bind("<Button-1>", self.handle_click)
        self.measure_mode = False
        self.add_heat_mode = True  # Start in add heat points mode

    def upload_floor_plan(self):
        """Upload the floor plan image."""
        file_path = filedialog.askopenfilename()
        if file_path:
            img = Image.open(file_path)

            # Resize the image to fit the canvas
            img = img.resize((self.canvas_width, self.canvas_height), Image.Resampling.LANCZOS)
            self.floor_plan = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.floor_plan)

    def handle_click(self, event):
        """Handle mouse clicks based on the current mode (add heat points or measure heat)."""
        if self.measure_mode or self.add_heat_mode:
            x, y = event.x, event.y

            if self.measure_mode:
                # Measure the heat at this point
                total_heat = self.calculate_heat_at_point(x, y)
                env_temp = float(self.env_temp_entry.get())
                final_temp = max(total_heat, env_temp)
                self.canvas.create_text(x, y, text=f"{final_temp:.2f}°C", fill="blue")
            elif self.add_heat_mode:
                # Add a new heat point with the selected values
                heat_radius = self.heat_radius_slider.get()
                heat_value = self.heat_value_slider.get()

                # Add the heat point to the list of points
                self.heat_points.append((x, y, heat_radius, heat_value))

                # Draw the heat circle
                self.canvas.create_oval(
                    x - heat_radius, y - heat_radius,
                    x + heat_radius, y + heat_radius,
                    outline="red", width=2
                )

                # Display the temperature value at the point
                self.canvas.create_text(x, y, text=f"{heat_value}°C", fill="black")

    def calculate_heat_at_point(self, x, y):
        """Calculate the cumulative heat at a specific point using a more realistic approach."""
        total_heat = 0
        for heat_x, heat_y, heat_radius, heat_value in self.heat_points:
            # Calculate the distance between the point and the heat source
            distance = math.sqrt((x - heat_x) ** 2 + (y - heat_y) ** 2)

            if distance <= heat_radius:
                # Apply a gradient for heat contribution
                gradient = max(0, (heat_radius - distance) / heat_radius)
                contribution = heat_value * gradient
                total_heat = max(total_heat, contribution)  # Keep the highest temperature

        return total_heat

    def enable_heat_measurement(self):
        """Enable the heat measurement mode."""
        self.measure_mode = True
        self.add_heat_mode = False
        self.measure_button.config(state=tk.DISABLED)
        self.add_heat_button.config(state=tk.NORMAL)

    def enable_heat_adding(self):
        """Enable the heat adding mode."""
        self.add_heat_mode = True
        self.measure_mode = False
        self.add_heat_button.config(state=tk.DISABLED)
        self.measure_button.config(state=tk.NORMAL)

    def clear_heat_points(self):
        """Clear all heat points and redraw the canvas."""
        self.heat_points.clear()
        self.canvas.delete("all")
        self.measure_mode = False
        self.add_heat_mode = True

        # Redraw the floor plan if it's uploaded
        if self.floor_plan:
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.floor_plan)

if __name__ == "__main__":
    app = WarehouseSimulator()
    app.mainloop()
