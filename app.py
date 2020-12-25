import os
import sys

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from fsm import TocMachine
from utils import send_text_message

path3='development.env'
load_dotenv(dotenv_path=path3,verbose=True)

#load_dotenv()

machine = TocMachine(
    states=[
        "input_language",
        "input_type",
        "input_text",
        "input_sound",
        "show_text",
        "show_sound"
    ],
    transitions=[
        {
            "trigger": "advance",
            "source": "user",
            "dest": "input_language",
            "conditions": "on_enter_language",
        },
        {
            "trigger": "advance",
            "source": "input_language",
            "dest": "input_type",
            "conditions": "on_enter_type",
        },
        {
            "trigger": "advance",
            "source": "input_type",
            "dest": "input_text",
            "conditions": "on_enter_text",
        },
        {
            "trigger": "advance",
            "source": "input_type",
            "dest": "input_sound",
            "conditions": "on_enter_sound",
        },
        {
            "trigger": "advance",
            "source": "input_text",
            "dest": "show_text",
            "conditions": "on_enter_stext",
        },
        {
            "trigger": "advance",
            "source": "input_sound",
            "dest": "show_sound",
            "conditions": "on_enter_ssound",
        },
        {"trigger": "go_back", "source": ["input_language", "input_type", "input_text", "input_sound", "show_text", "show_sound"], "dest": "user"},
    ],
    initial="user",
    auto_transitions=False,
    show_conditions=True,
)

app = Flask(__name__, static_url_path="")

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

mode = 0

@app.route("/webhook", methods=["POST"])
def webhook_handler():
    global mode
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        print(f"\nFSM STATE: {machine.state}")
        print(f"REQUEST BODY: \n{body}")

        response = machine.advance(event)
        if response == False:
            if machine.state == 'user':
                send_text_message(event.reply_token, '輸入start開始翻譯')
            elif machine.state != 'user' and event.message.text.lower() == 'restart':
                send_text_message(event.reply_token, '輸入『fitness』即可開始使用健身小幫手。\n隨時輸入『chat』可以跟機器人聊天。\n隨時輸入『restart』可以從頭開始。\n隨時輸入『fsm』可以得到當下的狀態圖。')
                machine.go_back()
            elif machine.state == 'start':
                send_text_message(event.reply_token, '想翻成什麼語言？')
            elif machine.state == 'input_language':
                send_text_message(event.reply_token, '以文字或是語音作為輸入？')
            elif machine.state == 'input_text':
                send_text_message(event.reply_token, '請輸入文字...')
            elif machine.state == 'input_sound':
                send_text_message(event.reply_token, '請輸入語音...')
            elif machine.state == 'show_text':
                send_text_message(event.reply_token, '以下是文字翻譯')
            elif machine.state == 'show_sound':
                send_text_message(event.reply_token, '以下是語音翻譯')
            elif machine.state == 'restart':
                send_text_message(event.reply_token, '是否繼續翻譯？')
            


    return "OK"


@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    machine.get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")


if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)
