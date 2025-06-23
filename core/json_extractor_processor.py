import sys
import os
import json
from typing import Any, Dict, List, Tuple, Union, Optional

# 确保能正确导入utils模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..utils.json_extractor import extract_from_json


class JSONExtractorProcessor:
    """JSON提取处理器核心类"""
    
    def __init__(self):
        self.debug_info = {}
    
    def extract(self, 
               json_str: str, 
               path_keys: List[str], 
               fuzzy_mode: bool = False,
               min_similarity: float = 0.6) -> Tuple[str, bool, Dict]:
        """
        从JSON字符串中提取值
        
        Args:
            json_str: JSON字符串
            path_keys: 路径键列表 [一级键, 二级键, 三级键, ...]
            fuzzy_mode: 是否启用模糊搜索
            min_similarity: 最小相似度阈值
            
        Returns:
            提取的值, 是否成功, 调试信息
        """
        if not json_str or not json_str.strip():
            return "", False, {"error": "JSON字符串为空"}
            
        # 过滤空路径    
        clean_path = [p for p in path_keys if p and p.strip()]
        
        if not clean_path:
            return json_str, True, {"message": "未提供路径，返回完整JSON"}
        
        # 调用通用提取函数
        result, success, debug = extract_from_json(
            json_str=json_str,
            path=clean_path,
            fuzzy_mode=fuzzy_mode,
            min_similarity=min_similarity
        )
        
        self.debug_info = debug
        
        if success:
            # 确保结果是字符串
            if isinstance(result, (dict, list)):
                result = json.dumps(result, ensure_ascii=False)
        else:
            if "error" in debug:
                result = f"提取失败: {debug['error']}"
            else:
                result = "未找到匹配项"
        
        return result, success, debug
    
    def format_debug_info(self) -> str:
        """格式化调试信息为可读文本"""
        if not self.debug_info:
            return "无调试信息"
            
        lines = []
        
        # 路径信息
        if "path" in self.debug_info:
            path_str = "->" .join([p for p in self.debug_info["path"] if p])
            lines.append(f"查询路径: {path_str}")
        
        # 模式信息
        if "fuzzy_mode" in self.debug_info:
            mode = "模糊搜索" if self.debug_info["fuzzy_mode"] else "精确路径"
            lines.append(f"搜索模式: {mode}")
        
        # 匹配结果
        if "matches" in self.debug_info and self.debug_info["matches"]:
            lines.append("匹配结果:")
            for i, match in enumerate(self.debug_info["matches"]):
                if "exact" in match:
                    lines.append(f"  ✓ 精确匹配: {match['path']}")
                elif "path" in match and "similarity" in match:
                    lines.append(f"  {i+1}. 路径: {match['path']} (相似度: {match['similarity']})")
                elif "partial_key" in match:
                    lines.append(f"  - 部分匹配: '{match['partial_key']}' → '{match['matched_to']}'")
                elif "final_path" in match:
                    lines.append(f"  最终路径: {match['final_path']}")
        
        # 错误信息
        if "error" in self.debug_info:
            lines.append(f"错误: {self.debug_info['error']}")
        
        return "\n".join(lines)
