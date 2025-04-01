import re
import json
import ast
import chardet
from typing import Tuple, Dict, Any, List, Union


def detect_encoding(text_bytes: bytes) -> str:
    """检测文本编码"""
    result = chardet.detect(text_bytes)
    return result['encoding'] or 'utf-8'


def fix_quotes(text: str) -> str:
    """修复单引号为双引号"""
    # 修复键名中的单引号
    text = re.sub(r"'([^']+)'(\s*:)", r'"\1"\2', text)
    
    # 修复值中的单引号 (考虑多种可能的结束符)
    text = re.sub(r":\s*'([^']*)'([,}\]])", r': "\1"\2', text)
    
    return text


def fix_unquoted_keys(text: str) -> str:
    """修复无引号的键名"""
    # 匹配无引号键 (排除已有双引号的情况)
    pattern = r"([{,]\s*)([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:"
    return re.sub(pattern, r'\1"\2":', text)


def remove_trailing_commas(text: str) -> str:
    """删除尾部逗号"""
    # 数组尾部逗号
    text = re.sub(r",\s*\]", "]", text)
    # 对象尾部逗号
    text = re.sub(r",\s*\}", "}", text)
    return text


def remove_comments(text: str) -> str:
    """删除JavaScript风格注释"""
    # 删除单行注释
    text = re.sub(r"//.*?$", "", text, flags=re.MULTILINE)
    # 删除多行注释
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    return text


def format_numeric_values(text: str) -> str:
    """格式化数值 (处理特殊值如Infinity, NaN)"""
    # 将JavaScript特殊值转换为字符串
    text = re.sub(r":\s*(Infinity|-Infinity|NaN)\s*([,}\]])", r': "\1"\2', text)
    
    # 转换十六进制为字符串
    text = re.sub(r":\s*(0x[0-9a-fA-F]+)\s*([,}\]])", r': "\1"\2', text)
    
    return text


def try_fix_json_structure(text: str) -> str:
    """尝试修复JSON结构问题"""
    text = text.strip()
    
    # 尝试添加缺失的外层括号
    if not text.startswith('{') and not text.startswith('['):
        if ':' in text:  # 可能是对象
            text = '{' + text + '}'
        else:  # 可能是数组
            text = '[' + text + ']'
    
    # 检查括号是否匹配
    open_brackets = {'(': ')', '{': '}', '[': ']'}
    stack = []
    
    for char in text:
        if char in open_brackets:
            stack.append(char)
        elif char in open_brackets.values():
            if not stack or open_brackets[stack.pop()] != char:
                # 不匹配，不进行修复
                return text
    
    # 添加缺失的闭合括号
    while stack:
        bracket = stack.pop()
        text += open_brackets[bracket]
    
    return text


def normalize_json(text: str, repair_level: int = 2) -> Tuple[str, bool]:
    """规范化JSON
    
    Args:
        text: 输入文本
        repair_level: 修复级别 (1=基础, 2=标准, 3=高级)
        
    Returns:
        修复后的文本, 是否修复成功
    """
    original = text
    success = False
    
    try:
        # 基础级别修复
        if repair_level >= 1:
            text = remove_comments(text)
            text = remove_trailing_commas(text)
        
        # 标准级别修复
        if repair_level >= 2:
            text = fix_quotes(text)
            text = fix_unquoted_keys(text)
            text = format_numeric_values(text)
        
        # 高级级别修复
        if repair_level >= 3:
            text = try_fix_json_structure(text)
        
        # 验证JSON
        json.loads(text)
        success = True
        return text, success
    
    except json.JSONDecodeError:
        # 如果还是解码失败，返回原始文本
        return original, success


def apply_format_style(json_str: str, indent: int = 2, sort_keys: bool = False) -> str:
    """应用格式化样式"""
    try:
        parsed = json.loads(json_str)
        return json.dumps(parsed, indent=indent, ensure_ascii=False, sort_keys=sort_keys)
    except:
        return json_str
