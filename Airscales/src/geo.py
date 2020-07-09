import re
from geopy.geocoders import Nominatim

class geobot:

    def __init__(slf, raw_df, doclean=False):
        try:
            slf.clean_df = slf.clean(raw_df) if doclean else raw_df
            if 'Latitude' not in set(slf.clean_df.columns) and \
                'Longitude' not in set(slf.clean_df.columns):
                slf.geo_df = slf.geo(slf.clean_df)
            else:
                slf.geo_df = raw_df
        except:
            raise TypeError("Malformed Clean")

    def geo(slf, clean_df):
        try:
            geol = Nominatim(user_agent="basicalily")
            geol.default_timeout = 10000
            def get_lat_lon_as_string(addr):
                q = {'street': addr, 'city' : 'Philadelphia', 'country': 'USA'}
                geoplace = geol.geocode(query=q, viewbox= [(40.151378, -75.432450), (39.796416, -74.933517)]) #GUESS BOX
                if geoplace:
                    print(geoplace)
                return f'{geoplace.latitude}*{geoplace.longitude}' if geoplace else 'NOTFOUND'
            clean_df.loc[:,'city_coord'] = clean_df['Address'].apply(lambda addr: get_lat_lon_as_string(addr))
            clean_df = clean_df[clean_df['city_coord'] != 'NOTFOUND']
            clean_df.loc[:,'Latitude'] = clean_df['city_coord'].apply(lambda x: x.split('*')[0])
            clean_df.loc[:,'Longitude'] = clean_df['city_coord'].apply(lambda x: x.split('*')[1])

            clean_df.drop(columns=['city_coord'], inplace=True)
            clean_df.loc[:,'Status Contractual Search Date'] = pd.to_datetime(clean_df['Status Contractual Search Date'])
        except:
            raise TypeError("Malformed Clean")
        return clean_df

    def clean(slf, raw_df):
        print('CLEANED')
        print(set(['Address','Structure Type','Status Contractual Search Date',\
            'Current Price','Longitude','Latitude']) in set(list(raw_df.columns)))
        print(set(list(raw_df.columns)))

        try:
            if set(['Address','Structure Type','Status Contractual Search Date',\
                'Current Price','Longitude','Latitude']) in set(raw_df.columns):
                    print('Rawdata was Cleandata')
            else:
                raw_df = raw_df[['Address','Structure Type','Status Contractual Search Date','Current Price']]
                raw_df.loc[:,'Current Price'] = raw_df['Current Price'].apply(lambda x: int(re.sub(r'[\$\,]','', str(x))))
        except:
            raise TypeError("Malformed Raw")
        return raw_df
