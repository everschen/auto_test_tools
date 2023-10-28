#!/usr/bin/env python3
import re
import sys

#preprocessor_pattern = re.compile(r'#[^\n]*|/\*.*?\*/|//.*?$', re.MULTILINE | re.DOTALL)
preprocessor_pattern = re.compile(r'^#[^\n]*|/\*.*?\*/|//.*?$|##|', re.MULTILINE | re.DOTALL)

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
                return False, matches
    return True, matches

def non_external_api_check(text):
    pattern = re.compile(r'\([^)]+\)', re.MULTILINE)
    matches = pattern.findall(text)
    #result = re.findall(r'\((.*?)\)', text)
    for item in matches:
        content_inside_brackets = item[1:-1]
        #print(item)
        items = content_inside_brackets.split(',')
        for sub_item in items:
            sub_item = sub_item.strip()
            #print(sub_item)
            if ' ' in sub_item:
                #print("sub_item has space:", sub_item)
                return False, matches
            # else:
            #     #print("sub_item", sub_item)
            #     return False, matches
    return True, matches


def get_external_api(c_code, own_funcs):
    external_api_pattern = re.compile(r'(\w+)\w*\((?:[^()]|\((?:[^()]|)*\))*\)', re.DOTALL)
    external_api_name_pattern = re.compile(r'(\w+)\w*\((?:[^()]|\((?:[^()]|)*\))*\)', re.DOTALL)
    # 使用正则表达式查找函数声明和定义
    external_apis_matches = external_api_pattern.finditer(c_code)

    # 提取函数名称
    external_apis = []
    for match in external_apis_matches:
        function_text = match.group()
        if(function_text.count('(') >= 2):
            #print(function_text)
            first_opening_bracket = function_text.find('(')
            last_closing_bracket = function_text.rfind(')')
            if first_opening_bracket != -1 and last_closing_bracket != -1 and first_opening_bracket < last_closing_bracket:
                content_between_brackets = function_text[first_opening_bracket + 1:last_closing_bracket]
                external_apis_inside = get_external_api(content_between_brackets, own_funcs)
                #print("inside external apis:", external_apis_inside)
                for item in external_apis_inside:
                    if all(func_name != item[0] for func_name, _ in external_apis):
                        if all(func_name != item[0] for func_name, _ in own_funcs):
                            external_apis.append(item)
                #external_apis.extend(external_apis_inside)
        ret, parameters = non_external_api_check(function_text)
        if not ret:
            #print("false:", function_text)
            continue
        #print(function_text)
        name_match = external_api_name_pattern.search(function_text)
        external_api_name = name_match.group(1)
        if all(func_name != external_api_name for func_name, _ in external_apis):
            if all(func_name != external_api_name for func_name, _ in own_funcs):
                external_apis.append((external_api_name, parameters))
        #functions_inside = function_text


    return external_apis


# 用于匹配C函数声明和定义的正则表达式
#function_pattern = re.compile(r'\w+\s+\w+\s*\(.*?\)\s*{[^{}]*}', re.DOTALL)
#function_pattern = re.compile(r'(\w+)\S*\([^)]*\)\s*{', re.DOTALL)
#function_pattern = re.compile(r'(\w+)\S*\((?:[^()]|\((?:[^()]|)*\))*\)\s*{', re.DOTALL)
function_pattern = re.compile(r'(\w+)\w*\((?:[^()]|\((?:[^()]|)*\))*\)\s*{', re.DOTALL)

# 用于从函数声明和定义中提取函数名称的正则表达式
#name_pattern = re.compile(r'\w+\s+(\w+)\s*\(.*?\)', re.DOTALL)
#name_pattern = re.compile(r'(\w+)\S*\([^)]*\)', re.DOTALL)
name_pattern = re.compile(r'(\w+)\w*\((?:[^()]|\((?:[^()]|)*\))*\)', re.DOTALL)



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
    #print(c_code)

    # 提取函数名称
    function_names = []
    #print(function_matches)
    #items_list = list(function_matches)
    #print(items_list)
    #print(len(function_matches))
    for match in function_matches:
        #print("1", match)
        function_text = match.group()
        #print("2", function_text)
        ret, parameters = non_func_define_check(function_text)
        #print("3", ret, parameters)
        if not ret:
            continue
        print(function_text)
        name_match = name_pattern.search(function_text)
        print("4", name_match, "\n")
        if name_match:
            function_name = name_match.group(1)
            print("5", function_name, "\n")
            if all(func_name != function_name for func_name, _ in function_names):
                function_names.append((function_name, parameters))
            #print("Function Name:", function_name, "\n\n")


    print("")
    for name in function_names:
        print("func impl: ", name)
    print("func impl len=", len(function_names))

    external_apis = get_external_api(c_code, function_names)
    print("")
    for name in external_apis:
        print("external api:", name)
    print("external api len=", len(external_apis))

except FileNotFoundError:
    print(f"Error: File '{c_file}' not found.")
    sys.exit(1)

