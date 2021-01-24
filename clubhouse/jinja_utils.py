import re


def regex_replace(s):
    return re.sub(r'`(.*?)`', r'<span class="pre pre--inline">\1</span>', s)
