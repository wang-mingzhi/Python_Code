# -*- coding: utf-8 -*-
"""
-*- coding: utf-8 -*-
Spyder Editor

This is a temporary script file.
"""
# Created on Tue Feb  4 10:27:51 2020
# project name:2019-nCoV
# @author: 帅帅de三叔
# %%
# 导入请求模块
import json
import csv
import requests


def str2json(str, code):
    return str.replace('\\', '').replace('(', '').replace(')', '')\
        .replace(code, '').replace('"{', '{').replace('}"', '}')


def get_json(url, code):
    response = str(requests.get(url).content, 'utf-8')
    res = str2json(response, code)
    data = json.loads(res)  # 提取数据部分
    return data


def get_china_data(data):
    update_time = data["data"]["lastUpdateTime"]
    areaTree = data["data"]["areaTree"]  # 各地方数据

    filepath = "中国各城市病例数据-new.csv"
    with open(filepath, "w+", newline="", encoding='utf_8_sig') as csv_file:
        writer = csv.writer(csv_file)
        header = [
            "province", "city_name", "today_confirm", "today_confirmCuts",
            "total_confirm", "total_dead", "total_heal", "total_nowConfirm",
            "total_suspect", "update_time"
        ]
        writer.writerow(header)

        china_data = areaTree[0]["children"]  # 中国数据
        for j in range(len(china_data)):
            province = china_data[j]["name"]  # 省份
            city_list = china_data[j]["children"]  # 该省份下面城市列表
            for k in range(len(city_list)):
                city_name = city_list[k]["name"]  # 城市名称
                today_confirm = city_list[k]["today"]["confirm"]  # 今日确认病例
                today_confirmCuts = city_list[k]["today"]["confirmCuts"]
                total_confirm = city_list[k]["total"]["confirm"]  # 总确认病例
                total_dead = city_list[k]["total"]["dead"]  # 总死亡病例
                total_heal = city_list[k]["total"]["heal"]  # 总治愈病例
                total_nowConfirm = city_list[k]["total"]["nowConfirm"]
                total_suspect = city_list[k]["total"]["suspect"]  # 总疑似病例

                data_row3 = [
                    province, city_name, today_confirm, today_confirmCuts,
                    total_confirm, total_dead, total_heal, total_nowConfirm,
                    total_suspect, update_time
                ]
                writer.writerow(data_row3)


if __name__ == "__main__":
    url = "https://view.inews.qq.com/g2/getOnsInfo?{0}&{1}"

    name_china = "name=disease_h5"
    callback_china = "callback=jQuery34105039333360681013_1584838849613&_=1584838849614"
    code_china = "jQuery34105039333360681013_1584838849613"
    url_china = url.format(name_china, callback_china)
    get_china_data(get_json(url_china, code_china))
    print("已完成中国数据的爬取")
