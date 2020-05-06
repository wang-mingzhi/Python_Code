# -*- coding: utf-8 -*-
"""
Created on Sat Mar  7 10:37:29 2020
project name:get crossRoadName's longitude and laititude from 高德地图
@author: 18120900
"""

import requests
import json
import time


def getCommentsFromDouban(crossRoadName, result, error):
    try:
        headers = {
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0;Win64;64) AppleWebKit/537.36(KHTML,like Gecko) Chrome/78.03904.108 '
            'Safari/537.36 '
        }
        url_1 = 'https://restapi.amap.com/v3/geocode/geo?address='
        url_2 = '&batch=true&city=北京&output=json&key=eff48ee434d763609e59839fa946b9e1'
        url = url_1 + '|'.join(crossRoadName) + url_2
        r_text = requests.get(url, headers=headers)
        content = json.loads(r_text.content)
        status = content["status"]
        for i in range(int(content["count"])):
            if status == "1":
                adcode = content["geocodes"][i]["adcode"]
                formatted_address = content["geocodes"][i]["formatted_address"]
                location = content["geocodes"][i]["location"]
                level = content["geocodes"][i]["level"]
                result.append((crossRoadName[i], formatted_address, adcode, location, level))
            else:
                error.append(crossRoadName[i])
                print('error!')
    except TimeoutError:
        print('timeout error')


if __name__ == "__main__":

    result = []
    error = []
    temp_crossRoadName = []
    result.append(('crossRoadName', 'formatted_address', 'adcode', 'location', 'level'))
    error.append('crossRoadName')

    with open(r'F:\18120900\桌面\123.txt', 'r', encoding='utf-8') as f:
        crossRoad = f.readlines()
    print(len(crossRoad) / 10)

    for i, crossRoadName in enumerate(crossRoad):
        temp_crossRoadName.append(crossRoadName.replace('\n', ''))
        if i % 10 == 9 or i == len(crossRoad) - 1:
            print(i + 1)
            getCommentsFromDouban(temp_crossRoadName, result, error)
            temp_crossRoadName.clear()
            time.sleep(10)

    print('Finished')
