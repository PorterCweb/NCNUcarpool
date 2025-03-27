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

app = Flask(__name__)
#.env必要
import os 
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
    global web_driver_data, web_driver_len, driver_Sure_id_dict, driver_Sure_name_dict
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
            driver_Sure_id_dict[i] = web_driver_data.json()[i][14]
            driver_Sure_name_dict[i] = web_driver_data.json()[i][15]
        print(driver_Sure_id_dict)
        print('司機發起之活動已抓取')
    except:
        print('司機發起之活動尚無資料')   
def get_passenger_sheet_case():
    global web_passenger_data, web_passenger_len, passenger_Sure_id_dict, passenger_Sure_name_dict
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
schedule.every(1).seconds.do(get_driver_sheet_case)
schedule.every(1).seconds.do(get_passenger_sheet_case)
scheduler_thread_case = threading.Thread(target=run_scheduler)
scheduler_thread_case.daemon = True  # 主程式結束此也結束
scheduler_thread_case.start()
''' '時間到，自動刪除列'的必要
# '時間到，自動刪除列'的必要(driver)
now_time = datetime.now()
formatted_now_time = now_time.strftime('%Y/%#m/%#d')
c_now_time = formatted_now_time.split('/')
for i in range(web_driver_len):
    case = get_sheet_time_fordatetime(web_driver_data.json()[i][4])
    case_datetime = case.split('/')
    if int(case_datetime[2])<int(c_now_time[2]):
        driver_sheet.delete_rows(i+2)
        print(i)
        break
    else:
        pass   
# '時間到，自動刪除列'的必要(passenger)
now_time = datetime.now()
formatted_now_time = now_time.strftime('%Y/%#m/%#d')
c_now_time = formatted_now_time.split('/')
for i in range(web_passenger_len):
    case = get_sheet_time_fordatetime(web_passenger_data.json()[i][4])
    case_datetime = case.split('/')
    if int(case_datetime[2])<int(c_now_time[2]):
        passenger_sheet.delete_rows(i+2)
        print(i)
        break
    else:
        pass
'''
#   獲得dict內的value
def get_key(dict, value):
    return [k for k, v in dict.items() if v == value]
#   獲取 GoogleSheet 的司機、揪團試算表
gc = gspread.service_account(filename = 'token.json')   
carpool = gc.open_by_url('https://docs.google.com/spreadsheets/d/1q8HKO2NBz1O8UBE7ag9Kq-eNAc114TKzkXyOq32vfSA/edit?gid=1437248658#gid=1437248658')
driver_sheet = carpool.get_worksheet(0)
passenger_sheet = carpool.get_worksheet(1)
''' 載入google sheet的方式
使用 service_account 函數載入 JSON 格式的API token文件
gc = gspread.service_account(filename = 'token.json')
打開 Goole sheets 文件
sh = gc.open_by_url('google sheet')
sh = gc.open('/public/write_sheet')
選擇要操作的工作表
worksheet = sh.get_worksheet(0)
準備要輸入的數據
data = [
    ['姓名','年齡']]
worksheet.insert_rows(data,6)
'''
#-------------------------練習------------------------------------------------------------------------------------------------------------------------------------------
# 訊息事件
# 傳送postback物件並回傳
@line_handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        if event.message.text == 'postback':
            buttons_template = ButtonsTemplate(
                title='Postback Sample',
                text='Postback Action',
                actions=[
                    PostbackAction(label='Postback Action', text='Postback Action Button Clicked!', data='postback'),
                ])
            template_message = TemplateMessage(
                alt_text='Postback Sample',
                template=buttons_template  
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[template_message]
                )  
            )
@line_handler.add(PostbackEvent)
def handle_postback(event):
        if event.postback.data == 'postback':
            print('Postback event is triggered!')
# 傳送訊息
@line_handler.add(MessageEvent, message = TextMessageContent)
def message_text(event):
    with ApiClient(configuration) as api_client: #透過confriguration創造ApiClient物件
        line_bot_api = MessagingApi(api_client)

        # Reply message
        #line_bot_api.reply_message( #傳送回復訊息
        #    ReplyMessageRequest(
        #        reply_token=event.reply_token,
        #        messages=[TextMessage(text='reply message')] #不可超過5個訊息
        #    )
        #)

        # HTTP INFO
        #result = line_bot_api.reply_message_with_http_info( #回傳HTTP的status code
        #    ReplyMessageRequest(
        #        reply_token = event.reply_token,
        #        messages = [TextMessage(text = 'Reply message with http info')]
        #    )
        #)

        # Push message
        #line_bot_api.push_message_with_http_info(
        #    PushMessageRequest(
        #        to = event.source.user_id,
        #        messages = [TextMessage(text='Push!')]
        #    )
        #)

        # Broadcast message
        #line_bot_api.broadcast_with_http_info(
        #    BroadcastRequest(
        #        messages = [TextMessage(text = 'BROADCAST!')]
        #    )
        #)

        # Multicast message
        #line_bot_api.multicast_with_http_info(
        #    MulticastRequest(
        #        to = ['Ufdd0787ca7bc63b64665cdb9a95fd477'],  #只放user ID 不可放群組，最多給五則訊息
        #        messages = [TextMessage(text='Multicast!')],
        #        notificationDisabled=True
        #    )
        #)
@line_handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    text = event.message.text
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        if text == 'flex':
            line_flex_json = {
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
                            "size": "sm"
                        },
                        {
                            "type": "text",
                            "text": "國立暨南國際大學",
                            "color": "#ffffff",
                            "size": "xl",
                            "flex": 4,
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
                            "size": "sm"
                        },
                        {
                            "type": "text",
                            "text": "台中高鐵站",
                            "color": "#ffffff",
                            "size": "xl",
                            "flex": 4,
                            "weight": "bold"
                        }
                        ]
                    }
                    ],
                    "paddingAll": "20px",
                    "backgroundColor": "#0367D3",
                    "spacing": "md",
                    "height": "154px",
                    "paddingTop": "22px"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                    {
                        "type": "text",
                        "text": "時程：1小時30分鐘",
                        "color": "#b7b7b7",
                        "size": "xs"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                        {
                            "type": "text",
                            "text": "20:30",
                            "size": "sm",
                            "gravity": "center"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                            {
                                "type": "filler"
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [],
                                "cornerRadius": "30px",
                                "height": "12px",
                                "width": "12px",
                                "borderColor": "#6486E3",
                                "borderWidth": "2px"
                            },
                            {
                                "type": "filler"
                            }
                            ],
                            "flex": 0
                        },
                        {
                            "type": "text",
                            "text": "國立暨南國際大學",
                            "gravity": "center",
                            "flex": 4,
                            "size": "sm"
                        }
                        ],
                        "spacing": "xl",
                        "cornerRadius": "30px",
                        "margin": "xl"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                        {
                            "type": "box",
                            "layout": "baseline",
                            "contents": [
                            {
                                "type": "filler"
                            }
                            ],
                            "flex": 1
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                {
                                    "type": "filler"
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [],
                                    "width": "2px",
                                    "backgroundColor": "#B7B7B7"
                                },
                                {
                                    "type": "filler"
                                }
                                ],
                                "flex": 1
                            }
                            ],
                            "width": "12px"
                        },
                        {
                            "type": "text",
                            "text": "20分鐘",
                            "gravity": "center",
                            "flex": 4,
                            "size": "xs",
                            "color": "#8c8c8c"
                        }
                        ],
                        "spacing": "lg",
                        "height": "64px"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                            {
                                "type": "text",
                                "text": "20:50",
                                "gravity": "center",
                                "size": "sm"
                            }
                            ],
                            "flex": 1
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                            {
                                "type": "filler"
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [],
                                "cornerRadius": "30px",
                                "width": "12px",
                                "height": "12px",
                                "borderWidth": "2px",
                                "borderColor": "#6486E3"
                            },
                            {
                                "type": "filler"
                            }
                            ],
                            "flex": 0
                        },
                        {
                            "type": "text",
                            "text": "埔里",
                            "gravity": "center",
                            "flex": 4,
                            "size": "sm"
                        }
                        ],
                        "spacing": "lg",
                        "cornerRadius": "30px"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                        {
                            "type": "box",
                            "layout": "baseline",
                            "contents": [
                            {
                                "type": "filler"
                            }
                            ],
                            "flex": 1
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                {
                                    "type": "filler"
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [],
                                    "width": "2px",
                                    "backgroundColor": "#6486E3"
                                },
                                {
                                    "type": "filler"
                                }
                                ],
                                "flex": 1
                            }
                            ],
                            "width": "12px"
                        },
                        {
                            "type": "text",
                            "text": "1小時10分鐘",
                            "gravity": "center",
                            "flex": 4,
                            "size": "xs",
                            "color": "#8c8c8c"
                        }
                        ],
                        "spacing": "lg",
                        "height": "64px"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                        {
                            "type": "text",
                            "text": "22:00",
                            "gravity": "center",
                            "size": "sm"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                            {
                                "type": "filler"
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [],
                                "cornerRadius": "30px",
                                "width": "12px",
                                "height": "12px",
                                "borderColor": "#6486E3",
                                "borderWidth": "2px"
                            },
                            {
                                "type": "filler"
                            }
                            ],
                            "flex": 0
                        },
                        {
                            "type": "text",
                            "text": "台中高鐵站",
                            "gravity": "center",
                            "flex": 4,
                            "size": "sm"
                        }
                        ],
                        "spacing": "lg",
                        "cornerRadius": "30px"
                    }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                    {
                        "type": "button",
                        "action": {
                        "type": "message",
                        "label": "我要共乘!",
                        "text": "我要共乘!"
                        },
                        "style": "primary"
                    }
                    ]
                }
}
            line_flex_str = json.dumps(line_flex_json) #改成字串格式
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[FlexMessage(alt_text='詳細說明', contents=FlexContainer.from_json(line_flex_str))]
                )
            )
import queue
class LineBotTaskQueue:
    def __init__(self):
        # 創建一個先進先出的佇列
        self.task_queue = queue.Queue()
        # 創建一個線程來處理佇列
        self.worker_thread = threading.Thread(target=self._process_tasks, daemon=True)
        self.worker_thread.start()
    def _process_tasks(self):
        while True:
            # 從佇列中取出任務並執行
            task = self.task_queue.get()
            try:
                task()
            except Exception as e:
                print(f"任務執行出錯: {e}")
            finally:
                # 標記任務完成
                self.task_queue.task_done()
    def add_task(self, task_function):
            # 將任務加入佇列
            self.task_queue.put(task_function)
    def wait_completion(self):
        # 等待所有任務完成
        self.task_queue.join()
# 創建全局任務佇列
linebot_task_queue = LineBotTaskQueue()
def queue_execution(func):
    """
    裝飾器：將函數加入任務佇列
    可以直接用於LineBot的事件處理函數
    """
    def wrapper(*args, **kwargs):
        def task():
            # 執行原始函數
            func(*args, **kwargs)
        # 將任務加入佇列
        linebot_task_queue.add_task(task)
    return wrapper

#---------------藥物-----------------------------------------------------------------------------------------------------------------------------------------------------
#試算表最後一欄新增'參與者名稱',將每次點擊確定的人紀錄，避免重複計算及新增'預約取消'的功能
#寄件給發起者郵件內容?
#表單是否需要LineID、名稱、系級?新增
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Tamplate Message
@line_handler.add(MessageEvent, message = TextMessageContent)
def handle_message(event):
    text = event.message.text
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        if text == '我想當司機!':
            url = request.url_root + '/static/images.jpg'
            url = url.replace('http', 'https')
            app.logger.info('url=' + url)
            buttons_template = ButtonsTemplate(
                thumbnail_image_url=url,
                title='發車時間',
                text='詳細說明',
                actions=[
                    #URIAction(label='連結', uri='https://www.youtube.com/watch?v=Mw3cODdkaFM'),
                    #PostbackAction(label='地點', data='address', displayText='傳了'),
                    MessageAction(label='傳"哈囉"', text='哈囉'),
                    DatetimePickerAction(label='選擇時間', data='時間', mode='datetime')
                ])
            template_message = TemplateMessage(
                alt_text='This is a buttons Template',
                template= buttons_template  
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[template_message]
                )
        )
            pass
        elif text == '我想當乘客!':
            url = request.url_root + '/static/images.jpg'
            url = url.replace('http', 'https')
            app.logger.info('url=' + url)
            buttons_template = ButtonsTemplate(
                thumbnail_image_url=url,
                title='搭車時間',
                text='詳細說明',
                actions=[
                    #URIAction(label='連結', uri='https://www.youtube.com/watch?v=Mw3cODdkaFM'),
                    #PostbackAction(label='地點', data='address', displayText='傳了'),
                    MessageAction(label='傳"哈囉"', text='哈囉'),
                    DatetimePickerAction(label='選擇時間', data='時間', mode='datetime')
                ])
            template_message = TemplateMessage(
                alt_text='This is a buttons Template',
                template= buttons_template  
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[template_message]
            )
        )
            pass
        # Carousel Template 
        elif text =='目前有哪些共乘（已有司機）？':
            if web_driver_len != 0:
                now_time = datetime.now()
                formatted_now_time = now_time.strftime('%Y/%#m/%#d')
                c_now_time = formatted_now_time.split('/')
                line_flex_json = {
                    "type": "carousel",
                    "contents": []
                }    
                for i in range(web_driver_len):
                    case = get_sheet_time_fordatetime(web_driver_data.json()[i][4])
                    case_datetime = case.split('/')
                    date1 = date(int(c_now_time[0]),int(c_now_time[1]),int(c_now_time[2])) 
                    date2 = date(int(case_datetime[0]),int(case_datetime[1]),int(case_datetime[2]))
                    if date2>=date1:
                        if web_driver_data.json()[i][6] != web_driver_data.json()[i][13]:
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
                                            "text": web_driver_data.json()[i][5],
                                            "color": "#ffffff",
                                            "size": "lg",
                                            "weight": "bold",
                                            "margin": "none"
                                        }
                                        ]
                                    },
                                    {
                                        "type": "text",
                                        "text": f"出發時間：{get_Sheet_time(web_driver_data.json()[i][4])}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "contents": [],
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"總時程：{time_hrmi(int(web_driver_data.json()[i][7]))}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"發起人：{web_driver_data.json()[i][10]}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"LineID：{web_driver_data.json()[i][11]}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"共乘人數上限：{web_driver_data.json()[i][6]}",
                                        "color": "#000000",
                                        "size": "xs"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"價格：{web_driver_data.json()[i][12]}",
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
                                        "text": f"集合地點：{web_driver_data.json()[i][3]}",
                                        "margin": "none",
                                        "size": "sm",
                                        "weight": "bold"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"簡介：{web_driver_data.json()[i][9]}",
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
                                        "displayText": f"我想共乘{web_driver_data.json()[i][2]}到{web_driver_data.json()[i][5]}!"
                                        },
                                        "style": "secondary"
                                    }
                                    ]
                                }
                            }
                            # 新增規範
                            if '上下車地點可討論' in web_driver_data.json()[i][8]:
                                r = {
                                            "type": "text",
                                            "text": "上下車地點可討論",
                                            "size": "sm",
                                            "margin": "none",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_driver_data_case['body']['contents'].insert(1,r)
                            if '自備零錢不找零' in web_driver_data.json()[i][8]:
                                r = {
                                            "type": "text",
                                            "text": "自備零錢不找零",
                                            "size": "sm",
                                            "margin": "none",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_driver_data_case['body']['contents'].insert(1,r)
                            if '接受線上付款 / 轉帳' in web_driver_data.json()[i][8]:
                                r = {
                                            "type": "text",
                                            "text": "接受線上付款 / 轉帳",
                                            "size": "sm",
                                            "margin": "none",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_driver_data_case['body']['contents'].insert(1,r)
                            if '禁食' in web_driver_data.json()[i][8]:
                                r = {
                                            "type": "text",
                                            "text": "禁食",
                                            "size": "sm",
                                            "margin": "none",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_driver_data_case['body']['contents'].insert(1,r)
                            if '※ 人滿才發車' in web_driver_data.json()[i][8]:
                                r = {
                                            "type": "text",
                                            "text": "※ 人滿才發車",
                                            "size": "sm",
                                            "margin": "none",
                                            "color": "#ff5551",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_driver_data_case['body']['contents'].insert(1,r)
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
                now_time = datetime.now()
                formatted_now_time = now_time.strftime('%Y/%#m/%#d')
                c_now_time = formatted_now_time.split('/')
                line_flex_json = {
                    "type": "carousel",
                    "contents": []
                }
                for i in range(web_passenger_len):
                    case = get_sheet_time_fordatetime(web_passenger_data.json()[i][4])
                    case_datetime = case.split('/')
                    date1 = date(int(c_now_time[0]),int(c_now_time[1]),int(c_now_time[2])) 
                    date2 = date(int(case_datetime[0]),int(case_datetime[1]),int(case_datetime[2]))
                    if date2>=date1: 
                        if web_passenger_data.json()[i][6] != web_passenger_data.json()[i][12]:
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
                                            "text": web_passenger_data.json()[i][5],
                                            "color": "#ffffff",
                                            "size": "lg",
                                            "weight": "bold",
                                            "margin": "none"
                                        }
                                        ]
                                    },
                                    {
                                        "type": "text",
                                        "text": f"出發時間：{get_Sheet_time(web_passenger_data.json()[i][4])}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "contents": [],
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"總時程：{time_hrmi(int(web_passenger_data.json()[i][7]))}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"發起人：{web_passenger_data.json()[i][10]}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"LineID：{web_passenger_data.json()[i][11]}",
                                        "color": "#000000",
                                        "size": "xs",
                                        "decoration": "underline"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"共乘人數上限：{web_passenger_data.json()[i][6]}",
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
                                        "text": f"集合地點：{web_passenger_data.json()[i][3]}",
                                        "margin": "none",
                                        "size": "sm",
                                        "weight": "bold"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"簡介：{web_passenger_data.json()[i][9]}",
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
                                        "displayText": f"我想共乘{web_passenger_data.json()[i][2]}到{web_passenger_data.json()[i][5]}!"
                                        },
                                        "style": "secondary"
                                    }
                                    ]
                                }
                            }
                            # 新增規範
                            if '上下車地點可討論' in web_passenger_data.json()[i][8]:
                                r = {
                                            "type": "text",
                                            "text": "上下車地點可討論",
                                            "size": "sm",
                                            "margin": "none",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_passenger_data_case['body']['contents'].insert(1,r)
                            if '不聊天' in web_passenger_data.json()[i][8]:
                                r = {
                                            "type": "text",
                                            "text": "不聊天",
                                            "size": "sm",
                                            "margin": "none",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_passenger_data_case['body']['contents'].insert(1,r)
                            if '嚴禁喝酒及抽菸' in web_passenger_data.json()[i][8]:
                                r = {
                                            "type": "text",
                                            "text": "嚴禁喝酒及抽菸",
                                            "size": "sm",
                                            "margin": "none",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_passenger_data_case['body']['contents'].insert(1,r)
                            if '禁食' in web_passenger_data.json()[i][8]:
                                r = {
                                            "type": "text",
                                            "text": "禁食",
                                            "size": "sm",
                                            "margin": "none",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_passenger_data_case['body']['contents'].insert(1,r)
                            if '謝絕寵物' in web_passenger_data.json()[i][8]:
                                r = {
                                            "type": "text",
                                            "text": "謝絕寵物",
                                            "size": "sm",
                                            "margin": "none",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_passenger_data_case['body']['contents'].insert(1,r)
                            if '寵物需裝籠' in web_passenger_data.json()[i][8]:
                                r = {
                                            "type": "text",
                                            "text": "寵物需裝籠",
                                            "size": "sm",
                                            "margin": "none",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_passenger_data_case['body']['contents'].insert(1,r)
                            if '※ 人滿才發車' in web_passenger_data.json()[i][8]:
                                r = {
                                            "type": "text",
                                            "text": "※ 人滿才發車",
                                            "size": "sm",
                                            "margin": "none",
                                            "color": "#ff5551",
                                            "contents": [],
                                            "offsetEnd": "none"
                                        }
                                web_passenger_data_case['body']['contents'].insert(1,r)
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
                        reservation = f'出發地：{web_driver_data.json()[i][2]}\n目的地：{web_driver_data.json()[i][5]}\n集合地點：{web_driver_data.json()[i][3]}\n出發時間：\n{get_Sheet_time(web_driver_data.json()[i][4])}\n總時程：{time_hrmi(int(web_driver_data.json()[i][7]))}\n發起人：{web_driver_data.json()[i][10]}\nLineID：{web_driver_data.json()[i][11]}\n共乘人數上限：{web_driver_data.json()[i][6]}\n價格：{web_driver_data.json()[i][12]}\n行車規範：\n{web_driver_data.json()[i][8]}\n簡介：{web_driver_data.json()[i][9]}\n'
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
                        reservation = f'出發地：{web_passenger_data.json()[i][2]}\n目的地：{web_passenger_data.json()[i][5]}\n集合地點：{web_passenger_data.json()[i][3]}\n出發時間：\n{get_Sheet_time(web_passenger_data.json()[i][4])}\n總時程：{time_hrmi(int(web_passenger_data.json()[i][7]))}\n發起人：{web_passenger_data.json()[i][10]}\nLineID：{web_passenger_data.json()[i][11]}\n共乘人數上限：{web_passenger_data.json()[i][6]}\n行車規範：\n{web_passenger_data.json()[i][8]}\n簡介：{web_passenger_data.json()[i][9]}\n'
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
                with ApiClient(configuration) as api_client:
                    line_bot_api = MessagingApi(api_client)
                    confirm_template = ConfirmTemplate(
                        text = f'出發地：{web_driver_data.json()[i][2]}\n目的地：{web_driver_data.json()[i][5]}\n集合地點：{web_driver_data.json()[i][3]}\n出發時間：\n{get_Sheet_time(web_driver_data.json()[i][4])}\n總時程：{time_hrmi(int(web_driver_data.json()[i][7]))}\n發起人：{web_driver_data.json()[i][10]}\nLineID：{web_driver_data.json()[i][11]}\n共乘人數上限：{web_driver_data.json()[i][6]}\n價格：{web_driver_data.json()[i][12]}\n行車規範：\n{web_driver_data.json()[i][8]}\n簡介：{web_driver_data.json()[i][9]}\n',
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
                pass
            # 使用者在Confirm Template按下確定後，試算表的搭車人數將+1
            if event.postback.data == f'driver_Sure{i}':
                get_driver_sheet_case()
                lock = threading.Lock()
                with ApiClient(configuration) as api_client:
                    line_bot_api = MessagingApi(api_client)
                    if web_driver_data.json()[i][6] != web_driver_data.json()[i][13]:
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
                            if driver_sheet.cell(i+2,14).value == None:
                                val = 0
                            else:
                                val = int(driver_sheet.cell(i+2,14).value) #因為dict只能start from 0，因此第一個共乘表單會在第0個，而google sheet第一行又是表單的項目，因此第一張表單會是i+1+1列。
                            driver_sheet.update_cell(i+2,14,val+1)
                            if driver_sheet.cell(i+2,15).value == None:
                                new_id = driver_user_id
                                new_name = driver_Sure_name
                            else:  
                                id = driver_sheet.cell(i+2,15).value
                                new_id = id+','+driver_user_id
                                name = driver_sheet.cell(i+2,16).value
                                new_name = name+','+driver_Sure_name
                            driver_sheet.update_cell(i+2,15,new_id) 
                            driver_sheet.update_cell(i+2,16,new_name)
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
    try:
        for i in range(web_passenger_len):
            if event.postback.data == f'passenger_Num{i}':
                with ApiClient(configuration) as api_client:
                    line_bot_api = MessagingApi(api_client)
                    confirm_template = ConfirmTemplate(
                        text = f'出發地：{web_passenger_data.json()[i][2]}\n目的地：{web_passenger_data.json()[i][5]}\n集合地點：{web_passenger_data.json()[i][3]}\n出發時間：\n{get_Sheet_time(web_passenger_data.json()[i][4])}\n總時程：{time_hrmi(int(web_passenger_data.json()[i][7]))}\n發起人：{web_passenger_data.json()[i][10]}\nLineID：{web_passenger_data.json()[i][11]}\n共乘人數上限：{web_passenger_data.json()[i][6]}\n行車規範：\n{web_passenger_data.json()[i][8]}\n簡介：{web_passenger_data.json()[i][9]}\n',
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
            else:
                pass
            # 使用者在Confirm Template按下確定後，試算表的搭車人數將+1
            if event.postback.data == f'passenger_Sure{i}':
                get_passenger_sheet_case()
                with ApiClient(configuration) as api_client:
                    line_bot_api = MessagingApi(api_client)
                    if web_passenger_data.json()[i][6] != web_passenger_data.json()[i][13]:
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
                            if passenger_sheet.cell(i+2,13).value == None:
                                val = 0
                            else:
                                val = int(passenger_sheet.cell(i+2,13).value) #因為dict只能start from 0，因此第一個共乘表單會在第0個，而google sheet第一行又是表單的項目，因此第一張表單會是i+1+1列。
                            passenger_sheet.update_cell(i+2,13,val+1)
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
        if i not in web_driver_Sure:
            if web_driver_data.json()[i][13]== web_driver_data.json()[i][6]:
                name_list = driver_Sure_name_dict.get(i).split(',')
                output = ','.join(map(str, name_list))
                html =f'''
                <h1>暨大共乘</h1>
                <div>您在NCNUcarpool發起的活動人數已滿了，活動資訊如下：</div>
                <div>出發地：{web_driver_data.json()[i][2]}<br>目的地：{web_driver_data.json()[i][5]}<br>集合地點：{web_driver_data.json()[i][3]}<br>出發時間：<br>{get_Sheet_time(web_driver_data.json()[i][4])}<br>總時程：{time_hrmi(int(web_driver_data.json()[i][7]))}<br>發起人：{web_driver_data.json()[i][10]}<br>LineID：{web_driver_data.json()[i][11]}<br>共乘人數上限：{web_driver_data.json()[i][6]}<br>價格：{web_driver_data.json()[i][12]}<br>行車規範：<br>{web_driver_data.json()[i][8]}<br>簡介：{web_driver_data.json()[i][9]}<br></div>
                <div>參加者Line名稱:{output}<div>
                '''
                mail = MIMEText(html, 'html', 'utf-8')   # plain 換成 html，就能寄送 HTML 格式的信件
                mail['Subject']='您在 NCNUcarpool 發起的活動人數已滿囉'
                mail['From']='NCNUcarpool'
                mail['To']= web_driver_data.json()[0][1]
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
                driver_Sure = web_driver_data.json()[i][14]
                driver_Sure_list = driver_Sure.split('/')
                for r in driver_Sure_list:
                    #   注意前方要有 Bearer
                    headers = {'Authorization':'Bearer UlaItdkkQW33Qln6YyLrLsLDo83MhILpEzQbtmQGiyk6Y6XbxGQ+sr0jjJb4TX8QhUTn3ZHim0LbFpyQ09SR/dEI09B30r4exhTcGJE+68Jbcyp75Ze3mvv2U9bF+G77dVSGKrdZcuQ5E7M8eJ6OFwdB04t89/1O/w1cDnyilFU=','Content-Type':'application/json'}
                    body = {
                        'to':f'{r}',
                        'messages':[{
                                'type': 'text',
                                'text': '您參加的活動人數已滿囉，記得透過LineID聯繫活動發起人!'
                            }]
                        }
                    # 向指定網址發送 request
                    req = requests.request('POST', 'https://api.line.me/v2/bot/message/push',headers=headers,data=json.dumps(body).encode('utf-8'))
                    # 印出得到的結果
                    print(req.text)

    for i in range(web_passenger_len):
        if i not in web_passenger_Sure :
            if web_passenger_data.json()[i][12] == web_passenger_data.json()[i][6]:
                name_list = passenger_Sure_name_dict.get(i).split(',')
                output = ','.join(map(str, name_list))
                html =f'''
                <h1>暨大共乘</h1>
                <div>您在NCNUcarpool發起的活動人數已滿了，活動資訊如下：</div>
                <div>出發地：出發地：{web_passenger_data.json()[i][2]}<br>目的地：{web_passenger_data.json()[i][5]}<br>集合地點：{web_passenger_data.json()[i][3]}<br>出發時間：<br>{get_Sheet_time(web_passenger_data.json()[i][4])}<br>總時程：{time_hrmi(int(web_passenger_data.json()[i][7]))}<br>發起人：{web_passenger_data.json()[i][10]}<br>LineID：{web_passenger_data.json()[i][11]}<br>共乘人數上限：{web_passenger_data.json()[i][6]}<br>行車規範：<br>{web_passenger_data.json()[i][8]}<br>簡介：{web_passenger_data.json()[i][9]}<br></div>
                <div>參加者Line名稱:{output}<div>
                '''
                mail = MIMEText(html, 'html', 'utf-8')   # plain 換成 html，就能寄送 HTML 格式的信件
                mail['Subject']='您在 NCNUcarpool 發起的活動人數已滿囉'
                mail['From']='NCNUcarpool'
                mail['To']= web_passenger_data.json()[0][1]
                try:
                    smtp = smtplib.SMTP('smtp.gmail.com', 587)
                    smtp.ehlo()
                    smtp.starttls()
                    smtp.login('ncnucarpool@gmail.com','jrab omvk bkql rruu')
                    status = smtp.send_message(mail)
                    print(status)
                    smtp.quit()
                    # 將此索引添加到已處理集合中
                    web_passenger_Sure.add(i)
                    print(f"乘客 {i} 已標記為處理完成")
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
                                'text': '您參加的活動人數已滿囉，記得透過LineID聯繫活動發起人!'
                            }]
                        }
                    # 向指定網址發送 request
                    req = requests.request('POST', 'https://api.line.me/v2/bot/message/push',headers=headers,data=json.dumps(body).encode('utf-8'))
                    # 印出得到的結果
                    print(req.text)
                
#   每隔3秒檢查試算表內容，若人數達上限即通知活動發起者人數已滿
def run_scheduler():
    global a
    a = True
    while a:
        schedule.run_pending()
        time.sleep(0.1)  
schedule.every(7).seconds.do(check_project)
scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.daemon = True 
scheduler_thread.start()
