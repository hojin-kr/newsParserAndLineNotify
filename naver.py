import requests
import os
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import gspread
import json
from datetime import datetime

# -----------------------------라인 Notify---------------------------------------#
# lineNotify 라인 Notify에 보낼 형태로 만들어서 전송
def lineNotify(message):
    # 라인 Nofify 토큰 조회
    lineNotifyHeaders = {
        "Authorization": "Bearer " + os.getenv("TOKEN_LINE_NOTIFY")
        }
    lineNotifyDatas = {
        "message" : message
    }
    requests.post(url="https://notify-api.line.me/api/notify", headers=lineNotifyHeaders, data=lineNotifyDatas)

# -----------------------------구글 스프레드 시트---------------------------------------#
SPREADSHEET_ID = os.getenv("TOKEN_GOOGLE_SHEET", "")
GOOGLE_APPLICATION_CREDENTIALS=os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")

# InitHeader 시트의 헤더 세팅
def InitHeader(worksheet):
    print("InitHeader")
    worksheet.batch_update([{
        'range': 'A1:C1',
        'values': [
            ["검색어", "제목", "url", "날짜"]
        ]
    }])

# checkDuplicate 중복검사 후 기존 데이터 앞에 삽입
def checkDuplicate(prev, now):
    # 중복검사 후 기존 데이터 앞에 삽입
    if len(prev) > 0:
        for data in now:
            # url이 같은지 확인
            isDuplicate = 0
            for value in prev:
                if value[2] == data[2]:
                    isDuplicate = 1
                    break
            if isDuplicate == 0:
                prev.insert(0, data)
    else :
        prev = now
    return prev

# 1. 시트가 있는지 확인
#     1-1. 시트가 없다면 생성
# 2. 시트의 내용을 확인
#   2-2. 중복 뉴스 확인
# 3. 새로운 뉴스 데이터를 추가
# 시트 확인해서 추가하는 작업 수행
def GoogleSpreadSheet(keyword, dataFrame):
    # sheet
    # gc = gspread.service_account(GOOGLE_APPLICATION_CREDENTIALS)
    gc = gspread.service_account_from_dict(json.loads(GOOGLE_APPLICATION_CREDENTIALS))
    sht = gc.open_by_key(SPREADSHEET_ID)
    try:
        # 작업할 시트 조회
        worksheet = sht.worksheet(keyword)
    except:
        # 시트가 없으면 생성
        print("Craete Sheet {keyword}")
        worksheet = sht.add_worksheet(title=keyword, rows="100", cols="20")
        InitHeader(worksheet)
    values = worksheet.get_all_values()
    # 시트의 데이터와 중복이 있는지 검사
    dataFrameUnique = checkDuplicate(values[1:999], dataFrame)
    # 삽입할게 1개 이상인 경우
    if len(dataFrameUnique) - len(values[1:999]) > 0:
        # 최대 1000개까지로 기사 개수 제한
        dataFrameUnique = dataFrameUnique[0:999]
        worksheet.batch_update([{
            'range': 'A2:D1000',
            'values': dataFrameUnique,
        }])
        # 신규 기사 발생시 라인 노티
        # lineNotify("[" + keyword +  "]\n" + dataFrame[0][1] + "\n" +  dataFrame[0][2])

# worker
def worker(keywords, sortType, count):
    today = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    # 입력한 키워드 만큼 반복
    for keyword in keywords:
        # 네이버에 검색
        r = requests.get(f'https://search.naver.com/search.naver?where=news&query={keyword}&sort={sortType}')
        soup = BeautifulSoup(r.text, 'html.parser')
        # 기사 목록을 원하는 기사 수 만큼 조회
        articles = soup.select('ul.list_news > li')
        _count = count
        dataFrame = []
        for index, article in enumerate(articles):
            if _count > 0:
                if articles[index].select_one('a.news_tit') is not None:
                    # 각 요소를 선택
                    title = articles[index].select_one('a.news_tit')['title']
                    url = articles[index].select_one('a.news_tit')['href']
                    dataFrame.append([keyword, title, url, today])
                    # 원하는 개수 만큼 기사를 가져왔는지 확인
                    _count = _count - 1
        # 구글 스프레드 시트에 최신 뉴스 추가
        GoogleSpreadSheet(keyword, dataFrame)


# -----------------------------검색 설정---------------------------------------#

# 검색 단어들 ","로 구분된 문자열로 지정
keywords = os.getenv("KEYWORDS", "IBM,AWS,IDG").split(',')
# 검색 우선 순위 설정
# relation 0
# leatest 1
# older 2
sortType = os.getenv("SORT_TYPE", 0)
# 검색당 가져올 기사 수 (최대 10개)
count = int(os.getenv("COUNT", 10))

# worker for googlesheet
worker(keywords, sortType, count)