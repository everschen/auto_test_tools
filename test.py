#!/usr/bin/env python3
import re

text = "je_sallocx(const void *ptr, int flags) {"
#text = "je_sallocx(void) {"
result = re.findall(r'\((.*?)\)', text)


for item in result:
    print(item)
    items = item.split(',')
    for sub_item in items:
        sub_item = sub_item.strip()
        print(sub_item)
        if sub_item == 'void':
                continue
        elif ' ' in sub_item:
                continue
        else:
                return False
return True


