# 使用 scrapy + selenium 爬取微信公众号

### 准备

```
scrapy startproject WinXinProj

cd WinXinProj/

scrapy genspider weixin weixin.sogou.com
```



### 编写爬虫

以爬取【Python】相关的微信公众主

1. 分页爬取所有 Python 相关的公众号
2. 然后爬取每一个公众号下所有的文章列表
3. 通过每一个文章的链接去爬取每一篇文章的内容



### 编写下载中间件

由于 Ajax/JS 数据特殊的加载形式

重写下载中间件，拦击默认的中间件，利用 selenium 请求，返回一个自定义的 Response 对象

注意：如果是公众号列表，使用默认的下载器；如果是文章列表和文章详情页面，就使用 selenium 去获取数据



### 写入文件中

写入到 CSV 文件中



### 注意

1. 由于公众号列表和文章列表属于两个不同域名，因此必须都加入到容许列表中

   ```
   allowed_domains = ['weixin.sogou.com', "mp.weixin.qq.com"]
   ```

2. 由于文章列表和文章详情的部分数据都是 AJAX 的形式获取的数据，因此这里使用 selenium 去发送请求，拦截默认的下载器，使用自定义的下载器中间件