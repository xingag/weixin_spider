#!/usr/bin/env python  
# encoding: utf-8  

""" 
@version: v1.0 
@author: xag 
@license: Apache Licence  
@contact: xinganguo@gmail.com 
@site: http://www.xingag.top 
@software: PyCharm 
@file: wx_spider.py 
@time: 12/14/18 21:40 
@description：爬取全部的文章并写入到 MongoDB 数据库中
"""

import requests
import re
import html
import json
import logging
import time
from datetime import datetime

from models import Post
from tools import sub_dict


class WeiXinSpider(object):
    def __init__(self):

        # 注意：微信安全性导致url_more、Cookie经常失效，需要重新请求更换
        self.headers = {
            'Host': 'mp.weixin.qq.com',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16B92 MicroMessenger/6.7.4(0x1607042c) NetType/WIFI Language/zh_CN',
            'Accept-Language': 'zh-cn',
            'X-Requested-With': 'XMLHttpRequest',
            'Cookie': 'devicetype=iOS12.1.2; lang=zh_CN; pass_ticket=KlcW/tVyaNTxBr3kYaB0QC5zLbhDzo0nhEGF2JPrpjPwpJi4TGz+XvxWoGhMPYqP; version=17000028; wap_sid2=CMOw8aYBEnBfM0UxZGdabGszY0lhZ0tCZlNhUmtNa0dYazd6dDJWeXFHZmZJczRJc2tIMUZZUXBJS3RVS1lIVXdTbmlkUkRpLVRZeDVlUjJ2Tk95U29acWRGRXVmcG14Y05NamtBU0VHb0hZMmZudGtzX2RBd0FBMLGQl+EFOA1AlU4=; wxuin=349984835; wxtokenkey=777; rewardsn=; pgv_pvid=2237276040; pac_uid=0_f82bd5abff9aa; tvfe_boss_uuid=05faefd1e90836f4',
            'Accept': '*/*',
            'Referer': 'https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MzIxNzYxMTU0OQ==&scene=126&bizpsid=0&sessionid=1545979942&subscene=0&devicetype=iOS12.1.2&version=17000028&lang=zh_CN&nettype=WIFI&a8scene=0&fontScale=100&pass_ticket=KlcW%2FtVyaNTxBr3kYaB0QC5zLbhDzo0nhEGF2JPrpjPwpJi4TGz%2BXvxWoGhMPYqP&wx_header=1'
        }

        # 更多文章 URL
        # # 请将appmsg_token和pass_ticket替换成你自己的
        self.url_more = 'https://mp.weixin.qq.com/mp/profile_ext?action=getmsg&__biz=MzIxNzYxMTU0OQ==&f=json&offset={}&count=10&is_ok=1&scene=126&uin=777&key=777&pass_ticket=KlcW%2FtVyaNTxBr3kYaB0QC5zLbhDzo0nhEGF2JPrpjPwpJi4TGz%2BXvxWoGhMPYqP&wxtoken=&appmsg_token=989_OeyBFD%252FX7XluAq0e-7Y_WOs1crl4AXsor39LGA~~&x5=0&f=json'

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def spider_more(self, offset):
        """
        爬取更多数据
        offset：消息索引
        :return:
        """
        current_request_url = self.url_more.format(offset)
        self.logger.info('当前请求的地址是:%s' % (current_request_url))

        response = requests.get(current_request_url, headers=self.headers, verify=False)
        result = response.json()

        if result.get("ret") == 0:
            msg_list = result.get('general_msg_list')

            # 保存数据
            self._save(msg_list)
            self.logger.info("获取到一页数据成功, data=%s" % (msg_list))

            # 获取下一页数据
            has_next_page = result.get('can_msg_continue')
            if has_next_page == 1:
                # 继续爬取写一页的数据【通过next_offset】
                next_offset = result.get('next_offset')

                # 休眠2秒，继续爬下一页
                time.sleep(2)
                self.spider_more(next_offset)
            else:  # 当 has_next 为 0 时，说明已经到了最后一页，这时才算爬完了一个公众号的所有历史文章
                print('爬取公号完成！')
        else:
            self.logger.info('无法获取到更多内容，请更新cookie或其他请求头信息')

    def _save(self, msg_list):
        """
        数据解析
        :param msg_list:
        :return:
        """
        # 1.去掉多余的斜线,使【链接地址】可用
        msg_list = msg_list.replace("\/", "/")
        data = json.loads(msg_list)

        # 2.获取列表数据
        msg_list = data.get("list")
        for msg in msg_list:
            # 3.发布时间
            p_date = msg.get('comm_msg_info').get('datetime')

            # 注意：非图文消息没有此字段
            msg_info = msg.get("app_msg_ext_info")

            if msg_info:  # 图文消息
                # 如果是多图文推送，把第二条第三条也保存
                multi_msg_info = msg_info.get("multi_app_msg_item_list")

                # 如果是多图文，就从multi_msg_info中获取数据插入；反之直接从app_msg_ext_info中插入
                if multi_msg_info:
                    for multi_msg_item in multi_msg_info:
                        self._insert(multi_msg_item, p_date)
                else:
                    self._insert(msg_info, p_date)
            else:
                # 非图文消息
                # 转换为字符串再打印出来
                self.logger.warning(u"此消息不是图文推送，data=%s" % json.dumps(msg.get("comm_msg_info")))

    def _insert(self, msg_info, p_date):
        """
        数据插入到 MongoDB 数据库中
        :param msg_info:
        :param p_date:
        :return:
        """
        keys = ['title', 'author', 'content_url', 'digest', 'cover', 'source_url']

        # 获取有用的数据,构建数据模型
        data = sub_dict(msg_info, keys)
        post = Post(**data)

        # 时间格式化
        date_pretty = datetime.fromtimestamp(p_date)
        post["p_date"] = date_pretty

        self.logger.info('save data %s ' % post.title)

        # 保存数据
        try:
            post.save()
        except Exception as e:
            self.logger.error("保存失败 data=%s" % post.to_json(), exc_info=True)

    # ==============================================================================================


if __name__ == '__main__':
    spider = WeiXinSpider()
    # 从首页开始爬取
    spider.spider_more(0)
    print('恭喜，爬取数据完成！')
