import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import math

class WarehouseSimulator(tk.Tk):
    def __init__(self):
        super().__init__()

        # Set window title
        self.title("Warehouse Temperature and Air Quality Simulator")

        # Get screen size
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Set canvas size to fit the screen
        self.canvas_width = screen_width - 200  # Adjust width to leave space for controls
        self.canvas_height = screen_height - 100  # Adjust height to leave space for controls

        self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Placeholder for floor plan image
        self.floor_plan = None

        # Frame for controls
        self.controls_frame = tk.Frame(self)
        self.controls_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        # Buttons for interaction
        self.upload_button = tk.Button(self.controls_frame, text="Upload Floor Plan", command=self.upload_floor_plan)
        self.upload_button.pack(fill=tk.X)

        self.add_heat_button = tk.Button(self.controls_frame, text="Add Heat Points", command=self.enable_heat_adding)
        self.add_heat_button.pack(fill=tk.X)

        self.add_air_quality_button = tk.Button(self.controls_frame, text="Add Air Quality Points", command=self.enable_air_quality_adding)
        self.add_air_quality_button.pack(fill=tk.X)

        self.add_smoke_button = tk.Button(self.controls_frame, text="Add Smoke Points", command=self.enable_smoke_adding)
        self.add_smoke_button.pack(fill=tk.X)

        self.clear_button = tk.Button(self.controls_frame, text="Clear All Points", command=self.clear_all_points)
        self.clear_button.pack(fill=tk.X)

        self.delete_button = tk.Button(self.controls_frame, text="Delete Points", command=self.enable_point_deletion)
        self.delete_button.pack(fill=tk.X)

        self.measure_button = tk.Button(self.controls_frame, text="Measure Heat/Air Quality/Smoke", command=self.enable_measurement)
        self.measure_button.pack(fill=tk.X)

        # Button to clear measurement points
        self.clear_measurement_button = tk.Button(self.controls_frame, text="Clear Measurement Points", command=self.clear_measurement_points)
        self.clear_measurement_button.pack(fill=tk.X)

        # Button to toggle radius visibility
        self.toggle_radius_button = tk.Button(self.controls_frame, text="Hide Radii", command=self.toggle_radius_visibility)
        self.toggle_radius_button.pack(fill=tk.X)

        # Sliders and input for heat point adjustment
        self.heat_value_label = tk.Label(self.controls_frame, text="Heat Value (°C):")
        self.heat_value_label.pack()
        self.heat_value_slider = tk.Scale(self.controls_frame, from_=50, to=500, orient=tk.HORIZONTAL)
        self.heat_value_slider.pack(fill=tk.X)

        self.heat_radius_label = tk.Label(self.controls_frame, text="Heat Radius:")
        self.heat_radius_label.pack()
        self.heat_radius_slider = tk.Scale(self.controls_frame, from_=10, to=200, orient=tk.HORIZONTAL)
        self.heat_radius_slider.pack(fill=tk.X)

        # Sliders and input for air quality point adjustment
        self.air_quality_label = tk.Label(self.controls_frame, text="Air Quality Value:")
        self.air_quality_label.pack()
        self.air_quality_slider = tk.Scale(self.controls_frame, from_=0, to=100, orient=tk.HORIZONTAL)
        self.air_quality_slider.pack(fill=tk.X)

        self.air_quality_radius_label = tk.Label(self.controls_frame, text="Air Quality Radius:")
        self.air_quality_radius_label.pack()
        self.air_quality_radius_slider = tk.Scale(self.controls_frame, from_=10, to=200, orient=tk.HORIZONTAL)
        self.air_quality_radius_slider.pack(fill=tk.X)

        # Sliders and input for smoke point adjustment
        self.smoke_value_label = tk.Label(self.controls_frame, text="Smoke Value:")
        self.smoke_value_label.pack()
        self.smoke_value_slider = tk.Scale(self.controls_frame, from_=0, to=100, orient=tk.HORIZONTAL)
        self.smoke_value_slider.pack(fill=tk.X)

        self.smoke_radius_label = tk.Label(self.controls_frame, text="Smoke Radius:")
        self.smoke_radius_label.pack()
        self.smoke_radius_slider = tk.Scale(self.controls_frame, from_=10, to=200, orient=tk.HORIZONTAL)
        self.smoke_radius_slider.pack(fill=tk.X)

        # Entry for environmental temperature
        self.env_temp_label = tk.Label(self.controls_frame, text="Environmental Temperature (°C):")
        self.env_temp_label.pack()
        self.env_temp_entry = tk.Entry(self.controls_frame)
        self.env_temp_entry.pack(fill=tk.X)
        self.env_temp_entry.insert(0, "30")  # Default environmental temperature

        # Store heat, air quality, and smoke points with identifiers
        self.heat_points = []
        self.air_quality_points = []
        self.smoke_points = []  # New list for smoke points
        self.point_ids = {}  # Track point IDs for deletion
        self.current_id = 0
        self.radius_visible = True  # Track visibility of radii
        self.delete_mode = False  # Track delete mode
        self.measure_mode = False
        self.add_heat_mode = True  # Start in add heat points mode
        self.add_air_quality_mode = False  # Start in add air quality points mode
        self.add_smoke_mode = False  # Start in add smoke points mode

        # Track measurement text IDs
        self.measurement_text_ids = []

        # Initialize rectangle drawing variables
        self.rect_start_x = None
        self.rect_start_y = None

        # Bind mouse events
        self.canvas.bind("<Button-1>", self.handle_click)
        self.canvas.bind("<B1-Motion>", self.handle_drag)
        self.canvas.bind("<ButtonRelease-1>", self.handle_release)

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
        """Handle mouse clicks based on the current mode (add heat points, air quality points, smoke points, delete points, or measure)."""
        x, y = event.x, event.y

        if self.measure_mode:
            # Measure the heat or air quality or smoke at this point
            total_heat = self.calculate_heat_at_point(x, y)
            total_air_quality = self.calculate_air_quality_at_point(x, y)
            total_smoke = self.calculate_smoke_at_point(x, y)
            env_temp = float(self.env_temp_entry.get())
            final_temp = max(total_heat, env_temp)
            text_id = self.canvas.create_text(x, y, text=f"Heat: {final_temp:.2f}°C\nAir Quality: {total_air_quality:.2f}\nSmoke: {total_smoke:.2f}", fill="blue")
            self.measurement_text_ids.append(text_id)

        elif self.add_heat_mode:
            # Add a new heat point with the selected values
            heat_radius = self.heat_radius_slider.get()
            heat_value = self.heat_value_slider.get()
            heat_point_id = self.current_id
            self.heat_points.append((heat_point_id, x, y, heat_radius, heat_value))
            self.point_ids[heat_point_id] = self.draw_heat_point(x, y, heat_radius, heat_value, heat_point_id)
            self.current_id += 1

        elif self.add_air_quality_mode:
            # Add a new air quality point with the selected values
            air_quality_radius = self.air_quality_radius_slider.get()
            air_quality_value = self.air_quality_slider.get()
            air_quality_point_id = self.current_id
            self.air_quality_points.append((air_quality_point_id, x, y, air_quality_radius, air_quality_value))
            self.point_ids[air_quality_point_id] = self.draw_air_quality_point(x, y, air_quality_radius, air_quality_value, air_quality_point_id)
            self.current_id += 1

        elif self.add_smoke_mode:
            # Add a new smoke point with the selected values
            smoke_radius = self.smoke_radius_slider.get()
            smoke_value = self.smoke_value_slider.get()
            smoke_point_id = self.current_id
            self.smoke_points.append((smoke_point_id, x, y, smoke_radius, smoke_value))
            self.point_ids[smoke_point_id] = self.draw_smoke_point(x, y, smoke_radius, smoke_value, smoke_point_id)
            self.current_id += 1

        elif self.delete_mode:
            # Check if a point is close enough to be deleted
            self.delete_point(x, y)

    def draw_heat_point(self, x, y, radius, value, point_id):
        """Draw a heat point on the canvas."""
        radius_visible = self.radius_visible
        if radius_visible:
            return self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, outline="red", width=2, tag=f"heat_{point_id}")
        return None

    def draw_air_quality_point(self, x, y, radius, value, point_id):
        """Draw an air quality point on the canvas."""
        radius_visible = self.radius_visible
        if radius_visible:
            return self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, outline="green", width=2, tag=f"air_quality_{point_id}")
        return None

    def draw_smoke_point(self, x, y, radius, value, point_id):
        """Draw a smoke point on the canvas."""
        radius_visible = self.radius_visible
        if radius_visible:
            return self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, outline="black", width=2, tag=f"smoke_{point_id}")
        return None

    def handle_drag(self, event):
        """Handle drag events for rectangle drawing or other interactions."""
        if self.rect_start_x is not None and self.rect_start_y is not None:
            x1, y1 = self.rect_start_x, self.rect_start_y
            x2, y2 = event.x, event.y
            self.canvas.delete("rectangle")
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="blue", tag="rectangle")

    def handle_release(self, event):
        """Handle the release event to finalize rectangle drawing."""
        if self.rect_start_x is not None and self.rect_start_y is not None:
            self.canvas.delete("rectangle")
            self.rect_start_x = None
            self.rect_start_y = None

    def calculate_heat_at_point(self, x, y):
        """Calculate total heat at a given point."""
        total_heat = 0
        for (point_id, px, py, radius, value) in self.heat_points:
            distance = math.sqrt((px - x) ** 2 + (py - y) ** 2)
            if distance <= radius:
                total_heat += value
        return total_heat

    def calculate_air_quality_at_point(self, x, y):
        """Calculate total air quality at a given point."""
        total_air_quality = 0
        for (point_id, px, py, radius, value) in self.air_quality_points:
            distance = math.sqrt((px - x) ** 2 + (py - y) ** 2)
            if distance <= radius:
                total_air_quality += value
        return total_air_quality

    def calculate_smoke_at_point(self, x, y):
        """Calculate total smoke at a given point."""
        total_smoke = 0
        for (point_id, px, py, radius, value) in self.smoke_points:
            distance = math.sqrt((px - x) ** 2 + (py - y) ** 2)
            if distance <= radius:
                total_smoke += value
        return total_smoke

    def clear_all_points(self):
        """Clear all points from the canvas."""
        self.canvas.delete("heat")
        self.canvas.delete("air_quality")
        self.canvas.delete("smoke")  # Clear smoke points
        self.heat_points.clear()
        self.air_quality_points.clear()
        self.smoke_points.clear()  # Clear smoke points
        self.point_ids.clear()
        self.current_id = 0
        self.measurement_text_ids.clear()

    def enable_heat_adding(self):
        """Enable adding heat points."""
        self.add_heat_mode = True
        self.add_air_quality_mode = False
        self.add_smoke_mode = False
        self.delete_mode = False
        self.measure_mode = False

    def enable_air_quality_adding(self):
        """Enable adding air quality points."""
        self.add_heat_mode = False
        self.add_air_quality_mode = True
        self.add_smoke_mode = False
        self.delete_mode = False
        self.measure_mode = False

    def enable_smoke_adding(self):
        """Enable adding smoke points."""
        self.add_heat_mode = False
        self.add_air_quality_mode = False
        self.add_smoke_mode = True
        self.delete_mode = False
        self.measure_mode = False

    def enable_point_deletion(self):
        """Enable point deletion mode."""
        self.add_heat_mode = False
        self.add_air_quality_mode = False
        self.add_smoke_mode = False
        self.delete_mode = True
        self.measure_mode = False

    def enable_measurement(self):
        """Enable measurement mode."""
        self.add_heat_mode = False
        self.add_air_quality_mode = False
        self.add_smoke_mode = False
        self.delete_mode = False
        self.measure_mode = True

    def clear_measurement_points(self):
        """Clear measurement points from the canvas."""
        for text_id in self.measurement_text_ids:
            self.canvas.delete(text_id)
        self.measurement_text_ids.clear()

    def toggle_radius_visibility(self):
        """Toggle the visibility of radii."""
        self.radius_visible = not self.radius_visible
        # Redraw all points with updated visibility
        self.canvas.delete("heat")
        self.canvas.delete("air_quality")
        self.canvas.delete("smoke")  # Clear smoke points for redrawing
        for (point_id, x, y, radius, value) in self.heat_points:
            self.draw_heat_point(x, y, radius, value, point_id)
        for (point_id, x, y, radius, value) in self.air_quality_points:
            self.draw_air_quality_point(x, y, radius, value, point_id)
        for (point_id, x, y, radius, value) in self.smoke_points:
            self.draw_smoke_point(x, y, radius, value, point_id)

    def delete_point(self, x, y):
        """Delete a point if within close proximity."""
        # Iterate through heat points
        for (point_id, px, py, radius, _) in self.heat_points:
            if self.is_within_radius(x, y, px, py, radius):
                self.canvas.delete(self.point_ids[point_id])
                del self.point_ids[point_id]
                self.heat_points = [point for point in self.heat_points if point[0] != point_id]
                return

        # Iterate through air quality points
        for (point_id, px, py, radius, _) in self.air_quality_points:
            if self.is_within_radius(x, y, px, py, radius):
                self.canvas.delete(self.point_ids[point_id])
                del self.point_ids[point_id]
                self.air_quality_points = [point for point in self.air_quality_points if point[0] != point_id]
                return

        # Iterate through smoke points
        for (point_id, px, py, radius, _) in self.smoke_points:
            if self.is_within_radius(x, y, px, py, radius):
                self.canvas.delete(self.point_ids[point_id])
                del self.point_ids[point_id]
                self.smoke_points = [point for point in self.smoke_points if point[0] != point_id]
                return

    def is_within_radius(self, x, y, px, py, radius):
        """Check if a point is within the radius of another point."""
        distance = math.sqrt((px - x) ** 2 + (py - y) ** 2)
        return distance <= radius

if __name__ == "__main__":
    app = WarehouseSimulator()
    app.mainloop()
