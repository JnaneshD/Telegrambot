from flask import Flask, request
import telegram
from telebot.credentials import bot_token, bot_user_name,URL
import re
import json
import requests
global bot
global TOKEN
TOKEN = bot_token
bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)

@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
   # retrieve the message in JSON and then transform it to Telegram object
   update = telegram.Update.de_json(request.get_json(force=True), bot)
   chat_id = update.message.chat.id
   msg_id = update.message.message_id
   # Telegram understands UTF-8, so encode text for unicode compatibility
   text = update.message.text.encode('utf-8').decode()
   # for debugging purposes only
   print("got text message :", text)
   # the first time you chat with the bot AKA the welcoming message
   if text == "/start":
       # print the welcoming message
       bot_welcome = """
       Welcome to JDBoT
       \nThe bot is using the service from http://avatars.adorable.io/ to generate cool looking avatars based on the name you enter so please enter a name and the bot will reply with an avatar for your name.
       \nType \n/meme to get some meme from reddit \n /joke to get some lame jokes \n /motivation to get some quotes lol.\n/corona to get the latest count of cases of India and Karnataka 
       """
       # send the welcoming message
       bot.sendMessage(chat_id=chat_id, text=bot_welcome, reply_to_message_id=msg_id)
   elif text=="/meme":
       r = requests.get("https://meme-api.herokuapp.com/gimme")
       meme = json.loads(r.text)
       url = meme['url']
       bot.sendPhoto(chat_id=chat_id, photo=url, reply_to_message_id=msg_id)
   elif text=="/joke":
       headers = {"Accept":"application/json"}
       r = requests.get("http://www.icanhazdadjoke.com/",headers=headers)
       joke = json.loads(r.text)
       jok = joke['joke']
       bot.sendMessage(chat_id=chat_id,text=jok,reply_to_message_id=msg_id)
   elif text=="/motivation":
       r = requests.get("https://www.affirmations.dev/")
       mot = json.loads(r.text)
       moti = mot["affirmation"]
       bot.sendMessage(chat_id=chat_id,text=moti,reply_to_message_id=msg_id)
   elif text=="/corona":
        r = requests.get("https://api.rootnet.in/covid19-in/stats/latest")
        data = json.loads(r.text)
        india_total = data['data']['summary']
        karnataka = data['data']['regional'][15]
        moti = "\nTotal India: "+str(india_total['total'])+" Recovered: "+str(india_total["discharged"])+" Deaths: "+str(india_total['deaths'])
        motik = "\nTotal Karnataka: "+str(karnataka['totalConfirmed'])+" Recovered: "+str(karnataka["discharged"])+" Deaths: "+str(karnataka['deaths'])
        ret = moti+motik
        html_text = ('<b>'+ret+'</b>')
        bot.sendMessage(chat_id=chat_id,text=html_text,reply_to_message_id=msg_id,parse_mode=ParseMode.HTML)
   else:
       try:
           # clear the message we got from any non alphabets
           text = re.sub(r"\W", "_", text)
           # create the api link for the avatar based on http://avatars.adorable.io/
           url = "https://api.adorable.io/avatars/285/{}.png".format(text.strip())
           # reply with a photo to the name the user sent,
           # note that you can send photos by url and telegram will fetch it for you
           bot.sendPhoto(chat_id=chat_id, photo=url, reply_to_message_id=msg_id)
       except Exception:
           # if things went wrong
           bot.sendMessage(chat_id=chat_id, text="There was a problem in the name you used, please enter different name", reply_to_message_id=msg_id)

   return 'ok'



@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    # we use the bot object to link the bot to our app which live
    # in the link provided by URL
    s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
    # something to let us know things work
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"

@app.route('/')
def index():
    return '.'

if __name__ == '__main__':
    # note the threaded arg which allow
    # your app to have more than one thread
    app.run(threaded=True)