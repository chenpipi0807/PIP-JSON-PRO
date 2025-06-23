import json
import ast
import re
import demjson3
from jsoncomment import JsonComment
from typing import Tuple, Dict, Any, Optional, Union
from ..utils.json_utils import (
    normalize_json, 
    apply_format_style,
    detect_encoding
)


class JSONProcessor:
    """处理各类伪JSON格式的核心处理器类"""
    
    def __init__(self):
        self.parser = JsonComment()
        self.debug_info = {}
        
    def process(self, 
               input_text: str, 
               repair_level: int = 2,
               indent: int = 2,
               pretty_print: bool = True,
               sort_keys: bool = False) -> Tuple[str, bool, Dict[str, Any]]:
        """处理JSON文本
        
        Args:
            input_text: 输入的JSON文本
            repair_level: 修复级别 (1=基础, 2=标准, 3=高级)
            indent: 缩进空格数
            pretty_print: 是否美化输出
            sort_keys: 是否按键排序
            
        Returns:
            处理后的JSON字符串, 是否成功, 调试信息
        """
        if not input_text or not input_text.strip():
            return "", False, {"error": "空输入"}
            
        # 记录原始输入
        self.debug_info = {
            "original_length": len(input_text),
            "original_preview": input_text[:100] + ("..." if len(input_text) > 100 else ""),
            "repair_methods": []
        }
        
        # 首先尝试提取JSON内容
        extracted_text = self._extract_json_content(input_text)
        if extracted_text != input_text:
            self.debug_info["repair_methods"].append("json_extraction")
        
        # 尝试各种修复方法
        result, success = self._try_repair_methods(extracted_text, repair_level)
        
        # 美化格式化
        if success and pretty_print:
            result = apply_format_style(result, indent, sort_keys)
            
        # 记录结果信息
        self.debug_info.update({
            "success": success,
            "final_length": len(result),
            "final_preview": result[:100] + ("..." if len(result) > 100 else "")
        })
        
        return result, success, self.debug_info
    
    def _extract_json_content(self, text: str) -> str:
        """从文本中提取JSON内容"""
        # 方法1: 提取markdown代码块中的JSON
        json_from_markdown = self._extract_from_markdown(text)
        if json_from_markdown:
            return json_from_markdown
        
        # 方法2: 查找第一个完整的JSON对象或数组
        json_from_braces = self._extract_from_braces(text)
        if json_from_braces:
            return json_from_braces
        
        # 方法3: 如果都没找到，返回原文本
        return text.strip()
    
    def _extract_from_markdown(self, text: str) -> Optional[str]:
        """从markdown代码块中提取JSON"""
        # 匹配 ```json ... ``` 格式
        json_pattern = r'```(?:json)?\s*\n?(.*?)\n?```'
        matches = re.findall(json_pattern, text, re.DOTALL | re.IGNORECASE)
        
        if matches:
            # 返回第一个匹配的内容
            return matches[0].strip()
        
        return None
    
    def _extract_from_braces(self, text: str) -> Optional[str]:
        """通过大括号或方括号提取JSON内容"""
        text = text.strip()
        
        # 查找对象 {...}
        if '{' in text:
            start_idx = text.find('{')
            if start_idx != -1:
                brace_count = 0
                for i, char in enumerate(text[start_idx:], start_idx):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            return text[start_idx:i+1]
        
        # 查找数组 [...]
        if '[' in text:
            start_idx = text.find('[')
            if start_idx != -1:
                bracket_count = 0
                for i, char in enumerate(text[start_idx:], start_idx):
                    if char == '[':
                        bracket_count += 1
                    elif char == ']':
                        bracket_count -= 1
                        if bracket_count == 0:
                            return text[start_idx:i+1]
        
        return None
    
    def _try_repair_methods(self, text: str, repair_level: int) -> Tuple[str, bool]:
        """按照顺序尝试各种修复方法"""
        methods = [
            self._try_direct_parse,
            self._try_normalize,
            self._try_jsoncomment,
            self._try_demjson,
            self._try_ast_eval
        ]
        
        # 根据修复级别选择尝试的方法
        methods_to_try = methods[:1 + repair_level]  # 至少尝试直接解析
        
        for method in methods_to_try:
            try:
                result, success = method(text)
                if success:
                    self.debug_info["repair_methods"].append(method.__name__)
                    return result, True
            except Exception as e:
                # 记录异常信息
                pass
        
        # 所有方法都尝试失败
        return text, False
    
    def _try_direct_parse(self, text: str) -> Tuple[str, bool]:
        """尝试直接解析JSON"""
        try:
            parsed = json.loads(text)
            return json.dumps(parsed, ensure_ascii=False), True
        except:
            raise Exception("Direct parse failed")
    
    def _try_normalize(self, text: str) -> Tuple[str, bool]:
        """尝试使用normalize_json修复JSON"""
        normalized, success = normalize_json(text, repair_level=3)
        if not success:
            raise Exception("Normalize failed")
        return normalized, True
    
    def _try_jsoncomment(self, text: str) -> Tuple[str, bool]:
        """尝试使用JsonComment解析JSON"""
        parsed = self.parser.loads(text)
        return json.dumps(parsed, ensure_ascii=False), True
    
    def _try_demjson(self, text: str) -> Tuple[str, bool]:
        """尝试使用demjson解析JSON"""
        parsed = demjson3.decode(text)
        return json.dumps(parsed, ensure_ascii=False), True
    
    def _try_ast_eval(self, text: str) -> Tuple[str, bool]:
        """尝试使用Python AST解析JSON"""
        # 尝试添加外层大括号
        if not text.strip().startswith('{') and not text.strip().startswith('['):
            text = '{' + text + '}'
        
        # 尝试替换单引号为双引号
        text = text.replace("'", '"')
        
        # 尝试使用ast.literal_eval解析
        parsed = ast.literal_eval(text)
        return json.dumps(parsed, ensure_ascii=False), True
