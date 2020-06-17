import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import math

class graphbot:
    def __init__(slf, geo_df, grid_cnt):
        if 'Latitude' not in set(geo_df.columns) and \
            'Longitude' not in set(geo_df.columns):
            raise TypeError("Malformed Geo")
        else:
            slf.geo_df = geo_df
            slf.xs, slf.ys = slf.geo_df['Longitude'], slf.geo_df['Latitude']
            slf.grid_cnt = grid_cnt
            slf.min_x, slf.max_x = np.min(slf.xs), np.max(slf.xs)
            slf.min_y, slf.max_y = np.min(slf.ys), np.max(slf.ys)
            slf.width = np.abs(slf.max_x - slf.min_x)
            slf.length = np.abs(slf.max_y - slf.min_y)

    def scatter_all(slf, colormap='cool'):
        def normalize(x):
            x = np.asarray(x)
            return (x - x.min()) / np.ptp(x)
        colors = normalize(slf.geo_df['Current Price'])

        fig = plt.figure()
        ax = fig.gca()

        min_x, max_x = np.min(slf.xs), np.max(slf.xs)
        min_y, max_y = np.min(slf.ys), np.max(slf.ys)

        ax.set_xticks(np.arange(min_x, max_x, (1/slf.grid_cnt) * abs(max_x - min_x)))
        ax.set_yticks(np.arange(min_y, max_y, (1/slf.grid_cnt) * abs(max_y - min_y)))

        plt.scatter(slf.xs, slf.ys, c=colors, cmap=colormap, alpha=0.99)
        plt.xlim(min_x, max_x)
        plt.ylim(min_y, max_y)
        plt.grid(which='major', linestyle='-', linewidth='0.5', color='blue')

        plt.show()

    def scatter_district(slf, distrix, model): #iterable of tuples or tuple
        if isinstance(distrix, pd.DataFrame): distrix = [distrix]
        if not all(isinstance(d, pd.DataFrame) for d in distrix):
            raise TypeError('Scatter District failed; bad type input')

        svrs = [model]
        model_color = ['m', 'c', 'g']
        fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(15, 10), sharey=True)
        kernel_label = ['RBF', 'Linear', 'Polynomial']
        dist = 0
        X = list(distrix[dist]['datesold'])
        y = list(distrix[dist]['price'])
        for ix, svr in enumerate(svrs):
            print(list(X), list(y))
            ys =  svr.fit(X, y).predict(X)
            axes[ix].plot(X, ys, color=model_color[ix], lw=lw, label='{} model'.format(kernel_label[ix]))
            axes[ix].scatter(X[svr.support_], y[svr.support_], facecolor="none", edgecolor=model_color[ix], s=50,\
                label='{} support vectors'.format(kernel_label[ix]))
            axes[ix].scatter(X[np.setdiff1d(np.arange(len(X)), svr.support_)],\
                y[np.setdiff1d(np.arange(len(X)), svr.support_)],\
                facecolor="none", edgecolor="k", s=50,\
                label='other training data')
            axes[ix].legend(loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=1, fancybox=True, shadow=True)

    def distrix_avg(slf, show=False, colormap='cool'):
        def normalize(x):
            x = np.asarray(x)
            return (x - x.min()) / np.ptp(x)
        colors = normalize(slf.geo_df['Current Price'])
        AVG_UNIVERSAL_PRICE = np.mean(slf.geo_df['Current Price'])

        distrix = [[None for _ in range(slf.grid_cnt)] for _ in range(slf.grid_cnt)]

        bounds = slf.grid_cnt - 1
        for i in range(len(slf.geo_df)): # Nasty iloc behavior
            lat, lon = slf.geo_df['Latitude'].iloc[i], slf.geo_df['Longitude'].iloc[i]
            y = bounds - math.floor(bounds * (lat - slf.min_y) / slf.length)
            x = math.floor(bounds * (lon - slf.min_x) / slf.width)
            cnt = 1
            total = slf.geo_df['Current Price'].iloc[i]
            if distrix[y][x]:
                cnt += distrix[y][x].get('cnt')
                total += distrix[y][x].get('total')
            distrix[y][x] = {'cnt' : cnt, 'total' : total}

        def avg(cntotal): return cntotal.get('total')/cntotal.get('cnt')

        for i in range(slf.grid_cnt):
            for j in range(slf.grid_cnt):
                if distrix[i][j]:
                    distrix[i][j] = avg(distrix[i][j])
                else:
                    distrix[i][j] = AVG_UNIVERSAL_PRICE
        if show: slf.interpolate(distrix)
        return distrix

    def interpolate(slf, distrix, colormap='cool'):
        fig = plt.figure()
        ax = fig.gca()
        ax.imshow(distrix, cmap=colormap, interpolation='nearest')
        ax.set_xticks(np.arange(-.5, slf.grid_cnt, 1))
        ax.set_yticks(np.arange(-.5, slf.grid_cnt, 1))
        ax.set_xticklabels(np.arange(1, slf.grid_cnt + 2, 1))
        ax.set_yticklabels(np.arange(1, slf.grid_cnt + 2, 1))
        ax.grid(b=True,color='w',linestyle='-',linewidth=2)
        # fig.colorbar()
        plt.show()

    def oculos(slf, matrix):
        def pprint(n, figs=3): #5

            sigfig = float(f'%.{figs}g' % n)
            if sigfig > 0:
                power = math.floor(math.log(sigfig,10))
            elif sigfig < 0:
                power = -math.floor(math.log(-sigfig,10))
            else:
                power = 0
            sci_figs = sigfig/10**power
            # print(sigfig,str(sci_figs)[:figs+2],power)
            if sigfig >= 0:
                pad = str(sci_figs)[:figs+2] + '0' * (figs + 1 - len(str(sci_figs)[:figs+2]) )
            else:
                pad = '0' * (figs + 1 - len(str(sci_figs)[:figs+2])) + str(sci_figs)[:figs+2]
            power = '0' * (figs - len(str(power))) + str(power)
            sci = f'{pad}e{power}'
            return sci if sci[0] == '-' else ' ' + sci

        if isinstance(matrix, list) and isinstance(matrix[0], list):
            for i in range(len(matrix)):
                print(list(map(lambda n: pprint(n), matrix[i])))
