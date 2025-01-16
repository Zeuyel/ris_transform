#%%
import json
import sys
from collections import defaultdict
import os
from deepxl import *

# 定义评价标准文件路径
RATING_FILES = {
    'CCF': 'ccf_data.json',
    'FMS': 'FMS.json',
    'AJG': 'ajg_2024.json',
    'ZUFE': 'zufe.json'
}

RATING = {
    'CCF': 'rank', 
    'FMS': 'Level', 
    'AJG': 'Level',
    'ZUFE': 'Level'
    }

Json_attribute = {
    'CCF': 'fullname',
    'FMS': 'Paper_name',
    'AJG': 'Paper_name',
    'ZUFE': 'Paper_name'
}

# 将所有选择标准整合到一个主字典中
selection_criteria = {
    #zufe
    'top': {
        'ZUFE': ['TOP'],
    },
    '1a': {
        'FMS': ['A'],
        'AJG': ['5', '4'],
        'ZUFE': ['1A']
    },
    
    'abs3+': {
        'AJG': ['5','4','3'],
    },
    'fmsB+': {
        'FMS': ['A', 'B'],
    },
    'ccfA': {
        'CCF': ['A期刊', 'A会议'],
    },
    'ccfB': {
        'CCF': ['B期刊', 'B会议'],
    },
    'ccfC': {
        'CCF': ['C期刊', 'C会议'],
    },
}

#%%

def parse_ris(content):
    """解析RIS文件内容，返回条目列表"""
    entries = []
    current_entry = defaultdict(list)
    
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        if line == 'ER  -':
            if current_entry:
                current_entry['C1'] = []
                current_entry['TT'] = []
                current_entry['LB'] = []
                entries.append(dict(current_entry))
                current_entry = defaultdict(list)
        elif len(line) > 6:
            tag = line[:2]
            value = line[6:].strip()
            current_entry[tag].append(value)
    
    if current_entry:
        current_entry['C1'] = []
        current_entry['TT'] = []
        current_entry['LB'] = []
        entries.append(dict(current_entry))
    
    return entries

def deduplicate_entries(entries):
    """对文献条目进行去重
    
    参数:
        entries: RIS条目列表
    
    返回:
        list: 去重后的条目列表
    """
    # 使用标题作为唯一标识
    unique_entries = {}
    for entry in entries:
        # 获取标题,如果没有标题则跳过
        if 'TI' not in entry or not entry['TI']:
            continue
            
        title = entry['TI'][0].lower()  # 转小写以忽略大小写差异
        
        if title not in unique_entries:
            unique_entries[title] = entry
        else:
            # 如果已存在该标题,保留更完整的条目
            existing = unique_entries[title]
            if len(entry) > len(existing):
                unique_entries[title] = entry
    
    return list(unique_entries.values())


def get_resource_path(relative_path):
    """获取资源文件的绝对路径"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller创建临时文件夹，将路径存储在_MEIPASS中
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def load_rating_data():
    """加载所有评级标准数据"""
    rating_data = {}
    for system, filename in RATING_FILES.items():
        try:
            file_path = get_resource_path(filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                rating_data[system] = json.load(f)
        except FileNotFoundError:
            print(f"警告: 未找到{filename}文件")
            continue
    return rating_data

def get_journal_rating(journal_name, rating_data):
    """查询期刊在各评级体系中的等级"""
    ratings = {}
    for system, data in rating_data.items():
        for entry in data:
            if Json_attribute[system] in entry and entry[Json_attribute[system]].lower() == journal_name.lower():
                if system == 'CCF':
                    ratings[system] = entry.get(RATING[system]) + entry.get('type')
                else:
                    ratings[system] = entry.get(RATING[system])
                break
            else:
                ratings[system] = 'Not Found'
    return ratings

def get_paper_criteria(entries, selected_entries, rating_data, balancer, trans_ti=True, trans_ab=True, progress_callback=None):
    """根据不同标准对文献进行分类"""
    
    # 记录已处理的条目数
    processed_entries = 0
    total_entries = len(entries)
    
    # 获取选择标准的名称
    for criteria in selected_entries.keys():
        criteria_dict = selection_criteria[criteria]
        init_length = len(selected_entries[criteria])
        for entry in entries:
            if 'T2' not in entry:
                continue
            
            T2 = entry['T2'][0]
            ratings = get_journal_rating(T2, rating_data)
            
            if not ratings:  # 如果ratings为None或空，跳过此条目
                continue
                
            for system, rating in ratings.items():
                if rating != 'Not Found' and criteria == 'top':  # 第一轮循环
                    entry['C1'].append(system + ':' + str(rating) + ";")

                if system in criteria_dict.keys():  # 一般情况
                    if criteria == '1A' and 'TOP' in entry['C1']:
                        continue
                    if str(rating) in criteria_dict[system]:
                        selected_entries[criteria].append(entry)
                #top 和 1A 特殊情况
                if criteria == 'top' and system == 'CCF':  # ccf a 必须为 期刊
                    if rating[1::] == '期刊' and rating[0] == 'A':
                        selected_entries[criteria].append(entry)
                elif criteria == '1a' and system == 'CCF':
                    if rating[1::] == '会议' and rating[0] == 'A':
                        selected_entries[criteria].append(entries)
                    if rating[1::] == '期刊' and rating[0] == 'B':
                        selected_entries[criteria].append(entry)
            
            # 如果条目被选中且需要翻译
            if len(selected_entries[criteria]) != init_length:
                title = entry['TI'][0].split(' ')
                for i in title:
                    # 去掉单词末尾的标点符号
                    word = i.strip('.,;:!?()[]{}"\'-')  # 去掉常见的标点符号
                    if (word.lower() not in ["a", "the", "an", "and", "or", "but", "if", 
                        "because", "as", "until", "while", "by"] and word):  # 确保word不为空
                        entry['LB'].append(entry['AU'][0].split(',')[0] + entry['PY'][0] + word)
                        break


                resultTi = None  # 初始化变量
                resultAb = None  # 初始化变量
                
                if trans_ti and 'TI' in entry:
                    try:
                        resultTi = translate_text(
                            text=entry['TI'][0],
                            source_lang="auto",
                            target_lang="ZH",
                            load_balancer=balancer
                        )
                    except Exception as e:
                        print(f"翻译标题出错: {str(e)}")
                        
                if trans_ab and 'AB' in entry:
                    try:
                        resultAb = translate_text(
                            text=entry['AB'][0],
                            source_lang="auto",
                            target_lang="ZH",
                            load_balancer=balancer
                        )
                    except Exception as e:
                        print(f"翻译摘要出错: {str(e)}")
                
                if resultTi:
                    main_text = resultTi[0]
                    entry['TT'].append(main_text)
                if resultAb:
                    main_text = resultAb[0]
                    entry['AB'].append(main_text)
                init_length = len(selected_entries[criteria])
            
            # 更新进度
            processed_entries += 1
            if progress_callback:
                progress_callback(processed_entries, total_entries)
    
    return selected_entries


#%%
def to_ris(entries):
    """将多个条目转换为RIS格式字符串"""
    all_ris_lines = []
    
    # 遍历所有条目
    for entry in entries:
        # 遍历当前条目中的所有标签和值
        for tag, values in entry.items():
            c2 = ''
            if tag == 'C1':
                for value in values:
                    c2 += value + ' '
                all_ris_lines.append(f"{tag}  - {c2}")
            else:
                for value in values:
                    all_ris_lines.append(f"{tag}  - {value}")
        
        # 每个条目后添加结束标记和空行
        all_ris_lines.append("ER  -")
        all_ris_lines.append("")
    
    # 用换行符连接所有行
    return "\n".join(all_ris_lines)


def process_ris_file(file_path, selected, output_directory='out_ris', 
                    trans_ti=False, trans_ab=False, 
                    tokenMissuo=None, tokenLinuxdo=None,
                    progress_callback=None):
    """处理RIS文件并分析期刊评级
    file_path: 输入的RIS文件路径        
    selected: 选择的标准
    output_directory: 输出文件夹
    trans_ti: 是否翻译标题
    trans_ab: 是否翻译摘要
    tokenMissuo: 免费翻译服务的token
    tokenLinuxdo: 付费翻译服务的token
    progress_callback: 进度回调函数，接收两个参数：
            - current: 当前处理的条目数
            - total: 总条目数
    """
    try:
        # 读取RIS文件
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            ris_content = f.read()
            
        # 解析RIS内容
        entries = parse_ris(ris_content)
        total_entries = len(entries)
        print(f'条目数量: {total_entries}')
        
        # 加载评级数据
        rating_data = load_rating_data()
        
        # 为每个选择标准创建空列表
        selected = {criteria: [] for criteria in selected}

        # 创建翻译器
        balancer = create_default_load_balancer(tokenMissuo, tokenLinuxdo)
        
        # 使用新的翻译器处理文献
        selected = get_paper_criteria(entries, selected, rating_data, balancer, 
                                    trans_ti, trans_ab, 
                                    progress_callback=progress_callback)
        
        # 处理其他条目
        other_entries = []
        for entry in entries:
            if entry['C2'] == []:
                other_entries.append(entry)

        os.makedirs(output_directory, exist_ok=True)

        # 将其他条目写入other.ris
        if other_entries:
            ris_out = to_ris(other_entries)
            print(f'other 条目数量: {len(other_entries)}')
            with open(os.path.join(output_directory, 'other.ris'), 
                    'w', encoding='utf-8-sig') as f:
                f.write(ris_out)
        
        for criteria, selected_entries_criteria in selected.items():
            if selected_entries_criteria == []:
                continue
            ris_out = to_ris(selected_entries_criteria)
            print(f'{criteria} 条目数量: {len(selected_entries_criteria)}')
            with open(os.path.join(output_directory, f'{criteria}.ris'),
                    'w', encoding='utf-8-sig') as f:
                f.write(ris_out)
                
        return True
    except Exception as e:
        print(f"处理过程中出现错误: {str(e)}")
        raise e

def main():
    """命令行入口函数"""
    # 测试用例
    test_file = "scopus.ris"  # 使用当前文件夹的scopus.ris文件
    test_folder = "test_output"
    
    try:
        # 检查文件是否存在
        if not os.path.exists(test_file):
            print(f"错误: 未找到 {test_file} 文件")
            return
            
        # 调用处理函数
        output_dir = os.path.join('out_ris', test_folder)
        result = process_ris_file(test_file, ['top', '1a', 'abs3+', 'fmsB+'], output_dir)
        
        if result:
            print("处理成功!")
            print(f"输出目录: {output_dir}")
        else:
            print("处理失败!")
            
    except Exception as e:
        print(f"处理出错: {str(e)}")

if __name__ == "__main__":
    main()

