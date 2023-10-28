#!/usr/bin/env python3
# 输入字符串


import matplotlib
matplotlib.use('TkAgg')  # Set the backend to TkAgg

import networkx as nx
import matplotlib.pyplot as plt

# 创建一个有向图
G = nx.DiGraph()

# 添加模块节点
modules = ['moduleA', 'moduleB', 'moduleC', 'moduleD', 'moduleE', 'moduleF']
G.add_nodes_from(modules)

# 添加依赖关系
dependencies = [
    ('moduleA', 'moduleB'),
    ('moduleA', 'moduleC'),
    ('moduleB', 'moduleD'),
    ('moduleC', 'moduleE'),
    ('moduleD', 'moduleF'),
    ('moduleE', 'moduleF')
]
G.add_edges_from(dependencies)

# 绘制图形
pos = nx.spring_layout(G, seed=42)  # 指定布局算法
nx.draw(G, pos, with_labels=True, node_size=1000, node_color='lightblue', font_size=10, font_weight='bold', arrows=True)
plt.title('Python模块依赖图')
plt.show()
