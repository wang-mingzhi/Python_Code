# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 08:44:43 2020

@author: 18120900
"""

import xlrd
import pandas as pd


# 读取包含转向流量的excel文件
workbook = xlrd.open_workbook(
    r"F:\18120900\桌面\初赛参赛材料\原始数据\交通数据_2\处理后的文件\流向级小时数据-停车次数+延误+流量.xlsx")
sheet = workbook.sheet_by_index(0)
result = []
dict = {}

for i in range(1, sheet.nrows):
    # 用交叉口编号，日期和转向组合作为key
    key = ','.join(sheet.cell(i, 0).value,sheet.cell(i, 3).value,sheet.cell(i, 4).value)
    value = [
        sheet.cell(i, 7).value,
        sheet.cell(i, 10).value,
        sheet.cell(i, 13).value,
        sheet.cell(i, 16).value
    ]
    dict.setdefault(key, []).append(value)

# 读取synchro中导出的csv文件
with open(r"F:\18120900\桌面\VOLUME.CSV", 'r', encoding='utf-8') as f:
    readlines = f.readlines()
    for line in readlines:
        splitedResult = line.split(',')
        if len(splitedResult) > 10:
            keys = [
                splitedResult[2] + ".0,20191202.0,掉头",
                splitedResult[2] + ".0,20191202.0,左后转",
                splitedResult[2] + ".0,20191202.0,左转",
                splitedResult[2] + ".0,20191202.0,直行",
                splitedResult[2] + ".0,20191202.0,右转",
                splitedResult[2] + ".0,20191202.0,右后转"
            ]
            for i in range(len(keys)):
                if keys[i] in dict:
                    splitedResult[3 + i] = dict[keys[i]][0][2]  # 南进口
                    splitedResult[9 + i] = dict[keys[i]][0][0]  # 北进口
                    splitedResult[15 + i] = dict[keys[i]][0][3]  # 西进口
                    splitedResult[21 + i] = dict[keys[i]][0][1]  # 东进口
        result.append(splitedResult)

df = pd.DataFrame(result)
# 保存的位置，可以自己定义
df.to_csv(r'F:\18120900\桌面\VOLUME-result.CSV', encoding='utf-8', index=None)
print('Done')
