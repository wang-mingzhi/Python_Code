# -*- coding: utf-8 -*-
"""
Created on Sat Mar  7 10:40:59 2020
project name:读取高德地图里面的收费站数据
project name:把高德地图坐标系下的经纬度转为WGS84坐标系下的经纬度
@author: 18120900
"""
# %%
import requests
import json
import pandas as pd
import math
from xlutils.copy import copy
import xlrd
# %%
url = 'https://restapi.amap.com/v3/place/text'
params = {
    'keywords': '收费站',
    'city': 'ningxia',
    'page': '1',
    'key': 'eff48ee434d763609e59839fa946b9e1'
}
res = requests.get(url, params)
jd = json.loads(res.text)
info = jd['pois'][0]['address']
pagecount = int(jd['count']) // 20 + 1

list = []
for i in range(pagecount):
    try:
        params = {
            'keywords': '收费站',
            'city': 'ningxia',
            'page': i + 1,
            'key': 'eff48ee434d763609e59839fa946b9e1'
        }
        res = requests.get(url, params)
        jd = json.loads(res.text)
        for k in range(20):
            name = jd['pois'][k]['name']
            typ = jd['pois'][k]['type']
            typecode = jd['pois'][k]['typecode']
            address = jd['pois'][k]['address']
            location = jd['pois'][k]['location']
            pname = jd['pois'][k]['pname']
            cityname = jd['pois'][k]['cityname']
            adname = jd['pois'][k]['adname']
            list.append([
                name, typ, typecode, address, location, pname, cityname, adname
            ])
    except TimeoutError:
        continue

name = [
    'name', 'typ', 'typecode', 'address', 'location', 'pname', 'cityname',
    'adname'
]
test = pd.DataFrame(columns=name, data=list)
test.to_csv('d:\\ningxia-toll.csv', encoding='gbk', index=False)
print('success')
# %%

# 官方API: http://lbs.amap.com/api/webservice/guide/api/convert
# 坐标体系说明：http://lbs.amap.com/faq/top/coordinate/3
# GCJ02->WGS84 Java版本：http://www.cnblogs.com/xinghuangroup/p/5787306.html
# 验证坐标转换正确性的地址：http://www.gpsspg.com/maps.htm
# 以下内容为原创，转载请注明出处。

workbook = xlrd.open_workbook(r"F:\18120900\桌面\工作簿1.xlsx")
sheet = workbook.sheet_by_index(0)

# 这里需要做相应的修改
locations = sheet.col_values(6)


def GCJ2WGS(location):
    # location格式如下：locations[1] = "113.923745,22.530824"
    lon = float(location[0:location.find(",")])
    lat = float(location[location.find(",") + 1:len(location)])
    a = 6378245.0  # 克拉索夫斯基椭球参数长半轴a
    ee = 0.00669342162296594323  # 克拉索夫斯基椭球参数第一偏心率平方
    PI = 3.14159265358979324  # 圆周率
    # 以下为转换公式
    x = lon - 105.0
    y = lat - 35.0
    # 经度
    dLon = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(
        abs(x))
    dLon += (20.0 * math.sin(6.0 * x * PI) +
             20.0 * math.sin(2.0 * x * PI)) * 2.0 / 3.0
    dLon += (20.0 * math.sin(x * PI) +
             40.0 * math.sin(x / 3.0 * PI)) * 2.0 / 3.0
    dLon += (150.0 * math.sin(x / 12.0 * PI) +
             300.0 * math.sin(x / 30.0 * PI)) * 2.0 / 3.0
    # 纬度
    dLat = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(
        abs(x))
    dLat += (20.0 * math.sin(6.0 * x * PI) +
             20.0 * math.sin(2.0 * x * PI)) * 2.0 / 3.0
    dLat += (20.0 * math.sin(y * PI) +
             40.0 * math.sin(y / 3.0 * PI)) * 2.0 / 3.0
    dLat += (160.0 * math.sin(y / 12.0 * PI) +
             320 * math.sin(y * PI / 30.0)) * 2.0 / 3.0
    radLat = lat / 180.0 * PI
    magic = math.sin(radLat)
    magic = 1 - ee * magic * magic
    sqrtMagic = math.sqrt(magic)
    dLat = (dLat * 180.0) / ((a * (1 - ee)) / (magic * sqrtMagic) * PI)
    dLon = (dLon * 180.0) / (a / sqrtMagic * math.cos(radLat) * PI)
    wgsLon = lon - dLon
    wgsLat = lat - dLat
    return wgsLon, wgsLat


wgsWorkbook = copy(
    workbook)  # CMD下：pip install xlutils，该库可以通过复制一个工作簿实现对已有内容的excel文件的写入。
wgsSheet = wgsWorkbook.get_sheet(
    0)  # 接上。方式为：复制原工作簿，获取工作表，在新表下写入，保存时名称可以与源文件一致。
wgsSheet.write(0, sheet.ncols, "wgsLocation")

for i in range(1, sheet.nrows):
    wgsSheet.write(i, sheet.ncols,
                   str(GCJ2WGS(locations[i])).replace("(", "").replace(
                       ")", ""))  # 在新的一列写入转换后的坐标
wgsWorkbook.save(r"F:\18120900\桌面\交叉口经纬度信息_1.csv")
print("Done!")
