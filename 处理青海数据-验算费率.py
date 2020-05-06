# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 17:14:56 2020

这里所用的数据是根据【处理青海数据-附表1.py】得到的
数据为已经清理后的数据

@author: 18120900
"""

import numpy as np
import pandas as pd


def readstationinfo(sheet):
    # key = station; value = [toll1-toll6,a0,a1,b1,a2,b2,k]
    data = np.array(sheet)
    return dict(zip(data[:, 0], data[:, 1:14]))


def caltoll(value, weight):
    # K=0或1，等于0时表示无k，1时表示有k
    money = 0
    r = value[1:7]

    if weight <= 5:  # M<=5 a0
        money = r[0]
    elif weight <= 15:  # 5<M<=15 a1+(M-5)*k*b1
        money = r[1] + (weight - 5) * r[2]
    elif weight <= 40:  # M>15 a2+(M-15)*k*b2
        k = 1 if r[5] == 0 else 1.3 - weight / 50
        money = r[3] + (weight - 15) * r[4] * k
    else:
        k = 1 if r[5] == 0 else 0.5
        money = r[3] + (weight - 15) * r[4] * k

    return round(money, 2)


def getresult(filepath, dict_station, q):
    st = pd.read_csv(filepath)
    # 根据车货总重对货车进行筛选，筛选结果为大于车货总重的数据
    data = st[((st.vehicletype == 1) & (st.weight >= 100000)) |
              ((st.vehicletype == 2) & (st.weight >= 6.5)) |
              ((st.vehicletype == 3) & (st.weight >= 10)) |
              ((st.vehicletype == 4) & (st.weight >= 13.6)) |
              ((st.vehicletype == 5) & (st.weight >= 16)) |
              ((st.vehicletype == 6) & (st.weight >= 17)) |
              ((st.vehicletype == 7) & (st.weight >= 100000))]
    grouped_data = data.groupby(['period', 'road', 'vehicletype', 'station'])

    result = []
    for name, group in grouped_data:
        temp = list(name)
        rate = dict_station[name[3]]
        # 计算现状费率
        temp.append(round(rate[name[2] + 6] / rate[0], 2))
        # 计算平均车货总重及费率
        w1 = round(group.weight.mean(), 2)
        temp.append(w1)
        temp.append(caltoll(rate, w1))
        # 计算里程加权平均车货总重及费率
        w2 = 0 if group.miles.sum() == 0 else round(sum(group.weight * group.miles) / group.miles.sum(), 2)
        temp.append(w2)
        temp.append(caltoll(rate, w2))
        # 计算百分位车货总重及费率
        for v in np.quantile(group.weight, q, interpolation='lower'):
            temp.append(v)
            temp.append(caltoll(rate, v))
            temp.append(len(group[group.weight >= v]))
            temp.append(len(group))
        result.append(temp)
    return result


if __name__ == "__main__":
    root = "F://18120900//桌面//青海省实车测试的表格-20200325//Data//"
    sheet = pd.read_excel(root + '0-辅助表.xlsx', 1)
    dict_station = readstationinfo(sheet)

    q = [0.4]  # 计算从小到大排列时，第q百分位的数据
    col = ['时段', '路段', '车型', '收费站', '现状费率', '平均货重', '费率',
           '加权平均货重', '费率', '60%吨位', '费率', 'count', 'totalcount']
    df = pd.DataFrame(getresult(root + "全部货车.csv", dict_station, q), columns=col)
    df.to_excel(r"F:\18120900\桌面\青海省费率验算.xlsx", index=False)
