#%%
import json
import sys
import os
from collections import defaultdict

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from utils.translator import *
from core.data_manager import DataManager
from core.data_types import RatingSystem

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
                current_entry['C2'] = []
                current_entry['LB'] = []
                entries.append(dict(current_entry))
                current_entry = defaultdict(list)
        elif len(line) > 6:
            tag = line[:2]
            value = line[6:].strip()
            current_entry[tag].append(value)
    
    if current_entry:
        current_entry['C1'] = []
        current_entry['C2'] = []
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




def load_rating_data(path_rating_file):
    """加载所有评级标准数据"""
    rating_data = {}
    for system, file_path in path_rating_file.items():
        try:
            with open(file_path, encoding='utf-8') as f:
                rating_data[system] = json.load(f)
        except FileNotFoundError:
            print(f"警告: 未找到{file_path}文件")
            continue
    return rating_data

def get_journal_rating(journal_name, rating_data, json_attribute_title, json_attribute_rating):
    """查询期刊在各评级体系中的等级
    args:
        journal_name: 期刊名称
        rating_data: 评级数据
        json_attribute_title: 评价文件json中 期刊名称对应的 key
        json_attribute_rating: 评价文件json中 期刊评级对应的 key
    """
    ratings = {}
    for system, data in rating_data.items():
        for criteria_paper_item in data:
            if criteria_paper_item[json_attribute_title[system]].lower() == journal_name.lower():
                if system == 'CCF':# ccf 期刊和会议分开
                    ratings[system] = criteria_paper_item.get(json_attribute_rating[system]) + criteria_paper_item.get('type')
                else:
                    ratings[system] = criteria_paper_item.get(json_attribute_rating[system])
                break
            else:
                ratings[system] = 'Not Found' # 如果未找到评级，则返回'Not Found'
    return ratings



def get_paper_criteria(entries, 
                    json_attribute_title, json_attribute_rating, 
                    rating_data, selection_criteria, 
                    balancer, trans_ti=True, trans_ab=True, 
                    progress_callback=None):
    """
    根据不同标准对文献进行分类
    
    args:
        entries: 文献条目列表
        json_attribute_title: 评价文件json中 期刊名称对应的 key
        json_attribute_rating: 评价文件json中 期刊评级对应的 key
        rating_data: 评级数据
        selection_criteria: 选择标准
        balancer: 翻译器
        trans_ti: 是否翻译标题
        trans_ab: 是否翻译摘要
        progress_callback: 进度回调函数
    """
    
    # 记录已处理的条目数
    processed_entries = 0
    total_entries = len(entries)
    selected_criteria_entries = {criteria: [] for criteria in selection_criteria}
    round = 1
    for criteria in selected_criteria_entries.keys(): # 遍历选择标准
        criteria_dict = selection_criteria[criteria] # 获取criteria对应的评级标准
        init_length = len(selected_criteria_entries[criteria])
        for entry in entries: # 遍历文献条目
            if 'T2' not in entry: # 如果没有T2，跳过此条目
                continue
            
            T2 = entry['T2'][0] # 获取journal 标题
            ratings = get_journal_rating(T2, rating_data, json_attribute_title, json_attribute_rating)
            
            if not ratings:  # 如果ratings为None或空，跳过此条目
                continue

            for system, rating in ratings.items():
                
                if rating != 'Not Found' and round == 1:  # 第一轮循环
                    entry['C2'].append(system + ':' + str(rating) + ";")

                if system in criteria_dict.keys(): 
                    if rating in criteria_dict[system]:
                        selected_criteria_entries[criteria].append(entry)

                # if system in criteria_dict.keys():  # 一般情况
                #     if criteria == '1A' and 'TOP' in entry['C1']:
                #         continue
                #     if str(rating) in criteria_dict[system]:
                #         selected_entries[criteria].append(entry)
                # #top 和 1A 特殊情况
                # if criteria == 'top' and system == 'CCF':  # ccf a 必须为 期刊
                #     if rating[1::] == '期刊' and rating[0] == 'A':
                #         selected_entries[criteria].append(entry)
                # elif criteria == '1a' and system == 'CCF':
                #     if rating[1::] == '会议' and rating[0] == 'A':
                #         selected_entries[criteria].append(entry)
                #     if rating[1::] == '期刊' and rating[0] == 'B':
                #         selected_entries[criteria].append(entry)
            
            # 只翻译 被 选中 的 条目，以及生成标签作为 bibtex的 citation_key
            if len(selected_criteria_entries[criteria]) != init_length:
                if entry['LB'] == []:
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

                if trans_ti and 'TI' in entry and entry['C1'] == []:
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
                    entry['C1'].append(main_text)
                if resultAb:
                    main_text = resultAb[0]
                    entry['AB'].append(main_text)
                init_length = len(selected_criteria_entries[criteria])
            
            # 更新进度
            processed_entries += 1
            if progress_callback:
                progress_callback(processed_entries, total_entries)
        round += 1
    return selected_criteria_entries

def get_paper_criteria_profile(entries, selection_profile):
    """
    二级标准，一般是 学校的 标准 除了目录上的 列举 还有 其他 评级中的条目
    
    args:
        entries: 文献条目列表
        selection_profile: 二级标准
    """
    selected_profile_entries = {
        profile:{ 
            criteria_set:[] for criteria_set in selection_profile[profile].keys()
                } for profile in selection_profile.keys()
        }
        
    for profile in selected_profile_entries.keys():
        for entry in entries:
            entry_added = False  # 添加标记
            for criteria_set, criteria_set_dict in selection_profile[profile].items():
                if entry_added:  # 如果已添加则跳过后续循环
                    break
                for criteria, rating_list in criteria_set_dict.items():
                    if entry_added:  # 如果已添加则跳过后续循环
                        break
                    for rating in rating_list:
                        if criteria+':'+rating +';' in entry['C2']:
                            selected_profile_entries[profile][criteria_set].append(entry)
                            entry_added = True  # 设置标记
                            break  # 跳出最内层循环
                            
                    
    return selected_profile_entries
#%%
def to_ris(entries):
    """将多个条目转换为RIS格式字符串"""
    all_ris_lines = []
    
    # 遍历所有条目
    for entry in entries:
        # 遍历当前条目中的所有标签和值
        for tag, values in entry.items():
            c2 = ''
            if tag == 'C2':
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


def process_ris_file(file_path, selection_criteria, selection_profile, 
                    path_rating_file, json_attribute_title, json_attribute_rating, output_directory='out_ris',
                    trans_ti=False, trans_ab=False, tokenMissuo=None, tokenLinuxdo=None,
                    progress_callback=None):
    """处理RIS文件并分析期刊评级
    file_path: 输入的RIS文件路径        
    selection_criteria: 选择的标准
    path_rating_file: 评级数据文件路径
    json_attribute_title: 评价文件json中 期刊名称对应的 key
    json_attribute_rating: 评价文件json中 期刊评级对应的 key
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
        entries = deduplicate_entries(entries)
        total_entries = len(entries)
        print(f'条目数量: {total_entries}')
        
        # 加载评级数据
        rating_data = load_rating_data(path_rating_file)
        
        # 为每个选择标准创建空列表
        

        # 创建翻译器
        balancer = create_default_load_balancer(tokenMissuo, tokenLinuxdo)
        
        # 基础分类
        after_selected = get_paper_criteria(entries, 
                                    json_attribute_title, json_attribute_rating,
                                    rating_data, selection_criteria,
                                    balancer, trans_ti, trans_ab, 
                                    progress_callback)

        # 处理其他条目
        selected_entries = []
        for entry in entries:
            if entry['C2'] != []:
                selected_entries.append(entry)

        os.makedirs(output_directory, exist_ok=True)

        # 二级分类
        if selection_profile:
            selected_profile = get_paper_criteria_profile(selected_entries, selection_profile)

        #基础分类
        for criteria, selected_entries_criteria in after_selected.items():
            if selected_entries_criteria == []:
                continue
            ris_out = to_ris(selected_entries_criteria)
            print(f'{criteria} 条目数量: {len(selected_entries_criteria)}')
            with open(os.path.join(output_directory, f'{criteria}.ris'),
                    'w', encoding='utf-8-sig') as f:
                f.write(ris_out)
                
        # 二级分类
        if selection_profile:
            for profile, selected_entries_profile in selected_profile.items():
                for criteria_set, selected_entries_criteria_set in selected_entries_profile.items():
                    if selected_entries_criteria_set == []:
                        continue
                    ris_out = to_ris(selected_entries_criteria_set)
                    print(f'{profile}_{criteria_set} 条目数量: {len(selected_entries_criteria_set)}')
                    with open(os.path.join(output_directory, f'{profile}_{criteria_set}.ris'),
                        'w', encoding='utf-8-sig') as f:
                        f.write(ris_out)
        return True
    except Exception as e:
        print(f"处理过程中出现错误: {str(e)}")
        raise e

def main():
    """命令行入口函数"""
    # 测试用例
    test_file = os.path.join("resources", "scopus.ris")
    test_folder = "test_output"
    sub_folder = "ceshi1"
    
    output_directory = os.path.join(test_folder, sub_folder)

    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    # 初始化数据管理器
    data_manager = DataManager(
        base_path=os.path.join(project_root, 'data'),
        config_path=os.path.join(project_root, 'data', 'config.json')
    )
    
    try:
        if not os.path.exists(test_file):
            print(f"错误: 未找到 {test_file} 文件")
            return
            
        # 获取评级数据文件路径
        path_rating_file = data_manager.config.rating_file_paths
        
        # 获取JSON属性映射
        json_attribute_mapping = data_manager.config.json_attribute_mapping
        json_attribute_rating = {
            system: mapping['level']
            for system, mapping in json_attribute_mapping.items()
        }
        json_attribute_title = {
            system: mapping['paper_name']
            for system, mapping in json_attribute_mapping.items()
        }
        
        # 获取分类标准
        selection_criteria = data_manager.get_selection_criteria()
        
        # 获取组合标准
        selection_profile = data_manager.get_selection_profiles()
        
        # 处理文件
        process_ris_file(
            file_path=test_file,
            selection_criteria=selection_criteria,
            selection_profile=selection_profile,
            path_rating_file=path_rating_file,
            json_attribute_title=json_attribute_title,
            json_attribute_rating=json_attribute_rating,
            output_directory=output_directory
        )
        
    except Exception as e:
        print(f"处理过程中出现错误: {str(e)}")
        return

if __name__ == "__main__":
    main()

