import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import math
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

from matplotlib import collections  as mc


import geo as ge
import graph as gr
import calc as cc

class airscales(cc.calcbot, gr.graphbot):
    def __init__(slf, geobot, params):
        slf.grid_cnt = params['grid_cnt'] if 'grid_cnt' in params.keys() else 10
        slf.window = params['window'] if 'window' in params.keys() else 30
        slf.model = params['model'] if 'model' in params.keys() else LinearRegression()
        slf.geo_df = geobot.geo_df
        cc.calcbot.__init__(slf, slf.geo_df, slf.grid_cnt)
        gr.graphbot.__init__(slf, slf.geo_df, slf.grid_cnt)

    def vanilla_linreg(slf):
        return slf.vna_analysis(LinearRegression())

class pfit:
    def __init__(slf, d):
        slf.degree = d

    def fit(slf, x, y):
        return np.polyfit(x, y, slf.degree)

if __name__ == '__main__':
    def q(string):
        print(string)
    realestate_file = '../assets/processed_real_estate.csv'
    raw_df = pd.read_csv(realestate_file,nrows=50)

    # params = {'grid_cnt':4, 'window':5, 'step':1, 'model': LinearRegression() }
    # M = airscales(ge.geobot(raw_df, False), params)
    # dix = M.raw_distrix

    # # M.scatter_district(dix[7][0], LinearRegression())
    # # Give function degree d, and return function consuming x,y that returns np.polyfit(x,y,d)
    # # P = pfit(2)
    # vanlinreg = M.vna_analysis(LinearRegression())
    # M.oculos(vanlinreg)
    # M.scatter_all()
    # M.interpolate(vanlinreg)
    # # # M.refract([[1,1,1],[1,1,1],[1,1,1]])
