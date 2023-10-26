#!/usr/bin/env python3
import re

# 用于匹配C函数定义的正则表达式，只匹配函数名，且位于左大括号之前
function_pattern = re.compile(r'(\w+)\s*\([^)]*\)\s*{', re.DOTALL)

c_code = """
JEMALLOC_ATTR
JEMALLOC_JET
JEMALLOC_ATTR(constructor)
static void
jemalloc_constructor(void) {
        malloc_init();
}
"""

function_matches = function_pattern.findall(c_code)

for match in function_matches:
    name = match.strip()  # 去除可能的空白
    print("Function Name:", name)
