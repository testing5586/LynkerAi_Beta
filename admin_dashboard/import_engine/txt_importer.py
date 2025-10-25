"""
TXT 文本格式导入器
Plain Text Importer - 解析纯文本命盘数据
"""

import os
import re
from supabase import create_client
from .normalize_chart import normalize_from_ocr

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
sb = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

def extract_fields_from_text(text):
    """
    从纯文本中提取命盘字段
    支持多种格式：
    - 姓名: 张三
    - 性别: 男
    - 出生时间: 1990-05-20 14:30
    - 夫妻宫: 天府
    - 财帛宫: 武曲
    - 化禄: 是/否
    - 化忌: 是/否
    """
    def find(pattern, default=None):
        m = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
        return m.group(1).strip() if m else default
    
    # 提取字段（支持中英文标签）
    name = find(r"(?:姓名|name|命主)[:：=\s]+([^\n]+)")
    
    # 性别处理
    gender_match = find(r"(?:性别|gender|sex)[:：=\s]*([男女MFmf])")
    if gender_match:
        gender = "男" if gender_match.upper() in ["男", "M"] else "女"
    else:
        gender = None
    
    # 出生时间（支持多种格式）
    birth_time_raw = find(r"(?:出生时间|出生|生辰|birth[\s_]?time|datetime)[:：=\s]*([0-9T:\-/\s]+)")
    if birth_time_raw:
        # 规范化时间格式
        birth_time = birth_time_raw.strip()
        # 将斜杠替换为短横线
        birth_time = birth_time.replace("/", "-")
        # 处理空格分隔的日期和时间
        if " " in birth_time and "T" not in birth_time:
            birth_time = birth_time.replace(" ", "T", 1)  # 只替换第一个空格
        # 如果没有时间部分，添加默认时间
        if "T" not in birth_time and ":" not in birth_time:
            birth_time += "T12:00:00"
        elif "T" in birth_time and birth_time.count(":") == 1:
            birth_time += ":00"
    else:
        birth_time = None
    
    # 宫位主星
    marriage_star = find(r"(?:夫妻宫|marriage[\s_]?palace)[:：=\s]*([^\s\n，,；;]+)")
    wealth_star = find(r"(?:财帛宫|wealth[\s_]?palace|money[\s_]?palace)[:：=\s]*([^\s\n，,；;]+)")
    
    # 飞化（支持多种表述）
    hualu_match = find(r"(?:化禄|hua[\s_]?lu)[:：=\s]*(是|否|有|无|true|false|yes|no)")
    hualu = hualu_match and hualu_match in ["是", "有", "true", "yes", "True", "YES"] if hualu_match else False
    
    huaji_match = find(r"(?:化忌|hua[\s_]?ji)[:：=\s]*(是|否|有|无|true|false|yes|no)")
    huaji = huaji_match and huaji_match in ["是", "有", "true", "yes", "True", "YES"] if huaji_match else False
    
    return {
        "name": name,
        "gender": gender,
        "birth_time": birth_time,
        "marriage_palace_star": marriage_star,
        "wealth_palace_star": wealth_star,
        "transformations": {"hualu": hualu, "huaji": huaji},
        "raw_text": text
    }

def process_txt_file(file_content):
    """
    处理 TXT 文件内容
    Returns: 解析后的字段字典
    """
    if isinstance(file_content, bytes):
        # 尝试不同编码
        for encoding in ['utf-8', 'gbk', 'gb2312']:
            try:
                text = file_content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            text = file_content.decode('utf-8', errors='ignore')
    else:
        text = file_content
    
    parsed = extract_fields_from_text(text)
    return parsed

def save_record(txt_obj):
    """保存 TXT 解析后的记录到数据库"""
    if not sb:
        raise Exception("Supabase 客户端未初始化")
    
    norm = normalize_from_ocr(txt_obj)
    
    return sb.table("birthcharts").insert({
        "name": norm["name"],
        "gender": norm["gender"],
        "birth_time": norm["birth_time"],
        "ziwei_palace": None,
        "main_star": None,
        "shen_palace": None,
        "birth_data": norm["birth_data"]
    }).execute()
