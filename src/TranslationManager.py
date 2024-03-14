import os

class TranslationManager():
    def __init__(self, directory:str=None, mainwindow=None):
        self.directory = directory
        self.mainwindow = mainwindow
        self.languages = {}
        for filename in os.listdir(self.directory):
            language_code, language_name = self.parse_keystring(open(f"{self.directory}/{filename}", "r", encoding="utf-8").read(), return_name=True)
            self.languages[language_name] = language_code

    def parse_keystring(self, strings, return_name = False):
        keymap = {}
        name = ""
        for line in strings.split("\n"):
            key=""
            content=""
            space_buffer = ""
            mode="search_key"
            skip_special_key = False
            for c in line:
                if mode=="end":
                    continue
                if mode=="search_key":
                    if c == " ":
                        continue
                    else:
                        mode="load_key"
                if mode =="search_data":
                    if c=='"':
                        mode="read_data"
                    continue
                if mode=="load_key":
                    if c == "=":
                        mode="search_data"
                        continue
                    if c != " ":
                        key += space_buffer
                        space_buffer = ""
                    if c == " ":
                        space_buffer += c
                        continue
                    key += c
                if mode=="read_data":
                    if c =='\\' and not skip_special_key:
                        skip_special_key=True
                        continue
                    if c == '"' and not skip_special_key:
                        mode="end"
                        continue
                    content += c
                    skip_special_key = False
            if key == "" and content == "":
                continue
            if key == "NAME" and return_name:
                name = content
            else:
                keymap[key] = content
        if return_name:
            return keymap, name
        return keymap

    def change_language(self, language:str=None):
        if language in self.languages:
            for key, value in self.languages[language].items():
                if '.' in key:
                    method_name, attribute_name = key.split('.')
                    method = getattr(getattr(self.mainwindow.ui, method_name), attribute_name)
                    method(value)
                else:
                    method = getattr(self, key)
                    method(value)