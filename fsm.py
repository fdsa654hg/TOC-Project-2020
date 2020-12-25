from transitions.extensions import GraphMachine
import googletrans

from utils import send_text_message
from linebot.models import MessageTemplateAction


which = ''
whichl = ''

class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)

    def is_going_to_language(self, event):
        text = event.message.text
        return text.lower() == 'start'

    def on_enter_language(self, event):

        reply_token = event.reply_token
        send_text_message(reply_token, "請輸入語種")

    def is_going_to_type(self, event):
        global whichl
        text = event.message.text
        send_text_message(reply_token, text)
        if text == '中文':
            whichl = text
            return True
        return False
    
    def on_enter_type(self, event):

        title = '請選擇翻譯方式'
        text = '您要『文字』還是『語音』'
        btn = [
            MessageTemplateAction(
                label = '文字',
                text ='文字'
            ),
            MessageTemplateAction(
                label = '語音',
                text = '語音'
            ),
        ]
        send_button_message(event.reply_token, title, text, btn)
    
    def is_going_to_text(self, event):
        global which
        text = event.message.text

        if text=='文字':
            which = text
            return True
        return False

    def on_enter_text(self, event):

        reply_token = event.reply_token
        send_text_message(reply_token, "文字已輸入")

    def is_going_to_sound(self, event):
        global which
        text = event.message.text

        if text=='語音':
            which = text
            return True
        return False

    def on_enter_sound(self, event):

        reply_token = event.reply_token
        send_text_message(reply_token, "語音已輸入")

    def is_going_to_stext(self, event):
        global whichl
        text = event.message.text
        translator = googletrans.Translator()
        if whichl=='中文':
            result = translator.translate('text', dest='zh-tw')
        reply_token = event.reply_token
        if result is not None:
            whichl = result
            return True
        
        return False
        

    def on_enter_stext(self, event):
        global whichl
        reply_token = event.reply_token
        send_text_message(reply_token, whichl)
        self.go_back()

    def is_going_to_ssound(self, event):
        return True

    def on_enter_ssound(self, event):

        reply_token = event.reply_token
        send_text_message(reply_token, "語音輸出")
        self.go_back()

