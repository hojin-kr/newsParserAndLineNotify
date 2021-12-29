import requests
import os
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

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

# -----------------------------구글 스프레드 시트---------------------------------------#
SPREADSHEET_ID = os.getenv("TOKEN_GOOGLE_SHEET", "")
GOOGLE_APPLICATION_CREDENTIALS=os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")

# 시트 확인해서 추가하는 작업 수행
def GoogleSpreadSheet(keyword, title, url):
    RANGE = '{keyword}!A1:E'
    creds = None
    creds = Credentials.from_service_account_file(GOOGLE_APPLICATION_CREDENTIALS)
    service = build('sheets', 'v4', credentials=creds)
    # sheet
    sheet = service.spreadsheets()
    # 1. 시트가 있는지 확인
    #     1-1. 시트가 없다면 생성
    # 2. 시트의 내용을 확인
    #   2-1. row수 확인
    #   2-2. 중복 뉴스 확인
    # 3. 새로운 뉴스 데이터를 추가

# 시트가 없다면 생성
def craeteSheet(sheet):
    # Call the Sheets API
    batch_update_spreadsheet_request_body = {
    # A list of updates to apply to the spreadsheet.
    # Requests will be applied in the order they are specified.
    # If any request is not valid, no requests will be applied.
    'requests' : [
        {
            'addSheet':
                {
                    'properties':
                    {
                        "sheetId": 1,
                        "title": "TEST",
                        "index": 0,
                        "sheetType": 0,
                    }
                }
        }
        ]
    }
    request = sheet.batchUpdate(spreadsheetId=SPREADSHEET_ID, body=batch_update_spreadsheet_request_body)
    response = request.execute()
    print(response)


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
                # TODO 구글 스프레드 시트에 최신 뉴스 추가
                # GoogleSpreadSheet(keyword, title, url)
                # 원하는 개수 만큼 기사를 가져왔는지 확인
                _count = _count - 1