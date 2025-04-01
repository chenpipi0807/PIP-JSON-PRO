import json
import ast
import demjson3
from jsoncomment import JsonComment
from typing import Tuple, Dict, Any, Optional, Union
from ..utils.json_utils import (
    normalize_json, 
    apply_format_style,
    detect_encoding
)


class JSONProcessor:
    """u5904u7406u5404u7c7bu4f2aJSONu683cu5f0fu7684u6838u5fc3u5904u7406u5668u7c7b"""
    
    def __init__(self):
        self.parser = JsonComment()
        self.debug_info = {}
        
    def process(self, 
               input_text: str, 
               repair_level: int = 2,
               indent: int = 2,
               pretty_print: bool = True,
               sort_keys: bool = False) -> Tuple[str, bool, Dict[str, Any]]:
        """u5904u7406JSONu6587u672c
        
        Args:
            input_text: u8f93u5165u7684JSONu6587u672c
            repair_level: u4feeu590du7ea7u522b (1=u57fau7840, 2=u6807u51c6, 3=u9ad8u7ea7)
            indent: u7f29u8fdbu7a7au683cu6570
            pretty_print: u662fu5426u7f8eu5316u8f93u51fa
            sort_keys: u662fu5426u6309u952eu6392u5e8f
            
        Returns:
            u5904u7406u540eu7684JSONu5b57u7b26u4e32, u662fu5426u6210u529f, u8c03u8bd5u4fe1u606f
        """
        if not input_text or not input_text.strip():
            return "", False, {"error": "u7a7au8f93u5165"}
            
        # u8bb0u5f55u539fu59cbu8f93u5165
        self.debug_info = {
            "original_length": len(input_text),
            "original_preview": input_text[:100] + ("..." if len(input_text) > 100 else ""),
            "repair_methods": []
        }
        
        # u5c1du8bd5u5404u79cdu4feeu590du65b9u6cd5
        result, success = self._try_repair_methods(input_text, repair_level)
        
        # u7f8eu5316u683cu5f0fu5316
        if success and pretty_print:
            result = apply_format_style(result, indent, sort_keys)
            
        # u8bb0u5f55u7ed3u679cu4fe1u606f
        self.debug_info.update({
            "success": success,
            "final_length": len(result),
            "final_preview": result[:100] + ("..." if len(result) > 100 else "")
        })
        
        return result, success, self.debug_info
    
    def _try_repair_methods(self, text: str, repair_level: int) -> Tuple[str, bool]:
        """u6309u987au5e8fu5c1du8bd5u4e0du540cu7684u4feeu590du65b9u6cd5"""
        methods = [
            self._try_direct_parse,
            self._try_normalize,
            self._try_jsoncomment,
            self._try_demjson,
            self._try_ast_eval
        ]
        
        # u6839u636eu4feeu590du7ea7u522bu9650u5236u5c1du8bd5u7684u65b9u6cd5
        methods_to_try = methods[:1 + repair_level]  # u81f3u5c11u5c1du8bd5u76f4u63a5u89e3u6790
        
        for method in methods_to_try:
            try:
                result, success = method(text)
                if success:
                    self.debug_info["repair_methods"].append(method.__name__)
                    return result, True
            except Exception as e:
                # u8bb0u5f55u9519u8befu4f46u7ee7u7eedu5c1du8bd5
                pass
        
        # u6240u6709u65b9u6cd5u90fdu5931u8d25
        return text, False
    
    def _try_direct_parse(self, text: str) -> Tuple[str, bool]:
        """u5c1du8bd5u76f4u63a5u89e3u6790JSON"""
        try:
            parsed = json.loads(text)
            return json.dumps(parsed, ensure_ascii=False), True
        except:
            raise Exception("Direct parse failed")
    
    def _try_normalize(self, text: str) -> Tuple[str, bool]:
        """u4f7fu7528u89c4u8303u5316u51fdu6570u5c1du8bd5u4feeu590d"""
        normalized, success = normalize_json(text, repair_level=3)
        if not success:
            raise Exception("Normalize failed")
        return normalized, True
    
    def _try_jsoncomment(self, text: str) -> Tuple[str, bool]:
        """u5c1du8bd5u4f7fu7528JsonCommentu89e3u6790"""
        parsed = self.parser.loads(text)
        return json.dumps(parsed, ensure_ascii=False), True
    
    def _try_demjson(self, text: str) -> Tuple[str, bool]:
        """u5c1du8bd5u4f7fu7528demjsonu89e3u6790"""
        parsed = demjson3.decode(text)
        return json.dumps(parsed, ensure_ascii=False), True
    
    def _try_ast_eval(self, text: str) -> Tuple[str, bool]:
        """u5c1du8bd5u4f7fu7528Python ASTu8bc4u4f30"""
        # u6dfbu52a0u5916u5c42u82b1u62ecu53f7uff0cu5982u679cu4e0du5b58u5728
        if not text.strip().startswith('{') and not text.strip().startswith('['):
            text = '{' + text + '}'
        
        # u5c1du8bd5u5c06u6240u6709u4e0du7b26u5408JSONu7684u5355u5f15u53f7u66ffu6362u4e3au53ccu5f15u53f7
        text = text.replace("'", '"')
        
        # u5c1du8bd5u4f7fu7528ast.literal_evalu89e3u6790
        parsed = ast.literal_eval(text)
        return json.dumps(parsed, ensure_ascii=False), True
