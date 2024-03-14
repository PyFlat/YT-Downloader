def parse_keystring(s):
    keymap = {}
    for line in s.split("\n"):
        key=""
        content=""
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
        keymap[key] = content
    return keymap