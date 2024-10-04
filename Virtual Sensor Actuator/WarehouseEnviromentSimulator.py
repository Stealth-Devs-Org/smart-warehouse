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

        self.clear_button = tk.Button(self.controls_frame, text="Clear All Points", command=self.clear_all_points)
        self.clear_button.pack(fill=tk.X)

        self.delete_button = tk.Button(self.controls_frame, text="Delete Points", command=self.enable_point_deletion)
        self.delete_button.pack(fill=tk.X)

        self.measure_button = tk.Button(self.controls_frame, text="Measure Heat/Air Quality", command=self.enable_measurement)
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

        # Entry for environmental temperature
        self.env_temp_label = tk.Label(self.controls_frame, text="Environmental Temperature (°C):")
        self.env_temp_label.pack()
        self.env_temp_entry = tk.Entry(self.controls_frame)
        self.env_temp_entry.pack(fill=tk.X)
        self.env_temp_entry.insert(0, "30")  # Default environmental temperature

        # Store heat and air quality points with identifiers
        self.heat_points = []
        self.air_quality_points = []
        self.point_ids = {}  # Track point IDs for deletion
        self.current_id = 0
        self.radius_visible = True  # Track visibility of radii
        self.delete_mode = False  # Track delete mode
        self.measure_mode = False
        self.add_heat_mode = True  # Start in add heat points mode
        self.add_air_quality_mode = False  # Start in add air quality points mode

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
        """Handle mouse clicks based on the current mode (add heat points, air quality points, delete points, or measure temp/smoke/air quality)."""
        x, y = event.x, event.y

        if self.measure_mode:
            # Measure the heat or air quality at this point
            total_heat = self.calculate_heat_at_point(x, y)
            total_air_quality = self.calculate_air_quality_at_point(x, y)
            env_temp = float(self.env_temp_entry.get())
            final_temp = max(total_heat, env_temp)
            text_id = self.canvas.create_text(x, y, text=f"Heat: {final_temp:.2f}°C\nAir Quality: {total_air_quality:.2f}", fill="blue")
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
        """Handle mouse release to finalize the selection rectangle and delete points."""
        if self.delete_mode:
            if self.rect_start_x is not None and self.rect_start_y is not None:
                x1, y1 = self.rect_start_x, self.rect_start_y
                x2, y2 = event.x, event.y

                # Ensure rectangle coordinates are in the correct order
                x1, x2 = min(x1, x2), max(x1, x2)
                y1, y2 = min(y1, y2), max(y1, y2)

                # Delete points within the selection rectangle
                self.delete_points_within(x1, y1, x2, y2)

                # Reset rectangle variables
                self.rect_start_x = None
                self.rect_start_y = None
                self.canvas.delete("selection")

    def draw_heat_point(self, x, y, heat_radius, heat_value, point_id):
        """Draw a heat point with an optional radius."""
        # Draw the radius circle if it is visible
        if self.radius_visible:
            radius_id = self.canvas.create_oval(
                x - heat_radius, y - heat_radius,
                x + heat_radius, y + heat_radius,
                outline="red", width=2, tags=f"heat_radius_{point_id}"
            )
        else:
            radius_id = None

        # Draw the heat value text at the point
        text_id = self.canvas.create_text(x, y, text=f"{heat_value}°C", fill="black", tags=f"heat_text_{point_id}")

        # Return the IDs of the radius and text elements
        return {'radius': radius_id, 'text': text_id}

    def draw_air_quality_point(self, x, y, air_quality_radius, air_quality_value, point_id):
        """Draw an air quality point with an optional radius."""
        # Draw the radius circle if it is visible
        if self.radius_visible:
            radius_id = self.canvas.create_oval(
                x - air_quality_radius, y - air_quality_radius,
                x + air_quality_radius, y + air_quality_radius,
                outline="blue", width=2, tags=f"air_quality_radius_{point_id}"
            )
        else:
            radius_id = None

        # Draw the air quality text at the point
        text_id = self.canvas.create_text(x, y, text=f"{air_quality_value}", fill="black", tags=f"air_quality_text_{point_id}")

        # Return the IDs of the radius and text elements
        return {'radius': radius_id, 'text': text_id}

    def delete_points_within(self, x1, y1, x2, y2):
        """Delete points within the specified rectangular area."""
        points_to_remove = []
        for point_id, px, py, radius, _ in self.heat_points + self.air_quality_points:
            if x1 <= px <= x2 and y1 <= py <= y2:
                points_to_remove.append(point_id)

                # Delete radius and text from canvas
                if point_id in self.point_ids:
                    if self.radius_visible:
                        if point_id in [point[0] for point in self.heat_points]:
                            self.canvas.delete(f"heat_radius_{point_id}")
                        else:
                            self.canvas.delete(f"air_quality_radius_{point_id}")
                    self.canvas.delete(f"heat_text_{point_id}" if point_id in [point[0] for point in self.heat_points] else f"air_quality_text_{point_id}")

        # Remove deleted points from the lists and ID tracking
        self.heat_points = [point for point in self.heat_points if point[0] not in points_to_remove]
        self.air_quality_points = [point for point in self.air_quality_points if point[0] not in points_to_remove]
        for point_id in points_to_remove:
            del self.point_ids[point_id]

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
    
    def calculate_smoke_at_point(self, x, y):
        """Calculate the cumulative smoke at a specific point using a more realistic approach."""
        total_smoke = 0
        for _, smoke_x, smoke_y, smoke_radius, smoke_value in self.smoke_points:
            # Calculate the distance between the point and the smoke source
            distance = math.sqrt((x - smoke_x) ** 2 + (y - smoke_y) ** 2)

            if distance <= smoke_radius:
                # Apply a gradient for smoke contribution
                gradient = max(0, (smoke_radius - distance) / smoke_radius)
                contribution = smoke_value * gradient
                total_smoke = max(total_smoke, contribution)  # Keep the highest smoke level

        return total_smoke


    def calculate_air_quality_at_point(self, x, y):
        """Calculate the cumulative air quality at a specific point using a more realistic approach."""
        total_air_quality = 0
        for _, air_quality_x, air_quality_y, air_quality_radius, air_quality_value in self.air_quality_points:
            # Calculate the distance between the point and the air quality source
            distance = math.sqrt((x - air_quality_x) ** 2 + (y - air_quality_y) ** 2)

            if distance <= air_quality_radius:
                # Apply a gradient for air quality contribution
                gradient = max(0, (air_quality_radius - distance) / air_quality_radius)
                contribution = air_quality_value * gradient
                total_air_quality = max(total_air_quality, contribution)  # Keep the highest air quality

        return total_air_quality

    def enable_measurement(self):
        """Enable the measurement mode."""
        self.measure_mode = True
        self.add_heat_mode = False
        self.add_air_quality_mode = False
        self.delete_mode = False
        self.measure_button.config(state=tk.DISABLED)
        self.add_heat_button.config(state=tk.NORMAL)
        self.add_air_quality_button.config(state=tk.NORMAL)
        self.delete_button.config(state=tk.NORMAL)

    def enable_heat_adding(self):
        """Enable the heat adding mode."""
        self.add_heat_mode = True
        self.add_air_quality_mode = False
        self.measure_mode = False
        self.delete_mode = False
        self.add_heat_button.config(state=tk.DISABLED)
        self.measure_button.config(state=tk.NORMAL)
        self.add_air_quality_button.config(state=tk.NORMAL)
        self.delete_button.config(state=tk.NORMAL)

    def enable_air_quality_adding(self):
        """Enable the air quality adding mode."""
        self.add_air_quality_mode = True
        self.add_heat_mode = False
        self.measure_mode = False
        self.delete_mode = False
        self.add_air_quality_button.config(state=tk.DISABLED)
        self.measure_button.config(state=tk.NORMAL)
        self.add_heat_button.config(state=tk.NORMAL)
        self.delete_button.config(state=tk.NORMAL)

    def enable_point_deletion(self):
        """Enable the point deletion mode."""
        self.delete_mode = True
        self.add_heat_mode = False
        self.add_air_quality_mode = False
        self.measure_mode = False
        self.delete_button.config(state=tk.DISABLED)
        self.add_heat_button.config(state=tk.NORMAL)
        self.add_air_quality_button.config(state=tk.NORMAL)
        self.measure_button.config(state=tk.NORMAL)

    def clear_all_points(self):
        """Clear all heat and air quality points and redraw the canvas."""
        self.heat_points.clear()
        self.air_quality_points.clear()
        self.point_ids.clear()
        self.canvas.delete("all")
        self.measure_mode = False
        self.add_heat_mode = True
        self.add_air_quality_mode = False
        self.delete_mode = False

        # Redraw the floor plan if it's uploaded
        if self.floor_plan:
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.floor_plan)

        # Redraw all heat points
        for _, x, y, radius, value in self.heat_points:
            self.draw_heat_point(x, y, radius, value, _)

        # Redraw all air quality points
        for _, x, y, radius, value in self.air_quality_points:
            self.draw_air_quality_point(x, y, radius, value, _)

    def clear_measurement_points(self):
        """Clear all measurement points from the canvas."""
        for text_id in self.measurement_text_ids:
            self.canvas.delete(text_id)
        self.measurement_text_ids.clear()


    def toggle_radius_visibility(self):
        """Toggle the visibility of heat and air quality radii."""
        self.radius_visible = not self.radius_visible

        # Update visibility of existing radii
        for point_id in self.point_ids:
            if self.radius_visible:
                if point_id in [point[0] for point in self.heat_points]:
                    self.canvas.itemconfig(f"heat_radius_{point_id}", state=tk.NORMAL)
                else:
                    self.canvas.itemconfig(f"air_quality_radius_{point_id}", state=tk.NORMAL)
            else:
                if point_id in [point[0] for point in self.heat_points]:
                    self.canvas.itemconfig(f"heat_radius_{point_id}", state=tk.HIDDEN)
                else:
                    self.canvas.itemconfig(f"air_quality_radius_{point_id}", state=tk.HIDDEN)

if __name__ == "__main__":
    app = WarehouseSimulator()
    app.mainloop() 