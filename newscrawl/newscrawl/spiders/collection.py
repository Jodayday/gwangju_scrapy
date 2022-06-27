import scrapy
import MySQLdb
from MySQLdb.connections import Connection
from scrapy.http.response.html import HtmlResponse
from newscrawl.items import NewsItem
from ..settings import DB


class CollectionSpider(scrapy.Spider):
    """
    광주의 공지사항들 크롤링
    db의 참조 데이터
    name, link , select1(링크),2(title),3(time)
    """
    name = 'collection'

    def start_requests(self):
        """db에서 값을 가져오고 크롤링 진행 """
        conn: Connection = MySQLdb.connect(
            host=DB['host'], user=DB['user'], password=DB['password'], database=DB['database'], port=DB['port'])
        sql = "SELECT * FROM CrawlLists "
        cur = conn.cursor()
        cur.execute(sql)
        result = cur.fetchall()
        conn.close()

        # 시작
        for _, name, url, s1, s2, s3, _ in result:
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
