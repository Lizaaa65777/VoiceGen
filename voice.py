import os
import logging
import telebot
from telebot import types
from gtts import gTTS
import pyttsx3
import edge_tts
import asyncio


logging.basicConfig(level=logging.INFO)
token = '8049026907:AAEblYRbs9V3paCRxlSRp40Z6TiQ6R-neC0'
bot = telebot.TeleBot(token)

# ... (остальные импорты и глобальные переменные остаются без изменений)
HELP = """/help - Введите текст, который нужно озвучить
/start - Начало диалога
/voice - Выбор типа голоса (мужской или женский)
/reset - Сброс настроек
/support - Поддержка"""

start_text = """Привет! Я – VoiceGen, ваш помощник для превращения текста в голос. Вот что я могу для вас сделать:

1. Конвертировать текст в голос – просто отправьте текст, и я озвучу его.

2. Настройки голоса – настройте скорость, тембр и даже эмоциональность голоса под ваши предпочтения.

3. Выбор языка – я поддерживаю несколько языков, чтобы озвучка была максимально понятной и естественной.

Если нужна помощь, нажмите 'Помощь', и я подскажу, как пользоваться моими возможностями. Добро пожаловать в VoiceGen!"""
# Словарь для хранения настроек каждого пользователя
settings = {}


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
    settings_dict = settings.get(chat_id, {})
    
    lang = settings_dict.get("lang", "ru")  # По умолчанию русский язык
    
    def format_russian(text):
        return text
    
    def format_english(text):
        return text
    
    format_func = format_russian if lang == "ru" else format_english
    
    lang = settings_dict.get("lang", "No language selected")
    gender = settings_dict.get("gender", "No gender selected")
    volume = settings_dict.get("volume", "No volume selected")
    pitch = settings_dict.get("pitch", "No pitch selected")
    rate = settings_dict.get("rate", "No rate selected")
    settings_text = f"""
Current Settings for Chat ID {chat_id}:

Язык: {format_func(lang)}
Пол: {format_func(gender)}
Громкость: {format_func(volume)}
Тон: {format_func(pitch)}
Скорость: {format_func(rate)}
"""
    
    bot.send_message(chat_id, settings_text)

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    
    # Проверяем наличие настроек для пользователя
    if chat_id not in settings:
        reset_settings(chat_id)
        
    bot.send_message(message.chat.id, start_text)
    send_language_selection(message)


@bot.message_handler(commands='reset')
def reset_settings_command(message):
    chat_id = message.chat.id
    # Проверяем наличие настроек для пользователя
    reset_settings(chat_id)
    # Отправляем сообщение пользователю о сбросе настроек
    bot.send_message(chat_id, "Ваши настройки были сброшены. Пожалуйста, выберите язык, пол и настройку тона заново.")
    # Отправляем начальное сообщение для выбора языка
    bot.send_message(chat_id, "Привет! Я могу озвучить текст. Для начала выберите язык:")
    send_language_selection(message)


def send_language_selection(message):
    markup = types.InlineKeyboardMarkup()
    ru_button = types.InlineKeyboardButton("Русский", callback_data="ru")
    en_button = types.InlineKeyboardButton("Английский", callback_data="en")
    markup.add(ru_button, en_button)
    bot.send_message(message.chat.id, "Выберите язык:", reply_markup=markup)


def send_gender_selection(chat_id):
    markup = types.InlineKeyboardMarkup()
    male_button = types.InlineKeyboardButton("Мужской", callback_data="male")
    female_button = types.InlineKeyboardButton("Женский", callback_data="female")
    markup.add(male_button, female_button)
    bot.send_message(chat_id, "Выберите голос:", reply_markup=markup)


def send_rate_selection(chat_id):
    markup = types.InlineKeyboardMarkup()
    fast = types.InlineKeyboardButton("Быстро", callback_data="fast")
    normal = types.InlineKeyboardButton("Умеренно", callback_data="normal")
    slow = types.InlineKeyboardButton("Медленно", callback_data="slow")
    markup.add(fast, normal, slow)
    bot.send_message(chat_id, "Выберите настройку скорости:", reply_markup=markup)


def send_volume_selection(chat_id):
    markup = types.InlineKeyboardMarkup()
    loud = types.InlineKeyboardButton("Громко", callback_data="loud")
    normal = types.InlineKeyboardButton("Умеренно", callback_data="default")
    quiet = types.InlineKeyboardButton("Тихо", callback_data="quiet")
    markup.add(loud, normal, quiet)
    bot.send_message(chat_id, "Выберите настройку громкости:", reply_markup=markup)


def send_pitch_selection(chat_id):
    markup = types.InlineKeyboardMarkup()
    high = types.InlineKeyboardButton("Высоко", callback_data="high")
    normal = types.InlineKeyboardButton("Стандартно", callback_data="okay")
    low = types.InlineKeyboardButton("Низко", callback_data="low")
    markup.add(high, normal, low)
    bot.send_message(chat_id, "Выберите настройку тона:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    
    if call.data == "reset":
        reset_settings(chat_id)
        bot.answer_callback_query(callback_query_id=call.id, text="Настройки сброшены.")
    
    elif call.data in ["ru", "en"]:
        set_language(chat_id, call.data)
        bot.answer_callback_query(callback_query_id=call.id, text=f"Вы выбрали {call.data} язык.")
        
        if call.data == "ru":
            send_gender_selection(chat_id)
        else:
            send_gender_selection(chat_id)
    
    elif call.data in ["male", "female"]:
        set_gender(chat_id, call.data)
        bot.answer_callback_query(callback_query_id=call.id, text=f"Вы выбрали {call.data} голос.")
        send_rate_selection(chat_id)
    elif call.data in ["fast", "normal", "slow"]:
        set_rate(chat_id, call.data)
        bot.answer_callback_query(callback_query_id=call.id, text=f"Вы выбрали {call.data} скорость.")
        send_volume_selection(chat_id)
    elif call.data in ["loud", "default", "quiet"]:
        set_volume(chat_id, call.data)
        bot.answer_callback_query(callback_query_id=call.id, text=f"Вы выбрали {call.data} громкость.")
        send_pitch_selection(chat_id)
    elif call.data in ["high", "okay", "low"]:
        set_pitch(chat_id, call.data)
        bot.answer_callback_query(callback_query_id=call.id, text=f"Вы выбрали {call.data} тон.")
        bot.send_message(chat_id, "Теперь введите текст для озвучки.")


def set_rate(chat_id, rate):
    settings[chat_id]["rate"] = rate


def set_volume(chat_id, volume):
    settings[chat_id]["volume"] = volume


def set_pitch(chat_id, pitch):
    settings[chat_id]["pitch"] = pitch


def set_language(chat_id, lang):
    settings[chat_id]["lang"] = lang


def set_gender(chat_id, gender):
    settings[chat_id]["gender"] = gender


def reset_settings(chat_id):
    settings[chat_id] = {"lang": None, 
                         "gender": None, 
                         "rate": None, 
                         "volume": None, 
                         "pitch": None}

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

@bot.message_handler(content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id
    
    lang = settings.get(chat_id, {}).get("lang")
    gender = settings.get(chat_id, {}).get("gender")
    rate = settings.get(chat_id, {}).get("rate")
    volume = settings.get(chat_id, {}).get("volume")
    pitch = settings.get(chat_id, {}).get("pitch")
    
    print(f"Chat ID: {chat_id}, Lang: {lang}, Gender: {gender}, Volume: {volume}, Rate: {rate}, Pitch: {pitch}")  # Добавьте эту строку
    
    if lang and gender and rate and volume and pitch:
        try: 
            generating_message_id = bot.send_message(message.chat.id, "⏳ Запрос обрабатывается: Подождите несколько секунд, пока я создаю голосовое сообщение.").message_id
            
            # Настройка голоса
            voice_name = ""
            if lang == "ru":
                if gender == "male":
                    voice_name = "ru-RU-DmitryNeural"
                elif gender == "female":
                    voice_name = "ru-RU-SvetlanaNeural"
            else:
                if gender == "male":
                    voice_name = "en-US-AndrewNeural"
                elif gender == "female":
                    voice_name = "en-US-AvaNeural"
            
            asyncio.run(make_sound(chat_id, message.text, voice_name, rate, volume, pitch))

            bot.send_voice(chat_id, open(f"cache/audio{chat_id}.mp3", 'rb'))

            bot.delete_message(chat_id=message.chat.id, message_id=generating_message_id)
            logging.info(f"Sent audio file for chat ID: {chat_id}")
        except Exception as e:
            logging.error(f"Error generating audio: {str(e)}")
            bot.send_message(chat_id, f"🚫 Ошибка сервера: Возникли технические неполадки. Пожалуйста, попробуйте еще раз позже. Мы работаем над решением проблемы: {str(e)}")
    else:
        bot.send_message(chat_id, "Пожалуйста, выберите язык, пол и настройку тона.(Команда /start)")



bot.polling(non_stop=True)
