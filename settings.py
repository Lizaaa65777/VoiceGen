class Settings:

    def __init__(self):
        self.setting_dict = {}

    def set_rate(self, chat_id, rate):
        self.setting_dict[chat_id]["rate"] = rate


    def set_volume(self, chat_id, volume):
        self.setting_dict[chat_id]["volume"] = volume


    def set_pitch(self, chat_id, pitch):
        self.setting_dict[chat_id]["pitch"] = pitch


    def set_language(self, chat_id, lang):
        self.setting_dict[chat_id]["lang"] = lang


    def set_gender(self, chat_id, gender):
        self.setting_dict[chat_id]["gender"] = gender


    def reset_settings(self, chat_id):
        self.setting_dict[chat_id] = {"lang": None, 
                            "gender": None, 
                            "rate": None, 
                            "volume": None, 
                            "pitch": None}
    
    def get_user(self, chat_id):
        return self.setting_dict.get(chat_id, {})


sett = Settings()

print(sett.get_user(123))