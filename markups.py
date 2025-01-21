from telebot import types


def lang_murkup():
    markup = types.InlineKeyboardMarkup()
    ru_button = types.InlineKeyboardButton("Русский", callback_data="ru")
    en_button = types.InlineKeyboardButton("Английский", callback_data="en")
    markup.add(ru_button, en_button)
    return markup

def gender_markup():
    markup = types.InlineKeyboardMarkup()
    male_button = types.InlineKeyboardButton("Мужской", callback_data="male")
    female_button = types.InlineKeyboardButton("Женский", callback_data="female")
    markup.add(male_button, female_button)
    return markup

def rate_markup():
    markup = types.InlineKeyboardMarkup()
    fast = types.InlineKeyboardButton("Быстро", callback_data="fast")
    normal = types.InlineKeyboardButton("Умеренно", callback_data="normal")
    slow = types.InlineKeyboardButton("Медленно", callback_data="slow")
    markup.add(fast, normal, slow)
    return markup

def volume_markup():
    markup = types.InlineKeyboardMarkup()
    loud = types.InlineKeyboardButton("Громко", callback_data="loud")
    normal = types.InlineKeyboardButton("Умеренно", callback_data="default")
    quiet = types.InlineKeyboardButton("Тихо", callback_data="quiet")
    markup.add(loud, normal, quiet)
    return markup

def pitch_markup():
    markup = types.InlineKeyboardMarkup()
    high = types.InlineKeyboardButton("Высоко", callback_data="high")
    normal = types.InlineKeyboardButton("Стандартно", callback_data="okay")
    low = types.InlineKeyboardButton("Низко", callback_data="low")
    markup.add(high, normal, low)
    return markup