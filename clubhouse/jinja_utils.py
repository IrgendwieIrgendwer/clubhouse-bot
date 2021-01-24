import re


def regex_replace(s):
    return re.sub(r'~~(.*?)~~', r'<strike>\1</strike>', s)
