import MySQLdb
from datetime import timedelta, datetime

from MySQLdb.connections import Connection
from pathlib import Path
import json
KEY_DIR = Path(__file__).resolve().parent
KEY_PATH = Path.joinpath(KEY_DIR, 'dbkey.json')
KEY_DICT = json.loads(open(KEY_PATH, 'r').read())
DB = KEY_DICT['DB']


conn: Connection = MySQLdb.connect(
    host=DB['host'], user=DB['user'], password=DB['password'], database=DB['database'], port=DB['port'])
sql = "SELECT * FROM CrawlLists "
cur = conn.cursor()
cur.execute(sql)
result = cur.fetchall()

print(result)


def day_filter(x):
    return True if datetime.now() > x - timedelta(hours=-6) else False


def day_add(tupe): return tupe[0]+(tupe[1],)


check = list(map(day_filter, [x[6] for x in result]))
result = list(map(day_add, [x for x in zip(result, check)]))

v = list(map(day_filter, [x[6] for x in result]))
for ur1, url2 in zip(result, v):
    print(ur1)


conn.close()
