# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 20:25:29 2020
ProjectedName: 处理深圳交叉口车辆行驶轨迹高精数据
@author: 18120900
"""

import json
import os
from datetime import datetime

import pandas as pd


def dealdata():
    rootdir_open = r'F:\18120900\桌面\深圳高精\解压后的数据\merge20200331'
    rootdir_save = r'F:\18120900\桌面\深圳高精\解压后的数据'
    filenames = os.listdir(rootdir_open)
    for filename in filenames:
        path_open = os.path.join(rootdir_open, filename)
        path_save = os.path.join(rootdir_save, filename)
        if not os.path.isfile(path_open):
            continue
        contentList = []
        with open(path_open, encoding='utf-8') as f:
            data = f.readlines()
            json_file = [json.loads(item) for item in data]
            title1 = [t1 for t1 in json_file[0].keys()]
            title2 = [t2 for t2 in json_file[0]['track'][0].keys()]
            title = title1 + title2
            title.pop(4)
            for items in json_file:
                ct1 = [v for v in items.values() if not isinstance(v, list)]
                ct1[1] = datetime.fromtimestamp(items['time'] / 1000.0).strftime("%Y-%m-%d %H:%M:%S.%f")
                for item in items['track']:
                    ct2 = [item_v for item_v in item.values()]
                    contentList.append(ct1 + ct2)

        df = pd.DataFrame(columns=title, data=contentList)
        df.drop(['type', 'crossID', 'cnodeMessageType', 'vehicleYearBrand'], axis=1, inplace=True)
        df.sort_values(by='time', ascending=True, inplace=True)
        df.to_csv(path_save+'.csv', index=False, encoding='utf_8_sig')
        print(filename + ' Done')


def infoextract():
    data = pd.read_csv(r"F:\18120900\桌面\深圳高精\解压后的数据\滨康路江虹路路口-20200331100000.txt.csv")
    dt = set(data.iloc[:, 0] // 1000)  # 去掉毫秒部分
    selected_data = [item for item in data if item[0][:, len(item[0] - 3)] in dt]


if __name__ == '__main__':
    dealdata()
