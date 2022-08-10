import requests
import folium
import polyline
from geopy.geocoders import Nominatim

def get_coordinates(address):
    locator = Nominatim(user_agent="myGeocoder")
    location = locator.geocode(address)
    return [location.latitude, location.longitude]

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
        'distance': str(distance),
        'duration': "%d:%02d"%(duration//3600, duration//60)
         }

    return str(out['distance']), str(out['duration'])


def get_distance_duration(start_address, end_address):
    locator = Nominatim(user_agent="myGeocoder")
    start_location = locator.geocode(start_address)
    end_location = locator.geocode(end_address)
    start_coordinate = [start_location.latitude, start_location.longitude]
    end_coordinate = [end_location.latitude, end_location.longitude]
    
    loc = "{},{};{},{}".format(start_coordinate[0], start_coordinate[1], end_coordinate[0], end_coordinate[1])
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
    if out['distance'] > 1000:
        distance_km = str(out['distance']/1000)
    if duration//3600 != 0:
        time = str(int(duration//3600))+' hour and '+str(int(duration//60))+' minutes'
    else:
        time = str(int(duration//60))+' minutes'

    return distance_km, time