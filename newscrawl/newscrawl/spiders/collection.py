import scrapy
import MySQLdb
from datetime import timedelta, datetime
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

    custom_settings = {
        'ITEM_PIPELINES': {
            'newscrawl.pipelines.NewsPipeline': 300,
        }
    }

    def start_requests(self):
        """db에서 값을 가져오고 크롤링 진행 """
        conn: Connection = MySQLdb.connect(
            host=DB['host'], user=DB['user'], password=DB['password'], database=DB['database'], port=DB['port'])
        sql = "SELECT * FROM CrawlLists "
        cur = conn.cursor()
        cur.execute(sql)
        result = cur.fetchall()
        conn.close()
        # 6시간 이후에 진행
        def day_filter(x): return True if datetime.now() > x - \
            timedelta(hours=-6) else False

        def day_add(tupe): return tupe[0]+(tupe[1],)

        checks = list(map(day_filter, [x[6] for x in result]))
        result = list(map(day_add, [x for x in zip(result, checks)]))

        # 시작 6시간에 한번씩 할수있도록
        for i, name, url, s1, s2, s3, _, check in result:
            if check:
                conn: Connection = MySQLdb.connect(
                    host=DB['host'], user=DB['user'], password=DB['password'], database=DB['database'], port=DB['port'])
                sql = f"UPDATE CrawlLists SET time='{datetime.now()}' WHERE id={i} "
                cur = conn.cursor()
                cur.execute(sql)
                conn.commit()
                conn.close()

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
