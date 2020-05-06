# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 08:48:04 2020

@author: 18120900
"""


def countchar(str):
    """
    统计字符串中的字符个数。
    """
    dict_statistic = {}
    for i in range(97, 123):
        dict_statistic[i] = 0
    for char in str:
        if ord(char) in dict_statistic.keys():
            dict_statistic[ord(char)] += 1
    a = list(dict_statistic.values())
    return a


if __name__ == '__main__':
    string = input()
    string = string.lower()
    print(countchar(string))


def pandigital(nums):
    """
    寻找输入数字中的全数字（pandigital）
    """
    list = []
    for num in nums:
        max_num = 0
        for index, number in enumerate(str(num)):
            max_num = int(number) if int(number) >= max_num else max_num
        d = [item for item in str(num)]
        if len(str(num)) == max_num and len(set(d)) == max_num:
            list.append(num)
    return list


def output(lst):
    if len(lst) == 0:
        print('not found')
    else:
        for item in lst:
            print(item)


if __name__ == '__main__':
    lst = pandigital(eval(input()))
    output(lst)


def find_person(dict_users, strU):
    if strU in dict_users.keys():
        return dict_users[strU]
    else:
        return 'Not Found'


if __name__ == "__main__":
    name = ['xiaoyun', 'xiaohong', 'xiaoteng', 'xiaoyi', 'xiaoyang']
    qq = [88888, 5555555, 11111, 12341234, 1212121]
    dict_users = dict(zip(name, qq))
    strU = input()
    print(find_person(dict_users, strU))
