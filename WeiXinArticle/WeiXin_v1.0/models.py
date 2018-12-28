#!/usr/bin/env python  
# encoding: utf-8  

""" 
@version: v1.0 
@author: xag 
@license: Apache Licence  
@contact: xinganguo@gmail.com 
@site: http://www.xingag.top 
@software: PyCharm 
@file: models.py 
@time: 12/15/18 23:08 
@description：数据模型【使用mongoengine来简化操作】
"""

from datetime import datetime

from mongoengine import connect
from mongoengine import DateTimeField
from mongoengine import Document
from mongoengine import IntField
from mongoengine import StringField
from mongoengine import URLField

__author__ = 'xag'

# 连接mongodb
# 普通连接数据库【数据库没有设置权限，可以任意的写入数据。不需要指定用户名和密码】
# response = connect('admin', host='localhost', port=27017)

# 权限连接数据库【数据库设置了权限，这里必须指定用户名和密码】
response = connect('admin', host='localhost', port=27017,username='root', password='xag')



class Post(Document):
    """
    文章【模型】
    """
    title = StringField()  # 标题
    content_url = StringField()  # 文章链接
    source_url = StringField()  # 原文链接
    digest = StringField()  # 文章摘要
    cover = URLField(validation=None)  # 封面图
    p_date = DateTimeField()  # 推送时间
    author = StringField()  # 作者

    content = StringField()  # 文章内容

    read_num = IntField(default=0)  # 阅读量
    like_num = IntField(default=0)  # 点赞数
    comment_num = IntField(default=0)  # 评论数
    reward_num = IntField(default=0)  # 点赞数

    c_date = DateTimeField(default=datetime.now)  # 数据生成时间
    u_date = DateTimeField(default=datetime.now)  # 数据最后更新时间
