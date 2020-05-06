# -*- coding: utf-8 -*-
"""
Created on Sat Mar 28 20:08:57 2020
projectName:提取海东地区的收费数据
@author: 18120900
"""
import pandas as pd


def readstationinfo(sheet):
    dict_station2road = {}

    # 仅提取海东区的收费站
    for index in range(len(sheet)):
        if sheet.iat[index, 2] != "海东区":
            continue
        if sheet.iat[index, 0] not in dict_station2road.keys():
            dict_station2road[sheet.iat[index, 0]] = sheet.iat[index, 1]
    return dict_station2road


def extratdata(data, dict_station2road):
    """
    根据收费站所在区域，提取海东区的数据
    """
    result = []
    for index in range(len(data)):
        if data[index][4] not in dict_station2road.keys():
            continue
        result.append(data[index])
    return result


def savedata(savedfilepath, data, title):
    df = pd.DataFrame(data, columns=title)
    df.to_csv(savedfilepath, encoding='utf_8_sig')


if __name__ == "__main__":
    # 获取海东区收费站和路段对应字典
    filepath_open = r"F:\18120900\桌面\青海省实车测试的表格-20200325\0-收费站与路段、地区对照表.xlsx"
    sheet = pd.read_excel(filepath_open, 0)
    dict_station2road = readstationinfo(sheet)
    print('完成第一阶段：找到海东区收费站信息')

    data = []
    temp_filepath = r"F:\18120900\桌面\青海省实车测试的表格-20200325\原始流水数据\全部货车三个时段\20200326truckdate-station.txt"
    with open(temp_filepath) as f:
        content = f.read().splitlines()
        for i in range(len(content)):
            data.append(content[i].split(';'))
    extratedata = extratdata(data, dict_station2road)
    print('完成第二阶段：提取数据')

    savedfilepath = r'F:\18120900\桌面\extrateddata-1到2月.csv'
    savedata(savedfilepath, extratedata, data[0])
    print('完成第三阶段：保存到文件')
    print('全部完成')
