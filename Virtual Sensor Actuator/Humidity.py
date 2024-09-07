import math

# Constants
HUMIDITY_PERSON = 0.1  # Moisture released per person (kg/hour)
VENTILATION_RATE = 1.0  # Ventilation rate in air changes per hour
SPECIFIC_HUMIDITY_OUTSIDE = 0.010  # Example specific humidity outside (kg/kg)
INITIAL_SPECIFIC_HUMIDITY_INSIDE = 0.008  # Initial specific humidity inside (kg/kg)

# Example warehouse data
warehouse = {
    'size': 1000,  # Size in square meters
    'height': 10,  # Height in meters
    'people': 10,
    'weather': 'mild',
    'outside_temp': 25,  # Outside temperature in Celsius
    'outside_humidity': 60  # Outside relative humidity in percentage
}

def calculate_specific_humidity(temperature, relative_humidity):
    # Calculate specific humidity from temperature and relative humidity
    # Using approximation formula
    return 0.622 * (relative_humidity / 100) * 6.112 * math.exp((17.67 * temperature) / (temperature + 243.5)) / 1013.25

def calculate_humidity_gains(warehouse):
    # Calculate moisture gains from people
    Q_people_humidity = warehouse['people'] * HUMIDITY_PERSON
    
    # Calculate external specific humidity
    T_outside = warehouse['outside_temp']
    RH_outside = warehouse['outside_humidity']
    specific_humidity_outside = calculate_specific_humidity(T_outside, RH_outside)
    
    # Calculate ventilation humidity exchange
    volume = warehouse['size'] * warehouse['height']
    ventilation_volume = volume * (VENTILATION_RATE / 3600)  # in m³/s
    specific_humidity_inside = INITIAL_SPECIFIC_HUMIDITY_INSIDE
    Q_ventilation_humidity = ventilation_volume * (specific_humidity_outside - specific_humidity_inside)
    
    # Total humidity gains
    Q_total_humidity = Q_people_humidity + Q_ventilation_humidity
    
    return Q_total_humidity, specific_humidity_outside

# Calculate and print the warehouse humidity
humidity_gains, specific_humidity_outside = calculate_humidity_gains(warehouse)
print(f"Total Humidity Gains: {humidity_gains:.2f} kg/h")

# Simplified humidity change estimation (adjust for dynamic simulations)
def estimate_humidity_change(humidity_gains, volume, initial_specific_humidity):
    # Assume specific humidity change
    specific_humidity_change = humidity_gains / volume
    final_specific_humidity = initial_specific_humidity + specific_humidity_change
    return final_specific_humidity

volume = warehouse['size'] * warehouse['height']
final_specific_humidity = estimate_humidity_change(humidity_gains, volume, INITIAL_SPECIFIC_HUMIDITY_INSIDE)
print(f"Estimated Specific Humidity: {final_specific_humidity:.4f} kg/kg")