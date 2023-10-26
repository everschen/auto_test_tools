#!/usr/bin/env python3
import re
import sys

preprocessor_pattern = re.compile(r'#[^\n]*|/\*.*?\*/|//.*?$', re.MULTILINE | re.DOTALL)

def remove_preprocessor_content(c_code):
    # 使用正则表达式删除预处理内容
    c_code_cleaned = preprocessor_pattern.sub('', c_code)
    return c_code_cleaned

def remove_comments(c_code):
    # 删除多行注释
    c_code = re.sub(r'/\*.*?\*/', '', c_code, flags=re.DOTALL) 
    # 删除单行注释
    c_code = re.sub(r'//.*?$', '', c_code, flags=re.MULTILINE)
    return c_code

def non_func_define_check(text):
    pattern = re.compile(r'\([^)]+\)', re.MULTILINE)
    matches = pattern.findall(text)
    #result = re.findall(r'\((.*?)\)', text)
    for item in matches:
        #print(item)
        items = item.split(',')
        for sub_item in items:
            sub_item = sub_item.strip()
            #print(sub_item)
            if sub_item == 'void' or sub_item == '(void)':
                continue
            elif ' ' in sub_item:
                continue
            else:
                #print("sub_item", sub_item)
                return False
    return True

# 用于匹配C函数声明和定义的正则表达式
#function_pattern = re.compile(r'\w+\s+\w+\s*\(.*?\)\s*{[^{}]*}', re.DOTALL)
#function_pattern = re.compile(r'(\w+)\S*\([^)]*\)\s*{', re.DOTALL)
function_pattern = re.compile(r'(\w+)\S*\((?:[^()]|\((?:[^()]|)*\))*\)\s*{', re.DOTALL)


# 用于从函数声明和定义中提取函数名称的正则表达式
#name_pattern = re.compile(r'\w+\s+(\w+)\s*\(.*?\)', re.DOTALL)
#name_pattern = re.compile(r'(\w+)\S*\([^)]*\)', re.DOTALL)
name_pattern = re.compile(r'(\w+)\S*\((?:[^()]|\((?:[^()]|)*\))*\)', re.DOTALL)



if len(sys.argv) != 2:
    print("Usage: python extract_functions.py your_c_file.c")
    sys.exit(1)

c_file = sys.argv[1]

try:
    # 打开C文件
    with open(c_file, 'r') as file:
        c_code = file.read()
        c_code = remove_comments(c_code)
        c_code = remove_preprocessor_content(c_code)
        #print(c_code)

    # 使用正则表达式查找函数声明和定义
    function_matches = function_pattern.finditer(c_code)

    # 提取函数名称
    function_names = []
    for match in function_matches:
        function_text = match.group()
        if not non_func_define_check(function_text):
            continue
        #print(function_text)
        name_match = name_pattern.search(function_text)
        if name_match:
            function_name = name_match.group(1)
            function_names.append(function_name)
            #print("Function Name:", function_name, "\n\n")

    # 打印提取的函数名称

    for name in function_names:
        print(name)
    
    print("len=", len(function_names))

except FileNotFoundError:
    print(f"Error: File '{c_file}' not found.")
    sys.exit(1)

