# 先需要點及右下角 並在搜尋欄輸入環境的路徑（venv-Scripts-python.exe）
#----------------------------------------LineSDK必要----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
from logging import Handler
from flask import Flask, request, abort

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    PushMessageRequest,
    BroadcastRequest,
    MulticastRequest,
    TemplateMessage,
    ConfirmTemplate,
    ButtonsTemplate,
    CarouselTemplate,
    CarouselColumn,
    ImageCarouselTemplate,
    ImageCarouselColumn,
    MessageAction,
    URIAction,
    PostbackAction,
    DatetimePickerAction,
    TextMessage,
    Emoji,
    VideoMessage,
    AudioMessage,
    LocationMessage,
    StickerMessage,
    ImageMessage,
    FlexBubble,
    FlexImage,
    FlexMessage,
    FlexBox,
    FlexText,
    FlexIcon,
    FlexButton,
    FlexSeparator,
    FlexContainer,
)
from linebot.v3.webhooks import (
    MessageEvent,
    FollowEvent,
    PostbackEvent,
    TextMessageContent
) 
import os
app = Flask(__name__)
configuration = Configuration(access_token=os.getenv('CHANNEL_ACCESS_TOKEN'))
line_handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body:  " + body)
    # handle webhook body
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'
#----------------------------------------LineSDK必要----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 額外必要
import json
import requests
import gspread #寫入google sheet的函數
# 換算總時程函數
def time_hrmi(time):
    hr=int(time/60)
    mi=int(time%60)
    if hr == 0:
        return f'{mi}分鐘'
    elif mi == 0:
        return f'{hr}小時'
    else:
        return f'{hr}小時{mi}分鐘' 
# 使用schedule及threading函數來每隔30秒檢查試算表的表單情況
import smtplib
from email.mime.text import MIMEText
import schedule
import time
import threading
#   因為json讀取google sheet的時間格式會錯誤，因此引入函數做矯正
import datetime
from datetime import datetime as datetime_datetime
# 解析含中文上午/下午的時間字符串為 datetime 對象
def parse_custom_time(time_str):
    # 解析含中文上午/下午的時間字符串為 datetime 對象
    parts = time_str.split()
    date_part = parts[0]
    ampm = parts[1]
    time_part = parts[2]
    # 轉換中文上午/下午為 AM/PM
    ampm_en = "AM" if ampm == "上午" else "PM"
    # 合併為可解析的字符串
    datetime_str = f"{date_part} {time_part} {ampm_en}"
    return datetime_datetime.strptime(datetime_str, "%Y/%m/%d %I:%M:%S %p")
# 獲得dict內的value
def get_key(dict, target):
    number_list = []
    for i in range(len(dict)):
        if str(target) in dict[i+1]:
            number_list.append(i+1)
        else:
            pass
    return(number_list)
# token.json的資料如放在公開伺服器上執行之類的，會遭停用，需到google cloud重新建立金鑰，否則會跳出JWP錯誤
# os函數 引用 env
import os
from dotenv import load_dotenv
load_dotenv()
# 從環境變數讀取 JSON 字串，否則env只能傳入string，且env檔須調整為單行。
credentials_str = os.getenv('GOOGLE_CREDENTIALS')
if credentials_str:
    credentials_dict = json.loads(credentials_str)
# 使用 credentials 修正後的字典開啟 Google Sheet 
gc = gspread.service_account_from_dict(credentials_dict)
carpool = gc.open_by_url('https://docs.google.com/spreadsheets/d/1q8HKO2NBz1O8UBE7ag9Kq-eNAc114TKzkXyOq32vfSA/edit?gid=1437248658#gid=1437248658')
driver_sheet_id = carpool.get_worksheet(0)
passenger_sheet_id = carpool.get_worksheet(1)
# 初始化追踪字典，為每個索引設置False
web_driver_Sure = set()
web_passenger_Sure = set()
from tenacity import retry, stop_after_attempt, retry_if_exception_type, wait_fixed, wait_exponential
def check_project():    
    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=60), retry=retry_if_exception_type(gspread.exceptions.APIError))
    def check_project_s():
        global web_driver_Sure, web_passenger_Sure
        print(f"目前已處理的司機: {web_driver_Sure}")
        print(f"目前已處理的乘客: {web_passenger_Sure}")
        for i in range(1,web_driver_len):
            driver_case_datetime = parse_custom_time(driver_sheet[i][3]).replace(minute=0, second=0, microsecond=0)
            driver_case_datetime_ahead = driver_case_datetime - datetime.timedelta(hours = 3)
            now_datetime = (datetime_datetime.now() + datetime.timedelta(hours = 8)).replace(minute=0, second=0, microsecond=0)
            if i not in web_driver_Sure and driver_sheet[i][19] == '否':
                if driver_case_datetime_ahead == now_datetime:
                    driver_limitnumber_type = ''
                    try :
                        int(driver_sheet[i][5])
                    except:
                        driver_limitnumber_type = '共乘人數上限不為數字'
                    # 未註明乘坐上限
                    if driver_limitnumber_type == '共乘人數上限不為數字':
                        # 寄信給發起人，告知結果
                        name_list = driver_Sure_name_dict.get(i).split(',')
                        output = '、'.join(map(str, name_list))
                        str1 = f'您在 共乘阿穿 發起的（司機揪團）共乘活動報名已截止，因為您未註明共乘人數上限，因此僅以此郵件做通知，也請留意是否有乘客臨時聯絡您需要共乘，共乘編號：{driver_sheet[i][17]}。活動資訊如下：'
                        str2 = f'共乘編號：{driver_sheet[i][17]}<br>發車地點：{driver_sheet[i][2]}<br>目的地：{driver_sheet[i][4]}<br>出發時間：<br>{driver_sheet[i][3]}<br>總時程：{time_hrmi(int(driver_sheet[i][6]))}<br>發起人：{driver_sheet[i][9]}<br>手機號碼：{driver_sheet[i][13]}<br>LineID：{driver_sheet[i][10]}<br>共乘人數上限：{driver_sheet[i][5]}<br>共乘費用分攤：{driver_sheet[i][11]}<br>交通工具：{driver_sheet[i][12]}<br>行車規範：<br>{driver_sheet[i][7]}<br>簡介：<br>{driver_sheet[i][8]}<br>'
                        str3 = f'參與者Line名稱:{output}'
                        str4 = '您在 共乘阿穿 發起的（司機揪團）共乘活動報名已截止'
                        # 針對 Linebot 參與的乘客
                        driver_text = f'您參與的（司機揪團）共乘活動報名截止囉，因發起人尚未註明共乘人數上限，因此僅以此郵件通知您記得聯絡發起人！發起人LineID：{driver_sheet[i][10]}，活動資訊如下：\n--------------------------------\n共乘編號：{driver_sheet[i][17]}\n發車地點：{driver_sheet[i][2]}\n目的地：{driver_sheet[i][4]}\n出發時間：\n{driver_sheet[i][3]}\n總時程：{time_hrmi(int(driver_sheet[i][6]))}\n發起人：{driver_sheet[i][9]}\n手機號碼：{driver_sheet[i][13]}\nLineID：{driver_sheet[i][10]}\n共乘人數上限：{driver_sheet[i][5]}\n共乘費用分攤：{driver_sheet[i][11]}\n交通工具：{driver_sheet[i][12]}\n行車規範：\n{driver_sheet[i][7]}\n簡介：\n{driver_sheet[i][8]}\n'
                    # 有人且已滿
                    elif int(driver_sheet[i][14])== int(driver_sheet[i][5]):
                        # 寄信給發起人，告知結果
                        name_list = driver_Sure_name_dict.get(i).split(',')
                        output = '、'.join(map(str, name_list))
                        str1 = '您在 共乘阿穿 發起的（司機揪團）共乘活動人數已滿了，活動資訊如下：'
                        str2 = f'共乘編號：{driver_sheet[i][17]}<br>發車地點：{driver_sheet[i][2]}<br>目的地：{driver_sheet[i][4]}<br>出發時間：{driver_sheet[i][3]}<br>總時程：{time_hrmi(int(driver_sheet[i][6]))}<br>發起人：{driver_sheet[i][9]}<br>手機號碼：{driver_sheet[i][13]}<br>LineID：{driver_sheet[i][10]}<br>共乘人數上限：{driver_sheet[i][5]}<br>共乘費用分攤：{driver_sheet[i][11]}<br>交通工具：{driver_sheet[i][12]}<br>行車規範：{driver_sheet[i][7]}<br>簡介：<br>{driver_sheet[i][8]}<br>'
                        str3 = f'參與者Line名稱:{output}'
                        str4 = '您在 共乘阿穿 發起的（司機揪團）共乘活動人數已滿囉'
                        # 針對 Linebot 參與的乘客
                        driver_text = f'您參加的（司機揪團）共乘活動成團囉，記得透過LineID聯繫活動發起人！發起人LineID：{driver_sheet[i][10]}，活動資訊如下：\n--------------------------------\n共乘編號：{driver_sheet[i][17]}\n發車地點：{driver_sheet[i][2]}\n目的地：{driver_sheet[i][4]}\n出發時間：\n{driver_sheet[i][3]}\n總時程：{time_hrmi(int(driver_sheet[i][6]))}\n發起人：{driver_sheet[i][9]}\n手機號碼：{driver_sheet[i][13]}\nLineID：{driver_sheet[i][10]}\n共乘人數上限：{driver_sheet[i][5]}\n共乘費用分攤：{driver_sheet[i][11]}\n交通工具：{driver_sheet[i][12]}\n行車規範：\n{driver_sheet[i][7]}\n簡介：\n{driver_sheet[i][8]}\n'
                    # 有人且發起者未勾選 ※ 人滿才發車
                    elif '※ 人滿才發車' not in driver_sheet[i][7] and int(driver_sheet[i][14])>0:
                        # 寄信給發起人，告知結果
                        name_list = driver_Sure_name_dict.get(i).split(',')
                        output = '、'.join(map(str, name_list))
                        str1 = '您在 共乘阿穿 發起的（司機揪團）共乘活動人數未滿，但您未勾選「人滿才發車」，因此成團喔，也請留意是否有乘客臨時聯絡您需要共乘！活動資訊如下：'
                        str2 = f'共乘編號：{driver_sheet[i][17]}<br>發車地點：{driver_sheet[i][2]}<br>目的地：{driver_sheet[i][4]}<br>出發時間：{driver_sheet[i][3]}<br>總時程：{time_hrmi(int(driver_sheet[i][6]))}<br>發起人：{driver_sheet[i][9]}<br>手機號碼：{driver_sheet[i][13]}<br>LineID：{driver_sheet[i][10]}<br>共乘人數上限：{driver_sheet[i][5]}<br>共乘費用分攤：{driver_sheet[i][11]}<br>交通工具：{driver_sheet[i][12]}<br>行車規範：{driver_sheet[i][7]}<br>簡介：<br>{driver_sheet[i][8]}<br>'
                        str3 = f'參與者Line名稱:{output}'
                        str4 = '您在 共乘阿穿 發起的（司機揪團）共乘活動人數未滿，但您未勾選「人滿才發車」，因此成團喔！'
                        # 針對 Linebot 參與的乘客
                        driver_text = f'您參加的（司機揪團）共乘活動成團囉，記得透過LineID聯繫活動發起人！發起人LineID：{driver_sheet[i][10]}，活動資訊如下：\n--------------------------------\n共乘編號：{driver_sheet[i][17]}\n發車地點：{driver_sheet[i][2]}\n目的地：{driver_sheet[i][4]}\n出發時間：\n{driver_sheet[i][3]}\n總時程：{time_hrmi(int(driver_sheet[i][6]))}\n發起人：{driver_sheet[i][9]}\n手機號碼：{driver_sheet[i][13]}\nLineID：{driver_sheet[i][10]}\n共乘人數上限：{driver_sheet[i][5]}\n共乘費用分攤：{driver_sheet[i][11]}\n交通工具：{driver_sheet[i][12]}\n行車規範：{driver_sheet[i][7]}\n簡介：\n{driver_sheet[i][8]}\n'
                    # 未成團
                    else:
                        # 寄信給發起人，告知結果
                        str1 = f'您在 共乘阿穿 發起的（司機揪團）共乘活動人數未滿，共乘編號為{driver_sheet[i][17]}，因此未發車，也請留意是否有乘客臨時聯絡您需要共乘。活動資訊如下：'
                        str2 = f'共乘編號：{driver_sheet[i][17]}<br>發車地點：{driver_sheet[i][2]}<br>目的地：{driver_sheet[i][4]}<br>出發時間：{driver_sheet[i][3]}<br>總時程：{time_hrmi(int(driver_sheet[i][6]))}<br>發起人：{driver_sheet[i][9]}<br>手機號碼：{driver_sheet[i][13]}<br>LineID：{driver_sheet[i][10]}<br>共乘人數上限：{driver_sheet[i][5]}<br>共乘費用分攤：{driver_sheet[i][11]}<br>交通工具：{driver_sheet[i][12]}<br>行車規範：{driver_sheet[i][7]}<br>簡介：<br>{driver_sheet[i][8]}<br>'
                        str3 = ''
                        str4 = '您在 共乘阿穿 發起的（司機揪團）共乘活動人數未滿'
                        # 針對 Linebot 參與的乘客
                        driver_text = f'您參與的（司機揪團）共乘活動因人數未滿而不發車喔！共乘編號為{driver_sheet[i][17]}'
                    # 寄信給發起人
                    name_list = driver_Sure_name_dict.get(i).split(',')
                    output = ','.join(map(str, name_list))
                    html =f'''
                    <h1 style="color:black">共乘阿穿</h1>
                    <div style="color:black">{str1}</div>
                    <div style="color:black">{str2}<div>
                    <div style="color:black">{str3}<div>
                    '''
                    mail = MIMEText(html, 'html', 'utf-8')   # plain 換成 html，就能寄送 HTML 格式的信件
                    mail['Subject']= f'{str4}'
                    mail['From']='adf'
                    mail['To']= driver_sheet[i][1]
                    try:
                        smtp = smtplib.SMTP('smtp.gmail.com', 587)
                        smtp.ehlo()
                        smtp.starttls()
                        smtp.login('ncnucarpool@gmail.com',os.getenv('GMAIL_PASSWORD'))
                        status = smtp.send_message(mail)
                        smtp.quit()
                        # 將此索引添加到已處理集合中
                        web_driver_Sure.add(i)
                        print(f"司機 {i} 已標記為處理完成")
                    except Exception as e:
                        print(f"發送郵件時出錯: {e}")    
                    # 當活動人數已滿的時候，向活動參與者發送提醒（告知可發車及聯繫發起人）
                    try:
                        driver_Sure = driver_sheet[i][15]
                        driver_Sure_list = driver_Sure.split(',')
                        for r in driver_Sure_list:
                            with ApiClient(configuration) as api_client:
                                line_bot_api = MessagingApi(api_client)
                                line_bot_api.push_message(
                                    PushMessageRequest(
                                        to=r,
                                        messages=[TextMessage(text=driver_text)]
                                    )
                                )  
                    except:
                        pass
                else:
                    pass
            else:
                pass
        for i in range(1,web_passenger_len):
            passenger_case_datetime = parse_custom_time(passenger_sheet[i][3]).replace(minute=0, second=0, microsecond=0)
            passenger_case_datetime_ahead = passenger_case_datetime - datetime.timedelta(hours = 3)
            now_datetime = (datetime_datetime.now() + datetime.timedelta(hours = 8)).replace(minute=0, second=0, microsecond=0)
            if i not in web_passenger_Sure and passenger_sheet[i][17] == '否':
                if passenger_case_datetime_ahead == now_datetime:
                    passenger_limitnumber_type = ''
                    try :
                        int(driver_sheet[i][5])
                    except:
                        passenger_limitnumber_type = '共乘人數上限不為數字'
                    # 未註明乘坐上限
                    if passenger_limitnumber_type == '共乘人數上限不為數字':
                        # 寄信給發起人，告知結果   
                        name_list = passenger_Sure_name_dict.get(i).split(',')
                        output = '、'.join(map(str, name_list)) 
                        str1 = f'您在 共乘阿穿 發起的（乘客揪團）共乘活動報名已截止，因為發起人未註明共乘人數上限，因此僅以此郵件做通知，也請留意是否有乘客臨時聯絡您需要共乘，共乘編號為{passenger_sheet[i][16]}。活動資訊如下：'
                        str2 = f'共乘編號：{passenger_sheet[i][16]}<br>發車地點：{passenger_sheet[i][2]}<br>目的地：{passenger_sheet[i][4]}<ber>出發時間：<br>{passenger_sheet[i][3]}<br>總時程：{time_hrmi(int(passenger_sheet[i][6]))}<br>發起人：{passenger_sheet[i][9]}<br>手機號碼：{passenger_sheet[i][12]}<br>LineID：{passenger_sheet[i][10]}<br>共乘人數上限：{passenger_sheet[i][5]}<br>交通工具：{passenger_sheet[i][11]}<br>行車規範：<br>{passenger_sheet[i][7]}\n簡介：{passenger_sheet[i][8]}<br>'
                        str3 = f'參與者Line名稱:{output}'
                        str4 = '您在 共乘阿穿 發起的（乘客揪團）共乘活動報名已截止'
                        # 針對 Linebot 參與的乘客
                        passenger_text = f'您參與的（乘客揪團）共乘活動報名截止囉，因發起人尚未註明共乘人數上限，因此僅以此郵件通知您記得聯絡發起人！發起人LineID：{passenger_sheet[i][10]}，活動資訊如下：\n--------------------------------\n共乘編號：{passenger_sheet[i][16]}\n發車地點：{passenger_sheet[i][2]}\n目的地：{passenger_sheet[i][4]}\n出發時間：\n{passenger_sheet[i][3]}\n總時程：{time_hrmi(int(passenger_sheet[i][6]))}\n發起人（乘客）：{passenger_sheet[i][9]}\n手機號碼：{passenger_sheet[i][12]}\nLineID：{passenger_sheet[i][10]}\n共乘人數上限：{passenger_sheet[i][5]}\n交通工具：{passenger_sheet[i][11]}\n行車規範：\n{passenger_sheet[i][7]}\n簡介：{passenger_sheet[i][8]}\n'
                    # 有人且已滿
                    elif int(passenger_sheet[i][13])== int(passenger_sheet[i][5]):
                        # 寄信給發起人，告知結果 
                        name_list = passenger_Sure_name_dict.get(i).split(',')
                        output = '、'.join(map(str, name_list))
                        str1 = '您在 共乘阿穿 發起的（乘客揪團）共乘活動人數已滿了，活動資訊如下：'
                        str2 = f'共乘編號：{passenger_sheet[i][16]}<br>發車地點：{passenger_sheet[i][2]}<br>目的地：{passenger_sheet[i][4]}<br>出發時間：{passenger_sheet[i][3]}<br>總時程：{time_hrmi(int(passenger_sheet[i][6]))}<br>發起人：{passenger_sheet[i][9]}<br>手機號碼：{passenger_sheet[i][12]}<br>LineID：{passenger_sheet[i][10]}<br>共乘人數上限：{passenger_sheet[i][5]}<br>交通工具：{passenger_sheet[i][11]}<br>行車規範：{passenger_sheet[i][7]}<br>簡介：<br>{passenger_sheet[i][8]}<br>'
                        str3 = f'參與者Line名稱:{output}'
                        str4 = '您在 共乘阿穿 發起的（乘客揪團）共乘活動人數已滿囉'
                        # 針對 Linebot 參與的乘客
                        passenger_text = f'您參加的（乘客揪團）共乘活動成團囉，記得透過LineID聯繫活動發起人！發起人LineID：{passenger_sheet[i][10]}，活動資訊如下：\n--------------------------------\n共乘編號：{passenger_sheet[i][16]}\n發車地點：{passenger_sheet[i][2]}\n目的地：{passenger_sheet[i][4]}\n出發時間：\n{passenger_sheet[i][3]}\n總時程：{time_hrmi(int(passenger_sheet[i][6]))}\n發起人：{passenger_sheet[i][9]}\n手機號碼：{passenger_sheet[i][12]}\nLineID：{passenger_sheet[i][10]}\n共乘人數上限：{passenger_sheet[i][5]}\n交通工具：{passenger_sheet[i][11]}\n行車規範：\n{passenger_sheet[i][7]}\n簡介：{passenger_sheet[i][8]}\n'
                    # 有人且發起者未勾選 ※ 人滿才發車
                    elif '※ 人滿才發車' not in passenger_sheet[i][7] and int(passenger_sheet[i][13])>0:
                        # 寄信給發起人，告知結果
                        name_list = passenger_Sure_name_dict.get(i).split(',')
                        output = '、'.join(map(str, name_list))
                        str1 = '您在 共乘阿穿 發起的（乘客揪團）共乘活動人數未滿，但您未勾選「人滿才發車」，因此成團喔，也請留意是否有乘客臨時聯絡您需要共乘！活動資訊如下：'
                        str2 = f'共乘編號：{passenger_sheet[i][16]}<br>發車地點：{passenger_sheet[i][2]}<br>目的地：{passenger_sheet[i][4]}<br>出發時間：{passenger_sheet[i][3]}<br>總時程：{time_hrmi(int(passenger_sheet[i][6]))}<br>發起人：{passenger_sheet[i][9]}<br>手機號碼：{passenger_sheet[i][12]}<br>LineID：{passenger_sheet[i][10]}<br>共乘人數上限：{passenger_sheet[i][5]}<br>交通工具：{passenger_sheet[i][11]}<br>行車規範：{passenger_sheet[i][7]}<br>簡介：<br>{passenger_sheet[i][8]}<br>'
                        str3 = f'參與者Line名稱:{output}'
                        str4 = '您在 共乘阿穿 發起的（乘客揪團）共乘活動人數未滿，但您未勾選「人滿才發車」，因此成團喔！'
                        # 針對 Linebot 參與的乘客
                        passenger_text = f'您參加的（乘客揪團）共乘活動成團囉，記得透過LineID聯繫活動發起人！發起人LineID：{passenger_sheet[i][10]}，活動資訊如下：\n--------------------------------\n共乘編號：{passenger_sheet[i][16]}\n發車地點：{passenger_sheet[i][2]}\n目的地：{passenger_sheet[i][4]}\n出發時間：\n{passenger_sheet[i][3]}\n總時程：{time_hrmi(int(passenger_sheet[i][6]))}\n發起人：{passenger_sheet[i][9]}\n手機號碼：{passenger_sheet[i][12]}\nLineID：{passenger_sheet[i][10]}\n共乘人數上限：{passenger_sheet[i][5]}\n交通工具：{passenger_sheet[i][11]}\n行車規範：\n{passenger_sheet[i][7]}\n簡介：{passenger_sheet[i][8]}\n'
                    # 未成團
                    else:
                        # 寄信給發起人，告知結果    
                        str1 = f'您在 共乘阿穿 發起的（乘客揪團）共乘活動人數未滿或是無人預定，共乘編號為{passenger_sheet[i][16]}，因此未發車，也請留意是否有乘客臨時聯絡您需要共乘。活動資訊如下：'
                        str2 = f'共乘編號：{passenger_sheet[i][16]}<br>發車地點：{passenger_sheet[i][2]}<br>目的地：{passenger_sheet[i][4]}<br>出發時間：{passenger_sheet[i][3]}<br>總時程：{time_hrmi(int(passenger_sheet[i][6]))}<br>發起人：{passenger_sheet[i][9]}<br>手機號碼：{passenger_sheet[i][12]}<br>LineID：{passenger_sheet[i][10]}<br>共乘人數上限：{passenger_sheet[i][5]}<br>交通工具：{passenger_sheet[i][11]}<br>行車規範：{passenger_sheet[i][7]}<br>簡介：<br>{passenger_sheet[i][8]}<br>'
                        str3 = ''
                        str4 = '您在 共乘阿穿 發起的（乘客揪團）共乘活動人數未滿'
                        # 針對 Linebot 參與的乘客
                        passenger_text = f'您參與的（乘客揪團）共乘活動因人數未滿而不發車喔！共乘編號為{passenger_sheet[i][16]}'
                    # 寄信給發起人
                    name_list = passenger_Sure_name_dict.get(i).split(',')
                    output = ','.join(map(str, name_list))
                    html =f'''
                    <h1 style="color:black">共乘阿穿</h1>
                    <div style="color:black">{str1}</div>
                    <div style="color:black">{str2}<div>
                    <div style="color:black">{str3}<div>
                    '''
                    mail = MIMEText(html, 'html', 'utf-8')   # plain 換成 html，就能寄送 HTML 格式的信件
                    mail['Subject']= str4
                    mail['From']='adf'
                    mail['To']= passenger_sheet[i][1]
                    try:
                        smtp = smtplib.SMTP('smtp.gmail.com', 587)
                        smtp.ehlo()
                        smtp.starttls()
                        smtp.login('ncnucarpool@gmail.com',os.getenv('GMAIL_PASSWORD'))
                        status = smtp.send_message(mail)
                        smtp.quit()
                        # 將此索引添加到已處理集合中
                        web_passenger_Sure.add(i)
                        print(f"乘客 {i} 已標記為處理完成")
                    except Exception as e:
                        print(f"發送郵件時出錯: {e}")           
                    # 當活動人數已滿的時候，向活動參與者發送提醒（告知可發車及聯繫發起人）
                    try:
                        passenger_Sure = passenger_sheet[i][14]
                        passenger_Sure_list = passenger_Sure.split(',')
                        for r in passenger_Sure_list:
                            with ApiClient(configuration) as api_client:
                                line_bot_api = MessagingApi(api_client)
                                line_bot_api.push_message(
                                    PushMessageRequest(
                                        to=r,
                                        messages=[TextMessage(text=passenger_text)]
                                    )
                                )
                    except:
                        pass
                else:
                    pass
            else:
                pass
    check_project_s()
def get_driver_sheet_case():
    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=60), retry=retry_if_exception_type(gspread.exceptions.APIError))
    def get_driver_sheet_case_s():
        global driver_sheet, web_driver_len, driver_Sure_id_dict, driver_Sure_name_dict, New_driver_update
        driver_sheet = driver_sheet_id.get_all_values()
        try:
            web_driver_len=len(driver_sheet) #抓取司機表單中有幾筆資料(已藉由更改其App script的程式碼扣除第一列的項目)
        except requests.exceptions.JSONDecodeError:
            web_driver_len = 0
        try:
            # 設定一個司機發起的活動dict容納確定參與的使用者
            driver_Sure_id_dict = {}
            driver_Sure_name_dict = {}
            New_driver_update = ''
            for i in range(1,web_driver_len):
                driver_Sure_id_dict[i] = driver_sheet[i][15]
                driver_Sure_name_dict[i] = driver_sheet[i][16]
                if driver_sheet[i][14] == '':
                    New_driver_update = 'New_driver_update'
                    driver_sheet_id.batch_update([
                        {
                            'values': [[0]],
                            'range': f'O{i+1}'
                        },
                        {
                            'values': [[i+1]],
                            'range': f'R{i+1}'
                        }
                    ])
                    driver_sheet[i][14] = 0
                    driver_sheet[i][17] = i+1
                else:
                    pass
            print('司機發起之活動已抓取')
        except:
            print('司機發起之活動尚無資料')
    get_driver_sheet_case_s()
def get_passenger_sheet_case():
    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=60), retry=retry_if_exception_type(gspread.exceptions.APIError))
    def get_passenger_sheet_case_s():
        global passenger_sheet, web_passenger_len, passenger_Sure_id_dict, passenger_bedriverSure_id_dict, passenger_Sure_name_dict, New_passenger_update
        passenger_sheet = passenger_sheet_id.get_all_values()
        try:
            web_passenger_len=len(passenger_sheet) #抓取司機表單中有幾筆資料(已藉由更改其App script的程式碼扣除第一列的項目)
        except requests.exceptions.JSONDecodeError:
            web_passenger_len = 0
        try:
            # 設定一個揪團的dict容納確定參與的使用者
            passenger_Sure_id_dict = {}
            passenger_bedriverSure_id_dict = {}
            passenger_Sure_name_dict = {}
            New_passenger_update = ''
            for i in range(1,web_passenger_len):
                passenger_Sure_id_dict[i] = passenger_sheet[i][14]
                passenger_bedriverSure_id_dict[i] = passenger_sheet[i][19]
                passenger_Sure_name_dict[i] = passenger_sheet[i][15]
                if passenger_sheet[i][13] == '':
                    New_passenger_update = 'New_passenger_update'
                    passenger_sheet_id.batch_update([
                        {
                            'values': [[0]],
                            'range': f'N{i+1}'
                            
                        },
                        {
                            'values': [[i+1]],
                            'range': f'Q{i+1}'
                        }
                    ])
                    print(New_passenger_update)
                    passenger_sheet[i][13] = 0
                    passenger_sheet[i][16] = i+1
                else:
                    pass
            print('乘客發起之揪團活動已抓取')
        except:
            print('乘客發起之揪團活動尚無資料')
    get_passenger_sheet_case_s()
#   每隔3秒檢查試算表內容，若人數達上限即通知活動發起者人數已滿
def run_scheduler():
    global a
    a = True
    while a:
        schedule.run_pending()
        time.sleep(0.1)  
schedule.every(30).minutes.do(check_project)
schedule.every(10).seconds.do(get_driver_sheet_case)
schedule.every(10).seconds.do(get_passenger_sheet_case)
scheduler_thread_case = threading.Thread(target=run_scheduler)
# 20250418有可能運行期間出現問題後(任何)，就會永久結束，需要伺服器重啟才能再執行，因此不使用。
# scheduler_thread_case.daemon = True 主程式結束此也結束
scheduler_thread_case.start()

# Tamplate Message
@line_handler.add(MessageEvent, message = TextMessageContent)
def handle_message(event):
    text = event.message.text
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        # Carousel Template 
        if text =='目前有哪些共乘（已有司機）？':
            if web_driver_len != 1:
                line_flex_json = {
                    "type": "carousel",
                    "contents": []
                }    
                for i in range(1,web_driver_len):
                    driver_case_date = parse_custom_time(driver_sheet[i][3]).replace(hour=0, minute=0, second=0, microsecond=0)
                    driver_case_launchdate = parse_custom_time(driver_sheet[i][0]).replace(hour=0, minute=0, second=0, microsecond=0)
                    now_date = (datetime_datetime.now() + datetime.timedelta(hours = 8)).replace(hour=0, minute=0, second=0, microsecond=0)
                    if driver_case_date>=now_date or driver_case_launchdate == now_date:
                        driver_limitnumber_type = ''
                        try :
                            int(driver_sheet[i][14])
                            pass
                        except ValueError:
                            driver_sheet[i][14]=0
                        try :
                            int(driver_sheet[i][5])
                        except:
                            driver_limitnumber_type = '共乘人數上限不為數字'
                        if driver_limitnumber_type == '共乘人數上限不為數字' or int(driver_sheet[i][14]) <= int(driver_sheet[i][5]) or int(driver_sheet[i][14])== 0:
                            web_driver_data_case={
                                "type": "bubble",
                                "size": "mega",
                                "header": {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                        {
                                            "type": "text",
                                            "text": "FROM",
                                            "color": "#ffffff66",
                                            "size": "xxs"
                                        },
                                        {
                                            "type": "text",
                                            "text": driver_sheet[i][2],
                                            "color": "#ffffff",
                                            "size": "lg",
                                            "weight": "bold"
                                        }
                                        ]
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                        {
                                            "type": "text",
                                            "text": "TO",
                                            "color": "#ffffff66",
                                            "size": "xxs"
                                        },
                                        {
                                            "type": "text",
                                            "text": driver_sheet[i][4],
                                            "color": "#ffffff",
                                            "size": "lg",
                                            "weight": "bold",
                                            "margin": "none"
                                        }
                                        ]
                                    },
                                    {
                                        "type": "text",
                                        "text": f"出發時間：{driver_sheet[i][3]}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "contents": [],
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"總時程：{time_hrmi(int(driver_sheet[i][6]))}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"發起人（司機）：{driver_sheet[i][9]}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"共乘人數上限：{driver_sheet[i][5]}",
                                        "color": "#000000",
                                        "size": "xs"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"共乘費用分攤：{driver_sheet[i][11]}",
                                        "color": "#000000",
                                        "size": "xs"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"當前預約人數：{int(driver_sheet[i][14])}",
                                        "color": "#000000",
                                        "size": "xs"
                                    }
                                    ],
                                    "paddingAll": "20px",
                                    "backgroundColor": "#e6b89d",
                                    "spacing": "md",
                                    "height": "265px",
                                    "paddingTop": "22px"
                                },
                                "body": {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                    {
                                        "type": "text",
                                        "text": f"共乘編號：{driver_sheet[i][17]}",
                                        "margin": "none",
                                        "size": "sm",
                                        "weight": "bold"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"交通工具：{driver_sheet[i][12]}",
                                        "margin": "none",
                                        "size": "sm",
                                        "weight": "bold"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"備註：{driver_sheet[i][8]}",
                                        "margin": "xl"
                                    }
                                    ]
                                },
                                "footer": {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                    {
                                        "type": "button",
                                        "action": {
                                        "type": "postback",
                                        "label": "我要共乘（詳細資訊）",
                                        "data": f"driver_Num{i}",
                                        "displayText": f"{driver_sheet[i][2]}到{driver_sheet[i][4]}的共乘資訊"
                                        },
                                        "style": "secondary"
                                    }
                                    ]
                                }
                            }
                            # 新增規範
                            driver_speci_set = ['上下車地點可討論', '自備零錢不找零', '接受線上付款 / 轉帳', '禁食', '不聊天', '寵物需裝籠', '謝絕寵物']
                            for specification in driver_speci_set:
                                if specification in driver_sheet[i][7]:
                                    r = {
                                            "type": "text",
                                            "text": specification,
                                            "size": "sm",
                                            "margin": "none",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                    web_driver_data_case['body']['contents'].insert(2,r)
                                else:
                                    pass
                            if '※ 人滿才發車' in driver_sheet[i][7]:
                                r = {
                                        "type": "text",
                                        "text": '※ 人滿才發車',
                                        "size": "sm",
                                        "margin": "none",
                                        "color": "#ff5551",
                                        "contents": [],
                                        "offsetEnd": "none"
                                    }
                                web_driver_data_case['body']['contents'].insert(2,r)
                            else:
                                pass
                            line_flex_json['contents'].append(web_driver_data_case)
                        else:
                            pass
                    else:
                        pass
                # 若有活動且人數未滿
                if line_flex_json != {
                    "type": "carousel",
                    "contents": []
                }:            
                    line_flex_str = json.dumps(line_flex_json) #改成字串格式
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[FlexMessage(alt_text='目前有的共乘（司機揪團）', contents=FlexContainer.from_json(line_flex_str))]
                        )
                    )
                # 若有活動但人數皆已滿
                else:
                    line_bot_api.reply_message( #傳送'目前司機發起之活動預約人數皆已滿'回復訊息
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(text='目前司機發起之活動預約人數皆已滿，或是逾期。')] 
                        )  
                    )
            else:
                line_bot_api.reply_message( #傳送'目前尚無司機發起共乘活動'回復訊息
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text='目前尚無司機發起共乘活動')] 
                    )  
                ) 
        elif text =='目前有哪些共乘（揪團）？':
            if web_passenger_len != 1:
                line_flex_json = {
                    "type": "carousel",
                    "contents": []
                }
                for i in range(1,web_passenger_len):
                    passenger_case_date = parse_custom_time(passenger_sheet[i][3]).replace(hour=0, minute=0, second=0, microsecond=0)
                    passenger_case_launchdate = parse_custom_time(passenger_sheet[i][0]).replace(hour=0, minute=0, second=0, microsecond=0)
                    now_date = (datetime_datetime.now() + datetime.timedelta(hours = 8)).replace(hour=0, minute=0, second=0, microsecond=0)
                    if passenger_case_date>=now_date or passenger_case_launchdate == now_date:
                        passenger_limitnumber_type = ''
                        try :
                            int(passenger_sheet[i][13])
                        except ValueError:
                            passenger_sheet[i][13]=0
                        try:
                            int(passenger_sheet[i][5])
                        except:
                            passenger_limitnumber_type = '共乘人數上限不為數字'
                        if passenger_sheet[i][18] == '':
                            passenger_driver = '無'
                        else:
                            passenger_driver = passenger_sheet[i][18]
                        if passenger_limitnumber_type == '共乘人數上限不為數字' or type(passenger_sheet[i][5])== str or int(passenger_sheet[i][13]) <= int(passenger_sheet[i][5]) or int(passenger_sheet[i][13])== 0:
                            web_passenger_data_case={
                                "type": "bubble",
                                "size": "mega",
                                "header": {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                        {
                                            "type": "text",
                                            "text": "FROM",
                                            "color": "#ffffff66",
                                            "size": "xxs"
                                        },
                                        {
                                            "type": "text",
                                            "text": passenger_sheet[i][2],
                                            "color": "#ffffff",
                                            "size": "lg",
                                            "weight": "bold"
                                        }
                                        ]
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                        {
                                            "type": "text",
                                            "text": "TO",
                                            "color": "#ffffff66",
                                            "size": "xxs"
                                        },
                                        {
                                            "type": "text",
                                            "text": passenger_sheet[i][4],
                                            "color": "#ffffff",
                                            "size": "lg",
                                            "weight": "bold",
                                            "margin": "none"
                                        }
                                        ]
                                    },
                                    {
                                        "type": "text",
                                        "text": f"出發時間：{passenger_sheet[i][3]}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "contents": [],
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"預估時程：{time_hrmi(int(passenger_sheet[i][6]))}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"發起人（乘客）：{passenger_sheet[i][9]}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"司機：{passenger_driver}",
                                        "color": "#000000",
                                        "size": "xs"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"共乘人數上限：{passenger_sheet[i][5]}",
                                        "color": "#000000",
                                        "size": "xs"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"當前預約人數：{int(passenger_sheet[i][13])}",
                                        "color": "#000000",
                                        "size": "xs"
                                    }
                                    ],
                                    "paddingAll": "20px",
                                    "backgroundColor": "#e6b89d",
                                    "spacing": "md",
                                    "height": "270px",
                                    "paddingTop": "22px"
                                },
                                "body": {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                    {
                                        "type": "text",
                                        "text": f"共乘編號：{passenger_sheet[i][16]}",
                                        "margin": "none",
                                        "size": "sm",
                                        "weight": "bold"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"交通工具：{passenger_sheet[i][11]}",
                                        "margin": "none",
                                        "size": "sm",
                                        "weight": "bold"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"備註：{passenger_sheet[i][8]}",
                                        "margin": "xl"
                                    }
                                    ]
                                },
                                "footer": {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                    {
                                        "type": "button",
                                        "action": {
                                        "type": "postback",
                                        "label": "我要共乘∕當司機（詳細資訊）",
                                        "data": f"passenger_Num{i}",
                                        "displayText": f"{passenger_sheet[i][2]}到{passenger_sheet[i][4]}的共乘資訊"
                                        },
                                        "style": "secondary"
                                    }
                                    ]
                                }
                            }
                            # 新增規範
                            passenger_speci_set = ['上下車地點可討論', '不聊天', '嚴禁喝酒及抽菸', '禁食', '謝絕寵物', '寵物需裝籠']
                            passenger_speci_red_set = ['已有司機', '尚未有司機（徵求司機！）', '叫車分攤費用', '※ 人滿才發車']
                            for specification in passenger_speci_set:
                                if specification in passenger_sheet[i][7]:
                                    r = {
                                            "type": "text",
                                            "text": specification,
                                            "size": "sm",
                                            "margin": "none",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                    web_passenger_data_case['body']['contents'].insert(2,r)
                                else:
                                    pass
                            for specification in passenger_speci_red_set:
                                if specification in passenger_sheet[i][7]:
                                    r = {
                                            "type": "text",
                                            "text": specification,
                                            "size": "sm",
                                            "margin": "none",
                                            "color": "#ff5551",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                    web_passenger_data_case['body']['contents'].insert(2,r)
                                else:
                                    pass
                            line_flex_json['contents'].append(web_passenger_data_case)   
                        else:
                            pass
                    else:
                        pass
                if line_flex_json != {
                    "type": "carousel",
                    "contents": []
                }:
                    line_flex_str = json.dumps(line_flex_json) #改成字串格式
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[FlexMessage(alt_text='目前有的共乘（乘客揪團）', contents=FlexContainer.from_json(line_flex_str))]
                        )
                    )
                # 若有活動但人數皆已滿
                else:
                    line_bot_api.reply_message( #傳送'目前乘客發起之揪團活動預約人數皆已滿'回復訊息
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(text='目前乘客發起之揪團活動預約人數皆已滿，或是逾期')] 
                        )  
                    )
            else:
                line_bot_api.reply_message( #傳送'目前尚無乘客發起揪團活動'回復訊息
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text='目前尚無乘客發起揪團活動')] 
                    )  
                )                
        elif text == '我的預約':
            line_flex_json = {
                    "type": "carousel",
                    "contents": []
            }
            # 獲取使用者 user_ID 
            user_id = event.source.user_id
            now_date = (datetime_datetime.now() + datetime.timedelta(hours = 8)).replace(hour=0, minute=0, second=0, microsecond=0)
            if user_id in str(driver_Sure_id_dict.values()): # dict_value type 不能用 str in 的判斷式
                for i in range(1,web_driver_len):
                    driver_case_date = parse_custom_time(driver_sheet[i][3]).replace(hour=0, minute=0, second=0, microsecond=0)
                    driver_case_launchdate = parse_custom_time(driver_sheet[i][0]).replace(hour=0, minute=0, second=0, microsecond=0)
                    if driver_case_date>=now_date or driver_case_launchdate == now_date:
                        try :
                            int(driver_sheet[i][14])
                            pass
                        except ValueError:
                            driver_sheet[i][14]=0
                        if user_id in driver_sheet[i][15]:
                            web_driver_data_case={
                                "type": "bubble",
                                "size": "mega",
                                "header": {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                        {
                                            "type": "text",
                                            "text": "FROM",
                                            "color": "#ffffff66",
                                            "size": "xxs"
                                        },
                                        {
                                            "type": "text",
                                            "text": driver_sheet[i][2],
                                            "color": "#ffffff",
                                            "size": "lg",
                                            "weight": "bold"
                                        }
                                        ]
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                        {
                                            "type": "text",
                                            "text": "TO",
                                            "color": "#ffffff66",
                                            "size": "xxs"
                                        },
                                        {
                                            "type": "text",
                                            "text": driver_sheet[i][4],
                                            "color": "#ffffff",
                                            "size": "lg",
                                            "weight": "bold",
                                            "margin": "none"
                                        }
                                        ]
                                    },
                                    {
                                        "type": "text",
                                        "text": f"出發時間：{driver_sheet[i][3]}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "contents": [],
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"總時程：{time_hrmi(int(driver_sheet[i][6]))}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"發起人（司機）：{driver_sheet[i][9]}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"手機號碼：{driver_sheet[i][13]}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"LineID：{driver_sheet[i][10]}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"共乘人數上限：{driver_sheet[i][5]}",
                                        "color": "#000000",
                                        "size": "xs"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"共乘費用分攤：{driver_sheet[i][11]}",
                                        "color": "#000000",
                                        "size": "xs"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"當前預約人數：{int(driver_sheet[i][14])}",
                                        "color": "#000000",
                                        "size": "xs"
                                    }
                                    ],
                                    "paddingAll": "20px",
                                    "backgroundColor": "#c89273",
                                    "spacing": "md",
                                    "height": "300px",
                                    "paddingTop": "22px"
                                },
                                "body": {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                    {
                                        "type": "text",
                                        "text": f"共乘編號：{driver_sheet[i][17]}",
                                        "margin": "none",
                                        "size": "sm",
                                        "weight": "bold"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"交通工具：{driver_sheet[i][12]}",
                                        "margin": "none",
                                        "size": "sm",
                                        "weight": "bold"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"備註：{driver_sheet[i][8]}",
                                        "margin": "xl"
                                    }
                                    ]
                                },
                                "footer": {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                        {
                                            "type": "button",
                                            "action": {
                                            "type": "postback",
                                            "label": "詳細資訊",
                                            "data": f"driver_template_detail_info{i}",
                                            "displayText": f"{driver_sheet[i][2]}到{driver_sheet[i][4]}的共乘資訊"
                                            },
                                            "style": "link",
                                            "margin": "none",
                                            "height": "sm"
                                        },
                                        {
                                            "type": "button",
                                            "action": {
                                            "type": "postback",
                                            "label": "取消乘客預約",
                                            "data": f"driver_cancel_Num{i}",
                                            "displayText": f"我想取消共乘編號：{driver_sheet[i][17]}的乘客預約"
                                            },
                                            "style": "primary",
                                            "height": "sm",
                                            "color": "#ff5757"
                                        }
                                    ]
                                }
                            }
                            # 新增規範
                            driver_speci_set = ['上下車地點可討論', '自備零錢不找零', '接受線上付款 / 轉帳', '禁食', '不聊天', '寵物需裝籠', '謝絕寵物']
                            for specification in driver_speci_set:
                                if specification in driver_sheet[i][7]:
                                    r = {
                                            "type": "text",
                                            "text": specification,
                                            "size": "sm",
                                            "margin": "none",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                    web_driver_data_case['body']['contents'].insert(2,r)
                                else:
                                    pass
                            if '※ 人滿才發車' in driver_sheet[i][7]:
                                r = {
                                        "type": "text",
                                        "text": '※ 人滿才發車',
                                        "size": "sm",
                                        "margin": "none",
                                        "color": "#ff5551",
                                        "contents": [],
                                        "offsetEnd": "none"
                                    }
                                web_driver_data_case['body']['contents'].insert(2,r)
                            else:
                                pass
                            line_flex_json['contents'].append(web_driver_data_case)
                        else:
                            pass
                    else:
                        pass
            else:
                pass
            if user_id in str(passenger_Sure_id_dict.values()) or str(passenger_bedriverSure_id_dict.values()): # dict_value type 不能用 str in 的判斷式
                for i in range(1,web_passenger_len):
                    passenger_case_date = parse_custom_time(passenger_sheet[i][3]).replace(hour=0, minute=0, second=0, microsecond=0)
                    passenger_case_launchdate = parse_custom_time(passenger_sheet[i][0]).replace(hour=0, minute=0, second=0, microsecond=0)
                    if passenger_case_date>=now_date or passenger_case_launchdate == now_date:
                        try :
                            int(passenger_sheet[i][13])
                        except ValueError:
                            passenger_sheet[i][13]=0
                        if passenger_sheet[i][18] == '':
                            passenger_driver = '無'
                        else:
                            passenger_driver = passenger_sheet[i][18]
                        # 使用者預約為乘客
                        if user_id in passenger_sheet[i][14]:
                            web_passenger_data_case={
                                "type": "bubble",
                                "size": "mega",
                                "header": {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                        {
                                            "type": "text",
                                            "text": "FROM",
                                            "color": "#ffffff66",
                                            "size": "xxs"
                                        },
                                        {
                                            "type": "text",
                                            "text": passenger_sheet[i][2],
                                            "color": "#ffffff",
                                            "size": "lg",
                                            "weight": "bold"
                                        }
                                        ]
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                        {
                                            "type": "text",
                                            "text": "TO",
                                            "color": "#ffffff66",
                                            "size": "xxs"
                                        },
                                        {
                                            "type": "text",
                                            "text": passenger_sheet[i][4],
                                            "color": "#ffffff",
                                            "size": "lg",
                                            "weight": "bold",
                                            "margin": "none"
                                        }
                                        ]
                                    },
                                    {
                                        "type": "text",
                                        "text": f"出發時間：{passenger_sheet[i][3]}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "contents": [],
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"預估時程：{time_hrmi(int(passenger_sheet[i][6]))}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"發起人（乘客）：{passenger_sheet[i][9]}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"手機號碼：{passenger_sheet[i][12]}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"LineID：{passenger_sheet[i][10]}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"司機：{passenger_driver}",
                                        "color": "#000000",
                                        "size": "xs"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"共乘人數上限：{passenger_sheet[i][5]}",
                                        "color": "#000000",
                                        "size": "xs"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"當前預約人數：{int(passenger_sheet[i][13])}",
                                        "color": "#000000",
                                        "size": "xs"
                                    }
                                    ],
                                    "paddingAll": "20px",
                                    "backgroundColor": "#c89273",
                                    "spacing": "md",
                                    "height": "300px",
                                    "paddingTop": "22px"
                                },
                                "body": {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                    {
                                        "type": "text",
                                        "text": f"共乘編號：{passenger_sheet[i][16]}",
                                        "margin": "none",
                                        "size": "sm",
                                        "weight": "bold"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"交通工具：{passenger_sheet[i][11]}",
                                        "margin": "none",
                                        "size": "sm",
                                        "weight": "bold"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"備註：{passenger_sheet[i][8]}",
                                        "margin": "xl"
                                    }
                                    ]
                                },
                                "footer": {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                        {
                                            "type": "button",
                                            "action": {
                                            "type": "postback",
                                            "label": "詳細資訊",
                                            "data": f"passenger_template_detail_info{i}",
                                            "displayText": f"{passenger_sheet[i][2]}到{passenger_sheet[i][4]}的共乘資訊"
                                            },
                                            "style": "link",
                                            "margin": "none",
                                            "height": "sm"
                                        },
                                        {
                                            "type": "button",
                                            "action": {
                                            "type": "postback",
                                            "label": "取消乘客預約",
                                            "data": f"passenger_cancel_Num{i}",
                                            "displayText": f"我想取消共乘編號：{driver_sheet[i][17]}的乘客預約"
                                            },
                                            "style": "primary",
                                            "height": "sm",
                                            "color": "#ff5757"
                                        }
                                    ]
                                }
                                }
                            # 新增規範
                            passenger_speci_set = ['上下車地點可討論', '不聊天', '嚴禁喝酒及抽菸', '禁食', '謝絕寵物', '寵物需裝籠']
                            passenger_speci_red_set = ['已有司機', '尚未有司機（徵求司機！）', '叫車分攤費用', '※ 人滿才發車']
                            for specification in passenger_speci_set:
                                if specification in passenger_sheet[i][7]:
                                    r = {
                                            "type": "text",
                                            "text": specification,
                                            "size": "sm",
                                            "margin": "none",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                    web_passenger_data_case['body']['contents'].insert(2,r)
                                else:
                                    pass
                            for specification in passenger_speci_red_set:
                                if specification in passenger_sheet[i][7]:
                                    r = {
                                            "type": "text",
                                            "text": specification,
                                            "size": "sm",
                                            "margin": "none",
                                            "color": "#ff5551",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                    web_passenger_data_case['body']['contents'].insert(2,r)
                                else:
                                    pass
                            line_flex_json['contents'].append(web_passenger_data_case)   
                        # 使用者預約為司機
                        elif user_id in passenger_sheet[i][19]:
                            web_passenger_data_case={
                                "type": "bubble",
                                "size": "mega",
                                "header": {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                        {
                                            "type": "text",
                                            "text": "FROM",
                                            "color": "#ffffff66",
                                            "size": "xxs"
                                        },
                                        {
                                            "type": "text",
                                            "text": passenger_sheet[i][2],
                                            "color": "#ffffff",
                                            "size": "lg",
                                            "weight": "bold"
                                        }
                                        ]
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                        {
                                            "type": "text",
                                            "text": "TO",
                                            "color": "#ffffff66",
                                            "size": "xxs"
                                        },
                                        {
                                            "type": "text",
                                            "text": passenger_sheet[i][4],
                                            "color": "#ffffff",
                                            "size": "lg",
                                            "weight": "bold",
                                            "margin": "none"
                                        }
                                        ]
                                    },
                                    {
                                        "type": "text",
                                        "text": f"出發時間：{passenger_sheet[i][3]}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "contents": [],
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"預估時程：{time_hrmi(int(passenger_sheet[i][6]))}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"發起人（乘客）：{passenger_sheet[i][9]}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"手機號碼：{passenger_sheet[i][12]}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"LineID：{passenger_sheet[i][10]}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"司機：{passenger_driver}",
                                        "color": "#000000",
                                        "size": "xs"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"共乘人數上限：{passenger_sheet[i][5]}",
                                        "color": "#000000",
                                        "size": "xs"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"當前預約人數：{int(passenger_sheet[i][13])}",
                                        "color": "#000000",
                                        "size": "xs"
                                    }
                                    ],
                                    "paddingAll": "20px",
                                    "backgroundColor": "#c89273",
                                    "spacing": "md",
                                    "height": "300px",
                                    "paddingTop": "22px"
                                },
                                "body": {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                    {
                                        "type": "text",
                                        "text": f"共乘編號：{passenger_sheet[i][16]}",
                                        "margin": "none",
                                        "size": "sm",
                                        "weight": "bold"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"交通工具：{passenger_sheet[i][11]}",
                                        "margin": "none",
                                        "size": "sm",
                                        "weight": "bold"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"備註：{passenger_sheet[i][8]}",
                                        "margin": "xl"
                                    }
                                    ]
                                },
                                "footer": {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                        {
                                            "type": "button",
                                            "action": {
                                            "type": "postback",
                                            "label": "詳細資訊",
                                            "data": f"passenger_template_detail_info{i}",
                                            "displayText": f"{passenger_sheet[i][2]}到{passenger_sheet[i][4]}的共乘資訊"
                                            },
                                            "style": "link",
                                            "margin": "none",
                                            "height": "sm"
                                        },
                                        {
                                            "type": "button",
                                            "action": {
                                            "type": "postback",
                                            "label": "取消司機預約",
                                            "data": f"passenger_cancel_bedriver_Num{i}",
                                            "displayText": f"我想取消共乘編號：{passenger_sheet[i][16]}的司機預約"
                                            },
                                            "style": "primary",
                                            "height": "sm",
                                            "color": "#ff5757"
                                        }
                                    ]
                                }
                            }
                            # 新增規範
                            passenger_speci_set = ['上下車地點可討論', '不聊天', '嚴禁喝酒及抽菸', '禁食', '謝絕寵物', '寵物需裝籠']
                            passenger_speci_red_set = ['已有司機', '尚未有司機（徵求司機！）', '叫車分攤費用', '※ 人滿才發車']
                            for specification in passenger_speci_set:
                                if specification in passenger_sheet[i][7]:
                                    r = {
                                            "type": "text",
                                            "text": specification,
                                            "size": "sm",
                                            "margin": "none",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                    web_passenger_data_case['body']['contents'].insert(2,r)
                                else:
                                    pass
                            for specification in passenger_speci_red_set:
                                if specification in passenger_sheet[i][7]:
                                    r = {
                                            "type": "text",
                                            "text": specification,
                                            "size": "sm",
                                            "margin": "none",
                                            "color": "#ff5551",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                    web_passenger_data_case['body']['contents'].insert(2,r)
                                else:
                                    pass
                            line_flex_json['contents'].append(web_passenger_data_case)                              
                        else:
                            pass
                    else:
                        pass
            else:
                pass
            if line_flex_json != {
                "type": "carousel",
                "contents": []
            }:
                line_flex_str = json.dumps(line_flex_json) #改成字串格式
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[FlexMessage(alt_text='已預約的共乘', contents=FlexContainer.from_json(line_flex_str))]
                    )
                )
            else:
                line_bot_api.reply_message( #傳送回復訊息
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text='您尚未預約任何活動')]
                    )
                )
driver_lock = threading.Lock()
passenger_lock = threading.Lock()
@line_handler.add(PostbackEvent)
def handle_postbak(event):
    try:
        for i in range(1,web_driver_len):
            if event.postback.data == f'driver_Num{i}':
                driver_case_datetime = parse_custom_time(driver_sheet[i][3]).replace(minute=0, second=0, microsecond=0)
                driver_case_datetime_ahead = driver_case_datetime - datetime.timedelta(hours = 3)
                driver_case_launchdate = parse_custom_time(driver_sheet[i][0]).replace(hour=0, minute=0, second=0, microsecond=0)
                now_date = (datetime_datetime.now() + datetime.timedelta(hours = 8)).replace(hour=0, minute=0, second=0, microsecond=0)
                now_datetime = (datetime_datetime.now() + datetime.timedelta(hours = 8)).replace(minute=0, second=0, microsecond=0)
                # 獲取使用者 user_ID
                driver_user_id = event.source.user_id
                with ApiClient(configuration) as api_client:
                    line_bot_api = MessagingApi(api_client)
                    if driver_case_datetime_ahead >= now_datetime or driver_sheet[i][19] == '是' and driver_case_datetime >= now_date:
                        confirm_template = ConfirmTemplate(
                            text = f'📎共乘編號：{driver_sheet[i][17]}\n📍出發地點：{driver_sheet[i][2]}\n📍目的地點：{driver_sheet[i][4]}\n🕒出發時間：\n{driver_sheet[i][3]}\n⏳預估時程：{time_hrmi(int(driver_sheet[i][6]))}\n#️⃣共乘上限：{driver_sheet[i][5]} 人\n🏷️共乘費用分攤：{driver_sheet[i][11]}\n🚗司機名稱：\n{driver_sheet[i][9]}\n🛞交通工具：{driver_sheet[i][12]}\n❗️行車規範：\n{driver_sheet[i][7]}\n💬備註：\n{driver_sheet[i][8]}\n',
                            actions=[ #只能放兩個Action
                                PostbackAction(label='我想共乘！', text='我想共乘！', data=f'driver_Sure{i}'),
                                PostbackAction(label='司機聯絡資訊', text='司機聯絡資訊', data = f'driver_info{i}')
                            ]
                        )
                        template_message = TemplateMessage(
                            alt_text = f'從{driver_sheet[i][2]}到{driver_sheet[i][4]}的詳細資訊',
                            template = confirm_template
                        )
                        line_bot_api.push_message(
                            PushMessageRequest(
                                to=driver_user_id,
                                messages = [template_message]
                            )
                        ) 
                    else:
                        line_bot_api.push_message(
                            PushMessageRequest(
                                to=driver_user_id,
                                messages = [TextMessage(text=f'報名已經截止囉！時間未到的話也可嘗試聯絡活動發起人。\n發起人（司機）名稱：\n{driver_sheet[i][9]}\nLineID：{driver_sheet[i][10]}\n手機號碼：{driver_sheet[i][13]}')]
                            )
                        )        
            # 使用者在Confirm Template按下確定後，試算表的搭車人數將+1
            elif event.postback.data == f'driver_Sure{i}':
                target_row = driver_sheet_id.row_values(i+1)
                with driver_lock:
                    with ApiClient(configuration) as api_client:
                        line_bot_api = MessagingApi(api_client)
                        # 獲取使用者 user_ID
                        driver_user_id = event.source.user_id
                        if int(target_row[14]) != target_row[5]:
                            # 獲取使用者資料
                            profile = line_bot_api.get_profile(driver_user_id)
                            # 獲取使用者名稱    
                            driver_Sure_name = profile.display_name 
                            driver_user_id_check = ''          
                            #-----------------------------------------------------
                            if driver_user_id in target_row[15]:
                                driver_user_id_check = 'Checked'
                                line_bot_api.push_message(
                                    PushMessageRequest(
                                        to=driver_user_id,
                                        messages = [TextMessage(text='您已預約')]
                                    )
                                )
                            elif driver_user_id_check != 'Checked':
                                line_bot_api.push_message(
                                    PushMessageRequest(
                                        to=driver_user_id,
                                        messages = [TextMessage(text=f'已幫您預約，記得透過LineID聯繫活動發起人!\n發起人（司機）名稱：\n{target_row[9]}\nLineID：{target_row[10]}\n手機號碼：{driver_sheet[i][13]}\n車牌及型號：\n{target_row[18]}')]
                                    )
                                )
                                try :
                                    int(target_row[14])
                                    pass
                                except ValueError:
                                    target_row[14]=0
                                if target_row[15] == '':
                                    new_id = driver_user_id
                                    new_name = driver_Sure_name
                                else:  
                                    id = target_row[15]
                                    new_id = id+','+driver_user_id
                                    name = target_row[16]
                                    new_name = name+','+driver_Sure_name
                                driver_sheet_id.update([[int(target_row[14])+1, new_id, new_name]], f'O{i+1}:Q{i+1}')
                                get_driver_sheet_case()
                            else:
                                pass                        
                        else:
                            line_bot_api.push_message(
                                PushMessageRequest(
                                    to=driver_user_id,
                                    messages = [TextMessage(text='此活動人數已滿')]
                                )
                            )
            elif event.postback.data == f'driver_info{i}':
                # 獲取使用者 user_ID
                driver_user_id = event.source.user_id
                target_row = driver_sheet_id.row_values(i+1)
                with ApiClient(configuration) as api_client:
                    line_bot_api = MessagingApi(api_client)
                    # 獲取使用者 user_ID
                    driver_user_id = event.source.user_id
                    line_bot_api.push_message(
                        PushMessageRequest(
                            to=driver_user_id,
                            messages = [TextMessage(text=f'發起人（司機）名稱：{target_row[9]}\nLineID：{target_row[10]}\n電話號碼：{target_row[13]}\n聯絡後仍要記得預約喔！後續搭乘問題都會依照實際預約者為先。')]
                        )
                    )
            elif event.postback.data == f"driver_template_detail_info{i}":
                # 獲取使用者 user_ID
                driver_user_id = event.source.user_id
                with ApiClient(configuration) as api_client:
                    line_bot_api = MessagingApi(api_client)
                    reservation = f'📎共乘編號：{driver_sheet[i][17]}\n📍出發地點：{driver_sheet[i][2]}\n📍目的地點：{driver_sheet[i][4]}\n🕒出發時間：\n{driver_sheet[i][3]}\n⏳預估時程：{time_hrmi(int(driver_sheet[i][6]))}\n#️⃣共乘上限：{driver_sheet[i][5]} 人\n🏷️共乘費用分攤：{driver_sheet[i][11]}\n🚗司機名稱：\n{driver_sheet[i][9]}\n🆔LineID：{driver_sheet[i][10]}\n📱手機號碼：{driver_sheet[i][13]}\n🛞交通工具：{driver_sheet[i][12]}\n❗️行車規範：\n{driver_sheet[i][7]}\n💬備註：\n{driver_sheet[i][8]}\n'
                    line_bot_api.push_message(
                        PushMessageRequest(
                            to=driver_user_id,
                            messages = [TextMessage(text=reservation)]
                        )
                    )
            elif event.postback.data == f"driver_cancel_Num{i}":
                target_row = driver_sheet_id.row_values(i+1)
                # 獲取使用者 user_ID
                driver_user_id = event.source.user_id
                with driver_lock:
                    with ApiClient(configuration) as api_client:
                        line_bot_api = MessagingApi(api_client)
                        # 獲取使用者資料
                        profile = line_bot_api.get_profile(driver_user_id)
                        # 獲取使用者名稱        
                        driver_Sure_name=profile.display_name
                        if driver_user_id in target_row[15]:
                            line_bot_api.reply_message(
                                ReplyMessageRequest(
                                    reply_token=event.reply_token,
                                    messages = [TextMessage(text=f'已幫您取消共乘編號：{target_row[17]}的乘客預約')]
                                )
                            )
                            # 刪除 UserID 紀錄
                            id = target_row[15].split(',')
                            target_position = id.index(driver_user_id)
                            del id[target_position]
                            deled_id = ','.join(id)
                            # 刪除 User名稱 紀錄
                            name = target_row[16].split(',')
                            del name[target_position]
                            deled_name = ','.join(name)
                            driver_sheet_id.update([[int(target_row[14])-1, deled_id, deled_name]], f'O{i+1}:Q{i+1}')
                            get_driver_sheet_case()
                        else:
                            line_bot_api.reply_message(
                                ReplyMessageRequest(
                                    reply_token=event.reply_token,
                                    messages = [TextMessage(text='您尚未預約')]
                                )
                            )
    except NameError:
        pass
    try:
        for i in range(1,web_passenger_len):
            if event.postback.data == f'passenger_Num{i}':
                passenger_case_datetime = parse_custom_time(passenger_sheet[i][3]).replace(minute=0, second=0, microsecond=0)
                passenger_case_datetime_ahead = passenger_case_datetime - datetime.timedelta(hours = 3)
                passenger_case_launchdate = parse_custom_time(passenger_sheet[i][0]).replace(hour=0, minute=0, second=0, microsecond=0)
                now_date = (datetime_datetime.now() + datetime.timedelta(hours = 8)).replace(hour=0, minute=0, second=0, microsecond=0)
                now_datetime = (datetime_datetime.now() + datetime.timedelta(hours = 8)).replace(minute=0, second=0, microsecond=0)
                # 獲取使用者 user_ID  
                passenger_user_id = event.source.user_id
                if passenger_sheet[i][18] == '':
                    passenger_driver = '無'
                else:
                    passenger_driver = passenger_sheet[i][18]
                with ApiClient(configuration) as api_client:
                    line_bot_api = MessagingApi(api_client)
                    if passenger_case_datetime_ahead >= now_datetime or passenger_sheet[i][17] == '是' and passenger_case_datetime >= now_date:
                        confirm_template = ConfirmTemplate(
                            text = f'📎共乘編號：{passenger_sheet[i][16]}\n📍出發地點：{passenger_sheet[i][2]}\n📍目的地點：{passenger_sheet[i][4]}\n🕒出發時間：\n{passenger_sheet[i][3]}\n⏳預估時程：{time_hrmi(int(passenger_sheet[i][6]))}\n#️⃣共乘上限：{passenger_sheet[i][5]} 人\n✨發起人（乘客）：\n{passenger_sheet[i][9]}\n🚗司機名稱：{passenger_driver}\n🛞交通工具：{passenger_sheet[i][11]}\n❗️行車規範：\n{passenger_sheet[i][7]}\n💬備註：\n{passenger_sheet[i][8]}\n',
                            actions=[ #一定只能放兩個Action
                                PostbackAction(label='我要共乘！', text='我要共乘！', data=f'passenger_Sure{i}'),
                                PostbackAction(label='我想當司機！', text='我想當司機！', data=f'passenger_bedriver{i}')   
                            ]
                        )
                        template_message = TemplateMessage(
                            alt_text = f'從{passenger_sheet[i][2]}到{passenger_sheet[i][4]}的詳細資訊',
                            template = confirm_template
                        )
                        line_bot_api.push_message(
                            PushMessageRequest(
                                to=passenger_user_id,
                                messages = [template_message]
                            )
                        )
                    else:
                        line_bot_api.push_message(
                            PushMessageRequest(
                                to=passenger_user_id,
                                messages = [TextMessage(text=f'報名已經截止囉！時間未到的話也可嘗試聯絡活動發起人。\n發起人（乘客）名稱：\n{passenger_sheet[i][9]}\nLineID：{passenger_sheet[i][10]}\n手機號碼：{passenger_sheet[i][12]}\n司機名稱：{passenger_driver}')]
                            )
                        )
            elif event.postback.data == f'passenger_Sure{i}':
                target_row = passenger_sheet_id.row_values(i+1)
                with passenger_lock:
                    with ApiClient(configuration) as api_client:
                        line_bot_api = MessagingApi(api_client)
                        # 獲取使用者 user_ID  
                        passenger_user_id = event.source.user_id
                        if passenger_sheet[i][18] == '':
                            passenger_driver = '無'
                        else:
                            passenger_driver = passenger_sheet[i][18]
                        if target_row[13] != target_row[5]:
                            # 獲取使用者資料
                            profile = line_bot_api.get_profile(passenger_user_id)
                            # 獲取使用者名稱
                            passenger_Sure_name=profile.display_name
                            passenger_user_id_check = ''
                            #-----------------------------------------------------
                            if passenger_user_id in target_row[14]:
                                passenger_user_id_check = 'Checked'
                                line_bot_api.push_message(
                                    PushMessageRequest(
                                        to=passenger_user_id,
                                        messages = [TextMessage(text='您已預約')]
                                    )
                                )
                                break
                            else:
                                pass
                            if passenger_user_id_check != 'Checked' and passenger_Sure_name not in target_row[18]:
                                line_bot_api.push_message(
                                    PushMessageRequest(
                                        to=passenger_user_id,
                                        messages = [TextMessage(text=f'已幫您預約為乘客，記得透過LineID聯繫活動發起人!\n發起人（乘客）名稱：\n{target_row[9]}\nLineID：{target_row[10]}\n手機號碼：{target_row[12]}\n司機名稱：{passenger_driver}')]
                                    )
                                )
                                try :
                                    int(target_row[13])
                                except ValueError:
                                    target_row[13]=0
                                if target_row[14] == '':
                                    new_id = passenger_user_id
                                    new_name = passenger_Sure_name
                                else:
                                    id = target_row[14]
                                    new_id = id+','+passenger_user_id
                                    name = target_row[15]
                                    new_name = name+','+passenger_Sure_name
                                passenger_sheet_id.update([[int(target_row[13])+1, new_id, new_name]], f'N{i+1}:P{i+1}')
                                get_passenger_sheet_case()
                            elif passenger_Sure_name in target_row[18]:
                                line_bot_api.push_message(
                                    PushMessageRequest(
                                        to=passenger_user_id,
                                        messages=[TextMessage(text='您已預約為司機！')]
                                    )
                                )
                            else:
                                pass
                        else:
                            line_bot_api.push_message(
                                PushMessageRequest(
                                    to=passenger_user_id,
                                    messages=[TextMessage(text='此活動人數已滿')]
                                )
                            )
            elif event.postback.data == f'passenger_bedriver{i}':  
                target_row = passenger_sheet_id.row_values(i+1)
                with passenger_lock:
                    with ApiClient(configuration) as api_client:
                        line_bot_api = MessagingApi(api_client)
                        # 獲取使用者 user_ID
                        passenger_user_id = event.source.user_id
                        # 獲取使用者資料
                        profile = line_bot_api.get_profile(passenger_user_id)
                        # 獲取使用者名稱        
                        passenger_Sure_name = profile.display_name
                        if target_row[18] == '' and passenger_Sure_name not in target_row[15]:
                            line_bot_api.push_message(
                                PushMessageRequest(
                                    to=passenger_user_id,
                                    messages = [TextMessage(text=f'已幫您預約為司機，記得透過LineID聯繫活動發起人!\n發起人（乘客）名稱：\n{passenger_sheet[i][9]}\nLineID：{target_row[10]}\n手機號碼：{target_row[12]}')]
                                )
                            )
                            passenger_sheet_id.update([[passenger_Sure_name, passenger_user_id]], f'S{i+1}:T{i+1}')     
                            get_passenger_sheet_case()
                        elif passenger_Sure_name in target_row[15]:
                            line_bot_api.push_message(
                                PushMessageRequest(
                                    to=passenger_user_id,
                                    messages = [TextMessage(text='您已預約為乘客！')]
                                )
                            )    
                        else:
                            line_bot_api.push_message(
                                PushMessageRequest(
                                    to=passenger_user_id,
                                    messages = [TextMessage(text='此活動已有司機囉！')]
                                )
                            )
            elif event.postback.data == f"passenger_template_detail_info{i}":
                # 獲取使用者 user_ID
                passenger_user_id = event.source.user_id
                with ApiClient(configuration) as api_client:
                    line_bot_api = MessagingApi(api_client)
                    if passenger_sheet[i][18] == '':
                        passenger_driver = '無'
                    else:
                        passenger_driver = passenger_sheet[i][18]
                    reservation = f'📎共乘編號：{passenger_sheet[i][16]}\n📍出發地點：{passenger_sheet[i][2]}\n📍目的地點：{passenger_sheet[i][4]}\n🕒出發時間：\n{passenger_sheet[i][3]}\n⏳預估時程：{time_hrmi(int(passenger_sheet[i][6]))}\n#️⃣共乘上限：{passenger_sheet[i][5]} 人\n✨發起人（乘客）：\n{passenger_sheet[i][9]}\n🆔LineID：{passenger_sheet[i][10]}\n📱手機號碼：{passenger_sheet[i][12]}\n🚗司機名稱：{passenger_driver}\n🛞交通工具：{passenger_sheet[i][11]}\n❗️行車規範：\n{passenger_sheet[i][7]}\n💬備註：\n{passenger_sheet[i][8]}\n'
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages = [TextMessage(text=reservation)]
                        )
                    )
            elif event.postback.data == f"passenger_cancel_Num{i}":
                target_row = passenger_sheet_id.row_values(i+1)
                # 獲取使用者 user_ID
                passenger_user_id = event.source.user_id
                with passenger_lock:
                    with ApiClient(configuration) as api_client:
                        line_bot_api = MessagingApi(api_client)
                        # 獲取使用者資料
                        profile = line_bot_api.get_profile(passenger_user_id)
                        # 獲取使用者名稱        
                        passenger_Sure_name=profile.display_name
                        if passenger_user_id in target_row[14]:
                            line_bot_api.reply_message(
                                ReplyMessageRequest(
                                    reply_token=event.reply_token,
                                    messages = [TextMessage(text=f'已幫您取消共乘編號：{target_row[16]}的乘客預約')]
                                )
                            )
                            # 刪除 UserID 紀錄
                            id = target_row[14].split(',')
                            target_position = id.index(passenger_user_id)
                            del id[target_position]
                            deled_id = ','.join(id)
                            # 刪除 User名稱 紀錄
                            name = target_row[15].split(',')
                            del name[target_position]
                            deled_name = ','.join(name)
                            passenger_sheet_id.update([[int(target_row[13])-1, deled_id, deled_name]], f'N{i+1}:P{i+1}')
                            get_passenger_sheet_case()
                        else:
                            line_bot_api.reply_message(
                                ReplyMessageRequest(
                                    reply_token=event.reply_token,
                                    messages = [TextMessage(text='您尚未預約')]
                                )
                            )
            elif event.postback.data == f"passenger_cancel_bedriver_Num{i}":
                target_row = passenger_sheet_id.row_values(i+1)
                # 獲取使用者 user_ID
                passenger_user_id = event.source.user_id
                with passenger_lock:
                    with ApiClient(configuration) as api_client:
                        line_bot_api = MessagingApi(api_client)
                        # 獲取使用者資料
                        profile = line_bot_api.get_profile(passenger_user_id)
                        # 獲取使用者名稱        
                        passenger_Sure_name=profile.display_name
                        if passenger_user_id in target_row[19]:
                            line_bot_api.reply_message(
                                ReplyMessageRequest(
                                    reply_token=event.reply_token,
                                    messages = [TextMessage(text=f'已幫您取消共乘編號：{target_row[16]}的司機預約')]
                                )
                            )
                            # 刪除 UserID、司機name 紀錄
                            passenger_sheet_id.update([['', '']], f'S{i+1}:T{i+1}')
                            get_passenger_sheet_case()
                        else:
                            line_bot_api.reply_message(
                                ReplyMessageRequest(
                                    reply_token=event.reply_token,
                                    messages = [TextMessage(text='您尚未預約')]
                                )
                            )
            else:
                pass
    except NameError:
        pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # 從環境變數 PORT 獲取埠位，預設為 10000
    app.run(host="0.0.0.0", port=port)
