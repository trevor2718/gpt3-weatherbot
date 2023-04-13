import pandas as pd
from tqdm import tqdm
from geopy.geocoders import Nominatim
from misc_utils import get_latest_csv_file

# Initialize the geolocator
geolocator = Nominatim(user_agent="my-app")
latest_csv_file = get_latest_csv_file()

df = pd.read_csv(latest_csv_file)

def get_location_name(latitude, longitude):
    # Use the reverse() method of the geolocator to get the location name
    location = geolocator.reverse(f"{latitude}, {longitude}")

    # Print the location name
    # print(location.address)
    if location and location.address:
        state = location.raw['address'].get('state', '')
        country = location.raw['address'].get('country', '')
        return state, country
    else:
        return "NaN", "NaN"


# Use a for loop to calculate the data for the new column

new_state_data = ["NaN"] * len(df)
new_country_data =["NaN"] * len(df)
new_df = pd.DataFrame(columns=['state_name', 'country_name'])

for index, row in tqdm(df.iterrows()):
    # if index < 12100:
    #     continue
    try:
        state, country = "NaN", "NaN"
        if row['latitude'] and row['longitude']:
            print("row['latitude'] => ", row['latitude'], "== row['longitude'] => ", row['longitude'])
            
            state, country = get_location_name(row['latitude'], row['longitude'])
            
            if not state and state.strip() == "":
                state = "NaN"
                
            if not country and country.strip() == "":
                country = "NaN"
                
        print("state name => ", state, "country name => ", country)
        new_state_data[index] = state
        new_country_data[index] = country

        # data = {'state_name': state, 'country_name': country}
        # new_df = new_df.append(data, ignore_index=True)
    except Exception as e:
        print("an exception occured ",e)
        print("\n writing the file")
        new_df = new_df.assign(state_name=new_state_data)
        new_df = new_df.assign(country_name=new_country_data)
        new_df.to_csv("relative_location_name_13.csv", index=False)
    
    
    if index % 100 == 0:
        new_df = new_df.assign(state_name=new_state_data)
        new_df = new_df.assign(country_name=new_country_data)
        new_df.to_csv("relative_location_name_13.csv", index=False)
    
    
new_df = new_df.assign(state_name=new_state_data)
new_df = new_df.assign(country_name=new_country_data)
new_df.to_csv("relative_location_name_13_1.csv", index=False)
# df = df.assign(state_name=new_state_data)
# df = df.assign(country_name=new_country_data)
# new_df.to_csv("with_location_name_hudart.csv", index=False)
