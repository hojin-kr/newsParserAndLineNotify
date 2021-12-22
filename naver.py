import requests
import os
from bs4 import BeautifulSoup

# -----------------------------Config lineNotify---------------------------------------#

lineNotifyToken = os.getenv("TOKEN_LINE_NOTIFY")
lineNotifyHeaders = {
    "Authorization": "Bearer " + lineNotifyToken
    }

# -----------------------------Config Searching---------------------------------------#

# keywords
keywords = os.getenv("KEYWORDS", "IBM,AWS,IDG").split(',')

# sortType
# relation 0
# leatest 1
# older 2
sortType = os.getenv("SORT_TYPE", 0)

# Each article max count per keyword
count = os.getenv("COUNT", 3)

# -----------------------------Script---------------------------------------#
for keyword in keywords:
    r = requests.get(f'https://search.naver.com/search.naver?where=news&query={keyword}&sort={sortType}')
    soup = BeautifulSoup(r.text, 'html.parser')
    articles = soup.select('ul.list_news > li')
    _count = count
    for index, article in enumerate(articles):
        if _count > 0:
            if articles[index].select_one('a.news_tit') is not None and articles[index].select_one('a.news_tit') is not None:
                title = articles[index].select_one('a.news_tit')['title']
                url = articles[index].select_one('a.news_tit')['href']
                print("[" + keyword + "]\n" + title + "\n" + url)
                lineNotifyDatas = {
                    "message" : "[" + keyword + "]\n" + title + "\n" + url,
                }
                requests.post(url="https://notify-api.line.me/api/notify", headers=lineNotifyHeaders, data=lineNotifyDatas)
                # counting article
                _count = _count - 1

