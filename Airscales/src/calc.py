import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import math
import datetime as dt

class calcbot:
    def __init__(slf, geo_df, grid_cnt):
        slf.geo_df = geo_df
        slf.grid_cnt = grid_cnt
        slf.xs, slf.ys = slf.geo_df['Longitude'], slf.geo_df['Latitude']
        slf.grid_cnt = grid_cnt
        slf.min_x, slf.max_x = np.min(slf.xs), np.max(slf.xs)
        slf.min_y, slf.max_y = np.min(slf.ys), np.max(slf.ys)
        slf.width = np.abs(slf.max_x - slf.min_x)
        slf.length = np.abs(slf.max_y - slf.min_y)
        slf.raw_distrix = slf.raw_distrix()

    def raw_distrix(slf):
        distrix = [[None for _ in range(slf.grid_cnt)] for _ in range(slf.grid_cnt)]

        bounds = slf.grid_cnt - 1
        for i in range(len(slf.geo_df)): #iterating all data
            #sorting into the box
            lat, lon = slf.geo_df['Latitude'].iloc[i], slf.geo_df['Longitude'].iloc[i]
            y = bounds - math.floor(bounds * (lat - slf.min_y) / slf.length)
            x = math.floor(bounds * (lon - slf.min_x) / slf.width)
            datesold = dt.datetime.strptime(slf.geo_df['Status Contractual Search Date'].iloc[i],'%Y-%m-%d')
            # datesold = dt.datetime.toordinal(datesold)
            sellprice = slf.geo_df['Current Price'].iloc[i]

            if distrix[y][x]:
                if datesold in distrix[y][x].keys():
                    cumprice = distrix[y][x].get(datesold)[0]
                    cumcnt = distrix[y][x].get(datesold)[1]
                    distrix[y][x].update({datesold: (cumprice + sellprice, cumcnt + 1)})
                else:
                    distrix[y][x].update({datesold: (sellprice, 1)})
            else:
                distrix[y][x] = {datesold: (sellprice, 1)}

        for i in range(slf.grid_cnt):
            for j in range(slf.grid_cnt):
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

    def vna_analysis(slf, model):
        coef_tally = [None,None] # {average of relevant coef: cnt}
        coef_matrix = [[None for _ in range(slf.grid_cnt)] for _ in range(slf.grid_cnt)]
        district = slf.raw_distrix
        for i in range(slf.grid_cnt):
            for j in range(slf.grid_cnt):
                if district[j][i].empty:
                    pass
                else:
                    xs = np.array(district[j][i]['datesold']).reshape(-1, 1)
                    ys = np.array(district[j][i]['price']).reshape(-1,1)
                    # plt.scatter(np.array(district[j][i]['datesold']).reshape(-1, 1), district[j][i]['price'], s =100, c = 'red')
                    # plt.show()
                    if type(model) is LinearRegression:
                        fitmodel = model.fit(list(xs), list(ys))
                        coeff = fitmodel.coef_.item()
                        if coef_tally[0] and coef_tally[1]:
                            coef_tally[0] = (coeff + coef_tally[0])
                            coef_tally[1] = coef_tally[1] + 1
                        else:
                            coef_tally[0] = coeff
                            coef_tally[1] = 1

                        coef_matrix[j][i] = coeff
                    else: #QUADRATIC
                        fitmodel = np.polyfit(xs, ys, 2)
                        coeff = fitmodel[0]
                        if coef_tally[0] and coef_tally[1]:
                            coef_tally[0] = (coeff + coef_tally[0])
                            coef_tally[1] = coef_tally[1] + 1
                        else:
                            coef_tally[0] = coeff
                            coef_tally[1] = 1

                        coef_matrix[j][i] = coeff
                        
        mileu = coef_tally[0]/coef_tally[1]
        for i in range(slf.grid_cnt):
            for j in range(slf.grid_cnt):
                if not coef_matrix[j][i]:
                    coef_matrix[j][i] = mileu
        return coef_matrix
