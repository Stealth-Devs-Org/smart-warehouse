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

        self.clear_button = tk.Button(self, text="Clear All Heat Points", command=self.clear_heat_points)
        self.clear_button.pack(side=tk.LEFT)

        self.delete_button = tk.Button(self, text="Delete Heat Points", command=self.enable_heat_deletion)
        self.delete_button.pack(side=tk.LEFT)

        self.measure_button = tk.Button(self, text="Measure Heat", command=self.enable_heat_measurement)
        self.measure_button.pack(side=tk.LEFT)

        # Button to clear measurement points
        self.clear_measurement_button = tk.Button(self, text="Clear Measurement Points", command=self.clear_measurement_points)
        self.clear_measurement_button.pack(side=tk.LEFT)

        # Button to toggle radius visibility
        self.toggle_radius_button = tk.Button(self, text="Hide Radii", command=self.toggle_radius_visibility)
        self.toggle_radius_button.pack(side=tk.LEFT)

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

        # Store heat points with identifiers
        self.heat_points = []
        self.heat_point_ids = {}  # Track heat point IDs for deletion
        self.current_id = 0
        self.radius_visible = True  # Track visibility of radii
        self.delete_mode = False  # Track delete mode
        self.measure_mode = False
        self.add_heat_mode = True  # Start in add heat points mode

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
        """Handle mouse clicks based on the current mode (add heat points, delete heat points, or measure heat)."""
        if self.measure_mode:
            # Measure the heat at this point
            x, y = event.x, event.y
            total_heat = self.calculate_heat_at_point(x, y)
            env_temp = float(self.env_temp_entry.get())
            final_temp = max(total_heat, env_temp)
            text_id = self.canvas.create_text(x, y, text=f"{final_temp:.2f}°C", fill="blue")
            self.measurement_text_ids.append(text_id)

        elif self.add_heat_mode:
            # Add a new heat point with the selected values
            x, y = event.x, event.y
            heat_radius = self.heat_radius_slider.get()
            heat_value = self.heat_value_slider.get()
            heat_point_id = self.current_id

            # Add the heat point to the list of points
            self.heat_points.append((heat_point_id, x, y, heat_radius, heat_value))
            self.heat_point_ids[heat_point_id] = self.draw_heat_point(x, y, heat_radius, heat_value, heat_point_id)
            self.current_id += 1

        elif self.delete_mode:
            # Start drawing the selection rectangle
            self.rect_start_x = event.x
            self.rect_start_y = event.y

    def handle_drag(self, event):
        """Handle dragging the mouse to draw the selection rectangle."""
        if self.delete_mode and self.rect_start_x is not None and self.rect_start_y is not None:
            self.canvas.delete("selection")
            self.canvas.create_rectangle(
                self.rect_start_x, self.rect_start_y, event.x, event.y,
                outline="blue", dash=(2, 2), tags="selection"
            )

    def handle_release(self, event):
        """Handle mouse release to finalize the selection rectangle and delete heat points."""
        if self.delete_mode:
            if self.rect_start_x is not None and self.rect_start_y is not None:
                x1, y1 = self.rect_start_x, self.rect_start_y
                x2, y2 = event.x, event.y

                # Ensure rectangle coordinates are in the correct order
                x1, x2 = min(x1, x2), max(x1, x2)
                y1, y2 = min(y1, y2), max(y1, y2)

                # Delete heat points within the selection rectangle
                self.delete_heat_points_within(x1, y1, x2, y2)

                # Reset rectangle variables
                self.rect_start_x = None
                self.rect_start_y = None
                self.canvas.delete("selection")

    def draw_heat_point(self, x, y, heat_radius, heat_value, heat_point_id):
        """Draw a heat point with an optional radius."""
        # Draw the radius circle if it is visible
        if self.radius_visible:
            radius_id = self.canvas.create_oval(
                x - heat_radius, y - heat_radius,
                x + heat_radius, y + heat_radius,
                outline="red", width=2, tags=f"heat_radius_{heat_point_id}"
            )
        else:
            radius_id = None

        # Draw the temperature text at the point
        text_id = self.canvas.create_text(x, y, text=f"{heat_value}°C", fill="black", tags=f"heat_text_{heat_point_id}")

        # Return the IDs of the radius and text elements
        return {'radius': radius_id, 'text': text_id}

    def delete_heat_points_within(self, x1, y1, x2, y2):
        """Delete heat points within the specified rectangular area."""
        points_to_remove = []
        for heat_point_id, hx, hy, heat_radius, _ in self.heat_points:
            if x1 <= hx <= x2 and y1 <= hy <= y2:
                points_to_remove.append(heat_point_id)

                # Delete radius and text from canvas
                if self.radius_visible:
                    self.canvas.delete(f"heat_radius_{heat_point_id}")
                self.canvas.delete(f"heat_text_{heat_point_id}")

        # Remove deleted points from the list and ID tracking
        self.heat_points = [point for point in self.heat_points if point[0] not in points_to_remove]
        for point_id in points_to_remove:
            del self.heat_point_ids[point_id]

    def calculate_heat_at_point(self, x, y):
        """Calculate the cumulative heat at a specific point using a more realistic approach."""
        total_heat = 0
        for _, heat_x, heat_y, heat_radius, heat_value in self.heat_points:
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
        self.delete_mode = False
        self.measure_button.config(state=tk.DISABLED)
        self.add_heat_button.config(state=tk.NORMAL)
        self.delete_button.config(state=tk.NORMAL)

    def enable_heat_adding(self):
        """Enable the heat adding mode."""
        self.add_heat_mode = True
        self.measure_mode = False
        self.delete_mode = False
        self.add_heat_button.config(state=tk.DISABLED)
        self.measure_button.config(state=tk.NORMAL)
        self.delete_button.config(state=tk.NORMAL)

    def enable_heat_deletion(self):
        """Enable the heat deletion mode."""
        self.delete_mode = True
        self.add_heat_mode = False
        self.measure_mode = False
        self.delete_button.config(state=tk.DISABLED)
        self.add_heat_button.config(state=tk.NORMAL)
        self.measure_button.config(state=tk.NORMAL)

    def clear_heat_points(self):
        """Clear all heat points and redraw the canvas."""
        self.heat_points.clear()
        self.heat_point_ids.clear()
        self.canvas.delete("all")
        self.measure_mode = False
        self.add_heat_mode = True
        self.delete_mode = False

        # Redraw the floor plan if it's uploaded
        if self.floor_plan:
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.floor_plan)

        # Redraw all heat points
        for _, x, y, radius, value in self.heat_points:
            self.draw_heat_point(x, y, radius, value, _)

    def clear_measurement_points(self):
        """Clear all measurement points from the canvas."""
        for text_id in self.measurement_text_ids:
            self.canvas.delete(text_id)
        self.measurement_text_ids.clear()

    def toggle_radius_visibility(self):
        """Toggle the visibility of heat radii."""
        self.radius_visible = not self.radius_visible

        # Update visibility of existing radii
        for heat_point_id in self.heat_point_ids:
            if self.radius_visible:
                self.canvas.itemconfig(f"heat_radius_{heat_point_id}", state=tk.NORMAL)
            else:
                self.canvas.itemconfig(f"heat_radius_{heat_point_id}", state=tk.HIDDEN)

if __name__ == "__main__":
    app = WarehouseSimulator()
    app.mainloop()
