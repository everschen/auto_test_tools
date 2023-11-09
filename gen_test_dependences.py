#!/usr/bin/env python3
import re
import sys
import os
import glob

import matplotlib
matplotlib.use('TkAgg')  # Set the backend to TkAgg

import networkx as nx
import matplotlib.pyplot as plt


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
    external_apis_only_name = []
    for match in external_apis_matches:
        function_text = match.group()
        if(function_text.count('(') >= 2):
            #print(function_text)
            first_opening_bracket = function_text.find('(')
            last_closing_bracket = function_text.rfind(')')
            if first_opening_bracket != -1 and last_closing_bracket != -1 and first_opening_bracket < last_closing_bracket:
                content_between_brackets = function_text[first_opening_bracket + 1:last_closing_bracket]
                external_apis_inside, external_apis_only_name_ret = get_external_api(content_between_brackets, own_funcs)
                #print("inside external apis:", external_apis_inside)
                for item in external_apis_inside:
                    if all(func_name != item[0] for func_name, _ in external_apis):
                        if all(func_name != item[0] for func_name, _ in own_funcs):
                            external_apis.append(item)
                            external_apis_only_name.append(item[0])
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
                external_apis_only_name.append(external_api_name)
        #functions_inside = function_text


    return external_apis, external_apis_only_name


if len(sys.argv) != 2:
    print("Usage: python extract_functions.py your_c_file.c")
    sys.exit(1)

test_file = sys.argv[1]

# 用于匹配C函数声明和定义的正则表达式
#function_pattern = re.compile(r'\w+\s+\w+\s*\(.*?\)\s*{[^{}]*}', re.DOTALL)
#function_pattern = re.compile(r'(\w+)\S*\([^)]*\)\s*{', re.DOTALL)
function_pattern = re.compile(r'(\w+)\S*\((?:[^()]|\((?:[^()]|)*\))*\)\s*{', re.DOTALL)


# 用于从函数声明和定义中提取函数名称的正则表达式
#name_pattern = re.compile(r'\w+\s+(\w+)\s*\(.*?\)', re.DOTALL)
#name_pattern = re.compile(r'(\w+)\S*\([^)]*\)', re.DOTALL)
name_pattern = re.compile(r'(\w+)\S*\((?:[^()]|\((?:[^()]|)*\))*\)', re.DOTALL)

# 指定要枚举的目录路径
dir_files = ['/home/evers/jemalloc/src/*.c','/home/evers/jemalloc/include/jemalloc/*.h','/home/evers/jemalloc/include/jemalloc/internal/*.h']
#dir_files = ['/home/evers/jemalloc/src/*.c']

# 使用 os.listdir() 列出目录中的文件和子目录

depedences = []


for pattern in dir_files:
    matched_files = glob.glob(pattern)
    #print(matched_files)
    for source_file in matched_files:
        #print(source_file)
        parts = source_file.split('/')
        #module_name = parts[-2] +'-'+ parts[-1].replace('.', '_')
        #module_name = parts[-2] +'/'+ parts[-1]
        module_name = parts[-1]
        print(source_file, module_name)

        #sys.exit(1)
        try:
            # 打开C文件
            with open(source_file, 'r') as file:
                c_code = file.read()
                c_code = remove_comments(c_code)
                c_code = remove_preprocessor_content(c_code)
                #print(c_code)

            # 使用正则表达式查找函数声明和定义
            function_matches = function_pattern.finditer(c_code)

            # 提取函数名称
            #print(function_matches)
            function_names_with_para = []
            function_names = []
            for match in function_matches:
                #print(match)
                function_text = match.group()
                ret, parameters = non_func_define_check(function_text)
                if not ret:
                    continue
                #print(function_text)
                name_match = name_pattern.search(function_text)
                if name_match:
                    function_name = name_match.group(1)
                    if all(func_name != function_name for func_name, _ in function_names_with_para):
                        function_names_with_para.append((function_name, parameters))
                        function_names.append(function_name)
                    #print("Function Name:", function_name, "\n\n")


            external_apis, external_apis_only_name = get_external_api(c_code, function_names_with_para)



            #for name in function_names:
                #print("func impl: ", name)
            print("func impl len=", len(function_names))


            #for name in external_apis:
                #print("external api:", name)
            print("external api len=", len(external_apis))
            depedences.append((module_name, function_names, external_apis_only_name))
            print("")

        except FileNotFoundError:
            print(f"Error: File '{source_file}' not found.")
            sys.exit(1)



func_impls = []
for depedence in depedences:
    functions = depedence[1]
    for function in functions:
        matching_mods = [mod for func, mod in func_impls if func == function]
        if matching_mods:
            continue
            #print(function, "from " + depedence[0] + " already in func_impls from " + matching_mods[0])
        else:
            func_impls.append((function, depedence[0]))
            print(function, depedence[0])

print("func_impls len=", len(func_impls))
#print(func_impls)

# 创建一个有向图
G = nx.DiGraph()
mod_dependencies = []

parts = test_file.split('/')
module_name = parts[-1]
modules_g = []

with open(test_file, 'r') as file:
    c_code = file.read()
    c_code = remove_comments(c_code)
    c_code = remove_preprocessor_content(c_code)
external_apis, external_apis_only_names = get_external_api(c_code, function_names_with_para)
print(external_apis_only_names)
# for depedence in depedences:
#     external_apis = depedence[2]
for external_apis_only_name in external_apis_only_names:
    matching_mods = [mod for func, mod in func_impls if func == external_apis_only_name]
    print(external_apis_only_name, matching_mods)
    if matching_mods:
        if (module_name, matching_mods[0]) not in mod_dependencies:
            mod_dependencies.append((module_name, matching_mods[0]))
            modules_g.append(matching_mods[0])
        if module_name not in modules_g:
            modules_g.append(module_name)
    # else:
    #     print("ERROR:", external_api, "not found in func_impls")





# 添加模块节点

center_node = module_name

print("mod_dependencies len=", len(mod_dependencies))
print("modules_g len=", len(modules_g))
#print("func_impls", list(func_impls))
G.add_nodes_from(modules_g)
G.add_edges_from(mod_dependencies)

# 绘制图形
pos = nx.circular_layout(G, scale=1)

if len(pos) > 2:
    pos[center_node] = [0, 0]
    x_offset = 0
    y_offset = 0

    for node in pos:
        if node != center_node:
            x_offset += pos[node][0]
            y_offset += pos[node][1]

    x_offset = x_offset/(len(pos) -1)
    y_offset = y_offset/(len(pos) -1)
    pos[center_node] = [x_offset, y_offset]

print(pos)


nx.draw(G, pos, with_labels=True, node_size=2000, node_color='lightblue', font_size=10, font_weight='bold', arrows=True)
plt.title(module_name + '模块依赖图')
plt.show()