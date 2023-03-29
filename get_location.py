from geopy.geocoders import Nominatim
 
loc = Nominatim(user_agent="GetLoc")
 

def get_coordinates(region): 
    """
    Get geographical coordinates of a region, 
    More precise information can be obtained using googemaps which provides an api to get the information 
    They provide lot more features i.e., where can we get a cafe, parks in the region  
    """
    getLoc = loc.geocode(region )
    if (getLoc.address):
        full_address = getLoc.address
        Latitude = getLoc.latitude
        Longitude =getLoc.longitude
        return full_address,Latitude,Longitude
    else:
        return None, None, None