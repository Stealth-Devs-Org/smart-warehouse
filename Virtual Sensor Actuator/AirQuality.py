# Constants
CO2_EMISSION_PERSON = 0.004  # CO2 emission per person (kg/hour)
PM25_EMISSION_MACHINE = 0.002  # PM2.5 emission per machine (kg/hour)
EXTERNAL_CO2_CONCENTRATION = 0.0004  # Example CO2 concentration outside (kg/kg)
EXTERNAL_PM25_CONCENTRATION = 0.00001  # Example PM2.5 concentration outside (kg/kg)
VENTILATION_RATE = 1.0  # Ventilation rate in air changes per hour

# Example warehouse data
warehouse = {
    'size': 1000,  # Size in square meters
    'height': 10,  # Height in meters
    'people': 10,
    'machines': 5,
    'weather': 'mild',
    'outside_temp': 25,  # Outside temperature in Celsius
    'outside_air_quality': 50  # Outside air quality index (AQI)
}

def calculate_air_quality_gains(warehouse):
    # Calculate CO2 gains from people
    Q_people_CO2 = warehouse['people'] * CO2_EMISSION_PERSON
    
    # Calculate PM2.5 gains from machines
    Q_machines_PM25 = warehouse['machines'] * PM25_EMISSION_MACHINE
    
    # External air quality
    specific_CO2_outside = EXTERNAL_CO2_CONCENTRATION
    specific_PM25_outside = EXTERNAL_PM25_CONCENTRATION
    
    # Calculate ventilation air quality exchange
    volume = warehouse['size'] * warehouse['height']
    ventilation_volume = volume * (VENTILATION_RATE / 3600)  # in m³/s
    specific_CO2_inside = EXTERNAL_CO2_CONCENTRATION  # Initial CO2 concentration inside (kg/kg)
    specific_PM25_inside = EXTERNAL_PM25_CONCENTRATION  # Initial PM2.5 concentration inside (kg/kg)
    Q_ventilation_CO2 = ventilation_volume * (specific_CO2_outside - specific_CO2_inside)
    Q_ventilation_PM25 = ventilation_volume * (specific_PM25_outside - specific_PM25_inside)
    
    # Total air quality gains
    Q_total_CO2 = Q_people_CO2 + Q_ventilation_CO2
    Q_total_PM25 = Q_machines_PM25 + Q_ventilation_PM25
    
    return Q_total_CO2, Q_total_PM25

# Calculate and print the warehouse air quality
CO2_gains, PM25_gains = calculate_air_quality_gains(warehouse)
print(f"Total CO2 Gains: {CO2_gains:.6f} kg/h")
print(f"Total PM2.5 Gains: {PM25_gains:.6f} kg/h")

# Simplified air quality change estimation (adjust for dynamic simulations)
def estimate_air_quality_change(CO2_gains, PM25_gains, volume, initial_CO2, initial_PM25):
    # Assume air quality change
    CO2_change = CO2_gains / volume
    PM25_change = PM25_gains / volume
    final_CO2 = initial_CO2 + CO2_change
    final_PM25 = initial_PM25 + PM25_change
    return final_CO2, final_PM25

volume = warehouse['size'] * warehouse['height']
initial_CO2 = EXTERNAL_CO2_CONCENTRATION
initial_PM25 = EXTERNAL_PM25_CONCENTRATION
final_CO2, final_PM25 = estimate_air_quality_change(CO2_gains, PM25_gains, volume, initial_CO2, initial_PM25)
print(f"Estimated CO2 Concentration: {final_CO2:.6f} kg/kg")
print(f"Estimated PM2.5 Concentration: {final_PM25:.6f} kg/kg")