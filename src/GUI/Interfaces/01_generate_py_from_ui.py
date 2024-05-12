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

    open(sys.argv[2], "w").write("\n".join(res))
    os.remove(sys.argv[1])
except Exception as e:
    print(e)
    input()
