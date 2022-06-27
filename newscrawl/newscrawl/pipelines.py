# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import MySQLdb
from MySQLdb.connections import Connection
from .settings import DB


class NewsPipeline:

    def __init__(self):
        # db 열기
        self.conn: Connection = MySQLdb.connect(
            host=DB['host'], user=DB['user'], password=DB['password'], database=DB['database'], port=DB['port'])

    def process_item(self, item, spider):
        self.save(dict(item))
        print("저장 완료!")
        return item

    def close_spider(self, spider):
        # db 닫기
        self.conn.close()

    def save(self, row):
        """db에 저장"""
        cursor = self.conn.cursor()
        create_query = (
            "INSERT INTO news(name, title, link, time, error)VALUES (%(name)s, %(title)s, %(link)s, %(time)s, %(error)s)")
        cursor.execute(create_query, row)
        self.conn.commit()
        cursor.close()
