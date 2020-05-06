# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 19:22:43 2020

@author: 18120900
"""
import requests
from bs4 import BeautifulSoup
import re
from matplotlib import colors
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import jieba

color_list = [
    '#CD853F', '#DC143C', '#00FF7F', '#FF6347', '#8B008B', '#00FFFF',
    '#0000FF', '#8B0000', '#FF8C00', '#1E90FF', '#00FF00', '#FFD700',
    '#008080', '#008B8B', '#8A2BE2', '#228B22', '#FA8072', '#808080'
]


def getCommentsFromDouban(url, headers, comments):
    try:
        r_text = requests.get(url, headers=headers)
        soup = BeautifulSoup(r_text.text, 'lxml')
        pattern = soup.find_all('span', 'short')
        for item in pattern:
            comments.append(item.string)

        pattern_s = re.compile('<span class="user-stars allstar(.*?) rating"')
        p = re.findall(pattern_s, r_text.text)
        s = 0
        for star in p:
            s += int(star)
        print(s)

    except TimeoutError:
        print('Unknow error')


def simpleWC3(sep=' ', back='black', freDictpath='data_fre.json', savepath='res.png'):
    """
    词云可视化Demo【自定义字体的颜色】
    """
    # 基于自定义颜色表构建colormap对象
    colormap = colors.ListedColormap(color_list)
    try:
        with open(freDictpath) as f:
            data = f.readlines()
            data_list = [one.strip().split(sep) for one in data if one]
        fre_dict = {}
        for one_list in data_list:
            fre_dict[one_list[0]] = int(one_list[1])
    except FileNotFoundError:
        fre_dict = freDictpath
    wc = WordCloud(
        font_path='font/simhei.ttf',  # 设置字体  #simhei
        background_color=back,  # 背景颜色
        max_words=2300,  # 词云显示的最大词数
        max_font_size=120,  # 字体最大值
        colormap=colormap,  # 自定义构建colormap对象
        margin=2,
        width=3200,
        height=2400,
        random_state=42,
        prefer_horizontal=0.5)  # 无法水平放置就垂直放置
    wc.generate_from_frequencies(fre_dict)
    plt.figure()
    plt.imshow(wc)
    plt.axis("off")
    # wc.to_file(savepath)


if __name__ == "__main__":
    # 获取书评内容
    pageNum = 10
    headers = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0;Win64;64) AppleWebKit/537.36(KHTML,like Gecko) Chrome/78.03904.108 Safari/537.36'
    }
    comments = []
    for index in range(1, pageNum + 1):
        url = 'https://book.douban.com/subject/1029553/comments/hot?p=' + str(index)
        getCommentsFromDouban(url, headers, comments)

    # 生成词云
    word_list = "/".join(jieba.cut('。'.join(comments))).split('/')
    fre_dict = {}
    for one in word_list:
        if one in fre_dict:
            fre_dict[one] += 1
        else:
            fre_dict[one] = 1
    simpleWC3(sep=' ',
              back='black',
              freDictpath=fre_dict,
              savepath='simpleWC3.png')
