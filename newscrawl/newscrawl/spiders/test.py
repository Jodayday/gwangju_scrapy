import scrapy

from scrapy.http.response.html import HtmlResponse
from newscrawl.items import NewsItem


class testSpider(scrapy.Spider):
    """
    광주의 공지사항들 크롤링 테스트

    """
    name = 'test'

    custom_settings = {
        'FEED_URI': 'result.json',
        'FEED_FORMAT': 'json',
        'FEED_EXPORT_ENCODING': 'utf-8',
        'FEED_EXPORT_INDENT': 2

    }

    def start_requests(self):
        """name, link , select1(링크),2(title),3(time)"""
        name = '광주동구청'
        url = 'https://www.donggu.kr/board.es?mid=a10101010000&bid=0001'
        s1 = 'div#listView > ul > li.title > a::attr("href")'
        s2 = 'div.tstyle_view > div.title::text'
        s3 = 'div#listView > ul > li.col03::text'
        result = [[name, url, s1, s2, s3], ]
        print(result, "결과는?")
        # 시작
        for name, url, s1, s2, s3 in result:
            yield scrapy.Request(url=url, callback=self.parse, cb_kwargs=dict(name=name, s1=s1, s2=s2, s3=s3))

    def parse(self, response: HtmlResponse, name, s1, s2, s3):
        """공지사항 파싱"""
        links = response.css(s1).getall()
        times = response.css(s3).getall()
        for link, time in zip(links, times):
            url = response.urljoin(link)
            yield scrapy.Request(url=url, callback=self.news, cb_kwargs=dict(name=name, time=time, s2=s2))

    def news(self, response: HtmlResponse, name, time, s2):
        """파싱 완료 후 파이프로 전달 """
        item = NewsItem()
        item['name'] = name  # db에서 가져올것
        item['title'] = response.css(s2).get().strip()
        item['link'] = response.url
        item['time'] = time
        item['error'] = False

        yield item
