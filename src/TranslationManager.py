import os

class TranslationManager():
    def __init__(self, directory:str=None, mainwindow=None):
        self.directory = directory
        self.mainwindow = mainwindow
        self.languages = {}
        self.language = None
        for filename in os.listdir(self.directory):
            file = open(f"{self.directory}/{filename}", "r", encoding="utf-8").read()
            language_code, language_name = self.parse_keystring(file, return_name=True, return_sections=["default", "inline"])
            self.languages[language_name] = language_code

    def parse_keystring(self, strings, return_name = False, return_sections=["default"]):
        sections = {"default":{}}
        active_section="default"
        keymap = {}
        _name = ""
        for line in strings.split("\n"):
            if len(line) > 0:
                if line[0] == "#":
                    section_name = line[1:]
                    sections[active_section] = keymap
                    active_section = section_name
                    if not section_name in sections:
                        sections[section_name] = {}
                    keymap = sections[section_name]
                    continue
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
                _name = content
            else:
                keymap[key] = content
        sections[active_section] = keymap
        returns = {}
        if len(return_sections) == 1:
            if return_sections[0] in sections:
                returns = sections[return_sections[0]]
            else:
                raise NameError(f"Return section {return_sections[0]} was not found!")
        else:
            for name in return_sections:
                if not name in sections:
                    raise NameError(f"Return section {name} was not found!")
                returns[name] = sections[name]
        if return_name:
            return returns, _name
        return returns

    def change_language(self, language: str = None):
        if language in self.languages:
            self.language = language
            for key, value in self.languages[language]["default"].items():
                try:
                    if key.startswith("__"):
                        method_name, attribute_name = key.split('.')
                        index = int(method_name[-1]) if not method_name.endswith("m") else 0
                        obj = self.mainwindow.ui.tableWidget.horizontalHeaderItem(index)
                        method = getattr(obj, attribute_name)
                        method(value)
                    elif '.' in key:
                        method_name, attribute_name = key.split('.')
                        method = getattr(getattr(self.mainwindow.ui, method_name), attribute_name)
                        method(value)
                    else:
                        method = getattr(self.mainwindow, key)
                        method(value)
                except Exception as e:
                    print(e, key)

    def get_inline_string(self, originalKey: str = None) -> str:
        if self.language in self.languages:
            key = self.languages[self.language]["inline"].get(originalKey, None)
            if key is None:
                key = self.languages["English"]["inline"].get(originalKey)

            return key

        else:
            return f"Language '{self.language}' is not supported."
