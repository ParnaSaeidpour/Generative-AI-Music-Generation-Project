from smhi.smhi_lib import (Smhi)

# Define the coordinates (longitude, latitude)
locations = {
     "Stockholm" : (59.32500, 18.07131),
     "Gothenburg" : (57.70713, 11.96703),
     "Malmö" : (55.60524, 13.00004),
     "Uppsala" : (59.85870, 17.63889),
     "Jönköping" : (57.77849, 14.16373),
     "Kiruna" : (67.85573, 20.22528),
}

def get_weather_data_by_city(city):
    """
    Get weather data for a specific city.
    """
    lat, lon = locations[city]
    smhi = Smhi(str(lon), str(lat))  # Initialize SMHI API
    forecasts = smhi.get_forecast()  # Get list of SmhiForecast objects
    forecast = forecasts[0]

    return {
            "location": city,
            "latitude": lat,
            "longitude": lon,
            "valid_time": forecast.valid_time,
            "temperature": forecast.temperature,
            "humidity": forecast.humidity,
            "pressure": forecast.pressure,
            "wind_speed": forecast.wind_speed,
            "wind_direction": forecast.wind_direction,
            "cloudiness": forecast.cloudiness,
            "precipitation": forecast.precipitation
        }
