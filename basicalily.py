import numpy as np
import pandas as pd
import datetime as dt
from geopy.geocoders import Nominatim
import matplotlib.pyplot as plt
import math
import re
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

class cleaner:
    def __init__(self, raw_df, doclean=False):
         self.clean_df = self.clean(raw_df) if doclean else raw_df

    def clean(self, raw_df):
        try:
            if set(['Address','Structure Type','Status Contractual Search Date',\
                'Current Price','Longitude','Latitude']) in set(raw_df.columns) and \
                len(df.columns) == 7:
                    print('Rawdata was Cleandata')
            else:
                raw_df = raw_df[['Address','Structure Type','Status Contractual Search Date','Current Price']]
                raw_df.loc[:,'Current Price'] = raw_df['Current Price'].apply(lambda x: int(re.sub(r'[\$\,]','', str(x))))
        except:
            raise TypeError("Malformed Raw")


        return raw_df

class geobot:

    def __init__(self, cleaned):
        try:
            if 'Latitude' not in set(cleaned.clean_df.columns) and \
                'Longitude' not in set(cleaned.clean_df.columns):
                self.geo_df = self.geo(cleaned.clean_df)
            else:
                self.geo_df = cleaned.clean_df

        except:
            raise TypeError("Malformed Clean")

    def geo(self, clean_df):
        try:
            geol = Nominatim(user_agent="imagellan")
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

class graphbot:
    def __init__(self, geo_df, grid_cnt):
        if 'Latitude' not in set(geo_df.columns) and \
            'Longitude' not in set(geo_df.columns):
            raise TypeError("Malformed Geo")
        else:
            self.geo_df = geo_df
            self.xs, self.ys = self.geo_df['Longitude'], self.geo_df['Latitude']
            self.grid_cnt = grid_cnt
            self.min_x, self.max_x = np.min(self.xs), np.max(self.xs)
            self.min_y, self.max_y = np.min(self.ys), np.max(self.ys)
            self.width = np.abs(self.max_x - self.min_x)
            self.length = np.abs(self.max_y - self.min_y)

    def scatter(self, colormap='cool'):
        def normalize(x):
            x = np.asarray(x)
            return (x - x.min()) / np.ptp(x)
        colors = normalize(self.geo_df['Current Price'])

        fig = plt.figure()
        ax = fig.gca()

        min_x, max_x = np.min(self.xs), np.max(self.xs)
        min_y, max_y = np.min(self.ys), np.max(self.ys)

        ax.set_xticks(np.arange(min_x, max_x, (1/self.grid_cnt) * abs(max_x - min_x)))
        ax.set_yticks(np.arange(min_y, max_y, (1/self.grid_cnt) * abs(max_y - min_y)))

        plt.scatter(self.xs, self.ys, c=colors, cmap=colormap, alpha=0.99)
        plt.xlim(min_x, max_x)
        plt.ylim(min_y, max_y)
        plt.grid(which='major', linestyle='-', linewidth='0.5', color='blue')

        plt.show()

    def distrix_avg(self, colormap='cool'):
        def normalize(x):
            x = np.asarray(x)
            return (x - x.min()) / np.ptp(x)
        colors = normalize(self.geo_df['Current Price'])
        AVG_UNIVERSAL_PRICE = np.mean(self.geo_df['Current Price'])

        distrix = [[None for _ in range(self.grid_cnt)] for _ in range(self.grid_cnt)]

        bounds = self.grid_cnt - 1
        for i in range(len(self.geo_df)): # Nasty iloc behavior
            lat, lon = self.geo_df['Latitude'].iloc[i], self.geo_df['Longitude'].iloc[i]
            y = bounds - math.floor(bounds * (lat - self.min_y) / self.length)
            x = math.floor(bounds * (lon - self.min_x) / self.width)
            cnt = 1
            total = self.geo_df['Current Price'].iloc[i]
            if distrix[y][x]:
                cnt += distrix[y][x].get('cnt')
                total += distrix[y][x].get('total')
            distrix[y][x] = {'cnt' : cnt, 'total' : total}

        def avg(cntotal): return cntotal.get('total')/cntotal.get('cnt')

        for i in range(self.grid_cnt):
            for j in range(self.grid_cnt):
                if distrix[i][j]:
                    distrix[i][j] = avg(distrix[i][j])
                else:
                    distrix[i][j] = AVG_UNIVERSAL_PRICE
        self.interpolate(distrix)
        return distrix

    def interpolate(self, distrix, colormap='cool'):
        fig = plt.figure()
        ax = fig.gca()
        ax.set_xticks(np.arange(self.min_x, self.max_x, (1/self.grid_cnt) * abs(self.width)))
        ax.set_yticks(np.arange(self.min_y, self.max_y, (1/self.grid_cnt) * abs(self.length)))
        plt.imshow(distrix, cmap=colormap, interpolation='nearest')
        plt.colorbar()
        plt.show()


class calcbot:
    def __init__(self, geo_df, grid_cnt):
        self.geo_df = geo_df
        self.grid_cnt = grid_cnt
        self.xs, self.ys = self.geo_df['Longitude'], self.geo_df['Latitude']
        self.grid_cnt = grid_cnt
        self.min_x, self.max_x = np.min(self.xs), np.max(self.xs)
        self.min_y, self.max_y = np.min(self.ys), np.max(self.ys)
        self.width = np.abs(self.max_x - self.min_x)
        self.length = np.abs(self.max_y - self.min_y)
        self.raw_distrix = self.raw_distrix()

    def raw_distrix(self):
        distrix = [[None for _ in range(self.grid_cnt)] for _ in range(self.grid_cnt)]

        bounds = self.grid_cnt - 1
        for i in range(len(self.geo_df)): #iterating all data
            #sorting into the box
            lat, lon = self.geo_df['Latitude'].iloc[i], self.geo_df['Longitude'].iloc[i]
            y = bounds - math.floor(bounds * (lat - self.min_y) / self.length)
            x = math.floor(bounds * (lon - self.min_x) / self.width)
            datesold = dt.datetime.strptime(self.geo_df['Status Contractual Search Date'].iloc[i],'%Y-%m-%d')
            # datesold = dt.datetime.toordinal(datesold)
            sellprice = self.geo_df['Current Price'].iloc[i]

            if distrix[y][x]:
                if datesold in distrix[y][x].keys():
                    cumprice = distrix[y][x].get(datesold)[0]
                    cumcnt = distrix[y][x].get(datesold)[1]
                    distrix[y][x].update({datesold: (cumprice + sellprice, cumcnt + 1)})
                else:
                    distrix[y][x].update({datesold: (sellprice, 1)})
            else:
                distrix[y][x] = {datesold: (sellprice, 1)}

        for i in range(self.grid_cnt):
            for j in range(self.grid_cnt):
                try:
                    sales = distrix[j][i]
                    for k in sales.keys():
                        sales.update({k: sales.get(k)[0] / sales.get(k)[1]})
                    sales = dict(sorted(sales.items()))
                    sales_df = pd.DataFrame({'datesold':list(sales.keys()),'price':list(sales.values())})
                    distrix[j][i] = sales_df
                except:
                    distrix[j][i] = pd.DataFrame({})

        return distrix

    def vna_analysis(self, model):
        coef_tally = () # {average of relevant coef: cnt}
        coef_matrix = [[None for _ in range(self.grid_cnt)] for _ in range(self.grid_cnt)]
        district = self.raw_distrix
        for i in range(self.grid_cnt):
            for j in range(self.grid_cnt):
                if district[j][i].empty:
                    pass
                else:
                    fitmodel = model.fit(np.array(district[j][i]['datesold']).reshape(-1, 1), district[j][i]['price'])
                    if type(fitmodel) is LinearRegression:
                        coef_tally[0] = fitmodel.coef_ + coef_tally[0] if len(coef_tally) else coef_tally[0]
                        coef_tally[1] = coef_tally[1] + 1 if len(coef_tally) else 1
                    coef_matrix[j][i] = fitmodel.coef_

        mileu = coef_tally[0]/coef_tally[1]
        for i in range(self.grid_cnt):
            for j in range(self.grid_cnt):
                if coef_matrix[j][i].empty: coef_matrix[j][i] = mileu

        print(coef_matrix)

class magellan(calcbot, graphbot):
    def __init__(self, geobot, params):
        self.grid_cnt = params['grid_cnt'] if 'grid_cnt' in params.keys() else 10
        self.window = params['window'] if 'window' in params.keys() else 30
        self.model = params['model'] if 'model' in params.keys() else LinearRegression()
        self.geo_df = geobot.geo_df

        calcbot.__init__(self, self.geo_df, self.grid_cnt)
        graphbot.__init__(self, self.geo_df, self.grid_cnt)

    def vanilla_linreg(self):
        self.vna_analysis(LinearRegression())

    # def rolling_district_avg(self, i, j, window, step):
    #     width, length = self.graphbot.width, self.graphbot.length
    #
    #     distrix = [[None for _ in range(10)] for _ in range(10)]
    #
    #
    #     return self.model



if __name__ == '__main__':
    realestate_file = 'processed_realestate.csv'
    raw_df = pd.read_csv(realestate_file)
    params = {'grid_cnt':4, 'window':5, 'step':1, 'model': LinearRegression() }
    M = magellan(geobot(cleaner(raw_df, False)), params)
    M.vanilla_linreg()
    # for i in range(4):
    #     for j in range(4):
    #         try:
    #             print(r[i][j])
    #         except:
    #             pass


    if False:
        realestate_file = 'processed_realestate.csv'
        raw_df = pd.read_csv(realestate_file)
        doclean = True
        geoed = geobot(cleaner(raw_df)) # Optimize, need to note if clean or not

        # print(geoed.geo_df)
        geoed.geo_df.to_csv('processed_realestate.csv')

        grapher = graphbot(geoed.geo_df, 40)

        grapher.districts_avg()
        grapher.scatter()
