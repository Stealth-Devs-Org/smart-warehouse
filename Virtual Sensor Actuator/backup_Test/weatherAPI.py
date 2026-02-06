# import required modules
import requests, json
 
api_key = "46642be04341c1815b314eba42613bff"
base_url = "http://api.openweathermap.org/data/2.5/weather?"
# city_name = input("Enter city name : ")
city_name= "Moratuwa,LK";
complete_url = base_url + "appid=" + api_key + "&q=" + city_name
response = requests.get(complete_url)
# print(complete_url)
 
x = response.json()
 
if x["cod"] != "404":
    y = x["main"]
    celsius_temperature = y["temp_max"]-273.15
    current_pressure = y["pressure"]
    current_humidity = y["humidity"]
    z = x["weather"]
    weather_description = z[0]["description"]
 
    # print("Temperature = " + f"{celsius_temperature:.2f} °C")
    # print("atmospheric pressure (in hPa unit) = " + str(current_pressure))
    # print("humidity (in percentage) = " +str(current_humidity))
    # print("description = " + str(weather_description))
else:
    print(" City Not Found ")