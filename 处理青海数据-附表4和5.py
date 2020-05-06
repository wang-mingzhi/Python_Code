# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 11:49:20 2020
discription: 处理青海省实车测试的结果
@author: 18120900
"""
import xlrd
import numpy as np
import pandas as pd
from xlutils.copy import copy
import datetime


def readstationinfo(sheet):
    data = np.array(sheet)
    key = [(data[i, 0], data[i, 1]) for i in range(len(data))]
    value = data[:, 2:17]
    return dict(zip(key, value))


def dealdata(dict_station2road, filepath, vehtype, start_time, end_time, tollway, origin_col):
    """
    vehtype 0全部车辆，1邮政，2快递，3危货，4大企
    tollway 0车型收费;1计重收费
    """
    dic_result = {}

    data = pd.read_csv(filepath, encoding='utf_8_sig')
    # 选择vehtype类型的数据
    data = data[data.type == vehtype]
    data['EXTIME'] = data['EXTIME'].astype('datetime64')
    # 筛选在该时段范围内的数据（start_time,end_time）
    data = data[(start_time <= data.EXTIME) & (data.EXTIME <= end_time)]
    # 清洗掉车货总重为0、轴数为0,1的数据
    data = data.query('(TOTALWEIGHT>0) & (AXISNUM>1)')
    # 根据车牌颜色对二轴车进行划分
    data.loc[(data.AXISNUM == 2) & (data.Explatecolor == 0), 'AXISNUM'] = 1

    list_data = np.array(data).tolist()
    for item in list_data:  # 对文件中的数据进行处理
        key = (item[3], item[5])
        # 清洗掉key不存在于字典中的数据，不可忽略
        if key not in dict_station2road.keys():
            continue

        weight = item[11] / 1000
        axisnum = item[9]
        low_weight = {2: 6.5, 3: 10, 4: 13.6, 5: 16, 6: 17}
        if weight <= low_weight.get(axisnum, 0):  # 清洗掉小于车辆自重的数据
            continue

        tollmoney = item[12]
        miles = item[14] / 1000

        if dict_station2road[key][1] == '开放式':  # 把开放式收费站的里程补全
            miles = dict_station2road[key][2]
            if axisnum == 1 or axisnum == 2:
                continue
        if int(miles) == 0 and origin_col != 16:  # 清理掉收费里程为0的数据(不包括疫情期间)
            continue

        # 根据x吨的范围为[(x-1).5,x.49]，确定吨数，x=0时[0,1.49]
        if weight - int(weight) <= 0.49:
            if int(weight) == 0:
                temp_key = (dict_station2road[key][0], axisnum, 1)
            else:
                temp_key = (dict_station2road[key][0], axisnum, int(weight))
        else:
            temp_key = (dict_station2road[key][0], axisnum, int(weight) + 1)

        money = caltoll(dict_station2road, key, axisnum, weight, miles, tollway)
        if temp_key not in dic_result.keys():
            dic_result[temp_key] = np.array([1, miles, tollmoney, money, weight, weight * miles])
        else:
            dic_result[temp_key] += np.array([1, miles, tollmoney, money, weight, weight * miles])
    return dic_result


def summary(result):
    # 第一列是对应的限重，第二列是开始行号（+吨数，就是excel中的行号）；均是从0开始的行号
    dict_info = {1: [5, 3], 2: [18, 9], 3: [28, 28], 4: [37, 57], 5: [44, 95], 6: [50, 140]}
    # dict_temp key=路段，轴数，excel中的行号（=开始行号+吨数，下标从0开始）
    # value=数量，里程，收费额，推算收费额，总重，总重*里程
    dict_temp = {}
    for k, v in result.items():
        # 设定key值
        road = k[0]
        axisnum = k[1]
        weight = k[2]
        if axisnum > 16:
            key = (road, 17, 202)
        elif axisnum >= 7:
            key = (road, axisnum, 185 + axisnum)
        else:
            if weight < dict_info[axisnum][0]:
                key = (road, axisnum, dict_info[axisnum][1] + weight)
            else:
                key = (road, axisnum, dict_info[axisnum][1] + dict_info[axisnum][0])

        # 对dict_temp 赋值
        dict_temp[key] = dict_temp[key] + np.array(v) if key in dict_temp else np.array(v)

        # 计算整个青海的数据
        qinghai = ('青海省', key[1], key[2])
        if qinghai in dict_temp:
            dict_temp[qinghai] += np.array(v)
        else:
            dict_temp[qinghai] = np.array(v)

    # 对每轴车辆进行小计统计
    distinct_road = list(set([road[0] for road in dict_temp.keys()]))
    for road in distinct_road:
        for k, v in dict_info.items():
            values = [value for key, value in dict_temp.items() if key[0] == road and key[1] == k]
            if len(values) == 0:
                continue
            dict_temp[(road, k, v[0] + v[1] + 1)] = np.array(np.sum(values, axis=0))

        # 对大于7轴的车辆进行小计
        values = [value for key, value in dict_temp.items() if key[0] == road and key[1] >= 7]
        if len(values) == 0:
            continue
        dict_temp[(road, 7, 203)] = np.array(np.sum(values, axis=0))
    return dict_temp


def writetofile(result, origin_col, index, suffix1, suffix2):
    """
    result dealdata处理得到的结果
    origin_col 把数据从哪一列开始写入
    index 把数据写入到哪个表；0：全部货车，1：典型货车
    suffix eg: F://18120900//桌面//测试成果// + 阿李路 + suffix
    """
    dict_temp = summary(result)
    filepath = "F://18120900//桌面//青海省实车测试的表格-20200325//Data//测试成果//"
    for road in set([k[0] for k in dict_temp.keys()]):
        # 处理货运车辆费率调整对比表
        r_wb = copy(xlrd.open_workbook(filepath + road + '-货运车辆费率调整对比表' + suffix1, 'r'))
        road_sheet = r_wb.get_sheet(index)
        for k, v in dict_temp.items():
            temp_a = 0 if v[1] == 0 else int(v[2]) / int(v[1])
            temp_b = 0 if v[1] == 0 else int(v[3]) / int(v[1])
            road_sheet.write(k[2], origin_col, int(v[0]))
            road_sheet.write(k[2], origin_col + 1, int(v[1]))
            if origin_col != 16:
                road_sheet.write(k[2], origin_col + 2, int(v[2]))
                road_sheet.write(k[2], origin_col + 3, int(v[3]))
                road_sheet.write(k[2], origin_col + 4, temp_a)
                road_sheet.write(k[2], origin_col + 5, temp_b)
        r_wb.save(filepath + road + '-货运车辆费率调整对比表' + suffix2)

        # 处理货车费率调整对比分析表
        r_wb2 = copy(xlrd.open_workbook(filepath + road + '-货车费率调整对比分析表' + suffix1, 'r'))
        road_sheet2 = r_wb2.get_sheet(index)

        dict_col = {4: 1, 10: 10, 16: 19}
        col = dict_col[origin_col]
        rowindex = [9, 28, 57, 95, 140, 191, 203]
        for r in range(7):
            key = (road, r + 1, rowindex[r])
            if key in dict_temp.keys():
                values = dict_temp[key]
                a = (0, 0) if values[0] == 0 else (values[1] / values[0], values[4] / values[0])
                if values[1] == 0:
                    b = [0, 0, 0]
                else:
                    b = list(map(lambda x: x / values[1], [values[5], values[2], values[3]]))
                v = [values[0], values[1], values[2], values[3], a[0], a[1], b[0], b[1], b[2]]
                if col != 19:
                    for c in range(len(v)):
                        road_sheet2.write(4 + r, col + c, v[c])
                else:
                    road_sheet2.write(4 + r, col, v[0])
                    road_sheet2.write(4 + r, col + 1, v[1])
                    road_sheet2.write(4 + r, col + 2, v[4])
                    road_sheet2.write(4 + r, col + 3, v[5])
                    road_sheet2.write(4 + r, col + 4, v[6])
        r_wb2.save(filepath + road + '-货车费率调整对比分析表' + suffix2)


def caltoll(dict_station2road, key, axisnum, weight, miles, tollway):
    money = 0
    if tollway == 0:  # 推算车型收费下的收费额
        if 6 >= axisnum > 0:
            if dict_station2road[key][1] == '封闭式':
                money = dict_station2road[key][axisnum + 2] * miles
            if dict_station2road[key][1] == '开放式':
                money = dict_station2road[key][axisnum + 2]
        elif axisnum <= 12:
            money = (1.25 + (axisnum - 6) * 0.2) * miles
        else:
            money = 2.45 * miles
        return round(money)
    elif tollway == 1:  # 推算计重收费下收费额
        r = dict_station2road[key][9:15]

        # 计算超限车辆的载重
        dict_tolllimt = {1: 200, 2: 200, 3: 300, 4: 400, 5: 500, 6: 550}
        limit = dict_tolllimt.get(axisnum, 55)
        if weight <= limit:
            weight = weight
        elif weight <= limit * 1.3:
            weight = 2 * weight - limit
        elif weight <= limit * 1.5:
            weight = 4 * weight - 3.6 * limit
        elif weight <= limit * 2:
            weight = 8 * weight - 9.6 * limit
        else:
            weight = 12 * weight - 17.6 * limit

        if weight <= 5:  # M<=5 a0
            money = r[0] * miles
        elif weight <= 15:  # 5<M<=15 a1+(M-5)*k*b1
            money = (r[1] + (weight - 5) * r[2]) * miles
        elif weight <= 40:  # M>15 a2+(M-15)*k*b2
            k = 1 if r[5] == 0 else 1.3 - weight / 50
            money = (r[3] + (weight - 15) * r[4] * k) * miles
        else:
            k = 1 if r[5] == 0 else 0.5
            money = (r[3] + (weight - 15) * r[4] * k) * miles

        # 计费不足10元，按10元计收；10元以上按实际里程计收；不足一元，四舍五入
        money = 10 if money < 10 else round(money)
    return money


def configuration(dict_station2road, sheet_index, vehtype, year1, month1, day1,
                  year2, month2, day2, index, origin_col, tollway, suffix1, suffix2):
    """
    sheet_index 读取哪个表的原始数据
    vehtype 0全部车辆，1邮政，2快递，3危货，4大企
    index =0把结果放到所有车辆的表，=1把结果放到典型车辆的表
    origin_col =4写入到12月份;=10写入到1月份；=16写入到2月份
    tollway =0车型收费；=1计重收费
    suffix1 打开的文件的后缀名
    suffix2 保存时文件的后缀名
    """
    dic = "F://18120900//桌面//青海省实车测试的表格-20200325//Data//"
    # 按要求处理数据，并返回一个结果列表
    filename = ['2019truckdata.csv', '2020truckdata-station.csv',
                '2019typicaltruckdata.csv', '2020typicaltruckdata.csv']
    filepath = dic + filename[sheet_index]  # 读取哪个表的原始数据
    start_time = datetime.datetime(year1, month1, day1, 0, 0, 0)  # 时间段的开始时间
    end_time = datetime.datetime(year2, month2, day2, 23, 59, 59)  # 时间段的结束时间
    # dic_result[key:[路段名，轴数，吨位数],
    # value:[车辆数，收费里程，应收金额, 推算下的收费额,总重，总重*里程]]
    dic_result = dealdata(dict_station2road, filepath, vehtype, start_time, end_time, tollway, origin_col)
    print("完成第二阶段：处理数据")

    # 把结果写入文件
    writetofile(dic_result, origin_col, index, suffix1, suffix2)
    print("完成第三阶段：写入文件")


if __name__ == "__main__":
    '''
    处理过程中清理掉了：载重为零；或收费里程为零；或轴数为零的数据
    '''
    # 获取收费站和路段对应字典
    filename_open = r"F:\18120900\桌面\青海省实车测试的表格-20200325\Data\0-辅助表.xlsx"
    sheet = pd.read_excel(filename_open, 0)
    # key=(stationid,lane)，value=[road,roadtype,miles(km),toll1-toll6](9个元素),a0,a1,b1,a2,b2,k]
    # M<=15,k=1;M<=40,k=1.3-M/50;M>40,k=0.5;这里K=0或1，等于0时表示无k，1时表示有k
    # a0;a1+(M-5)*k*b1;a2+(M-15)*k*b2
    dict_station2road = readstationinfo(sheet)
    print('完成第一阶段：找到海东区收费站信息')

    config = [[2, 1, 2019, 12, 1, 2019, 12, 31, 1, 4, 0, '.xlsx', '.xls'],
              [3, 1, 2020, 1, 10, 2020, 1, 24, 1, 10, 1, '.xls', 'temp.xls'],
              [3, 1, 2020, 2, 17, 2020, 3, 2, 1, 16, 1, 'temp.xls', '.xls'],
              [2, 2, 2019, 12, 1, 2019, 12, 31, 2, 4, 0, '.xls', 'temp.xls'],
              [3, 2, 2020, 1, 10, 2020, 1, 24, 2, 10, 1, 'temp.xls', '.xls'],
              [3, 2, 2020, 2, 17, 2020, 3, 2, 2, 16, 1, '.xls', 'temp.xls'],
              [2, 3, 2019, 12, 1, 2019, 12, 31, 3, 4, 0, 'temp.xls', '.xls'],
              [3, 3, 2020, 1, 10, 2020, 1, 24, 3, 10, 1, '.xls', 'temp.xls'],
              [3, 3, 2020, 2, 17, 2020, 3, 2, 3, 16, 1, 'temp.xls', '.xls'],
              [2, 4, 2019, 12, 1, 2019, 12, 31, 4, 4, 0, '.xls', 'temp.xls'],
              [3, 4, 2020, 1, 10, 2020, 1, 24, 4, 10, 1, 'temp.xls', '.xls'],
              [3, 4, 2020, 2, 17, 2020, 3, 2, 4, 16, 1, '.xls', 'temp.xls'],
              [0, 0, 2019, 12, 1, 2019, 12, 31, 0, 4, 0, 'temp.xls', '.xls'],
              [1, 0, 2020, 1, 10, 2020, 1, 24, 0, 10, 1, '.xls', 'temp.xls'],
              [1, 0, 2020, 2, 17, 2020, 3, 2, 0, 16, 1, 'temp.xls', '.xls']]

    for v in config:
        configuration(dict_station2road, v[0], v[1], v[2], v[3], v[4], v[5],
                      v[6], v[7], v[8], v[9], v[10], v[11], v[12])
        print('完成一次迭代')
