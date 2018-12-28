#!/usr/bin/env python  
# encoding: utf-8  

""" 
@version: v1.0 
@author: xag 
@license: Apache Licence  
@contact: xinganguo@gmail.com 
@site: http://www.xingag.top 
@software: PyCharm 
@file: tools.py 
@time: 12/15/18 23:23 
@description：工具类
"""

import html
from urllib.parse import urlsplit


def sub_dict(data, keys):
    """
    取字典中有用的数据出来
    获取字典的子字典可以用字典推导式实现
    :param data:字典
    :param keys:键值列表
    :return:有用的键值组成的字典
    """
    return {k: html.unescape(data[k]) for k in data if k in keys}


def str_to_dict(s, join_symbol="\n", split_symbol=":"):
    """
    把参数字符串转换为一个字典
    例如： a=b&c=d   join_symbol是&, split_symbol是=
    :param s: 原字符串
    :param join_symbol: 连接符
    :param split_symbol: 分隔符
    :return: 字典
    """
    # 通过join_symbol把字符串分为一个列表
    s_list = s.split(join_symbol)

    # 定义一个新的字典
    data = dict()

    for item in s_list:
        item = item.strip()
        if item:
            # a = b 分成一个元组，第二个参数：分割次数
            k, v = item.split(split_symbol, 1)

            # 去除空格
            data[k.strip()] = v.strip()
    return data


def dic_to_str(source_dict):
    """
    字典拆出来，通过&和=连接起来；和上面的str_to_dict函数是逆操作
    :param source_dict: {"a":1,"b":2}
    :return: a=1&b=2
    """
    dict_item = []
    for key, value in source_dict.items():
        dict_item.append("%s=%s" % (key, str(value)))
    return "&".join(dict_item)




def compound_dict(dict1, dict2):
    """
    合并两个Dict
    :param dict1:
    :param dict2:
    :return:
    """
    dict1.update(dict2)
    return dict1


def update_url_query_params(url, query_update_data):
    # 把url分割：返回一个包含5个字符串项目的元组：协议、位置、路径、查询、片段
    parse_result = urlsplit(url)
    scheme = parse_result.scheme
    netloc = parse_result.netloc
    path = parse_result.path
    query = parse_result.query
    fragment = parse_result.fragment
    # print('scheme:%s,netloc:%s,path:%s,query:%s,fragment:%s' % (scheme, netloc, path, query, fragment))

    # query内容转换为dict
    query_dict = str_to_dict(query, "&", "=")

    # 更新query内容
    if query_update_data:
        query_dict.update(query_update_data)

    # 再把query内容由dict类型转换为str类型
    # 字典和字符串相互转换
    # myDict = eval(myStr)
    # myStr = str(myDict)
    # query_dict_result = str(query_dict)

    # 把字典转换为普通的连接方式
    query_dict_result = dic_to_str(query_dict)

    # 重新组装成一个字符串
    url_result = "%s://%s" % (scheme, ''.join([netloc, path, query_dict_result, fragment]))

    print(url_result)


# 测试
# d = {"a": "1", "b": "2", "c": "3"}
# print(sub_dict(d, ("a", "b")))
# print(sub_dict(d, ["a", "b"]))

# url_more = 'https://mp.weixin.qq.com/mp/profile_ext?action=getmsg&__biz=MzIxNzYxMTU0OQ==&f=json&offset={}&count=10&is_ok=1&scene=126&uin=777&key=777&pass_ticket=9hPJTQdf%2Bb2ggjH2MqJn9y481xiwLT4d1q2SFGi4BEuzA7Bbw4rSn2Hya1%2BLOexv&wxtoken=&appmsg_token=988_JDEZ3T3UkeiLmP4Gq6tztDPOHNaDfZPb5IDHDg~~&x5=0&f=json'
# update_dict = {'__biz':'xag_biz','pass_ticket':'xag_pass_ticket','appmsg_token':23}
# update_url_query_params(url_more, update_dict)
