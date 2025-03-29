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
#   讀取google試算表
url = 'https://script.google.com/macros/s/AKfycbyOMg_YtbDdWeIVSYRX5Q32uKGY0ZZSpuWP1AX_1NbjkrFhfe5E82_0ooHez8bfbAuVSA/exec'
driversheet_name = '司機'
passengersheet_name = '揪團'
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
def get_Sheet_time(json_time):
    # 步驟 1：解析 UTC 時間
    time = datetime.strptime(json_time, '%Y-%m-%dT%H:%M:%S.%fZ')
    time = time.replace(tzinfo=pytz.UTC)  # 明確指定時區
    # 步驟 2：轉換為本地時區（例如：台北 UTC+8）
    local_timezone = pytz.timezone('Asia/Taipei')
    local_time = time.astimezone(local_timezone)
    # 步驟 3：格式化輸出（含上午/下午）
    formatted_time = local_time.strftime('%Y/%#m/%#d %p %I:%M:%S').replace('AM', '上午').replace('PM','下午')
    # 輸出：2025/3/18 上午 03:00:00
    return formatted_time
def get_sheet_time_fordatetime(json_time):
    time = datetime.strptime(json_time, '%Y-%m-%dT%H:%M:%S.%fZ')
    time = time.replace(tzinfo=pytz.UTC)
    local_timezone = pytz.timezone('Asia/Taipei')
    local_time = time.astimezone(local_timezone)
    formatted_time = local_time.strftime('%Y/%#m/%#d')
    return formatted_time
def get_driver_sheet_case():
    global web_driver_data, web_driver_len, driver_Sure_id_dict, driver_Sure_name_dict, driver_val
    web_driver_data = requests.get(f'{url}?name={driversheet_name}')
    try:
        web_driver_len=len(web_driver_data.json()) #抓取司機表單中有幾筆資料(已藉由更改其App script的程式碼扣除第一列的項目)
    except requests.exceptions.JSONDecodeError:
        web_driver_len = 0
    try:
        # 設定一個司機發起的活動dict容納確定參與的使用者
        driver_Sure_id_dict = {}
        driver_Sure_name_dict = {}
        for i in range(web_driver_len):
            driver_Sure_id_dict[i] = web_driver_data.json()[i][15]
            driver_Sure_name_dict[i] = web_driver_data.json()[i][16]
            if driver_sheet.cell(i+2,15).value == None:
                driver_sheet.update_cell(i+2,15,0)
                driver_val = 0
            else:
                driver_val = int(driver_sheet.cell(i+2,15).value)
        print(driver_Sure_id_dict)
        print('司機發起之活動已抓取')
    except:
        print('司機發起之活動尚無資料')   
def get_passenger_sheet_case():
    global web_passenger_data, web_passenger_len, passenger_Sure_id_dict, passenger_Sure_name_dict, passenger_val
    web_passenger_data = requests.get(f'{url}?name={passengersheet_name}')
    try:
        web_passenger_len=len(web_passenger_data.json()) #抓取司機表單中有幾筆資料(已藉由更改其App script的程式碼扣除第一列的項目)
    except requests.exceptions.JSONDecodeError:
        web_passenger_len = 0
    try:
        # 設定一個揪團的dict容納確定參與的使用者
        passenger_Sure_id_dict = {}
        passenger_Sure_name_dict = {}
        for i in range(web_passenger_len):
            passenger_Sure_id_dict[i] = web_passenger_data.json()[i][13]
            passenger_Sure_name_dict[i] = web_passenger_data.json()[i][14]
            if passenger_sheet.cell(i+2,13).value == None:
                passenger_sheet.update_cell(i+2,13,0)
                passenger_val = 0
            else:
                passenger_val = int(passenger_sheet.cell(i+2,13).value)
        print(passenger_Sure_id_dict)
        print('乘客發起之揪團活動已抓取')
    except:
        web_passenger_len = 0
        print('乘客發起之揪團活動尚無資料')
def run_scheduler():
    a = True
    while a:
        schedule.run_pending()
        time.sleep(0.1)
schedule.every(3).seconds.do(get_driver_sheet_case)
schedule.every(3).seconds.do(get_passenger_sheet_case)
scheduler_thread_case = threading.Thread(target=run_scheduler)
scheduler_thread_case.daemon = True  # 主程式結束此也結束
scheduler_thread_case.start()
#   獲得dict內的value
def get_key(dict, value):
    return [k for k, v in dict.items() if v == value]
#   獲取 GoogleSheet 的司機、揪團試算表
#       token.json的資料如放在公開伺服器上執行之類的，會遭停用，需到google cloud重新建立金鑰，否則會跳出JWP錯誤
import tempfile
import os
import json
import gspread
from dotenv import load_dotenv
load_dotenv()
# 從環境變數讀取 JSON 字串，否則env只能傳入string，且env檔須調整為單行。
credentials_str = os.getenv('GOOGLE_CREDENTIALS')
if credentials_str:
    credentials_dict = json.loads(credentials_str)
# 使用修正後的字典創建 gspread 客戶端
gc = gspread.service_account_from_dict(credentials_dict)
carpool = gc.open_by_url('https://docs.google.com/spreadsheets/d/1q8HKO2NBz1O8UBE7ag9Kq-eNAc114TKzkXyOq32vfSA/edit?gid=1437248658#gid=1437248658')
driver_sheet = carpool.get_worksheet(0)
passenger_sheet = carpool.get_worksheet(1)
# 抓取現在時間
now_time = datetime.now()
formatted_now_time = now_time.strftime('%Y/%#m/%#d')
c_now_time = formatted_now_time.split('/')
# Tamplate Message
@line_handler.add(MessageEvent, message = TextMessageContent)
def handle_message(event):
    text = event.message.text
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        # Carousel Template 
        if text =='目前有哪些共乘（已有司機）？':
            if web_driver_len != 0:
                line_flex_json = {
                    "type": "carousel",
                    "contents": []
                }    
                for i in range(web_driver_len):
                    driver_case = get_sheet_time_fordatetime(web_driver_data.json()[i][3])
                    driver_case_datetime = driver_case.split('/')
                    driver_date = date(int(c_now_time[0]),int(c_now_time[1]),int(c_now_time[2])) 
                    driver_date_due = date(int(driver_case_datetime[0]),int(driver_case_datetime[1]),int(driver_case_datetime[2]))
                    if driver_date_due>=driver_date:
                        if web_driver_data.json()[i][14] != web_driver_data.json()[i][5]:
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
                                            "text": web_driver_data.json()[i][2],
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
                                            "text": web_driver_data.json()[i][4],
                                            "color": "#ffffff",
                                            "size": "lg",
                                            "weight": "bold",
                                            "margin": "none"
                                        }
                                        ]
                                    },
                                    {
                                        "type": "text",
                                        "text": f"出發時間：{get_Sheet_time(web_driver_data.json()[i][3])}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "contents": [],
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"總時程：{time_hrmi(int(web_driver_data.json()[i][6]))}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"發起人：{web_driver_data.json()[i][9]}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"手機號碼：{web_driver_data.json()[i][13]}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"LineID：{web_driver_data.json()[i][10]}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"共乘人數上限：{web_driver_data.json()[i][5]}",
                                        "color": "#000000",
                                        "size": "xs"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"價格：{web_driver_data.json()[i][11]}",
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
                                        "text": f"活動編號：{web_driver_data.json()[i][17]}",
                                        "margin": "none",
                                        "size": "sm",
                                        "weight": "bold"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"交通工具：{web_driver_data.json()[i][12]}",
                                        "margin": "none",
                                        "size": "sm",
                                        "weight": "bold"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"簡介：{web_driver_data.json()[i][8]}",
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
                                        "displayText": f"我想共乘{web_driver_data.json()[i][2]}到{web_driver_data.json()[i][4]}!"
                                        },
                                        "style": "secondary"
                                    }
                                    ]
                                }
                            }
                            # 新增規範
                            if '上下車地點可討論' in web_driver_data.json()[i][7]:
                                r = {
                                            "type": "text",
                                            "text": "上下車地點可討論",
                                            "size": "sm",
                                            "margin": "none",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_driver_data_case['body']['contents'].insert(3,r)
                            if '自備零錢不找零' in web_driver_data.json()[i][7]:
                                r = {
                                            "type": "text",
                                            "text": "自備零錢不找零",
                                            "size": "sm",
                                            "margin": "none",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_driver_data_case['body']['contents'].insert(3,r)
                            if '接受線上付款 / 轉帳' in web_driver_data.json()[i][7]:
                                r = {
                                            "type": "text",
                                            "text": "接受線上付款 / 轉帳",
                                            "size": "sm",
                                            "margin": "none",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_driver_data_case['body']['contents'].insert(3,r)
                            if '禁食' in web_driver_data.json()[i][7]:
                                r = {
                                            "type": "text",
                                            "text": "禁食",
                                            "size": "sm",
                                            "margin": "none",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_driver_data_case['body']['contents'].insert(2,r)
                            if '※ 人滿才發車' in web_driver_data.json()[i][7]:
                                r = {
                                            "type": "text",
                                            "text": "※ 人滿才發車",
                                            "size": "sm",
                                            "margin": "none",
                                            "color": "#ff5551",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_driver_data_case['body']['contents'].insert(3,r)
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
                            messages=[TextMessage(text='目前司機發起之活動預約人數皆已滿')] 
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
            if web_passenger_len != 0:
                line_flex_json = {
                    "type": "carousel",
                    "contents": []
                }
                for i in range(web_passenger_len):
                    passenger_case = get_sheet_time_fordatetime(web_passenger_data.json()[i][3])
                    passenger_case_datetime = passenger_case.split('/')
                    passenger_date = date(int(c_now_time[0]),int(c_now_time[1]),int(c_now_time[2])) 
                    passenger_date_due = date(int(passenger_case_datetime[0]),int(passenger_case_datetime[1]),int(passenger_case_datetime[2]))
                    if passenger_date_due>=passenger_date: 
                        if web_passenger_data.json()[i][12] != web_passenger_data.json()[i][5]:
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
                                            "text": web_passenger_data.json()[i][2],
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
                                            "text": web_passenger_data.json()[i][4],
                                            "color": "#ffffff",
                                            "size": "lg",
                                            "weight": "bold",
                                            "margin": "none"
                                        }
                                        ]
                                    },
                                    {
                                        "type": "text",
                                        "text": f"出發時間：{get_Sheet_time(web_passenger_data.json()[i][3])}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "contents": [],
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"總時程：{time_hrmi(int(web_passenger_data.json()[i][6]))}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"發起人：{web_passenger_data.json()[i][9]}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"LineID：{web_passenger_data.json()[i][10]}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"共乘人數上限：{web_passenger_data.json()[i][5]}",
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
                                        "text": f"活動編號：{web_passenger_data.json()[i][15]}",
                                        "margin": "none",
                                        "size": "sm",
                                        "weight": "bold"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"交通工具：{web_passenger_data.json()[i][2]}",
                                        "margin": "none",
                                        "size": "sm",
                                        "weight": "bold"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"簡介：{web_passenger_data.json()[i][8]}",
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
                                        "displayText": f"我想共乘{web_passenger_data.json()[i][2]}到{web_passenger_data.json()[i][4]}!"
                                        },
                                        "style": "secondary"
                                    }
                                    ]
                                }
                                }
                            # 新增規範
                            if '上下車地點可討論' in web_passenger_data.json()[i][7]:
                                r = {
                                            "type": "text",
                                            "text": "上下車地點可討論",
                                            "size": "sm",
                                            "margin": "none",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_passenger_data_case['body']['contents'].insert(3,r)
                            if '不聊天' in web_passenger_data.json()[i][7]:
                                r = {
                                            "type": "text",
                                            "text": "不聊天",
                                            "size": "sm",
                                            "margin": "none",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_passenger_data_case['body']['contents'].insert(3,r)
                            if '嚴禁喝酒及抽菸' in web_passenger_data.json()[i][7]:
                                r = {
                                            "type": "text",
                                            "text": "嚴禁喝酒及抽菸",
                                            "size": "sm",
                                            "margin": "none",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_passenger_data_case['body']['contents'].insert(3,r)
                            if '禁食' in web_passenger_data.json()[i][7]:
                                r = {
                                            "type": "text",
                                            "text": "禁食",
                                            "size": "sm",
                                            "margin": "none",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_passenger_data_case['body']['contents'].insert(3,r)
                            if '謝絕寵物' in web_passenger_data.json()[i][7]:
                                r = {
                                            "type": "text",
                                            "text": "謝絕寵物",
                                            "size": "sm",
                                            "margin": "none",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_passenger_data_case['body']['contents'].insert(3,r)
                            if '寵物需裝籠' in web_passenger_data.json()[i][7]:
                                r = {
                                            "type": "text",
                                            "text": "寵物需裝籠",
                                            "size": "sm",
                                            "margin": "none",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_passenger_data_case['body']['contents'].insert(3,r)
                            if '※ 人滿才發車' in web_passenger_data.json()[i][7]:
                                r = {
                                            "type": "text",
                                            "text": "※ 人滿才發車",
                                            "size": "sm",
                                            "margin": "none",
                                            "color": "#ff5551",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_passenger_data_case['body']['contents'].insert(3,r)
                            line_flex_json['contents'].append(web_passenger_data_case)   
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
                            messages=[TextMessage(text='目前乘客發起之揪團活動預約人數皆已滿')] 
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
            get_driver_sheet_case()
            get_passenger_sheet_case()
            # 獲取使用者 user_ID 
            user_id = event.source.user_id
            text = ''
            for id in driver_Sure_id_dict.values():
                if id == user_id:
                    reservation_case = get_key(driver_Sure_id_dict,id)
                    for i in reservation_case:
                        reservation = f'活動編號：{web_driver_data.json()[i][17]}\n發車地點：{web_driver_data.json()[i][2]}\n目的地：{web_driver_data.json()[i][4]}\n出發時間：\n{get_Sheet_time(web_driver_data.json()[i][3])}\n總時程：{time_hrmi(int(web_driver_data.json()[i][6]))}\n發起人：{web_driver_data.json()[i][9]}\n手機號碼：{web_driver_data.json()[i][13]}\nLineID：{web_driver_data.json()[i][10]}\n共乘人數上限：{web_driver_data.json()[i][5]}\n價格：{web_driver_data.json()[i][11]}\n交通工具：{web_driver_data.json()[i][12]}\n行車規範：\n{web_driver_data.json()[i][7]}\n簡介：{web_driver_data.json()[i][8]}\n'
                        text = text+reservation+'--------------------------------\n'
                    text = '司機預約：\n'+text
                    break       
                else:
                    pass      
            for id in passenger_Sure_id_dict.values():
                if id == user_id:
                    text = text+'乘客（揪團）預約：\n'
                    reservation_case = get_key(passenger_Sure_id_dict,id)
                    for i in reservation_case:
                        reservation = f'活動編號：{web_passenger_data.json()[i][15]}\n發車地點：{web_passenger_data.json()[i][2]}\n目的地：{web_passenger_data.json()[i][4]}\n出發時間：\n{get_Sheet_time(web_passenger_data.json()[i][3])}\n總時程：{time_hrmi(int(web_passenger_data.json()[i][6]))}\n發起人：{web_passenger_data.json()[i][9]}\nLineID：{web_passenger_data.json()[i][10]}\n共乘人數上限：{web_passenger_data.json()[i][5]}\n交通工具：{web_passenger_data.json()[i][11]}行車規範：\n{web_passenger_data.json()[i][7]}\n簡介：{web_passenger_data.json()[i][8]}\n'
                        text = text+reservation+'--------------------------------\n'      
                    break    
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
@line_handler.add(PostbackEvent)
def handle_postbak(event):
    try:
        for i in range(web_driver_len):
            if event.postback.data == f'driver_Num{i}':
                driver_case = get_sheet_time_fordatetime(web_driver_data.json()[i][3])
                driver_case_datetime = driver_case.split('/')
                driver_date = date(int(c_now_time[0]),int(c_now_time[1]),int(c_now_time[2])) 
                driver_date_due = date(int(driver_case_datetime[0]),int(driver_case_datetime[1]),int(driver_case_datetime[2]))
                with ApiClient(configuration) as api_client:
                    line_bot_api = MessagingApi(api_client)
                    if driver_date_due>driver_date:
                        confirm_template = ConfirmTemplate(
                            text = f'活動編號：{web_driver_data.json()[i][17]}\n發車地點：{web_driver_data.json()[i][2]}\n目的地：{web_driver_data.json()[i][4]}\n出發時間：\n{get_Sheet_time(web_driver_data.json()[i][3])}\n總時程：{time_hrmi(int(web_driver_data.json()[i][6]))}\n發起人：{web_driver_data.json()[i][9]}\n手機號碼：{web_driver_data.json()[i][13]}\nLineID：{web_driver_data.json()[i][10]}\n共乘人數上限：{web_driver_data.json()[i][5]}\n價格：{web_driver_data.json()[i][11]}\n交通工具：{web_driver_data.json()[i][12]}\n行車規範：\n{web_driver_data.json()[i][7]}\n簡介：{web_driver_data.json()[i][8]}\n',
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
                            messages=[TextMessage(text='報名已經截止囉')] 
                        )  
                    )         
            else:
                pass
            # 使用者在Confirm Template按下確定後，試算表的搭車人數將+1
            if event.postback.data == f'driver_Sure{i}':
                get_driver_sheet_case()
                with ApiClient(configuration) as api_client:
                    line_bot_api = MessagingApi(api_client)
                    if web_driver_data.json()[i][14] != web_driver_data.json()[i][5]:
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
                            if driver_sheet.cell(i+2,15).value == None:
                                val = 0
                            else:
                                val = int(driver_sheet.cell(i+2,15).value) #因為dict只能start from 0，因此第一個共乘表單會在第0個，而google sheet第一行又是表單的項目，因此第一張表單會是i+1+1列。
                            driver_sheet.update_cell(i+2,15,val+1)
                            if driver_sheet.cell(i+2,16).value == None:
                                new_id = driver_user_id
                                new_name = driver_Sure_name
                            else:  
                                id = driver_sheet.cell(i+2,16).value
                                new_id = id+','+driver_user_id
                                name = driver_sheet.cell(i+2,17).value
                                new_name = name+','+driver_Sure_name
                            driver_sheet.update_cell(i+2,16,new_id) 
                            driver_sheet.update_cell(i+2,17,new_name)
                        time.sleep()
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
        for i in range(web_passenger_len):
            if event.postback.data == f'passenger_Num{i}':
                passenger_case = get_sheet_time_fordatetime(web_passenger_data.json()[i][3])
                passenger_case_datetime = passenger_case.split('/')
                passenger_date = date(int(c_now_time[0]),int(c_now_time[1]),int(c_now_time[2])) 
                passenger_date_due = date(int(passenger_case_datetime[0]),int(passenger_case_datetime[1]),int(passenger_case_datetime[2]))
                with ApiClient(configuration) as api_client:
                    line_bot_api = MessagingApi(api_client)
                    if passenger_date_due>passenger_date:
                        confirm_template = ConfirmTemplate(
                            text = f'活動編號：{web_passenger_data.json()[i][15]}發車地點：{web_passenger_data.json()[i][2]}\n目的地：{web_passenger_data.json()[i][4]}\n出發時間：\n{get_Sheet_time(web_passenger_data.json()[i][3])}\n總時程：{time_hrmi(int(web_passenger_data.json()[i][6]))}\n發起人：{web_passenger_data.json()[i][9]}\nLineID：{web_passenger_data.json()[i][10]}\n共乘人數上限：{web_passenger_data.json()[i][5]}\n交通工具：{web_passenger_data.json()[i][11]}行車規範：\n{web_passenger_data.json()[i][7]}\n簡介：{web_passenger_data.json()[i][8]}\n',
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
                            messages=[TextMessage(text='報名已經截止囉')] 
                        )  
                    )
            else:
                pass
            # 使用者在Confirm Template按下確定後，試算表的搭車人數將+1
            if event.postback.data == f'passenger_Sure{i}':
                get_passenger_sheet_case()
                with ApiClient(configuration) as api_client:
                    line_bot_api = MessagingApi(api_client)
                    if web_passenger_data.json()[i][12] != web_passenger_data.json()[i][5]:
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
                            passenger_sheet.update_cell(i+2,13,passenger_val+1) #因為dict只能start from 0，因此第一個共乘表單會在第0個，而google sheet第一行又是表單的項目，因此第一張表單會是i+1+1列。
                            if passenger_sheet.cell(i+2,14).value == None:
                                new_id = passenger_user_id
                                new_name = passenger_Sure_name
                            else:
                                id = passenger_sheet.cell(i+2,14).value
                                new_id = id+','+passenger_user_id
                                name = passenger_sheet.cell(i+2,15).value
                                new_name = name+','+passenger_Sure_name
                            passenger_sheet.update_cell(i+2,14,new_id)
                            passenger_sheet.update_cell(i+2,15,new_name)
                        time.sleep(2)
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
    app.run()
# 初始化追踪字典，為每個索引設置False
web_driver_Sure = set()
web_passenger_Sure = set()
def check_project():
    global web_driver_Sure, web_passenger_Sure
    print(f"目前已處理的司機: {web_driver_Sure}")
    print(f"目前已處理的乘客: {web_passenger_Sure}")
    for i in range(web_driver_len):
        driver_case = get_sheet_time_fordatetime(web_driver_data.json()[i][3])
        driver_case_datetime = driver_case.split('/')
        driver_date = date(int(c_now_time[0]),int(c_now_time[1]),int(c_now_time[2])) 
        driver_date_due = date(int(driver_case_datetime[0]),int(driver_case_datetime[1]),int(driver_case_datetime[2]))
        print(driver_date)
        print(driver_date_due)
        if i not in web_driver_Sure:
            if driver_date_due == driver_date:
                # 有人且已滿
                if '※ 人滿才發車' in web_driver_data.json()[i][7] and driver_val== web_driver_data.json()[i][5]:
                    # 寄信給發起人，告知結果
                    name_list = driver_Sure_name_dict.get(i).split(',')
                    output = ','.join(map(str, name_list))
                    str1 = '您在 共乘阿穿 發起的活動人數已滿了，活動資訊如下：'
                    str2 = f'活動編號：{web_driver_data.json()[i][17]}<br>發車地點：{web_driver_data.json()[i][2]}<br>目的地：{web_driver_data.json()[i][4]}<br>出發時間：<br>{get_Sheet_time(web_driver_data.json()[i][3])}<br>總時程：{time_hrmi(int(web_driver_data.json()[i][6]))}<br>發起人：{web_driver_data.json()[i][9]}<br>手機號碼：{web_driver_data.json()[i][13]}<br>LineID：{web_driver_data.json()[i][10]}<br>共乘人數上限：{web_driver_data.json()[i][5]}<br>價格：{web_driver_data.json()[i][11]}<br>交通工具：{web_driver_data.json()[i][12]}<br>行車規範：<br>{web_driver_data.json()[i][7]}<br>簡介：{web_driver_data.json()[i][8]}<br>'
                    str3 = f'參加者Line名稱:{output}'
                    str4 = '您在 共乘阿穿 發起的活動人數已滿囉'
                    # 針對 Linebot 參與的乘客
                    text = f'您參加的活動成團囉，活動編號為{web_driver_data.json()[i][17]}，記得透過LineID聯繫活動發起人!發起人LineID：{web_driver_data.json()[i][10]}，活動資訊如下：\n活動編號：{web_driver_data.json()[i][17]}\n發車地點：{web_driver_data.json()[i][2]}\n目的地：{web_driver_data.json()[i][4]}\n出發時間：\n{get_Sheet_time(web_driver_data.json()[i][3])}\n總時程：{time_hrmi(int(web_driver_data.json()[i][6]))}\n發起人：{web_driver_data.json()[i][9]}\n手機號碼：{web_driver_data.json()[i][13]}\nLineID：{web_driver_data.json()[i][10]}\n共乘人數上限：{web_driver_data.json()[i][5]}\n價格：{web_driver_data.json()[i][11]}\n交通工具：{web_driver_data.json()[i][12]}\n行車規範：\n{web_driver_data.json()[i][7]}\n簡介：{web_driver_data.json()[i][8]}\n'
                # 有人且發起者未勾選 ※ 人滿才發車
                elif '※ 人滿才發車' not in web_driver_data.json()[i][7] and driver_val>0:
                    # 寄信給發起人，告知結果
                    name_list = driver_Sure_name_dict.get(i).split(',')
                    output = ','.join(map(str, name_list))
                    str1 = '您在 共乘阿穿 發起的活動人數未滿，但您未勾選「人滿才發車」，因此成團喔！活動資訊如下：'
                    str2 = f'活動編號：{web_driver_data.json()[i][17]}<br>發車地點：{web_driver_data.json()[i][2]}<br>目的地：{web_driver_data.json()[i][4]}<br>出發時間：<br>{get_Sheet_time(web_driver_data.json()[i][3])}<br>總時程：{time_hrmi(int(web_driver_data.json()[i][6]))}<br>發起人：{web_driver_data.json()[i][9]}<br>手機號碼：{web_driver_data.json()[i][13]}<br>LineID：{web_driver_data.json()[i][10]}<br>共乘人數上限：{web_driver_data.json()[i][5]}<br>價格：{web_driver_data.json()[i][11]}<br>交通工具：{web_driver_data.json()[i][12]}<br>行車規範：<br>{web_driver_data.json()[i][7]}<br>簡介：{web_driver_data.json()[i][8]}<br>'
                    str3 = f'參加者Line名稱:{output}'
                    str4 = '您在 共乘阿穿 發起的活動人數未滿，但您未勾選「人滿才發車」，因此成團喔！'
                    # 針對 Linebot 參與的乘客
                    text = f'您參加的活動成團囉，活動編號為{web_driver_data.json()[i][17]}，記得透過LineID聯繫活動發起人!發起人LineID：{web_driver_data.json()[i][10]}，活動資訊如下：\n活動編號：{web_driver_data.json()[i][17]}\n發車地點：{web_driver_data.json()[i][2]}\n目的地：{web_driver_data.json()[i][4]}\n出發時間：\n{get_Sheet_time(web_driver_data.json()[i][3])}\n總時程：{time_hrmi(int(web_driver_data.json()[i][6]))}\n發起人：{web_driver_data.json()[i][9]}\n手機號碼：{web_driver_data.json()[i][13]}\nLineID：{web_driver_data.json()[i][10]}\n共乘人數上限：{web_driver_data.json()[i][5]}\n價格：{web_driver_data.json()[i][11]}\n交通工具：{web_driver_data.json()[i][12]}\n行車規範：\n{web_driver_data.json()[i][7]}\n簡介：{web_driver_data.json()[i][8]}\n'
                # 未成團
                else:
                    # 寄信給發起人，告知結果
                    str1 = f'您在 共乘阿穿 發起的活動人數未滿，活動編號為{web_driver_data.json()[i][17]}，因此未發車。'
                    str2 = '活動資訊如下：'
                    str3 = f'活動編號：{web_driver_data.json()[i][17]}<br>發車地點：{web_driver_data.json()[i][2]}<br>目的地：{web_driver_data.json()[i][4]}<br>出發時間：<br>{get_Sheet_time(web_driver_data.json()[i][3])}<br>總時程：{time_hrmi(int(web_driver_data.json()[i][6]))}<br>發起人：{web_driver_data.json()[i][9]}<br>手機號碼：{web_driver_data.json()[i][13]}<br>LineID：{web_driver_data.json()[i][10]}<br>共乘人數上限：{web_driver_data.json()[i][5]}<br>價格：{web_driver_data.json()[i][11]}<br>交通工具：{web_driver_data.json()[i][12]}<br>行車規範：<br>{web_driver_data.json()[i][7]}<br>簡介：{web_driver_data.json()[i][8]}<br>'
                    str4 = '您在 共乘阿穿 發起的活動人數未滿'
                    # 針對 Linebot 參與的乘客
                    text = f'您參與的共乘活動因人數未滿而不發車喔!活動編號為{web_driver_data.json()[i][17]}'
                # 寄信給發起人
                name_list = driver_Sure_name_dict.get(i).split(',')
                output = ','.join(map(str, name_list))
                html =f'''
                <h1>共乘阿穿</h1>
                <div>{str1}</div>
                <div>{str2}<div>
                <div>{str3}<div>
                '''
                mail = MIMEText(html, 'html', 'utf-8')   # plain 換成 html，就能寄送 HTML 格式的信件
                mail['Subject']= f'{str4}'
                mail['From']='adf'
                mail['To']= web_driver_data.json()[i][1]
                try:
                    smtp = smtplib.SMTP('smtp.gmail.com', 587)
                    smtp.ehlo()
                    smtp.starttls()
                    smtp.login('ncnucarpool@gmail.com','jrab omvk bkql rruu')
                    status = smtp.send_message(mail)
                    print(status)
                    smtp.quit()
                    # 將此索引添加到已處理集合中
                    web_driver_Sure.add(i)
                    print(f"司機 {i} 已標記為處理完成")
                except Exception as e:
                    print(f"發送郵件時出錯: {e}")              
                # 當活動人數已滿的時候，向活動參與者發送提醒（告知可發車及聯繫發起人）
                driver_Sure = web_driver_data.json()[i][15]
                driver_Sure_list = driver_Sure.split('/')
                for r in driver_Sure_list:
                    #   注意前方要有 Bearer
                    headers = {'Authorization':'Bearer UlaItdkkQW33Qln6YyLrLsLDo83MhILpEzQbtmQGiyk6Y6XbxGQ+sr0jjJb4TX8QhUTn3ZHim0LbFpyQ09SR/dEI09B30r4exhTcGJE+68Jbcyp75Ze3mvv2U9bF+G77dVSGKrdZcuQ5E7M8eJ6OFwdB04t89/1O/w1cDnyilFU=','Content-Type':'application/json'}
                    body = {
                        'to':f'{r}',
                        'messages':[{
                                'type': 'text',
                                'text': text
                            }]
                        }
                    # 向指定網址發送 request
                    req = requests.request('POST', 'https://api.line.me/v2/bot/message/push',headers=headers,data=json.dumps(body).encode('utf-8'))
                    # 印出得到的結果
                    print(req.text)
            else:
                pass
    for i in range(web_passenger_len):
        passenger_case = get_sheet_time_fordatetime(web_passenger_data.json()[i][3])
        passenger_case_datetime = passenger_case.split('/')
        passenger_date = date(int(c_now_time[0]),int(c_now_time[1]),int(c_now_time[2])) 
        passenger_date_due = date(int(passenger_case_datetime[0]),int(passenger_case_datetime[1]),int(passenger_case_datetime[2]))
        if i not in web_passenger_Sure :
            if passenger_date_due == passenger_date:
                # 有人且已滿
                if '※ 人滿才發車' in web_passenger_data.json()[i][7] and passenger_val== web_passenger_data.json()[i][5]:
                    name_list = passenger_Sure_name_dict.get(i).split(',')
                    output = ','.join(map(str, name_list))
                    str1 = '您在 共乘阿穿 發起的活動人數已滿了，活動資訊如下：'
                    str2 = f'活動編號：{web_passenger_data.json()[i][15]}<br>發車地點：{web_passenger_data.json()[i][2]}<br>目的地：{web_passenger_data.json()[i][4]}\n出發時間：<br>{get_Sheet_time(web_passenger_data.json()[i][3])}<br>總時程：{time_hrmi(int(web_passenger_data.json()[i][6]))}<br>發起人：{web_passenger_data.json()[i][9]}<br>LineID：{web_passenger_data.json()[i][10]}<br>共乘人數上限：{web_passenger_data.json()[i][5]}<br>交通工具：{web_passenger_data.json()[i][11]}行車規範：<br>{web_passenger_data.json()[i][7]}\n簡介：{web_passenger_data.json()[i][8]}<br>'
                    str3 = f'參加者Line名稱:{output}'
                    str4 = '您在 共乘阿穿 發起的活動人數已滿囉'
                    # 針對 Linebot 參與的乘客
                    text = f'您參加的活動成團囉，活動編號為{web_passenger_data.json()[i][15]}，記得透過LineID聯繫活動發起人!發起人LineID：{web_passenger_data.json()[i][10]}，活動資訊如下：活動編號：{web_passenger_data.json()[i][15]}發車地點：{web_passenger_data.json()[i][2]}\n目的地：{web_passenger_data.json()[i][4]}\n出發時間：\n{get_Sheet_time(web_passenger_data.json()[i][3])}\n總時程：{time_hrmi(int(web_passenger_data.json()[i][6]))}\n發起人：{web_passenger_data.json()[i][9]}\nLineID：{web_passenger_data.json()[i][10]}\n共乘人數上限：{web_passenger_data.json()[i][5]}\n交通工具：{web_passenger_data.json()[i][11]}行車規範：\n{web_passenger_data.json()[i][7]}\n簡介：{web_passenger_data.json()[i][8]}\n'                
                # 有人且發起者未勾選 ※ 人滿才發車
                elif '※ 人滿才發車' not in web_passenger_data.json()[i][7] and passenger_val>0:
                    # 寄信給發起人，告知結果
                    name_list = passenger_Sure_name_dict.get(i).split(',')
                    output = ','.join(map(str, name_list))
                    str1 = '您在 共乘阿穿 發起的活動人數未滿，但您未勾選「人滿才發車」，因此成團喔！活動資訊如下：'
                    str2 = f'活動編號：{web_passenger_data.json()[i][15]}<br>發車地點：{web_passenger_data.json()[i][2]}<br>目的地：{web_passenger_data.json()[i][4]}\n出發時間：<br>{get_Sheet_time(web_passenger_data.json()[i][3])}<br>總時程：{time_hrmi(int(web_passenger_data.json()[i][6]))}<br>發起人：{web_passenger_data.json()[i][9]}<br>LineID：{web_passenger_data.json()[i][10]}<br>共乘人數上限：{web_passenger_data.json()[i][5]}<br>交通工具：{web_passenger_data.json()[i][11]}行車規範：<br>{web_passenger_data.json()[i][7]}\n簡介：{web_passenger_data.json()[i][8]}<br>'
                    str3 = f'參加者Line名稱:{output}'
                    str4 = '您在 共乘阿穿 發起的活動人數未滿，但您未勾選「人滿才發車」，因此成團喔！'
                    # 針對 Linebot 參與的乘客
                    text = f'您參加的活動成團囉，活動編號為{web_passenger_data.json()[i][15]}，記得透過LineID聯繫活動發起人!發起人LineID：{web_passenger_data.json()[i][10]}，活動資訊如下：活動編號：{web_passenger_data.json()[i][15]}發車地點：{web_passenger_data.json()[i][2]}\n目的地：{web_passenger_data.json()[i][4]}\n出發時間：\n{get_Sheet_time(web_passenger_data.json()[i][3])}\n總時程：{time_hrmi(int(web_passenger_data.json()[i][6]))}\n發起人：{web_passenger_data.json()[i][9]}\nLineID：{web_passenger_data.json()[i][10]}\n共乘人數上限：{web_passenger_data.json()[i][5]}\n交通工具：{web_passenger_data.json()[i][11]}行車規範：\n{web_passenger_data.json()[i][7]}\n簡介：{web_passenger_data.json()[i][8]}\n'
                # 未成團
                else:
                    # 寄信給發起人，告知結果
                    str1 = f'您在 共乘阿穿 發起的活動人數未滿，活動編號為{web_passenger_data.json()[i][15]}，因此未發車。'
                    str2 = '活動資訊如下：'
                    str3 = f'活動編號：{web_passenger_data.json()[i][15]}<br>發車地點：{web_passenger_data.json()[i][2]}<br>目的地：{web_passenger_data.json()[i][4]}\n出發時間：<br>{get_Sheet_time(web_passenger_data.json()[i][3])}<br>總時程：{time_hrmi(int(web_passenger_data.json()[i][6]))}<br>發起人：{web_passenger_data.json()[i][9]}<br>LineID：{web_passenger_data.json()[i][10]}<br>共乘人數上限：{web_passenger_data.json()[i][5]}<br>交通工具：{web_passenger_data.json()[i][11]}行車規範：<br>{web_passenger_data.json()[i][7]}\n簡介：{web_passenger_data.json()[i][8]}<br>'
                    str4 = '您在 共乘阿穿 發起的活動人數未滿'
                    # 針對 Linebot 參與的乘客
                    text = f'您參與的共乘活動因人數未滿而不發車喔!活動編號為{web_driver_data.json()[i][15]}'
                # 寄信給發起人
                name_list = passenger_Sure_name_dict.get(i).split(',')
                output = ','.join(map(str, name_list))
                html =f'''
                <h1>共乘阿穿</h1>
                <div>{str1}</div>
                <div>{str2}<div>
                <div>{str3}<div>
                '''
                mail = MIMEText(html, 'html', 'utf-8')   # plain 換成 html，就能寄送 HTML 格式的信件
                mail['Subject']= str4
                mail['From']='adf'
                mail['To']= web_passenger_data.json()[i][1]
                try:
                    smtp = smtplib.SMTP('smtp.gmail.com', 587)
                    smtp.ehlo()
                    smtp.starttls()
                    smtp.login('ncnucarpool@gmail.com','jrab omvk bkql rruu')
                    status = smtp.send_message(mail)
                    print(status)
                    smtp.quit()
                    # 將此索引添加到已處理集合中
                    web_driver_Sure.add(i)
                    print(f"司機 {i} 已標記為處理完成")
                except Exception as e:
                    print(f"發送郵件時出錯: {e}")              
                # 當活動人數已滿的時候，向活動參與者發送提醒（告知可發車及聯繫發起人）
                passenger_Sure = web_passenger_data.json()[i][13]
                passenger_Sure_list = passenger_Sure.split('/')
                for r in passenger_Sure_list:
                    #   注意前方要有 Bearer
                    headers = {'Authorization':'Bearer UlaItdkkQW33Qln6YyLrLsLDo83MhILpEzQbtmQGiyk6Y6XbxGQ+sr0jjJb4TX8QhUTn3ZHim0LbFpyQ09SR/dEI09B30r4exhTcGJE+68Jbcyp75Ze3mvv2U9bF+G77dVSGKrdZcuQ5E7M8eJ6OFwdB04t89/1O/w1cDnyilFU=','Content-Type':'application/json'}
                    body = {
                        'to':f'{r}',
                        'messages':[{
                                'type': 'text',
                                'text': text
                            }]
                        }
                    # 向指定網址發送 request
                    req = requests.request('POST', 'https://api.line.me/v2/bot/message/push',headers=headers,data=json.dumps(body).encode('utf-8'))
                    # 印出得到的結果
                    print(req.text)
            else:
                pass
                
#   每隔3秒檢查試算表內容，若人數達上限即通知活動發起者人數已滿
def run_scheduler():
    global a
    a = True
    while a:
        schedule.run_pending()
        time.sleep(0.1)  
schedule.every(5).minutes.do(check_project)
scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.daemon = True 
scheduler_thread.start()


