import requests
import telebot
from telebot import types
import flask

appname="test-bot-ainur"
token="741658068:AAHC5WWTIL1LN_fUICoeCKxw9GUC5NOSct0"
bot = telebot.TeleBot(token)

apikey="a5f0fc8611a415ab2f3dddca814f4516"

@bot.message_handler(commands=["start"])
def HandleStart(msg):
    chatId=msg.chat.id
    name=msg.from_user.first_name
    
    reply = "Hello,"+name+"!\n"
    reply+= "Type any song title to find out its lyrics!\n"
    bot.send_message(chatId,reply)

@bot.message_handler(content_types=['text'])
def HandleText(msg):
    chatId = msg.chat.id
    song_title=msg.text.lower()

    link="http://api.musixmatch.com/ws/1.1/track.search?apikey="+apikey
    link += "&page_size=3&page=1&s_track_rating=desc"
    link +="&q_track="+song_title
    data=requests.get(link)
    json=data.json()

    track_list=json["message"]["body"]["track_list"]
    if len(track_list)>1:
        bot.send_message(chatId,"Hm...It looks like there're several songs with such title...")

        keyboard=types.InlineKeyboardMarkup()
        for t in track_list:
            song_artist = t["track"]["artist_name"]
            song_id = t["track"]["track_id"]
            btn=types.InlineKeyboardButton(song_artist,callback_data=song_id)
            keyboard.row(btn)
        btn=types.InlineKeyboardButton("None of them!",callback_data="None")
        keyboard.row(btn)
        bot.send_message(chatId,"Please, choose the artist of the song:",reply_markup=keyboard)
    else:
        track_id = track_list[0]["track"]["track_id"]     
        SendLyrics(chatId,track_id)

@bot.callback_query_handler(func=lambda call: True)
def HandleInlineButton(call):
    chatId=call.message.chat.id
    if call.message:
        if call.data=="None":
            bot.send_message(chatId,"Sorry... Try another song!")
        else:                             
            track_id = call.data        
            SendLyrics(chatId,track_id)
        

def SendLyrics(chatId,track_id):
    link="http://api.musixmatch.com/ws/1.1/track.lyrics.get?apikey="+apikey
    link +="&track_id="+track_id
    data=requests.get(link)
    json=data.json()

    lyrics=json["message"]["body"]["lyrics"]["lyrics_body"]
    bot.send_message(chatId,lyrics)
    bot.send_message(chatId,"One more? Write next title!")

@server.route('/' + token, methods=['POST'])
def get_message():
     bot.process_new_updates([types.Update.de_json(flask.request.stream.read().decode("utf-8"))])
     return "!", 200

@server.route('/', methods=["GET"])
def index():
     bot.remove_webhook()
     bot.set_webhook(url=f"https://{appname}.herokuapp.com/{token}")
     return "Hello from Heroku!", 200
     

if __name__ == "__main__":
     server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
#bot.polling(none_stop=True)
