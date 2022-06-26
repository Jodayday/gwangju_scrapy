import scrapy
from scrapy.http.response.html import HtmlResponse

from newscrawl.items import NewsItem


class CollectionSpider(scrapy.Spider):
    """
    광주의 공지사항들 크롤링
    db의 참조 데이터
    name, link , select1(링크),2(title),3(time)
    """
    name = 'collection'

    def start_requests(self):
        """db에서 값을 가져오고 크롤링 진행 """
        names = ['광주시청']
        start_urls = [
            'https://www.gwangju.go.kr/boardList.do?boardId=BD_0000000022&pageId=www788']
        select1s = [
            'div.board_list_body > div.body_row > div.subject > a::attr("href")']
        select2s = ['h6::text']
        select3s = ['div.board_list_body > div.body_row > div.date::text ']

        # 시작
        for name, url, s1, s2, s3 in zip(names, start_urls, select1s, select2s, select3s):
            yield scrapy.Request(url=url, callback=self.parse, cb_kwargs=dict(name=name, s1=s1, s2=s2, s3=s3))

    def parse(self, response: HtmlResponse, name, s1, s2, s3):
        """공지사항 파싱"""
        print("값 테스트", name, s1, s2, s3)

        links = response.css(s1).getall()
        times = response.css(s3).getall()
        print("크롤링 된값", links, times)
    #     for link, time in zip(links, times):
    #         url = response.urljoin(link)
    #         yield scrapy.Request(url=url, callback=self.news, cb_kwargs=dict(time=time,s2=s2))

    # def news(self, response: HtmlResponse, time,s2):
    #     """파싱 완료 후 파이프로 전달 """
    #     item = NewsItem()
    #     item['name'] = '광주시청'  # db에서 가져올것
    #     item['title'] = response.css().get(s2).strip()
    #     item['link'] = response.url
    #     item['time'] = time

    #     yield item
