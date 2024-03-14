def parse_keystring(s, return_name=False):
    keymap = {}
    for line in s.split("\n"):
        key=""
        content=""
        space_buffer = ""
        name = ""
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
        if key == "NAME":
            name = c
        keymap[key] = content
    return keymap