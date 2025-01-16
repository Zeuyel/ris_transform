# 每一行 有这几种 可能
# 中文 或 英文 期刊 标题 一级标题
# 一级A 或 一级B 或 二级A 或 二级B  二级标题
# 序列号 
# 期刊 标题
# 期刊 idx
# 其他内容

#%%
# 分类存储 行号
dict = {
    'H1':[],
    'TOP':[], # 中文 或 英文
    '1A':[], # 中文 或 英文
    '1B':[], # 中文
    'content1':[], 
    'content2':[], 
    'content3':[], 
    'other':[],
}

other_list = ['序号\n','期刊名称\n','国内刊号（CN）\n']

#%%
paper_name = ''
with open('期刊.txt', 'r', encoding='utf-8') as file:
    # for id,line in enumerate(file):
    #     print(id,line)
    #     if id == 10:
    #         break
    a = file.readlines()
    for id,line in enumerate(a):
        if line[0] == '一' or line[0] == '二':
            dict['H1'].append(id)
        elif line[0] == "（":
            if line[3] == 'T':
                dict['TOP'].append(id)
            elif line[5] == 'A':
                dict['1A'].append(id)
            elif line[5] == 'B':
                dict['1B'].append(id)
        else:
            if line.isupper() and len(line.split('-')) == 1: # 国内刊号 也会触发全为 大写 条件
                pass
            else:    
                try:
                    float(line.strip())
                    dict['content1'].append(id)
                except ValueError:
                    if len(line.split('-')) == 2 or line == '\u3000\n' or line == '\n' or line == ' \n':
                        dict['content3'].append(id)
                        for i in range(dict['content1'][-1]+1,id):
                            paper_name += a[i].strip()
                        dict['content2'].append(paper_name)
                        paper_name = ''

#%%
len(dict['content1'])

#%%
len(dict['content2'])


dict['1B'][0]
#%%
import json
import numpy as np
# 创建一个字典用于存储期刊信息
journals = []

tree1 = np.array(dict['TOP'])
tree2 = np.array([
    [dict['1A'][0],dict['1B'][0]],
    [dict['1A'][1],99999]
    ])

# 遍历content2中的期刊名称
# 数轴 id
# TOP ---------- 1A ---------- 1B ---------- TOP ---------- 1A -------

# 树
#    top1                    top2
#    /   \                  /   \
#  1A     1B              1A     10000

#%%
for id,paper in enumerate(dict['content2']):
    line = dict['content3'][id]
    score = tree2[tree1 < line] < line
    if score.shape[0] == 2:
        score = score[1]

    if score.sum() == 0:
        level = 'TOP'
    elif score.all():
        level = '1B'
    else:
        level = '1A'
    journal = {
        "Paper_name": paper.strip(),  # 去除首尾空白字符
        "Level": level,  
    }
    journals.append(journal)

# 将数据保存为JSON文件
with open('ZUFE.json', 'w', encoding='utf-8') as f:
    json.dump(journals, f, ensure_ascii=False, indent=4)
# %%

import pandas as pd

# 读取Excel文件
df_fms = pd.read_excel('global.xlsx')

# 将第一行设置为列名
df_fms.columns = df_fms.iloc[1]
# 删除第一行数据(原标题行)
df_fms = df_fms.iloc[2:].reset_index(drop=True)


# 创建一个新的列表来存储期刊信息
journals = []

# 遍历DataFrame的每一行
for index, row in df_fms.iterrows():
    journal = {
        "Paper_name": row["期刊名称"],  # 去除首尾空白字符
        "Level": row["FMS等级"]
    }
    journals.append(journal)

# 将数据保存为JSON文件
with open('FMS.json', 'w', encoding='utf-8') as f:
    json.dump(journals, f, ensure_ascii=False, indent=4)


# %%
import toml
import json

# 读取TOML文件
with open('config.toml', 'r', encoding='utf-8') as f:
    config = toml.load(f)

# 只保存核心数据
data = config['params']['journal']['list'] + config['params']['conf']['list']

with open('ccf_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# %%
import requests
import json
import time

# URL和查询参数
base_url = "https://pqzas87g1f-3.algolianet.com/1/indexes/*/queries"
params = {
    "x-algolia-agent": "Algolia for JavaScript (4.24.0); Browser (lite); instantsearch.js (4.75.1); Vue (3.5.12); Vue InstantSearch (4.19.7); JS Helper (3.22.5)",
    "x-algolia-api-key": "d6a828ee96b827130b256dde6b196464", 
    "x-algolia-application-id": "PQZAS87G1F"
}

# 请求头
headers = {
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://charteredabs.org",
    "Referer": "https://charteredabs.org/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"'
}

# 分页获取所有数据
all_hits = []
page = 0
hits_per_page = 50  # 每页获取1000条记录


while True:
    # 构造请求体
    request_data = {
        "requests": [{
            "indexName": "dev_CABS_AJG",  # 修正索引名称
            "params": f"facets=%5B%22ajg_2021%22%2C%22ajg_2024%22%2C%22field%22%2C%22publisher%22%5D&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&hitsPerPage={hits_per_page}&maxValuesPerFacet=999&page={page}&query="
        }]
    }

    try:
        # 发送POST请求
        response = requests.post(
            base_url,
            params=params, 
            headers=headers,
            data=json.dumps(request_data)  # 将字典转换为JSON字符串
        )

        # 检查响应状态码
        if response.status_code == 200:
            # 解析响应数据
            response_data = response.json()
            hits = response_data['results'][0]['hits']
            
            if not hits:  # 如果没有更多数据则退出循环
                break
                
            all_hits.extend(hits)  # 将本页数据添加到总列表中
            print(f"第{page+1}页: 获取到 {len(hits)} 条记录")
            page += 1  # 页码加1
            
            time.sleep(0.5)  # 添加延迟避免请求过快
            
        else:
            print(f"请求失败,状态码: {response.status_code}")
            break
            
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
        break

# 将所有结果保存到文件
with open('response_data.json', 'w', encoding='utf-8') as f:
    json.dump(all_hits, f, ensure_ascii=False, indent=2)
print(f"总共获取到 {len(all_hits)} 条记录,数据已保存到 response_data.json")


# %%
# 读取 response_data.json 文件
with open('response_data.json', 'r', encoding='utf-8') as f:
    response_data = json.load(f)
    # 提取 title 和 ajg_2024 属性
    ajg2024_data = []
    for item in response_data:
            ajg2024_data.append({
            "Paper_name": item["title"],
            "Level": item["ajg_2024"]
        })
    
    # 保存简化后的数据到新文件
    with open('ajg_2024.json', 'w', encoding='utf-8') as f:
        json.dump(ajg2024_data, f, ensure_ascii=False, indent=4)
    
    print(f"已提取 {len(ajg2024_data)} 条记录的标题和等级信息,保存到 ajg_2024.json")

# %%
