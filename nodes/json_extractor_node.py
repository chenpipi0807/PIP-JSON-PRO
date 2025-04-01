import os
import sys
import json
from typing import Dict, Any, Tuple, List, Optional

# 确定模块能被正确导入
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..core.json_extractor_processor import JSONExtractorProcessor

class PIP_JSON_Extractor_Pro:
    """PIP-JSON提取-Pro节点，用于从复杂JSON中提取特定数据"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_text": ("STRING", {"multiline": True, "default": ""}),
                "search_mode": (["精确路径", "模糊搜索"], {"default": "精确路径"}),
            },
            "optional": {
                "key_level_1": ("STRING", {"default": ""}),
                "key_level_2": ("STRING", {"default": ""}),
                "key_level_3": ("STRING", {"default": ""}),
                "key_level_4": ("STRING", {"default": ""}),
                "key_level_5": ("STRING", {"default": ""}),
                "similarity_threshold": (["0.5", "0.6", "0.7", "0.8", "0.9"], {"default": "0.6"}),
                "show_debug": ("BOOLEAN", {"default": False}),
            }
        }
    
    RETURN_TYPES = ("STRING", "BOOLEAN", "STRING")
    RETURN_NAMES = ("extracted_value", "success", "debug_info")
    FUNCTION = "extract_json_value"
    CATEGORY = "PIP/JSON"
    
    def __init__(self):
        self.processor = JSONExtractorProcessor()
        
    def extract_json_value(self, 
                        json_text: str, 
                        search_mode: str,
                        key_level_1: str = "",
                        key_level_2: str = "",
                        key_level_3: str = "",
                        key_level_4: str = "",
                        key_level_5: str = "",
                        similarity_threshold: str = "0.6",
                        show_debug: bool = False) -> Tuple[str, bool, str]:
        """从JSON中提取值
        
        Args:
            json_text: JSON字符串
            search_mode: 搜索模式 (精确路径/模糊搜索)
            key_level_1-5: 1-5级路径键
            similarity_threshold: 相似度阈值
            show_debug: 是否显示调试信息
            
        Returns:
            提取的值, 是否成功, 调试信息
        """
        try:
            # 收集路径键值
            path_keys = [key_level_1, key_level_2, key_level_3, key_level_4, key_level_5]
            
            # 模糊搜索模式
            fuzzy_mode = search_mode == "模糊搜索"
            
            # 相似度阈值
            min_similarity = float(similarity_threshold)
            
            # 处理JSON
            result, success, debug = self.processor.extract(
                json_str=json_text,
                path_keys=path_keys,
                fuzzy_mode=fuzzy_mode,
                min_similarity=min_similarity
            )
            
            # 生成调试信息
            debug_str = self.processor.format_debug_info() if show_debug else ""
            
            return result, success, debug_str
            
        except Exception as e:
            return f"错误: {str(e)}", False, f"处理异常: {str(e)}"


class PIP_JSON_Path_Builder:
    """JSON路径构建器节点"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_text": ("STRING", {"multiline": True, "default": ""}),
                "display_mode": (["层级树", "路径列表", "推荐路径"], {"default": "层级树"}),
            },
            "optional": {
                "max_depth": (["1", "2", "3", "4", "5", "全部"], {"default": "3"}),
                "filter_pattern": ("STRING", {"default": ""}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("path_info",)
    FUNCTION = "build_path_info"
    CATEGORY = "PIP/JSON"
    
    def __init__(self):
        pass
        
    def build_path_info(self, 
                      json_text: str, 
                      display_mode: str,
                      max_depth: str = "3",
                      filter_pattern: str = "") -> Tuple[str]:
        """构建JSON路径信息
        
        Args:
            json_text: JSON字符串
            display_mode: 展示模式
            max_depth: 最大层级深度
            filter_pattern: 过滤模式
            
        Returns:
            路径信息字符串
        """
        try:
            # 解析JSON
            try:
                data = json.loads(json_text)
            except json.JSONDecodeError as e:
                return (f"无效JSON格式: {str(e)}",)
            
            # 设置最大深度
            depth_limit = int(max_depth) if max_depth != "全部" else 999
            
            # 收集路径
            if display_mode == "层级树":
                result = self._build_tree_view(data, depth_limit, filter_pattern)
            elif display_mode == "路径列表":
                result = self._build_path_list(data, depth_limit, filter_pattern)
            else:  # 推荐路径
                result = self._suggest_paths(data, depth_limit, filter_pattern)
            
            return (result,)
            
        except Exception as e:
            return (f"错误: {str(e)}",)
    
    def _build_tree_view(self, data: Any, depth_limit: int, filter_pattern: str, prefix: str = "", depth: int = 0) -> str:
        """构建树状图结构"""
        if depth >= depth_limit:
            return ""
            
        lines = []
        indent = "  " * depth
        
        if isinstance(data, dict):
            for key, value in data.items():
                # 过滤模式
                if filter_pattern and filter_pattern.lower() not in key.lower():
                    continue
                    
                if isinstance(value, (dict, list)):
                    if isinstance(value, dict):
                        lines.append(f"{indent}└─ {key}: {{")  # 对象开始
                    else:
                        lines.append(f"{indent}└─ {key}: [")  # 数组开始
                        
                    next_prefix = f"{prefix}.{key}" if prefix else key
                    sub_tree = self._build_tree_view(value, depth_limit, filter_pattern, next_prefix, depth + 1)
                    if sub_tree:
                        lines.append(sub_tree)
                        
                    if isinstance(value, dict):
                        lines.append(f"{indent}  }}")  # 对象结束
                    else:
                        lines.append(f"{indent}  ]]")  # 数组结束
                else:
                    # 显示简单值的类型和概述
                    value_preview = str(value)
                    if len(value_preview) > 30:
                        value_preview = value_preview[:27] + "..."
                    lines.append(f"{indent}└─ {key}: {value_preview} ({type(value).__name__})")
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if i >= 3 and len(data) > 4:  # 仅显示前3项和最后1项
                    if i == 3:
                        lines.append(f"{indent}│ ... ({len(data)-4} more items) ...")
                    if i < len(data) - 1:
                        continue
                        
                if isinstance(item, (dict, list)):
                    lines.append(f"{indent}[{i}]: {type(item).__name__}")
                    next_prefix = f"{prefix}[{i}]"
                    sub_tree = self._build_tree_view(item, depth_limit, filter_pattern, next_prefix, depth + 1)
                    if sub_tree:
                        lines.append(sub_tree)
                else:
                    # 显示简单值
                    value_preview = str(item)
                    if len(value_preview) > 30:
                        value_preview = value_preview[:27] + "..."
                    lines.append(f"{indent}[{i}]: {value_preview} ({type(item).__name__})")
        
        return "\n".join(lines)
    
    def _build_path_list(self, data: Any, depth_limit: int, filter_pattern: str) -> str:
        """构建路径列表"""
        paths = []
        
        def collect_paths(obj, current_path="", current_depth=0):
            if current_depth >= depth_limit:
                return
                
            if isinstance(obj, dict):
                for key, value in obj.items():
                    # 过滤匹配
                    if filter_pattern and filter_pattern.lower() not in key.lower():
                        continue
                        
                    path = f"{current_path}.{key}" if current_path else key
                    
                    if isinstance(value, (dict, list)):
                        collect_paths(value, path, current_depth + 1)
                    else:
                        # 显示完整路径和值类型
                        value_type = type(value).__name__
                        paths.append(f"{path} ({value_type})")
            
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    if i >= 5:  # 数组限制显示前5项
                        paths.append(f"{current_path}[...] (省略{len(obj)-5}项)")
                        break
                        
                    path = f"{current_path}[{i}]"
                    if isinstance(item, (dict, list)):
                        collect_paths(item, path, current_depth + 1)
                    else:
                        value_type = type(item).__name__
                        paths.append(f"{path} ({value_type})")
        
        collect_paths(data)
        
        if not paths:
            return "未找到匹配的路径"
            
        return "\n".join(paths)
    
    def _suggest_paths(self, data: Any, depth_limit: int, filter_pattern: str) -> str:
        """构建推荐路径"""
        # 收集所有可能路径
        all_paths = []
        
        def collect_interesting_paths(obj, current_path="", current_depth=0):
            if current_depth >= depth_limit:
                return
                
            if isinstance(obj, dict):
                for key, value in obj.items():
                    path = f"{current_path}.{key}" if current_path else key
                    
                    # 收集"有趣"的终端路径（字符串/数字/布尔等）
                    if not isinstance(value, (dict, list)):
                        # 过滤匹配
                        if not filter_pattern or filter_pattern.lower() in key.lower():
                            path_info = {
                                "path": path,
                                "type": type(value).__name__,
                                "key": key,
                                "preview": str(value)[:30] + ("..." if len(str(value)) > 30 else ""),
                                "depth": current_depth,
                                "interesting": self._is_interesting_key(key)
                            }
                            all_paths.append(path_info)
                    else:
                        collect_interesting_paths(value, path, current_depth + 1)
            
            elif isinstance(obj, list) and len(obj) > 0:
                # 收集数组中第一个元素的路径示例
                path = f"{current_path}[0]"
                if isinstance(obj[0], (dict, list)):
                    collect_interesting_paths(obj[0], path, current_depth + 1)
                else:
                    all_paths.append({
                        "path": path,
                        "type": type(obj[0]).__name__,
                        "key": "[0]",
                        "preview": str(obj[0])[:30] + ("..." if len(str(obj[0])) > 30 else ""),
                        "depth": current_depth,
                        "interesting": False
                    })
        
        collect_interesting_paths(data)
        
        # 如果未找到路径
        if not all_paths:
            return "未找到推荐路径"
        
        # 进行排序：有趣的路径优先，其次是浅层路径
        sorted_paths = sorted(all_paths, key=lambda x: (-x["interesting"], x["depth"]))
        
        lines = ["🔍 推荐路径:"]
        
        for i, path_info in enumerate(sorted_paths[:10]):  # 只展示前10条
            icon = "⭐" if path_info["interesting"] else "•"
            lines.append(f"{icon} {path_info['path']}\n  → {path_info['preview']} ({path_info['type']})")
        
        if len(sorted_paths) > 10:
            lines.append(f"... 还有 {len(sorted_paths)-10} 条路径 ...")
            
        return "\n".join(lines)
    
    def _is_interesting_key(self, key: str) -> bool:
        """判断键名是否"有趣"（为推荐排序用）"""
        interesting_patterns = [
            "id", "name", "title", "text", "content", "value", "data", "result",
            "url", "link", "image", "picture", "photo", "description", "type",
            "status", "message", "response", "success", "error", "code"
        ]
        
        key_lower = key.lower()
        return any(pattern in key_lower for pattern in interesting_patterns)


# 节点映射
NODE_CLASS_MAPPINGS = {
    "PIP_JSON_Extractor_Pro": PIP_JSON_Extractor_Pro,
    "PIP_JSON_Path_Builder": PIP_JSON_Path_Builder,
}

# 显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "PIP_JSON_Extractor_Pro": "PIP JSON提取-Pro", 
    "PIP_JSON_Path_Builder": "PIP JSON路径分析",
}
