import pandas as pd

record_identifier_dic = {
    'C':"Closest approach to a coast, not followed by a landfall"
    ,'G':"Genesis"
    ,'I':"An intensity peak in terms of both pressure and wind"
    ,'L':"Landfall (center of system crossing a coastline)"
    ,'P':"Minimum in central pressure"
    ,'R':"Provides additional detail on the intensity of the cyclone when rapid changes are underway"
    ,'S':"Change of status of the system"
    ,'T':"Provides additional detail on the track (position) of the cyclone"
    ,'W':"Maximum sustained wind speed"
}
status_of_system_dic = {
    'TD':"Tropical cyclone of tropical depression intensity (< 34 knots)"
    ,'TS':"Tropical cyclone of tropical storm intensity (34-63 knots)"
    ,'HU':"Tropical cyclone of hurricane intensity (> 64 knots)"
    ,'EX':"Extratropical cyclone (of any intensity)"
    ,'SD':"Subtropical cyclone of subtropical depression intensity (< 34 knots)"
    ,'SS':"Subtropical cyclone of subtropical storm intensity (> 34 knots)"
    ,'LO':"A low that is neither a tropical cyclone, a subtropical cyclone, nor an extratropical cyclone (of any intensity)"
    ,'WV':"Tropical Wave (of any intensity)"
    ,'DB':"Disturbance (of any intensity)"
} 
    
def process_details(data):
    data=data.split(',')
    year=int(data[0][0:4])
    month=int(data[0][4:6])
    day=int(data[0][6:8])
    hours_in_utc=int(data[1][0:2])
    minutes_in_utc=int(data[1][2:4])
    record_identifier=data[2].strip()
    try:
        record_identifier_desc=record_identifier_dic[data[2].strip()]
    except:
        record_identifier_desc=None
        
    status_of_system=data[3].strip()
    try:
        status_of_system_desc=status_of_system_dic[status_of_system]
    except:
        status_of_system_desc=None
        
    if data[4].strip()[-1:] in ('N','S'):
        if data[4].strip()[-1:]=='N':
            latitude=float(data[4].strip()[:-1])
        else:
            latitude=-1.0*float(data[4].strip()[:-1])
    else:
        latitude=-999
    
    if data[5].strip()[-1:] in ('E','W'):
        if data[5].strip()[-1:]=='E':
            longitude=float(data[5].strip()[:-1])
        else:
            longitude=-1.0*float(data[5].strip()[:-1])
    else:
        longitude=-999
    maximum_sustained_wind_in_knots=float(data[6].strip())
    minimum_Pressure_in_millibars=float(data[7].strip())
    i=8
    f34_kt_wind_radii_maximum_northeastern=float(data[i].strip())
    i+=1
    f34_kt_wind_radii_maximum_southeastern=float(data[i].strip())
    i+=1
    f34_kt_wind_radii_maximum_southwestern=float(data[i].strip())
    i+=1
    f34_kt_wind_radii_maximum_northwestern=float(data[i].strip())
    

    i+=1
    f50_kt_wind_radii_maximum_northeastern=float(data[i].strip())
    i+=1
    f50_kt_wind_radii_maximum_southeastern=float(data[i].strip())
    i+=1
    f50_kt_wind_radii_maximum_southwestern=float(data[i].strip())
    i+=1
    f50_kt_wind_radii_maximum_northwestern=float(data[i].strip())
    
    i+=1
    f64_kt_wind_radii_maximum_northeastern=float(data[i].strip())
    i+=1
    f64_kt_wind_radii_maximum_southeastern=float(data[i].strip())
    i+=1
    f64_kt_wind_radii_maximum_southwestern=float(data[i].strip())
    i+=1
    f64_kt_wind_radii_maximum_northwestern=float(data[i].strip())


    
    res=year,month,day,hours_in_utc,minutes_in_utc,record_identifier,record_identifier_desc,status_of_system,status_of_system_desc,latitude,longitude,maximum_sustained_wind_in_knots,minimum_Pressure_in_millibars,f34_kt_wind_radii_maximum_northeastern,f34_kt_wind_radii_maximum_southeastern,f34_kt_wind_radii_maximum_southwestern,f34_kt_wind_radii_maximum_northwestern,f50_kt_wind_radii_maximum_northeastern,f50_kt_wind_radii_maximum_southeastern,f50_kt_wind_radii_maximum_southwestern,f50_kt_wind_radii_maximum_northwestern,f64_kt_wind_radii_maximum_northeastern,f64_kt_wind_radii_maximum_southeastern,f64_kt_wind_radii_maximum_southwestern,f64_kt_wind_radii_maximum_northwestern
    return res

def process_header(data):
    data=data.split(',')
    basin,atcf_cyclone_number_for_that_year,year,name,number_of_best_track_entries=data[0][0:2],data[0][2:4],data[0][4:8],data[1].strip(),data[2].strip()
    res=basin,atcf_cyclone_number_for_that_year,year,name,number_of_best_track_entries
    return res


def identify_line_type(data):
    # print(data.split(','))
    if len(data.split(','))>4:
        return 2
    else:
        return 1
def columns_name():
    res=['basin','atcf_cyclone_number_for_that_year','year_','name',
         'year','month','day','hours_in_utc','minutes_in_utc',
         'record_identifier','record_identifier_desc','status_of_system','status_of_system_desc','latitude','longitude'
         ,'maximum_sustained_wind_in_knots','minimum_pressure_in_millibars','f34_kt_wind_radii_maximum_northeastern',
         'f34_kt_wind_radii_maximum_southeastern','f34_kt_wind_radii_maximum_southwestern',
         'f34_kt_wind_radii_maximum_northwestern','f50_kt_wind_radii_maximum_northeastern',
         'f50_kt_wind_radii_maximum_southeastern','f50_kt_wind_radii_maximum_southwestern',
         'f50_kt_wind_radii_maximum_northwestern','f64_kt_wind_radii_maximum_northeastern',
         'f64_kt_wind_radii_maximum_southeastern','f64_kt_wind_radii_maximum_southwestern',
         'f64_kt_wind_radii_maximum_northwestern']
    return res


def convert_to_df(filepath):
    # this method returns new converted csv filepath else False will be returned
    new_filepath = ""
    try:
        if filepath.strip().endswith(".txt"):
            new_filepath = filepath.strip()[:-4] + ".csv"
            print("newfile path => ", new_filepath)

        if new_filepath:
            pf=[]
            header_fields=[]
            with open(filepath) as fp:
                ln = fp.readline()
                while ln:
                    
                    lt=identify_line_type(ln)

                    details=[]
                    if (lt==1):
                        header_fields=process_header(ln)
                        details=[]
                    else:
                        details=process_details(ln)
                    if (details!=[]):
                        n=list(header_fields[:-1])+list(details)

                        pf.append(n)
                    ln=fp.readline()

            df=pd.DataFrame(pf)
            df.columns=columns_name()
            
            # add atcf_id
            atcf_id_list = []
            for index, row in enumerate(df.iterrows()):
                
                cur_row = row[1]
                atcf_id = f'{cur_row["basin"].strip()}{(cur_row["atcf_cyclone_number_for_that_year"].strip())}{cur_row["year"]}'
                atcf_id_list.append( atcf_id )
            df.insert(loc=0, column='atcf_id', value=atcf_id_list)
            df.to_csv(new_filepath)
            print(df.shape)
            return new_filepath
        else:
            return False
    except Exception as e:
        print("error while converting the data to df => ",e)
        return False