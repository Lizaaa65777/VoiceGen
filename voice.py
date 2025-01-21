import logging
import telebot
from telebot import types
import edge_tts
import asyncio
import settings as set
import markups

logging.basicConfig(level=logging.INFO)
token = '8049026907:AAEblYRbs9V3paCRxlSRp40Z6TiQ6R-neC0'
bot = telebot.TeleBot(token)

# ... (остальные импорты и глобальные переменные остаются без изменений)
HELP = """/help - Введите текст, который нужно озвучить
/start - Начало диалога
/voice - Выбор типа голоса (мужской или женский)
/reset - Сброс настроек
/support - Поддержка"""

start_text = '''Привет! Я – VoiceGen, ваш помощник для превращения текста в голос. Вот что я могу для вас сделать:

1. Конвертировать текст в голос – просто отправьте текст, и я озвучу его.

2. Настройки голоса – настройте скорость, тембр и даже эмоциональность голоса под ваши предпочтения.

3. Выбор языка – я поддерживаю несколько языков, чтобы озвучка была максимально понятной и естественной.

Если нужна помощь, нажмите "Помощь", и я подскажу, как пользоваться моими возможностями. Добро пожаловать в VoiceGen!'''

settings = set.Settings()


@bot.message_handler(commands=['support'])
def support_command(message):
    urlkb = types.InlineKeyboardMarkup()
    urlButton2 = types.InlineKeyboardButton(text='Поддержка', url='https://t.me/ilkft')
    urlkb.add(urlButton2)
    bot.send_message(message.chat.id, "Поддержка", reply_markup=urlkb)


@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id, HELP)

@bot.message_handler(commands=['voice'])
def show_settings(message):
    chat_id = message.chat.id
    
    # Получаем текущие настройки пользователя
    user_settings = settings.get_user(chat_id)
    
    lang = user_settings.get("lang", "No language selected")
    gender = user_settings.get("gender", "No gender selected")
    volume = user_settings.get("volume", "No volume selected")
    pitch = user_settings.get("pitch", "No pitch selected")
    rate = user_settings.get("rate", "No rate selected")
    settings_text = f"""
Current Settings for Chat ID {chat_id}:

Язык: {lang}
Пол: {gender}
Громкость: {volume}
Тон: {pitch}
Скорость: {rate}
"""
    
    bot.send_message(chat_id, settings_text)

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    
    # Проверяем наличие настроек для пользователя
    if settings.get_user(chat_id) == {}:
        settings.reset_settings(chat_id)
        
    bot.send_message(message.chat.id, start_text)
    bot.send_message(chat_id, "Выберите язык:", reply_markup=markups.lang_murkup())


@bot.message_handler(commands='reset')
def reset_settings_command(message):
    chat_id = message.chat.id
    # Проверяем наличие настроек для пользователя
    settings.reset_settings(chat_id)
    # Отправляем сообщение пользователю о сбросе настроек
    bot.send_message(chat_id, "Ваши настройки были сброшены. Пожалуйста, выберите язык, пол и настройку тона заново.")
    # Отправляем начальное сообщение для выбора языка
    bot.send_message(chat_id, "Выберите язык:", reply_markup=markups.lang_murkup())
    

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    user_settings = settings.get_user(chat_id)
    if not user_settings:
        settings.reset_settings(chat_id)
    
    if call.data == "reset":
        settings.reset_settings(chat_id)
        bot.answer_callback_query(callback_query_id=call.id, text="Настройки сброшены.")
    
    elif call.data in ["ru", "en"]:
        settings.set_language(chat_id, call.data)
        bot.answer_callback_query(callback_query_id=call.id, text=f"Вы выбрали {call.data} язык.")
        bot.send_message(chat_id, "Выберите голос:", reply_markup=markups.gender_markup())
    
    elif call.data in ["male", "female"]:
        settings.set_gender(chat_id, call.data)
        bot.answer_callback_query(callback_query_id=call.id, text=f"Вы выбрали {call.data} голос.")
        bot.send_message(chat_id, "Выберите настройку скорости:", reply_markup=markups.rate_markup())
    
    elif call.data in ["fast", "normal", "slow"]:
        settings.set_rate(chat_id, call.data)
        bot.answer_callback_query(callback_query_id=call.id, text=f"Вы выбрали {call.data} скорость.")
        bot.send_message(chat_id, "Выберите настройку громкости:", reply_markup=markups.volume_markup())
    
    elif call.data in ["loud", "default", "quiet"]:
        settings.set_volume(chat_id, call.data)
        bot.answer_callback_query(callback_query_id=call.id, text=f"Вы выбрали {call.data} громкость.")
        bot.send_message(chat_id, "Выберите настройку тона:", reply_markup=markups.pitch_markup())
    
    elif call.data in ["high", "okay", "low"]:
        settings.set_pitch(chat_id, call.data)
        bot.answer_callback_query(callback_query_id=call.id, text=f"Вы выбрали {call.data} тон.")
        bot.send_message(chat_id, "Теперь введите текст для озвучки.")


rate_ttn = {"fast" : "+50%", #ttn - text to number
            "normal": "+0%",
            "slow" : "-50%"}

volume_ttn = {"loud" : "+50%",
            "default": "+0%",
            "quiet" : "-50%"}

pitch_ttn = {"high" : "+50Hz",
            "okay": "+0Hz",
            "low" : "-50Hz"}

async def make_sound(chat_id, text, voice_name, rate, volume, pitch):
    tts = edge_tts.Communicate(
        text=text,
        voice=voice_name,
        rate=rate_ttn[rate],
        volume=volume_ttn[volume],
        pitch=pitch_ttn[pitch]
    )
    await tts.save(f"cache/audio{chat_id}.mp3")

def voice_name_selection(lang, gender):
    if lang == "ru":
        if gender == "male":
            return "ru-RU-DmitryNeural"
        elif gender == "female":
            return "ru-RU-SvetlanaNeural"
    else:
        if gender == "male":
            return "en-US-AndrewNeural"
        elif gender == "female":
            return "en-US-AvaNeural"

@bot.message_handler(content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id

    user_settings = settings.get_user(chat_id)
    
    if user_settings:
        try:

            lang = user_settings["lang"]
            gender = user_settings["gender"]
            rate = user_settings["rate"]
            volume = user_settings["volume"]
            pitch = user_settings["pitch"]

            if lang and gender and rate and volume and pitch:
                generating_message_id = bot.send_message(message.chat.id, "⏳ Запрос обрабатывается: Подождите несколько секунд, пока я создаю голосовое сообщение.").message_id
                
                print(f"Chat ID: {chat_id}, Lang: {lang}, Gender: {gender}, Volume: {volume}, Rate: {rate}, Pitch: {pitch}")
                voice_name = voice_name_selection(lang, gender)
                
                asyncio.run(make_sound(chat_id, message.text, voice_name, rate, volume, pitch))

                bot.send_voice(chat_id, open(f"cache/audio{chat_id}.mp3", 'rb'))

                bot.delete_message(chat_id=message.chat.id, message_id=generating_message_id)
                logging.info(f"Sent audio file for chat ID: {chat_id}")
            else:
                bot.send_message(chat_id, "Пожалуйста, выберите язык, пол и настройку тона.(Команда /start)")

        except Exception as e:
            logging.error(f"Error generating audio: {str(e)}")
            bot.send_message(chat_id, f"🚫 Ошибка сервера: Возникли технические неполадки. Пожалуйста, попробуйте еще раз позже. Мы работаем над решением проблемы: {str(e)}")
    else:
        bot.send_message(chat_id, "Пожалуйста, выберите язык, пол и настройку тона.(Команда /start)")



bot.polling(non_stop=True)
