# -*- coding: utf-8 -*-
import scrapy
import time
import re

from WeiXinProj.items import WeixinprojItem


class WeixinSpider(scrapy.Spider):
    name = 'weixin'
    allowed_domains = ['weixin.sogou.com', "mp.weixin.qq.com"]
    start_urls = ['https://weixin.sogou.com/weixin?type=1&query=python&ie=utf8&s_from=input&_sug_=y&_sug_type_=']

    def parse(self, response):

        # 第一页的公众号
        a_list = response.xpath('//p[@class="tit"]/a/@href').getall()

        # 遍历每一个公众号
        for a_item in a_list:
            # 继续爬取每一个公众主的内容
            yield scrapy.Request(a_item, callback=self.parse_article_list)
            time.sleep(2)


        # 爬下一页的数据
        next_btn = response.xpath('//a[@id="sogou_next"]')
        if next_btn:
            next_url = response.urljoin(next_btn.xpath('./@href').get())
            time.sleep(2)
            print('先休息2秒，再爬取下一页的数据，url:%s' % next_url)
            yield scrapy.Request(next_url, callback=self.parse)
            pass
        else:
            print('已经爬完前10页所有的公众号')

    def parse_article_list(self, response):
        """
        爬取文章列表
        :param response:
        :return:
        """

        # 公众号作者
        author = response.xpath('//strong[@class="profile_nickname"]/text()').get().strip()

        articles = response.xpath('//h4[@class="weui_media_title"]')

        # 文章列表
        for article in articles:

            # 标题
            title_pre = '-'.join(article.xpath('.//text()').getall())
            title = re.sub('\s', '', title_pre)

            if title.startswith('-'):
                title = title[1:]

            if title.endswith('-'):
                title = title[:-2]

            # 文章详情url
            article_url_pre = article.xpath('./@hrefs').get()

            # 拼接url【下面 2 种方式都可以】
            article_url = 'https://mp.weixin.qq.com' + article_u

            yield scrapy.Request(article_url, callback=self.parse_article_detail,
                                 meta={"article": (author, title)})

    def parse_article_detail(self, response):
        """
        文章详情
        :param response:
        :return:
        """
        author, title = response.meta.get('article')

        # 文章内容
        content_pre = "".join(response.xpath('//div[@class="rich_media_content "]//text()').getall())

        content = "".join(content_pre.split())

        print('==' * 30)
        print(content)
        print('==' * 30)

        item = WeixinprojItem(author=author, title=title, content=content)

        yield item
