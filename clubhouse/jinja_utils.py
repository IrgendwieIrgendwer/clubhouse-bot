import re


def regex_replace(s):
    #re.sub(r'<(\\/)?p>', r'<\1div>',
    return re.sub(r'~~(.*?)~~', r'<strike>\1</strike>', s)
