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
    realestate_file = '../assets/Street_Centerline.csv'
    raw_df = pd.read_csv(realestate_file,nrows=50)
    q(raw_df.columns)
    raw_df.drop(columns=['ONEWAY','OBJECTID','STREETLABE','CLASS','RESPONSIBL',\
        'STNAME','LPOLY_','RPOLY_','STCL2_','STCL2_ID','MULTI_REP','ZIP_LEFT','ZIP_RIGHT',\
        'NEWSEGDATE','PRE_DIR','ST_NAME','ST_TYPE','ST_CODE','SEG_ID','SUF_DIR','UPDATE_'], inplace=True)


    SAMPLE_SIZE=15
    SAMP=[]
    for a in range(40):
        row = raw_df.iloc[a,]
        SAMP += [[(row['FNODE_'],row['TNODE_']),(row['FNODE_']+(row['L_F_ADD']-row['R_F_ADD']),row['TNODE_']+(row['L_T_ADD']-row['R_T_ADD']))]]

    c = np.array([(1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1)]*5)
    q(SAMP)
    lc = mc.LineCollection(SAMP, colors=c, linewidths=2)
    fig, ax = plt.subplots()
    ax.add_collection(lc)
    ax.autoscale()
    ax.margins(0.1)
    plt.show()

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
