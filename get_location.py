from geopy.geocoders import Nominatim
 
loc = Nominatim(user_agent="GetLoc")
 

def get_coordinates(region): 
    """
    get geographical coordinated of a region on earth, 
    More precise information can be obtained using googemaps which provides an api to get the information 
    There are lot more features where we can even get cafes, resturants or parks near a location  
    """
    getLoc = loc.geocode(region )
    if (getLoc.address):
        full_address = getLoc.address
        Latitude = getLoc.latitude
        Longitude =getLoc.longitude
        return full_address,Latitude,Longitude
    else:
        return None, None, None