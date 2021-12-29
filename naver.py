import requests
import os
from bs4 import BeautifulSoup

# -----------------------------라인 Notify---------------------------------------#
# lineNotify 라인 Notify에 보낼 형태로 만들어서 전송
def lineNotify(keyword, title, url):
    # 라인 Nofify 토큰 조회
    lineNotifyHeaders = {
        "Authorization": "Bearer " + os.getenv("TOKEN_LINE_NOTIFY")
        }
    lineNotifyDatas = {
        "message" : "[" + keyword + "]\n" + title + "\n" + url,
    }
    requests.post(url="https://notify-api.line.me/api/notify", headers=lineNotifyHeaders, data=lineNotifyDatas)


# -----------------------------검색 설정---------------------------------------#

# 검색 단어들 ","로 구분된 문자열로 지정
keywords = os.getenv("KEYWORDS", "IBM,AWS,IDG").split(',')

# 검색 우선 순위 설정
# relation 0
# leatest 1
# older 2
sortType = os.getenv("SORT_TYPE", 0)

# 검색당 가져올 기사 수 (최대 10개)
count = int(os.getenv("COUNT", 3))

# -----------------------------Script---------------------------------------#
# 입력한 키워드 만큼 반복
for keyword in keywords:
    # 네이버에 검색
    r = requests.get(f'https://search.naver.com/search.naver?where=news&query={keyword}&sort={sortType}')
    soup = BeautifulSoup(r.text, 'html.parser')
    # 기사 목록을 원하는 기사 수 만큼 조회
    articles = soup.select('ul.list_news > li')
    _count = count
    for index, article in enumerate(articles):
        if _count > 0:
            if articles[index].select_one('a.news_tit') is not None:
                # 각 요소를 선택
                title = articles[index].select_one('a.news_tit')['title']
                url = articles[index].select_one('a.news_tit')['href']
                print("[" + keyword + "]\n" + title + "\n" + url)
                lineNotify(keyword, title, url)
                # 원하는 개수 만큼 기사를 가져왔는지 확인
                _count = _count - 1