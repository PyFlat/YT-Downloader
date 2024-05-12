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
    for i, line in enumerate(res):
        class_name = sys.argv[2].split('.')[0]
        if line[0:5] == "class":
            res[i] = f"class {class_name}(QWidget):"
            res[i+1] = "    def __init__(self, parent):"
            res[i+2] = "        super().__init__(parent=parent)"
            res[i+3] = f'        self.setObjectName("{class_name}")'
            res = res[:i+4] + ["        Form = self"] + res[i+4:]
            break
    open(sys.argv[2], "w").write("\n".join(res))
    os.remove(sys.argv[1])
except Exception as e:
    print(e)
    input()
