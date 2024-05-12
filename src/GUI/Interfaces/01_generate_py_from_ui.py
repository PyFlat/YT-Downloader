import sys, os


def valid(line):
    for c in line:
        if c == " ":
            continue
        if c == '"' or c == "#":
            return False
        return True


try:
    # Usage: python <name> <infile> <outfile>

    content = open(sys.argv[1]).read().split("\n")
    res = []
    for line in content:
        if not valid(line):
            continue
        if "Form.setStyleSheet" in line:
            continue
        res.append(line)
    for line, i in enumerate(res):
        if line[0:5] == "class":
            res[i] = f"class {sys.argv[2].split('.')[0]}(QWidget):"
            res[i+1] = "    def init(self, parent):"
            res[i+2] = "        super().init(parent=parent)"
            res[i+3] = '        self.setObjectName("MainInterface")'
            res = res[:i+4] + ["        Form = self"] + res[i+4:]
            break
    open(sys.argv[2], "w").write("\n".join(res))
    os.remove(sys.argv[1])
except Exception as e:
    print(e)
    input()
