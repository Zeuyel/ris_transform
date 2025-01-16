# RIS 文件处理器

一个用于处理和分类学术文献 RIS 文件的工具，支持多种期刊分类标准和自动翻译功能。

## 功能特点

- 支持多种期刊分类标准（CCF、FMS、AJG、ZUFE）
- 自动翻译标题和摘要
- 为Endnote更好的Bib文件的citationkey
- 现代化的图形界面
- 拖放文件支持
- 进度显示
- 批量处理
- 自动保存配置

## 目录结构

```
project_root/
├── app.py              # 主程序入口
├── core/               # 核心处理逻辑
│   └── paper_processor.py
├── gui/                # 图形界面相关
│   └── main_window.py
├── utils/              # 工具类
│   ├── translator.py   # 翻译工具
│   └── json_processor.py
├── data/               # 数据文件
│   ├── ccf_data.json
│   ├── FMS.json
│   ├── ajg_2024.json
│   └── zufe.json
└── resources/          # 资源文件
    ├── filter.ico
    └── scopus.ris
```

## 使用方法

1. 运行程序：
   ```bash
   python app.py
   ```

2. 选择或拖入 RIS 文件

3. 选择分类标准：
   - top: ZUFE TOP 期刊
   - 1a: FMS A类、AJG 4-5星、ZUFE 1A类期刊
   - abs3+: AJG 3星及以上期刊
   - fmsB+: FMS A类和B类期刊
   - ccfA/B/C: CCF A/B/C类期刊和会议

4. 翻译选项（可选）：
   - 支持标题翻译
   - 支持摘要翻译
   - 可配置翻译服务令牌

5. 选择输出目录并处理

## 依赖项

- Python 3.8+
- PyQt5
- requests

## 安装依赖

```bash
pip install -r requirements.txt
```

## 编译方法

1. 开发环境编译：
   ```bash
   pyinstaller --clean --name "RIS文件处理器" --icon "resources/filter.ico" --add-data "data/*;data" --add-data "resources/*;resources" --noconsole app.py
   ```

2. 使用 build.py 编译（推荐）：
   ```bash
   python build.py
   ```
   这将自动处理资源文件打包和图标设置。

3. 编译后的文件位置：
   - Windows: `dist/RIS文件处理器/RIS文件处理器.exe`
   - 其他系统: `dist/RIS文件处理器/RIS文件处理器`

## 自定义数据

### 添加新的期刊分类数据

1. JSON 文件格式要求：
   ```json
   [
     {
       "Paper_name": "期刊全名",
       "Level": "期刊等级",
       "type": "期刊类型（可选）"
     }
   ]
   ```

2. 添加步骤：
   1. 将 JSON 文件放入 `data` 目录
   2. 在 `core/paper_processor.py` 中更新 `RATING_FILES`：
      ```python
      RATING_FILES = {
          'NEW_SYSTEM': os.path.join('data', 'new_system.json'),
          # ... 其他系统 ...
      }
      ```
   3. 更新 `RATING` 和 `Json_attribute`：
      ```python
      RATING = {
          'NEW_SYSTEM': 'Level',  # JSON中表示等级的字段名
          # ... 其他系统 ...
      }
      
      Json_attribute = {
          'NEW_SYSTEM': 'Paper_name',  # JSON中表示期刊名的字段名
          # ... 其他系统 ...
      }
      ```

### 添加新的分类标准

在 `core/paper_processor.py` 中的 `selection_criteria` 添加新规则：

```python
selection_criteria = {
    'new_category': {
        'NEW_SYSTEM': ['A', 'B'],  # 系统名称和期刊等级列表
        'OTHER_SYSTEM': ['1', '2']  # 可以组合多个系统
    },
    # ... 其他分类 ...
}
```

分类规则说明：
- 键名（如 'new_category'）将显示在界面的复选框中
- 值为字典，指定各系统中符合条件的等级
- 可以组合多个系统的条件

## 配置说明

- 配置文件位置：`config.json`
- 支持保存：
  - 输出目录
  - 翻译选项
  - 翻译服务令牌

## 注意事项

1. RIS 文件需要使用 UTF-8 编码
2. 翻译功能需要网络连接
3. 大量条目的处理可能需要较长时间
4. 建议定期备份重要的 RIS 文件
5. 自定义数据文件必须使用 UTF-8 编码
6. 编译时确保所有数据文件都在正确的目录中

## 开发说明

- 添加新的分类标准：
  1. 在 `core/paper_processor.py` 的 `selection_criteria` 中添加新的分类规则
  2. 界面会自动更新以包含新的分类选项

- 自定义翻译服务：
  1. 修改 `utils/translator.py`
  2. 实现新的翻译接口

## 许可证

MIT License 