import logging
import telebot
from telebot import types
from gtts import gTTS
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
    mood = settings_dict.get("mood", "Neutral mood")

    settings_text = f"""
    Current Settings for Chat ID {chat_id}:

    Язык: {format_func(lang)}
    Пол: {format_func(gender)}
    Эмоция: {format_func(mood)}
    """
    bot.send_message(chat_id, settings_text)


@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id

    # Проверяем наличие настроек для пользователя
    if chat_id not in settings:
        # Если нет настроек, создаем их с базовым значением для языка
        set_language(chat_id, "ru")  # Предполагаем русский язык по умолчанию

    bot.send_message(message.chat.id, "Привет! Я могу озвучить текст. Для начала выберите язык:")
    send_language_selection(message)


@bot.message_handler(commands='reset')
def reset_settings(message):
    chat_id = message.chat.id
    # Проверяем наличие настроек для пользователя
    if chat_id in settings:
        # Если есть настройки, удаляем их
        del settings[chat_id]
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


def send_voice_selection(chat_id):
    markup = types.InlineKeyboardMarkup()
    male_button = types.InlineKeyboardButton("Мужской", callback_data="male")
    female_button = types.InlineKeyboardButton("Женский", callback_data="female")
    markup.add(male_button, female_button)
    bot.send_message(chat_id, "Выберите голос:", reply_markup=markup)


def send_mood_selection(chat_id):
    markup = types.InlineKeyboardMarkup()
    joyful = types.InlineKeyboardButton("Радостный", callback_data="joyful")
    cheerful = types.InlineKeyboardButton("Веселый", callback_data="cheerful")
    fear = types.InlineKeyboardButton("Страх", callback_data="fear")
    sad = types.InlineKeyboardButton("Грустный", callback_data="sad")
    angry = types.InlineKeyboardButton("Злой", callback_data="angry")
    markup.add(joyful, cheerful, fear, sad, angry)
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
            send_voice_selection(chat_id)
        else:
            send_voice_selection(chat_id)

    elif call.data in ["male", "female"]:
        set_gender(chat_id, call.data)
        bot.answer_callback_query(callback_query_id=call.id, text=f"Вы выбрали {call.data} голос.")
        send_mood_selection(chat_id)

    elif call.data in ["joyful", "cheerful", "fear", "sad", "angry"]:
        set_mood(chat_id, call.data)
        bot.answer_callback_query(callback_query_id=call.id, text=f"Вы выбрали {call.data} настройку тона.")
        bot.send_message(chat_id, "Теперь введите текст для озвучки.")


def set_language(chat_id, lang):
    settings[chat_id] = {"lang": lang, "gender": None, "mood": None}


def set_gender(chat_id, gender):
    settings[chat_id]["gender"] = gender


def set_mood(chat_id, mood):
    settings[chat_id]["mood"] = mood


def reset_settings(chat_id):
    settings.pop(chat_id, None)


async def make_sound(text, voice_name, id):
    tts = edge_tts.Communicate(
        text=text,
        voice=voice_name
    )
    await tts.save(f"audio{id}.mp3")


@bot.message_handler(content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id

    lang = settings.get(chat_id, {}).get("lang")
    gender = settings.get(chat_id, {}).get("gender")
    mood = settings.get(chat_id, {}).get("mood")

    print(f"Chat ID: {chat_id}, Lang: {lang}, Gender: {gender}, Mood: {mood}")

    if lang and gender and mood:
        try:
            generating_message_id = bot.send_message(message.chat.id,
                                                     "⏳ Запрос обрабатывается: Подождите несколько секунд, пока я создаю голосовое сообщение.").message_id
            # engine = pyttsx3.init()

            # Настройка голоса

            voice_name = 0
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

            asyncio.run(make_sound(message.text, voice_name, chat_id))
            bot.send_voice(chat_id, open(f"audio{chat_id}.mp3", 'rb'))

            bot.delete_message(chat_id=message.chat.id, message_id=generating_message_id)
            logging.info(f"Sent audio file for chat ID: {chat_id}")
        except Exception as e:
            logging.error(f"Error generating audio: {str(e)}")
            bot.send_message(chat_id, f"Произошла ошибка при генерации речи: {str(e)}")
    else:
        bot.send_message(chat_id, "Пожалуйста, выберите язык, пол и настройку тона.(Команда /start)")


bot.polling(non_stop=True)
