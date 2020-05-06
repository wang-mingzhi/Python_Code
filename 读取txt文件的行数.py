# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 16:32:06 2020
project name: count txt files lines
@author: 18120900
"""

import datetime
import os


def countLines(fname):
    try:
        with open(fname, 'r', encoding='gb18030', errors='ignore') as f:
            data = f.readlines()
    except FileNotFoundError:
        print(fname + ' does not exists!')
    lens = len(data)
    fnames = fname.split('\\')
    print(fnames[len(fnames) - 1] + ' has ' + str(lens) + ' lines; readTime: ',
          end=' ')


if __name__ == '__main__':
    # 在此处修改目录即可
    path = r"F:\18120900\桌面\高速公路\黑龙江资料\基础数据\2018黑龙江高速公路刷卡数据\货车原始数据"
    for fname in os.listdir(path):
        if fname.endswith('.txt'):
            starTime = datetime.datetime.now()
            file_path = os.path.join(path, fname)
            countLines(file_path)
            endTime = datetime.datetime.now()
            print(endTime - starTime)
