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
import linecache
import gspread #寫入google sheet的函數
def time_hrmi(time):
    hr=int(time/60)
    mi=int(time%60)
    if hr == 0:
        return f'{mi}分鐘'
    elif mi == 0:
        return f'{hr}小時'
    else:
        return f'{hr}小時{mi}分鐘' 
# 使用schedule及threading函數來每隔0.1秒檢查試算表的表單情況
import smtplib
from email.mime.text import MIMEText
import schedule
import time
import threading
#   因為json讀取google sheet的時間格式會錯誤，因此引入函數做矯正
from datetime import datetime 
from datetime import date
from datetime import timezone
import pytz
# 解析含中文上午/下午的時間字符串為 datetime 對象
def parse_custom_time(time_str):
    """解析含中文上午/下午的時間字符串為 datetime 對象"""
    parts = time_str.split()
    date_part = parts[0]
    ampm = parts[1]
    time_part = parts[2]
    # 轉換中文上午/下午為 AM/PM
    ampm_en = "AM" if ampm == "上午" else "PM"
    # 合併為可解析的字符串
    datetime_str = f"{date_part} {time_part} {ampm_en}"
    return datetime.strptime(datetime_str, "%Y/%m/%d %I:%M:%S %p")
# 獲得dict內的value
dict= {1: 'Ufdd0787ca7bc63b64665cdb9a95fd477,Ufdd0787ca7bc63b64665cdb9a95fd477', 2: ''}
def get_key(dict, target):
    number_list = []
    for i in range(len(dict)):
        if str(target) in dict[i+1]:
            number_list.append(i+1)
        else:
            pass
    return(number_list)
#   token.json的資料如放在公開伺服器上執行之類的，會遭停用，需到google cloud重新建立金鑰，否則會跳出JWP錯誤
import tempfile
import os
from dotenv import load_dotenv
load_dotenv()
# 從環境變數讀取 JSON 字串，否則env只能傳入string，且env檔須調整為單行。
credentials_str = os.getenv('GOOGLE_CREDENTIALS')
if credentials_str:
    credentials_dict = json.loads(credentials_str)
# 使用修正後的字典創建 gspread 客戶端
gc = gspread.service_account_from_dict(credentials_dict)
carpool = gc.open_by_url('https://docs.google.com/spreadsheets/d/1q8HKO2NBz1O8UBE7ag9Kq-eNAc114TKzkXyOq32vfSA/edit?gid=1437248658#gid=1437248658')
driver_sheet_id = carpool.get_worksheet(0)
passenger_sheet_id = carpool.get_worksheet(1)
# 獲取 GoogleSheet 的司機、揪團試算表，並讓其變list
driver_sheet = driver_sheet_id.get_all_values()
passenger_sheet = passenger_sheet_id.get_all_values()
# 初始化追踪字典，為每個索引設置False
web_driver_Sure = set()
web_passenger_Sure = set()
def check_project():
    global web_driver_Sure, web_passenger_Sure
    print(f"目前已處理的司機: {web_driver_Sure}")
    print(f"目前已處理的乘客: {web_passenger_Sure}")
    for i in range(1,web_driver_len):
        driver_case_datetime = parse_custom_time(driver_sheet[i][3])
        driver_case_date = driver_case_datetime.strftime("%Y-%m-%d")
        now_datetime = datetime.now()
        now_date = now_datetime.strftime("%Y-%m-%d")
        if i not in web_driver_Sure:
            if driver_case_date == now_date:
                # 有人且已滿
                if int(driver_sheet[i][14])== int(driver_sheet[i][5]):
                    # 寄信給發起人，告知結果
                    name_list = driver_Sure_name_dict.get(i).split(',')
                    output = '、'.join(map(str, name_list))
                    str1 = '您在 共乘阿穿 發起的（有司機）共乘活動人數已滿了，活動資訊如下：'
                    str2 = f'共乘編號：{driver_sheet[i][17]}<br>發車地點：{driver_sheet[i][2]}<br>目的地：{driver_sheet[i][4]}<br>出發時間：<br>{driver_sheet[i][3]}<br>總時程：{time_hrmi(int(driver_sheet[i][6]))}<br>發起人：{driver_sheet[i][9]}<br>手機號碼：{driver_sheet[i][13]}<br>LineID：{driver_sheet[i][10]}<br>共乘人數上限：{driver_sheet[i][5]}<br>價格：{driver_sheet[i][11]}<br>交通工具：{driver_sheet[i][12]}<br>行車規範：<br>{driver_sheet[i][7]}<br>簡介：<br>{driver_sheet[i][8]}<br>'
                    str3 = f'參與者Line名稱:{output}'
                    str4 = '您在 共乘阿穿 發起的（有司機）共乘活動人數已滿囉'
                    # 針對 Linebot 參與的乘客
                    driver_text = f'您參加的（有司機）共乘活動成團囉，記得透過LineID聯繫活動發起人!發起人LineID：{driver_sheet[i][10]}，活動資訊如下：\n--------------------------------\n共乘編號：{driver_sheet[i][17]}\n發車地點：{driver_sheet[i][2]}\n目的地：{driver_sheet[i][4]}\n出發時間：\n{driver_sheet[i][3]}\n總時程：{time_hrmi(int(driver_sheet[i][6]))}\n發起人：{driver_sheet[i][9]}\n手機號碼：{driver_sheet[i][13]}\nLineID：{driver_sheet[i][10]}\n共乘人數上限：{driver_sheet[i][5]}\n價格：{driver_sheet[i][11]}\n交通工具：{driver_sheet[i][12]}\n行車規範：\n{driver_sheet[i][7]}\n簡介：\n{driver_sheet[i][8]}\n'
                # 有人且發起者未勾選 ※ 人滿才發車
                elif '※ 人滿才發車' not in driver_sheet[i][7] and int(driver_sheet[i][14])>0:
                    # 寄信給發起人，告知結果
                    name_list = driver_Sure_name_dict.get(i).split(',')
                    output = '、'.join(map(str, name_list))
                    str1 = '您在 共乘阿穿 發起的（司機揪團）共乘活動人數未滿，但您未勾選「人滿才發車」，因此成團喔！活動資訊如下：'
                    str2 = f'共乘編號：{driver_sheet[i][17]}<br>發車地點：{driver_sheet[i][2]}<br>目的地：{driver_sheet[i][4]}<br>出發時間：<br>{driver_sheet[i][3]}<br>總時程：{time_hrmi(int(driver_sheet[i][6]))}<br>發起人：{driver_sheet[i][9]}<br>手機號碼：{driver_sheet[i][13]}<br>LineID：{driver_sheet[i][10]}<br>共乘人數上限：{driver_sheet[i][5]}<br>價格：{driver_sheet[i][11]}<br>交通工具：{driver_sheet[i][12]}<br>行車規範：<br>{driver_sheet[i][7]}<br>簡介：<br>{driver_sheet[i][8]}<br>'
                    str3 = f'參與者Line名稱:{output}'
                    str4 = '您在 共乘阿穿 發起的（司機揪團）共乘活動人數未滿，但您未勾選「人滿才發車」，因此成團喔！'
                    # 針對 Linebot 參與的乘客
                    driver_text = f'您參加的（司機揪團）共乘活動成團囉，記得透過LineID聯繫活動發起人!發起人LineID：{driver_sheet[i][10]}，活動資訊如下：\n--------------------------------\n共乘編號：{driver_sheet[i][17]}\n發車地點：{driver_sheet[i][2]}\n目的地：{driver_sheet[i][4]}\n出發時間：\n{driver_sheet[i][3]}\n總時程：{time_hrmi(int(driver_sheet[i][6]))}\n發起人：{driver_sheet[i][9]}\n手機號碼：{driver_sheet[i][13]}\nLineID：{driver_sheet[i][10]}\n共乘人數上限：{driver_sheet[i][5]}\n價格：{driver_sheet[i][11]}\n交通工具：{driver_sheet[i][12]}\n行車規範：{driver_sheet[i][7]}\n簡介：\n{driver_sheet[i][8]}\n'
                # 未成團
                else:
                    # 寄信給發起人，告知結果
                    str1 = f'您在 共乘阿穿 發起的（司機揪團）共乘活動人數未滿，共乘編號為{driver_sheet[i][17]}，因此未發車。活動資訊如下：'
                    str2 = f'共乘編號：{driver_sheet[i][17]}<br>發車地點：{driver_sheet[i][2]}<br>目的地：{driver_sheet[i][4]}<br>出發時間：<br>{driver_sheet[i][3]}<br>總時程：{time_hrmi(int(driver_sheet[i][6]))}<br>發起人：{driver_sheet[i][9]}<br>手機號碼：{driver_sheet[i][13]}<br>LineID：{driver_sheet[i][10]}<br>共乘人數上限：{driver_sheet[i][5]}<br>價格：{driver_sheet[i][11]}<br>交通工具：{driver_sheet[i][12]}<br>行車規範：<br>{driver_sheet[i][7]}<br>簡介：<br>{driver_sheet[i][8]}<br>'
                    str3 = ''
                    str4 = '您在 共乘阿穿 發起的（司機揪團）共乘活動人數未滿'
                    # 針對 Linebot 參與的乘客
                    driver_text = f'您參與的（司機揪團）共乘活動因人數未滿而不發車喔!共乘編號為{driver_sheet[i][17]}'
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
        passenger_case_datetime = parse_custom_time(passenger_sheet[i][3])
        passenger_case_date = passenger_case_datetime.strftime("%Y-%m-%d")
        now_datetime = datetime.now()
        now_date = now_datetime.strftime("%Y-%m-%d")
        if i not in web_passenger_Sure :
            if passenger_case_date == now_date:
                # 有人且已滿
                if int(passenger_sheet[i][13])== int(passenger_sheet[i][5]):
                    name_list = passenger_Sure_name_dict.get(i).split(',')
                    output = '、'.join(map(str, name_list))
                    str1 = '您在 共乘阿穿 發起的（乘客揪團）共乘活動人數已滿了，活動資訊如下：'
                    str2 = f'共乘編號：{passenger_sheet[i][16]}<br>發車地點：{passenger_sheet[i][2]}<br>目的地：{passenger_sheet[i][4]}<br>出發時間：<br>{passenger_sheet[i][3]}<br>總時程：{time_hrmi(int(passenger_sheet[i][6]))}<br>發起人：{passenger_sheet[i][9]}<br>手機號碼：{passenger_sheet[i][12]}<br>LineID：{passenger_sheet[i][10]}<br>共乘人數上限：{passenger_sheet[i][5]}<br>交通工具：{passenger_sheet[i][11]}行車規範：<br>{passenger_sheet[i][7]}\n簡介：\n{passenger_sheet[i][8]}<br>'
                    str3 = f'參與者Line名稱:{output}'
                    str4 = '您在 共乘阿穿 發起的（乘客揪團）共乘活動人數已滿囉'
                    # 針對 Linebot 參與的乘客
                    passenger_text = f'您參加的（乘客揪團）共乘活動成團囉，記得透過LineID聯繫活動發起人!發起人LineID：{passenger_sheet[i][10]}，活動資訊如下：\n--------------------------------\n共乘編號：{passenger_sheet[i][16]}\n發車地點：{passenger_sheet[i][2]}\n目的地：{passenger_sheet[i][4]}\n出發時間：\n{passenger_sheet[i][3]}\n總時程：{time_hrmi(int(passenger_sheet[i][6]))}\n發起人：{passenger_sheet[i][9]}\n手機號碼：{passenger_sheet[i][12]}\nLineID：{passenger_sheet[i][10]}\n共乘人數上限：{passenger_sheet[i][5]}\n交通工具：{passenger_sheet[i][11]}行車規範：\n{passenger_sheet[i][7]}\n簡介：{passenger_sheet[i][8]}\n'
                # 有人且發起者未勾選 ※ 人滿才發車
                elif '※ 人滿才發車' not in passenger_sheet[i][7] and int(passenger_sheet[i][13])>0:
                    # 寄信給發起人，告知結果
                    name_list = passenger_Sure_name_dict.get(i).split(',')
                    output = '、'.join(map(str, name_list))
                    str1 = '您在 共乘阿穿 發起的（乘客揪團）共乘活動人數未滿，但您未勾選「人滿才發車」，因此成團喔！活動資訊如下：'
                    str2 = f'共乘編號：{passenger_sheet[i][16]}<br>發車地點：{passenger_sheet[i][2]}<br>目的地：{passenger_sheet[i][4]}<br>出發時間：<br>{passenger_sheet[i][3]}<br>總時程：{time_hrmi(int(passenger_sheet[i][6]))}<br>發起人：{passenger_sheet[i][9]}<br>手機號碼：{passenger_sheet[i][12]}<br>LineID：{passenger_sheet[i][10]}<br>共乘人數上限：{passenger_sheet[i][5]}<br>交通工具：{passenger_sheet[i][11]}<br>行車規範：<br>{passenger_sheet[i][7]}\n簡介：<br>{passenger_sheet[i][8]}<br>'
                    str3 = f'參與者Line名稱:{output}'
                    str4 = '您在 共乘阿穿 發起的（乘客揪團）共乘活動人數未滿，但您未勾選「人滿才發車」，因此成團喔！'
                    # 針對 Linebot 參與的乘客
                    passenger_text = f'您參加的（乘客揪團）共乘活動成團囉，記得透過LineID聯繫活動發起人!發起人LineID：{passenger_sheet[i][10]}，活動資訊如下：\n--------------------------------\n共乘編號：{passenger_sheet[i][16]}\n發車地點：{passenger_sheet[i][2]}\n目的地：{passenger_sheet[i][4]}\n出發時間：\n{passenger_sheet[i][3]}\n總時程：{time_hrmi(int(passenger_sheet[i][6]))}\n發起人：{passenger_sheet[i][9]}\n手機號碼：{passenger_sheet[i][12]}\nLineID：{passenger_sheet[i][10]}\n共乘人數上限：{passenger_sheet[i][5]}\n交通工具：{passenger_sheet[i][11]}\n行車規範：\n{passenger_sheet[i][7]}\n簡介：{passenger_sheet[i][8]}\n'
                # 未成團
                else:
                    # 寄信給發起人，告知結果    
                    str1 = f'您在 共乘阿穿 發起的（乘客揪團）共乘活動人數未滿，共乘編號為{passenger_sheet[i][16]}，因此未發車。活動資訊如下：'
                    str2 = f'共乘編號：{passenger_sheet[i][16]}<br>發車地點：{passenger_sheet[i][2]}<br>目的地：{passenger_sheet[i][4]}<ber>出發時間：<br>{passenger_sheet[i][3]}<br>總時程：{time_hrmi(int(passenger_sheet[i][6]))}<br>發起人：{passenger_sheet[i][9]}<br>手機號碼：{passenger_sheet[i][12]}<br>LineID：{passenger_sheet[i][10]}<br>共乘人數上限：{passenger_sheet[i][5]}<br>交通工具：{passenger_sheet[i][11]}<br>行車規範：<br>{passenger_sheet[i][7]}\n簡介：{passenger_sheet[i][8]}<br>'
                    str3 = ''
                    str4 = '您在 共乘阿穿 發起的（乘客揪團）共乘活動人數未滿'
                    # 針對 Linebot 參與的乘客
                    passenger_text = f'您參與的（乘客揪團）共乘活動因人數未滿而不發車喔!共乘編號為{passenger_sheet[i][16]}'
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
def get_driver_sheet_case():
    global driver_sheet, web_driver_len, driver_Sure_id_dict, driver_Sure_name_dict
    driver_sheet = driver_sheet_id.get_all_values()
    try:
        web_driver_len=len(driver_sheet) #抓取司機表單中有幾筆資料(已藉由更改其App script的程式碼扣除第一列的項目)
    except requests.exceptions.JSONDecodeError:
        web_driver_len = 0
    try:
        # 設定一個司機發起的活動dict容納確定參與的使用者
        driver_Sure_id_dict = {}
        driver_Sure_name_dict = {}
        for i in range(1,web_driver_len):
            driver_Sure_id_dict[i] = driver_sheet[i][15]
            driver_Sure_name_dict[i] = driver_sheet[i][16]
            if driver_sheet_id.cell(i+1,18).value == None:
                driver_sheet_id.update_cell(i+1,15,0)
                driver_sheet_id.update_cell(i+1,18,i+1)
        print('司機發起之活動已抓取')
        print(driver_Sure_id_dict)
    except:
        print('司機發起之活動尚無資料')   
def get_passenger_sheet_case():
    global passenger_sheet, web_passenger_len, passenger_Sure_id_dict, passenger_Sure_name_dict
    passenger_sheet = passenger_sheet_id.get_all_values()
    try:
        web_passenger_len=len(passenger_sheet) #抓取司機表單中有幾筆資料(已藉由更改其App script的程式碼扣除第一列的項目)
    except requests.exceptions.JSONDecodeError:
        web_passenger_len = 0
    try:
        # 設定一個揪團的dict容納確定參與的使用者
        passenger_Sure_id_dict = {}
        passenger_Sure_name_dict = {}
        for i in range(1,web_passenger_len):
            passenger_Sure_id_dict[i] = passenger_sheet[i][14]
            passenger_Sure_name_dict[i] = passenger_sheet[i][15]
            if passenger_sheet_id.cell(i+1,17).value == None:
                passenger_sheet_id.update_cell(i+1,14,0)
                passenger_sheet_id.update_cell(i+1,17,i+1)
            else:
                pass
        print('乘客發起之揪團活動已抓取')
        print(passenger_Sure_id_dict)
    except:
        print('乘客發起之揪團活動尚無資料')
#   每隔3秒檢查試算表內容，若人數達上限即通知活動發起者人數已滿
def run_scheduler():
    global a
    a = True
    while a:
        schedule.run_pending()
        time.sleep(0.1)  
schedule.every(30).minutes.do(check_project)
schedule.every(30).seconds.do(get_driver_sheet_case)
schedule.every(30).seconds.do(get_passenger_sheet_case)
scheduler_thread_case = threading.Thread(target=run_scheduler)
scheduler_thread_case.daemon = True  # 主程式結束此也結束
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
                    driver_case_datetime = parse_custom_time(driver_sheet[i][3])
                    driver_case_date = driver_case_datetime.strftime("%Y-%m-%d")
                    now_datetime = datetime.now()
                    now_date = now_datetime.strftime("%Y-%m-%d")
                    if driver_case_date>=now_date:
                        try :
                            int(driver_sheet[i][14])
                            pass
                        except ValueError:
                            driver_sheet[i][14]=0
                        if int(driver_sheet[i][14]) < int(driver_sheet[i][5]) or int(driver_sheet[i][14])== 0:
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
                                        "text": f"發起人：{driver_sheet[i][9]}",
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
                                        "text": f"價格：{driver_sheet[i][11]}",
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
                                    "backgroundColor": "#0367D3",
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
                                        "text": f"簡介：{driver_sheet[i][8]}",
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
                                        "label": "我想共乘!",
                                        "data": f"driver_Num{i}",
                                        "displayText": f"我想共乘{driver_sheet[i][2]}到{driver_sheet[i][4]}!"
                                        },
                                        "style": "secondary"
                                    }
                                    ]
                                }
                            }
                            # 新增規範
                            if '上下車地點可討論' in driver_sheet[i][7]:
                                r = {
                                            "type": "text",
                                            "text": "上下車地點可討論",
                                            "size": "sm",
                                            "margin": "none",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_driver_data_case['body']['contents'].insert(2,r)
                            if '自備零錢不找零' in driver_sheet[i][7]:
                                r = {
                                            "type": "text",
                                            "text": "自備零錢不找零",
                                            "size": "sm",
                                            "margin": "none",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_driver_data_case['body']['contents'].insert(2,r)
                            if '接受線上付款 / 轉帳' in driver_sheet[i][7]:
                                r = {
                                            "type": "text",
                                            "text": "接受線上付款 / 轉帳",
                                            "size": "sm",
                                            "margin": "none",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_driver_data_case['body']['contents'].insert(2,r)
                            if '禁食' in driver_sheet[i][7]:
                                r = {
                                            "type": "text",
                                            "text": "禁食",
                                            "size": "sm",
                                            "margin": "none",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_driver_data_case['body']['contents'].insert(2,r)
                            if '※ 人滿才發車' in driver_sheet[i][7]:
                                r = {
                                            "type": "text",
                                            "text": "※ 人滿才發車",
                                            "size": "sm",
                                            "margin": "none",
                                            "color": "#ff5551",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_driver_data_case['body']['contents'].insert(2,r)
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
                            messages=[FlexMessage(alt_text='目前有的共乘(已有司機)', contents=FlexContainer.from_json(line_flex_str))]
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
                    passenger_case_datetime = parse_custom_time(passenger_sheet[i][3])
                    passenger_case_date = passenger_case_datetime.strftime("%Y-%m-%d")
                    now_datetime = datetime.now()
                    now_date = now_datetime.strftime("%Y-%m-%d")
                    if passenger_case_date>=now_date:
                        try :
                            int(passenger_sheet[i][13])
                        except ValueError:
                            passenger_sheet[i][13]=0
                        if int(passenger_sheet[i][13]) < int(passenger_sheet[i][5]) or int(passenger_sheet[i][13])== 0:
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
                                        "text": f"總時程：{time_hrmi(int(passenger_sheet[i][6]))}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"發起人：{passenger_sheet[i][9]}",
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
                                    "backgroundColor": "#0367D3",
                                    "spacing": "md",
                                    "height": "275px",
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
                                        "text": f"簡介：{passenger_sheet[i][8]}",
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
                                        "label": "我想共乘!",
                                        "data": f"passenger_Num{i}",
                                        "displayText": f"我想共乘{passenger_sheet[i][2]}到{passenger_sheet[i][4]}!"
                                        },
                                        "style": "secondary"
                                    }
                                    ]
                                }
                                }
                            # 新增規範
                            if '上下車地點可討論' in passenger_sheet[i][7]:
                                r = {
                                            "type": "text",
                                            "text": "上下車地點可討論",
                                            "size": "sm",
                                            "margin": "none",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_passenger_data_case['body']['contents'].insert(2,r)
                            if '不聊天' in passenger_sheet[i][7]:
                                r = {
                                            "type": "text",
                                            "text": "不聊天",
                                            "size": "sm",
                                            "margin": "none",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_passenger_data_case['body']['contents'].insert(2,r)
                            if '嚴禁喝酒及抽菸' in passenger_sheet[i][7]:
                                r = {
                                            "type": "text",
                                            "text": "嚴禁喝酒及抽菸",
                                            "size": "sm",
                                            "margin": "none",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_passenger_data_case['body']['contents'].insert(2,r)
                            if '禁食' in passenger_sheet[i][7]:
                                r = {
                                            "type": "text",
                                            "text": "禁食",
                                            "size": "sm",
                                            "margin": "none",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_passenger_data_case['body']['contents'].insert(3,r)
                            if '謝絕寵物' in passenger_sheet[i][7]:
                                r = {
                                            "type": "text",
                                            "text": "謝絕寵物",
                                            "size": "sm",
                                            "margin": "none",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_passenger_data_case['body']['contents'].insert(2,r)
                            if '寵物需裝籠' in passenger_sheet[i][7]:
                                r = {
                                            "type": "text",
                                            "text": "寵物需裝籠",
                                            "size": "sm",
                                            "margin": "none",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_passenger_data_case['body']['contents'].insert(2,r)
                            if '※ 人滿才發車' in passenger_sheet[i][7]:
                                r = {
                                            "type": "text",
                                            "text": "※ 人滿才發車",
                                            "size": "sm",
                                            "margin": "none",
                                            "color": "#ff5551",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_passenger_data_case['body']['contents'].insert(2,r)
                            if '已有司機' in passenger_sheet[i][7]:
                                r = {
                                            "type": "text",
                                            "text": "已有司機",
                                            "size": "sm",
                                            "margin": "none",
                                            "color": "#ff5551",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_passenger_data_case['body']['contents'].insert(2,r)
                            if '尚未有司機（徵求司機！）' in passenger_sheet[i][7]:
                                r = {
                                            "type": "text",
                                            "text": "尚未有司機（徵求司機！）",
                                            "size": "sm",
                                            "margin": "none",
                                            "color": "#ff5551",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_passenger_data_case['body']['contents'].insert(2,r)    
                            if '叫車分攤費用' in passenger_sheet[i][7]:
                                r = {
                                            "type": "text",
                                            "text": "叫車分攤費用",
                                            "size": "sm",
                                            "margin": "none",
                                            "color": "#ff5551",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_passenger_data_case['body']['contents'].insert(2,r) 
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
                            messages=[FlexMessage(alt_text='目前有的共乘(揪團)', contents=FlexContainer.from_json(line_flex_str))]
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
            # 獲取使用者 user_ID 
            user_id = event.source.user_id
            text = ''
            driver_text = ''
            now_datetime = datetime.now()
            now_date = now_datetime.strftime("%Y-%m-%d")
            if user_id in str(driver_Sure_id_dict.values()): # dict_value type 不能用 str in 的判斷式
                reservation_case = get_key(driver_Sure_id_dict,str(user_id))
                for i in reservation_case:
                    driver_case_datetime = parse_custom_time(driver_sheet[i][3])
                    driver_case_date = driver_case_datetime.strftime("%Y-%m-%d")
                    if driver_case_date >= now_date:
                        reservation = f'共乘編號：{driver_sheet[i][17]}\n發車地點：{driver_sheet[i][2]}\n目的地：{driver_sheet[i][4]}\n出發時間：\n{driver_sheet[i][3]}\n總時程：{time_hrmi(int(driver_sheet[i][6]))}\n發起人：{driver_sheet[i][9]}\n手機號碼：{driver_sheet[i][13]}\nLineID：{driver_sheet[i][10]}\n共乘人數上限：{driver_sheet[i][5]}\n價格：{driver_sheet[i][11]}\n交通工具：{driver_sheet[i][12]}\n行車規範：\n{driver_sheet[i][7]}\n簡介：{driver_sheet[i][8]}\n'
                        driver_text = driver_text+reservation+'--------------------------------\n'
                    else:
                        pass
            else:
                pass
            if driver_text != '':
                text = '司機（揪團）預約：\n'+driver_text      
            else:
                pass 
            passenger_text = '乘客（揪團）預約：\n'  
            if user_id in str(passenger_Sure_id_dict.values()): # dict_value type 不能用 str in 的判斷式
                reservation_case = get_key(passenger_Sure_id_dict,str(user_id))
                for i in reservation_case:
                    passenger_case_datetime = parse_custom_time(passenger_sheet[i][3])
                    passenger_case_date = passenger_case_datetime.strftime("%Y-%m-%d")
                    if passenger_case_date>= now_date:
                        reservation = f'共乘編號：{passenger_sheet[i][16]}\n發車地點：{passenger_sheet[i][2]}\n目的地：{passenger_sheet[i][4]}\n出發時間：\n{passenger_sheet[i][3]}\n總時程：{time_hrmi(int(passenger_sheet[i][6]))}\n發起人：{passenger_sheet[i][9]}\n手機號碼：{passenger_sheet[i][12]}\nLineID：{passenger_sheet[i][10]}\n共乘人數上限：{passenger_sheet[i][5]}\n交通工具：{passenger_sheet[i][11]}行車規範：\n{passenger_sheet[i][7]}\n簡介：{passenger_sheet[i][8]}\n'
                        passenger_text = passenger_text+reservation+'--------------------------------\n'    
                    else:
                        pass 
            else:
                pass
            if passenger_text!= '乘客（揪團）預約：\n':
                text = text + passenger_text
            else:
                pass   
            if text == '':
                text = '您尚未預約任何活動'
            else:
                pass
            line_bot_api.reply_message( #傳送回復訊息
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=text)]
                )
            )
driver_sure_lock = threading.Lock()
passenger_sure_lock = threading.Lock()
@line_handler.add(PostbackEvent)
def handle_postbak(event):
    try:
        for i in range(1,web_driver_len):
            if event.postback.data == f'driver_Num{i}':
                driver_case_datetime = parse_custom_time(driver_sheet[i][3])
                driver_case_date = driver_case_datetime.strftime("%Y-%m-%d")
                now_datetime = datetime.now()
                now_date = now_datetime.strftime("%Y-%m-%d")
                with ApiClient(configuration) as api_client:
                    line_bot_api = MessagingApi(api_client)
                    if driver_case_date>now_date:
                        confirm_template = ConfirmTemplate(
                            text = f'共乘編號：{driver_sheet[i][17]}\n發車地點：{driver_sheet[i][2]}\n目的地：{driver_sheet[i][4]}\n出發時間：\n{driver_sheet[i][3]}\n總時程：{time_hrmi(int(driver_sheet[i][6]))}\n發起人：{driver_sheet[i][9]}\n手機號碼：{driver_sheet[i][13]}\nLineID：{driver_sheet[i][10]}\n共乘人數上限：{driver_sheet[i][5]}\n價格：{driver_sheet[i][11]}\n交通工具：{driver_sheet[i][12]}\n行車規範：\n{driver_sheet[i][7]}\n簡介：{driver_sheet[i][8]}\n',
                            actions=[ #只能放兩個Action
                                PostbackAction(label='確定搭乘', text='確定!',data=f'driver_Sure{i}'),
                                MessageAction(label='再考慮', text='再考慮')
                            ]
                        )
                        template_message = TemplateMessage(
                            alt_text = '是否確認搭乘?',
                            template = confirm_template
                        )
                        line_bot_api.reply_message(
                            ReplyMessageRequest(
                                reply_token = event.reply_token,
                                messages = [template_message]
                            )
                        )
                    else:
                        line_bot_api.reply_message( #傳送'已逾期'回復訊息
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(text='報名已經截止囉！時間未到的話也可嘗試聯絡活動發起人。')] 
                        )  
                    )         
            else:
                pass
            # 使用者在Confirm Template按下確定後，試算表的搭車人數將+1
            if event.postback.data == f'driver_Sure{i}':
                with driver_sure_lock:
                    get_driver_sheet_case()
                    with ApiClient(configuration) as api_client:
                        line_bot_api = MessagingApi(api_client)
                        if int(driver_sheet[i][14]) != driver_sheet[i][5]:
                            # 獲取使用者 user_ID
                            driver_user_id = event.source.user_id
                            profile = line_bot_api.get_profile(driver_user_id)
                            # 獲取使用者名稱
                            driver_Sure_name=profile.display_name           
                            #-----------------------------------------------------
                            if driver_user_id in driver_Sure_id_dict[i]:
                                driver_user_id = 'Checked'
                                line_bot_api.reply_message(
                                    ReplyMessageRequest(
                                        reply_token = event.reply_token,
                                        messages = [TextMessage(text='您已預約')]
                                    )
                                )
                            else:
                                pass
                            if driver_user_id != 'Checked':
                                line_bot_api.reply_message(
                                    ReplyMessageRequest(
                                        reply_token = event.reply_token,
                                        messages = [TextMessage(text='已幫您預約')]
                                    )
                                )
                                try :
                                    int(driver_sheet[i][14])
                                    pass
                                except ValueError:
                                    driver_sheet[i][14]=0
                                driver_sheet_id.update_cell(i+1,15,int(driver_sheet[i][14])+1)
                                if driver_sheet_id.cell(i+1,16).value == None:
                                    new_id = driver_user_id
                                    new_name = driver_Sure_name
                                else:  
                                    id = driver_sheet_id.cell(i+1,16).value
                                    new_id = id+','+driver_user_id
                                    name = driver_sheet_id.cell(i+1,17).value
                                    new_name = name+','+driver_Sure_name
                                driver_sheet_id.update_cell(i+1,16,new_id) 
                                driver_sheet_id.update_cell(i+1,17,new_name)
                        else:
                            line_bot_api.reply_message(
                                ReplyMessageRequest(
                                    reply_token = event.reply_token,
                                    messages = [TextMessage(text='此活動人數已滿')]
                                )
                            )
            else:
                pass
    except NameError:
        pass
    try:
        for i in range(1,web_passenger_len):
            if event.postback.data == f'passenger_Num{i}':
                passenger_case_datetime = parse_custom_time(passenger_sheet[i][3])
                passenger_case_date = passenger_case_datetime.strftime("%Y-%m-%d")
                now_datetime = datetime.now()
                now_date = now_datetime.strftime("%Y-%m-%d")
                with ApiClient(configuration) as api_client:
                    line_bot_api = MessagingApi(api_client)
                    if passenger_case_date > now_date:
                        confirm_template = ConfirmTemplate(
                            text = f'共乘編號：{passenger_sheet[i][16]}\n發車地點：{passenger_sheet[i][2]}\n目的地：{passenger_sheet[i][4]}\n出發時間：\n{passenger_sheet[i][3]}\n總時程：{time_hrmi(int(passenger_sheet[i][6]))}\n發起人：{passenger_sheet[i][9]}\n手機號碼：{passenger_sheet[i][12]}\nLineID：{passenger_sheet[i][10]}\n共乘人數上限：{passenger_sheet[i][5]}\n交通工具：{passenger_sheet[i][11]}行車規範：\n{passenger_sheet[i][7]}\n簡介：{passenger_sheet[i][8]}\n',
                            actions=[ #一定只能放兩個Action
                                PostbackAction(label='確定搭乘', text='確定!', data=f'passenger_Sure{i}'),
                                MessageAction(label='再考慮', text='再考慮')   
                            ]
                        )
                        template_message = TemplateMessage(
                            alt_text = '是否確認搭乘?',
                            template = confirm_template
                        )
                        line_bot_api.reply_message(
                            ReplyMessageRequest(
                                reply_token = event.reply_token,
                                messages = [template_message]
                            )
                        )
                    line_bot_api.reply_message( #傳送'已逾期'回復訊息
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(text='報名已經截止囉！時間未到的話也可嘗試聯絡活動發起人。')] 
                        )  
                    )
            else:
                pass
            # 使用者在Confirm Template按下確定後，試算表的搭車人數將+1
            if event.postback.data == f'passenger_Sure{i}':
                with driver_sure_lock:
                    get_passenger_sheet_case()
                    with ApiClient(configuration) as api_client:
                        line_bot_api = MessagingApi(api_client)
                        if passenger_sheet[i][13] != passenger_sheet[i][5]:
                            # 獲取使用者 user_ID  
                            passenger_user_id = event.source.user_id
                            profile = line_bot_api.get_profile(passenger_user_id)
                            # 獲取使用者名稱
                            passenger_Sure_name=profile.display_name
                            #-----------------------------------------------------
                            if passenger_user_id in passenger_Sure_id_dict[i]:
                                passenger_user_id = 'Checked'
                                line_bot_api.reply_message(
                                    ReplyMessageRequest(
                                        reply_token = event.reply_token,
                                        messages = [TextMessage(text='您已預約')]
                                    )
                                )
                                break
                            else:
                                pass
                            if passenger_user_id != 'Checked':
                                line_bot_api.reply_message(
                                    ReplyMessageRequest(
                                        reply_token = event.reply_token,
                                        messages = [TextMessage(text='已幫您預約')]
                                    )
                                )
                                try :
                                    int(passenger_sheet[i][13])
                                except ValueError:
                                    passenger_sheet[i][13]=0
                                passenger_sheet_id.update_cell(i+1,14,int(passenger_sheet[i][13])+1) #因為dict只能start from 0，因此第一個共乘表單會在第0個，而google sheet第一行又是表單的項目，因此第一張表單會是i+1+1列。
                                if passenger_sheet_id.cell(i+1,15).value == None:
                                    new_id = passenger_user_id
                                    new_name = passenger_Sure_name
                                else:
                                    id = passenger_sheet_id.cell(i+1,15).value
                                    new_id = id+','+passenger_user_id
                                    name = passenger_sheet_id.cell(i+1,16).value
                                    new_name = name+','+passenger_Sure_name
                                passenger_sheet_id.update_cell(i+1,15,new_id)
                                passenger_sheet_id.update_cell(i+1,16,new_name)
                        else:
                            line_bot_api.reply_message(
                                ReplyMessageRequest(
                                    reply_token = event.reply_token,
                                    messages = [TextMessage(text='此活動人數已滿')]
                                )
                            )
            else:
                pass
    except NameError:
        pass
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # 從環境變數 PORT 獲取埠位，預設為 10000
    app.run(host="0.0.0.0", port=port)
