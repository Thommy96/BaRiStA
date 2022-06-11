import requests
import folium
import polyline
from geopy.geocoders import Nominatim

def get_coordinates(address):
    locator = Nominatim(user_agent="myGeocoder")
    location = locator.geocode(address)
    return (location.latitude, location.longitude)

def get_route(start_lon, start_lat, destination_lon, destination_lat):
    
    loc = "{},{};{},{}".format(start_lon, start_lat, destination_lon, destination_lat)
    url = "http://router.project-osrm.org/route/v1/bike/"
    r = requests.get(url + loc) 
    if r.status_code!= 200:
        return {}
    res = r.json()   
    #routes = polyline.decode(res['routes'][0]['geometry'])
    start_point = [res['waypoints'][0]['location'][1], res['waypoints'][0]['location'][0]]
    end_point = [res['waypoints'][1]['location'][1], res['waypoints'][1]['location'][0]]
    distance = res['routes'][0]['distance']
    duration = res['routes'][0]['duration']

    out = {
        'start_point': start_point,
        'end_point': end_point,
        'distance': distance,
        'duration': "%d:%02d"%(duration//3600, duration//60)
         }

    return out['duration']
