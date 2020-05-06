# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 11:49:20 2020
discription: 处理青海省实车测试的结果
@author: 18120900
"""
import numpy as np
import pandas as pd
import datetime


def readstationinfo(sheet):
    data = np.array(sheet)
    key = [(data[i, 0], data[i, 1]) for i in range(len(data))]
    value = data[:, 2:18]
    dict_station2road = dict(zip(key, value))
    return dict_station2road


def dealdata(result, dict_station2road, filepath, vehtype, start_time, end_time, tollway, period):
    """
    vehtype 0全部车辆，1邮政，2快递，3危货，4大企
    tollway 0推算时按车型收费;1推算时按计重收费
    """
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

    dic_veh = {1: '一类货车', 2: '二类货车', 3: '三类货车', 4: '四类货车', 5: '五类货车', 6: '六类货车'}
    list_data = np.array(data).tolist()
    for item in list_data:  # 对文件中的数据进行处理
        key = (item[3], item[5])
        # 清洗掉key不存在于字典中的数据，不可忽略
        if key not in dict_station2road.keys():
            continue

        weight = item[11] / 1000
        axisnum = item[9]
        # low_weight = {2: 4.5, 3: 6.5, 4: 7.5, 5: 16, 6: 17}
        low_weight = {2: 6.5, 3: 10, 4: 13.6, 5: 16, 6: 17}
        if weight <= low_weight.get(axisnum, 0):  # 清洗掉小于车辆自重的数据
            continue

        tollmoney = item[12]
        miles = item[14] / 1000
        if dict_station2road[key][1] == '开放式':  # 把开放式收费站的里程补全
            miles = dict_station2road[key][2]
            if axisnum == 1 or axisnum == 2:
                continue
        if int(miles) == 0 and period != '免费时段':  # 清理掉收费里程为0的数据(不包括疫情期间)
            continue

        money = caltoll(dict_station2road, key, axisnum, weight, miles, tollway)
        road = dict_station2road[key][0]
        veh = dic_veh.get(axisnum, '超限大件运输车')
        station = dict_station2road[key][15]
        if tollway == 0:
            temp_result = [item[0], period, veh, weight, miles, tollmoney, money, road, station]
        else:
            temp_result = [item[0], period, veh, weight, miles, money, tollmoney, road, station]
        result.append(temp_result)
    return result


def caltoll(dict_station2road, key, axisnum, weight, miles, tollway):
    money = 0
    if tollway == 0:  # 推算车型收费下的收费额
        if 6 >= axisnum > 0:
            m = miles if dict_station2road[key][1] == '封闭式' else 1
            money = dict_station2road[key][axisnum + 2] * m
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
        key = (0, 1), (1, 1.3), (1.3, 1.5), (1.5, 2), (2, 1000)
        value = [1, 0], [2, 1], [4, 3.6], [8, 9.6], [12, 17.6]
        dict_coe = dict(zip(key, value))
        coe = [value for key, value in dict_coe.items() if key[0] < weight / limit <= key[1]]
        weight = weight * coe[0] - limit * coe[1]

        if weight <= 5:  # M<=5 0.45
            money = r[0] * miles
        elif weight <= 15:  # 5<M<=15 0.45+(M-5)*0.03
            money = (r[1] + (weight - 5) * r[2]) * miles
        elif weight <= 40:  # 40>=M>15 0.75+(M-15)*0.015
            k = 1 if r[5] == 0 else 1.3 - weight / 50
            money = (r[3] + (weight - 15) * r[4] * k) * miles
        else:
            k = 1 if r[5] == 0 else 0.5
            money = (r[3] + (weight - 15) * r[4] * k) * miles

        # 计费不足10元，按10元计收；10元以上按实际里程计收；不足一元，四舍五入
        money = 10 if money < 10 else round(money)
    return money


def write2csv(results, savepath):
    title = ['车牌', '出行时段', '收费车型', '车货总质量（吨）', '行驶里程（公里）',
             '计重收费（旧标准）费额（元）', '车型收费（新标准）费额（元）', '路段', '收费站']
    dic_file = {0: '全部货车', 1: '邮政', 2: '快递', 3: '危货', 4: '大企'}
    with pd.ExcelWriter(savepath) as writer:
        for index, result in enumerate(results):
            df = pd.DataFrame(data=result, columns=title)
            df.to_excel(writer, sheet_name=dic_file[index])


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
    dict_station = readstationinfo(sheet)

    config = [[2019, 12, 1, 2019, 12, 31, 0, '费率调整前时段'],
              [2020, 1, 10, 2020, 1, 24, 1, '费率调整后时段'],
              [2020, 2, 17, 2020, 3, 2, 1, '免费时段']]
    dic_file = {0: '全部货车', 1: '邮政', 2: '快递', 3: '危货', 4: '大企'}

    re = []
    dic = "F://18120900//桌面//青海省实车测试的表格-20200325//Data//"
    filename = ['2019truckdata.csv', '2020truckdata-station.csv',
                '2019typicaltruckdata.csv', '2020typicaltruckdata.csv']
    for vehtype in range(5):
        result = []
        for v in config:
            i = 0 if vehtype == 0 else 2
            k = 0 if v[7] == '费率调整前时段' else 1
            filepath = dic + filename[i + k]  # 读取哪个表的原始数据
            start_time = datetime.datetime(v[0], v[1], v[2], 0, 0, 0)  # 时间段的开始时间
            end_time = datetime.datetime(v[3], v[4], v[5], 23, 59, 59)  # 时间段的结束时间
            result = dealdata(result, dict_station, filepath, vehtype, start_time, end_time, v[6], v[7])
        re.append(result)
    savepath = 'F://18120900//桌面//附表1 货车行驶记录表.xlsx'
    write2csv(re, savepath)
