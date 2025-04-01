import json
import re
from typing import Any, Dict, List, Tuple, Union, Optional
from difflib import SequenceMatcher


def parse_json_safely(json_str: str) -> Dict:
    """u5b89u5168u89e3u6790JSONu5b57u7b26u4e32"""
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"u65e0u6548JSONu683cu5f0f: {str(e)}")


def get_by_exact_path(data: Dict, path_parts: List[str]) -> Any:
    """u6839u636eu7cbeu786eu8defu5f84u83b7u53d6u503c"""
    current = data
    
    for part in path_parts:
        # u5904u7406u6570u7ec4u7d22u5f15u8bbfu95ee pattern: key[index]
        array_match = re.match(r"(.*?)\[(\d+)\]$", part)
        
        if array_match:  # u6570u7ec4u8bbfu95ee
            key, index = array_match.groups()
            index = int(index)
            
            if key and key in current:
                if isinstance(current[key], list) and 0 <= index < len(current[key]):
                    current = current[key][index]
                else:
                    raise KeyError(f"u65e0u6548u7684u6570u7ec4u8bbfu95ee: {key}[{index}]")
            else:
                raise KeyError(f"u952eu4e0du5b58u5728: {key}")
                
        elif part in current:  # u666eu901au952eu8bbfu95ee
            current = current[part]
            
        else:
            raise KeyError(f"u952eu4e0du5b58u5728: {part}")
    
    return current


def find_partial_match(data: Dict, target_key: str, min_similarity: float = 0.6) -> List[Tuple[str, Any, float]]:
    """u5728u5f53u524du5c42u7ea7u4e2du67e5u627eu90e8u5206u5339u914du7684u952e"""
    matches = []
    
    for key, value in data.items():
        # u4f7fu7528SequenceMatcheru8ba1u7b97u76f8u4f3cu5ea6
        similarity = SequenceMatcher(None, target_key.lower(), key.lower()).ratio()
        
        if similarity >= min_similarity:
            matches.append((key, value, similarity))
    
    # u6309u76f8u4f3cu5ea6u964du5e8fu6392u5e8f
    return sorted(matches, key=lambda x: x[2], reverse=True)


def fuzzy_search(data: Any, target_key: str, prefix: str = "", results: List[Tuple[str, Any, float]] = None) -> List[Tuple[str, Any, float]]:
    """u9012u5f52u6a21u7ccau641cu7d22u6574u4e2aJSONu4e2du7684u952e"""
    if results is None:
        results = []
    
    if isinstance(data, dict):
        # u5728u5f53u524du5c42u7ea7u4e2du67e5u627eu90e8u5206u5339u914d
        for key, value in data.items():
            current_path = f"{prefix}.{key}" if prefix else key
            similarity = SequenceMatcher(None, target_key.lower(), key.lower()).ratio()
            
            if similarity >= 0.5:  # u76f8u4f3cu5ea6u9608u503c
                results.append((current_path, value, similarity))
            
            # u9012u5f52u641cu7d22u5b50u5c42u7ea7
            if isinstance(value, (dict, list)):
                fuzzy_search(value, target_key, current_path, results)
                
    elif isinstance(data, list):
        # u9012u5f52u641cu7d22u6570u7ec4u5143u7d20
        for i, item in enumerate(data):
            current_path = f"{prefix}[{i}]" if prefix else f"[{i}]"
            if isinstance(item, (dict, list)):
                fuzzy_search(item, target_key, current_path, results)
    
    return sorted(results, key=lambda x: x[2], reverse=True)


def extract_from_json(json_str: str, 
                     path: List[str], 
                     fuzzy_mode: bool = False, 
                     min_similarity: float = 0.6) -> Tuple[str, bool, Dict]:
    """u4eceJSONu4e2du63d0u53d6u503c
    
    Args:
        json_str: JSONu5b57u7b26u4e32
        path: u8defu5f84u5217u8868 [u4e00u7ea7u952e, u4e8cu7ea7u952e, ...]
        fuzzy_mode: u662fu5426u542fu7528u6a21u7ccau641cu7d22
        min_similarity: u6700u5c0fu76f8u4f3cu5ea6u9608u503c
        
    Returns:
        u63d0u53d6u7684u503c, u662fu5426u6210u529f, u8c03u8bd5u4fe1u606f
    """
    debug_info = {
        "path": path,
        "fuzzy_mode": fuzzy_mode,
        "matches": []
    }
    
    try:
        # u89e3u6790JSON
        data = parse_json_safely(json_str)
        
        # u8fc7u6ee4u6389u7a7au8defu5f84u6bb5
        path = [p for p in path if p and p.strip()]
        
        # u6a21u7ccau641cu7d22u6a21u5f0f
        if fuzzy_mode and path:
            target_key = path[-1]  # u53d6u8defu5f84u7684u6700u540eu4e00u90e8u5206u4f5cu4e3au641cu7d22u76eeu6807
            matches = fuzzy_search(data, target_key)
            
            debug_info["matches"] = [
                {"path": m[0], "similarity": f"{m[2]:.2f}"} 
                for m in matches[:5]  # u53eau8bb0u5f55u524d5u4e2au5339u914d
            ]
            
            if matches:
                best_match = matches[0]
                result = best_match[1]  # u53d6u76f8u4f3cu5ea6u6700u9ad8u7684u503c
                return str(result), True, debug_info
            else:
                return "", False, debug_info
        
        # u7cbeu786eu5339u914du6a21u5f0f
        elif path:  
            try:
                # u5148u5c1du8bd5u5b8cu6574u8defu5f84u7cbeu786eu5339u914d
                result = get_by_exact_path(data, path)
                debug_info["matches"] = [{"path": ".".join(path), "exact": True}]
                return str(result), True, debug_info
            except KeyError:
                # u5982u679cu7cbeu786eu5339u914du5931u8d25uff0cu5c1du8bd5u90e8u5206u8defu5f84u5339u914d
                current = data
                remaining_path = path.copy()
                matched_path = []
                
                while remaining_path:
                    current_key = remaining_path[0]
                    remaining_path = remaining_path[1:]
                    
                    # u5904u7406u6570u7ec4u7d22u5f15
                    array_match = re.match(r"(.*?)\[(\d+)\]$", current_key)
                    if array_match:
                        key, index = array_match.groups()
                        index = int(index)
                        
                        if key in current and isinstance(current[key], list) and 0 <= index < len(current[key]):
                            matched_path.append(current_key)
                            current = current[key][index]
                            continue
                    
                    # u76f4u63a5u952eu5339u914d
                    if current_key in current:
                        matched_path.append(current_key)
                        current = current[current_key]
                        continue
                    
                    # u5982u679cu6ca1u6709u76f4u63a5u5339u914duff0cu5c1du8bd5u90e8u5206u5339u914d
                    matches = find_partial_match(current, current_key, min_similarity)
                    
                    if matches:
                        best_match = matches[0]
                        debug_info["matches"].append({
                            "partial_key": current_key,
                            "matched_to": best_match[0],
                            "similarity": f"{best_match[2]:.2f}"
                        })
                        matched_path.append(best_match[0])
                        current = best_match[1]
                    else:
                        # u5982u679cu5f53u524du5c42u6ca1u6709u5339u914duff0cu8df3u8fc7u5e76u5c1du8bd5u4e0bu4e00u4e2au952e
                        continue
                        
                # u5982u679cu6210u529fu5339u914du4e86u81f3u5c11u4e00u90e8u5206u8defu5f84
                if matched_path:
                    debug_info["matches"].append({"final_path": ".".join(matched_path)})
                    return str(current), True, debug_info
                else:
                    return "", False, debug_info
        else:
            # u65e0u6548u8defu5f84
            return "", False, {"error": "u672au63d0u4f9bu6709u6548u8defu5f84"}
    
    except Exception as e:
        return "", False, {"error": str(e)}
