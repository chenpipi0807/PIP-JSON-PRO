import os
import sys
import json
from typing import Dict, Any, Tuple, List, Optional

# 确保模块能被正确导入
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..core.json_processor import JSONProcessor

class PIP_JSON_Corrector_Pro:
    """PIP-JSON修正-Pro节点，用于修复各类LLM模型生成的伪JSON格式"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_text": ("STRING", {"multiline": True, "default": ""}),
                "repair_mode": (["标准", "宽松", "极限修复"], {"default": "标准"}),
            },
            "optional": {
                "pretty_print": ("BOOLEAN", {"default": True}),
                "indent_size": (["2", "4", "无缩进"], {"default": "2"}),
                "sort_keys": ("BOOLEAN", {"default": False}),
                "show_debug": ("BOOLEAN", {"default": False}),
            }
        }
    
    RETURN_TYPES = ("STRING", "BOOLEAN", "STRING")
    RETURN_NAMES = ("corrected_json", "is_valid", "debug_info")
    FUNCTION = "correct_json"
    CATEGORY = "PIP/JSON"
    
    def __init__(self):
        self.processor = JSONProcessor()
        
    def correct_json(self, 
                    input_text: str, 
                    repair_mode: str,
                    pretty_print: bool = True,
                    indent_size: str = "2",
                    sort_keys: bool = False,
                    show_debug: bool = False) -> Tuple[str, bool, str]:
        """修正JSON格式
        
        Args:
            input_text: 输入文本
            repair_mode: 修复模式 (标准/宽松/极限修复)
            pretty_print: 是否美化输出
            indent_size: 缩进大小
            sort_keys: 是否对键进行排序
            show_debug: 是否显示调试信息
            
        Returns:
            修正后的JSON, 是否有效, 调试信息
        """
        # 映射修复级别
        repair_level_map = {
            "标准": 1,  # 基础修复
            "宽松": 2,  # 标准修复
            "极限修复": 3   # 高级修复
        }
        repair_level = repair_level_map.get(repair_mode, 2)
        
        # 设置缩进
        indent = None if indent_size == "无缩进" else int(indent_size)
        
        # 处理JSON
        corrected, is_valid, debug = self.processor.process(
            input_text=input_text,
            repair_level=repair_level,
            indent=indent,
            pretty_print=pretty_print,
            sort_keys=sort_keys
        )
        
        # 生成调试信息
        debug_str = self._format_debug_info(debug) if show_debug else ""
        
        return corrected, is_valid, debug_str
    
    def _format_debug_info(self, debug_info: Dict[str, Any]) -> str:
        """格式化调试信息"""
        if not debug_info:
            return "无调试信息"
            
        success = debug_info.get("success", False)
        status = "✅ 成功" if success else "❌ 失败"
        
        methods = debug_info.get("repair_methods", [])
        method_str = "无" if not methods else ", ".join([m.replace("_try_", "") for m in methods])
        
        original_len = debug_info.get("original_length", 0)
        final_len = debug_info.get("final_length", 0)
        
        lines = [
            f"状态: {status}",
            f"原长度: {original_len} 字符",
            f"结果长度: {final_len} 字符",
            f"使用方法: {method_str}"
        ]
        
        if "error" in debug_info:
            lines.append(f"错误: {debug_info['error']}")
            
        return "\n".join(lines)


class PIP_JSON_Preview:
    """JSON预览节点"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_text": ("STRING", {"multiline": True}),
                "display_mode": (["完整", "紧凑", "摘要"], {"default": "完整"}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("preview_text",)
    FUNCTION = "preview_json"
    CATEGORY = "PIP/JSON"
    
    def preview_json(self, json_text: str, display_mode: str) -> Tuple[str]:
        """预览JSON内容"""
        if not json_text:
            return ("无内容可预览",)
            
        try:
            # 尝试解析JSON
            data = json.loads(json_text)
            
            if display_mode == "完整":
                # 完整模式：返回格式化后的JSON
                return (json.dumps(data, indent=2, ensure_ascii=False),)
                
            elif display_mode == "紧凑":
                # 紧凑模式：无换行和缩进
                return (json.dumps(data, ensure_ascii=False),)
                
            elif display_mode == "摘要":
                # 摘要模式：显示结构摘要
                return (self._generate_summary(data),)
                
        except json.JSONDecodeError:
            return (f"无效JSON内容: {json_text[:100]}...",)
        
        return (json_text,)
    
    def _generate_summary(self, data: Any) -> str:
        """生成JSON摘要"""
        if isinstance(data, dict):
            keys = list(data.keys())
            key_count = len(keys)
            preview = ", ".join(keys[:5])
            if key_count > 5:
                preview += f"... 等{key_count}个键"
            return f"对象 {{{preview}}}"
            
        elif isinstance(data, list):
            item_count = len(data)
            preview_items = [self._preview_value(item) for item in data[:3]]
            preview = ", ".join(preview_items)
            if item_count > 3:
                preview += f"... 等{item_count}项"
            return f"数组 [{preview}]"
            
        else:
            return self._preview_value(data)
    
    def _preview_value(self, value: Any) -> str:
        """预览单个值"""
        if isinstance(value, dict):
            return f"对象 {{{len(value)}个键}}"
        elif isinstance(value, list):
            return f"数组 [{len(value)}项]"
        elif isinstance(value, str):
            if len(value) > 30:
                return f'"{value[:27]}..."'
            return f'"{value}"'
        else:
            return str(value)


# 节点映射
NODE_CLASS_MAPPINGS = {
    "PIP_JSON_Corrector_Pro": PIP_JSON_Corrector_Pro,
    "PIP_JSON_Preview": PIP_JSON_Preview,
}

# 显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "PIP_JSON_Corrector_Pro": "PIP JSON修正-Pro",
    "PIP_JSON_Preview": "PIP JSON预览",
}
