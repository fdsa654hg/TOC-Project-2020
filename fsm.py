from transitions.extensions import GraphMachine
from googletrans import Translator

from utils import send_text_message, send_button_message
from linebot.models import MessageTemplateAction


whichl = ''

class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)

    def is_going_to_language(self, event):
        text = event.message.text
        return text.lower() == 'start'

    def on_enter_input_language(self, event):

        title = '請選擇目標語種'
        text = '想要翻譯成什麼語言呢'
        btn = [
            MessageTemplateAction(
                label = '英文(English)',
                text = '英文',
            ),
            MessageTemplateAction(
                label = '日文(Japanese)',
                text = '日文',
            ),
            MessageTemplateAction(
                label = '韓文(Korean)',
                text = '韓文',
            ),
            MessageTemplateAction(
                label = '法文(French)',
                text = '法文',
            ),
        ]
        send_button_message(event.reply_token, title, text, btn)
    
    def is_going_to_text(self, event):
        global whichl
        text = event.message.text

        if text == '英文':
            whichl = text
            return True
        elif text == '日文':
            whichl = text
            return True
        elif text == '韓文':
            whichl = text
            return True
        elif text == '法文':
            whichl = text
            return True

        return False

    def on_enter_input_text(self, event):

        reply_token = event.reply_token
        send_text_message(reply_token, "請輸入文字")

    def is_going_to_stext(self, event):
        reply_token = event.reply_token
        global whichl
        text = event.message.text
        translator = Translator()
        if whichl=='英文':
            result = translator.translate(text, dest='en').text
        elif whichl=='日文':
            result = translator.translate(text, dest='ja').text
        elif whichl=='韓文':
            result = translator.translate(text, dest='ko').text
        elif whichl=='法文':
            result = translator.translate(text, dest='fr').text
        if result is not None:
            whichl = result
            return True
        
        return False
        

    def on_enter_show_text(self, event):
        global whichl
        reply_token = event.reply_token
        send_text_message(reply_token, whichl+'\n\n"請輸入start以重新開始"')
        self.go_back()


