# JSON 完全指官

## 1. 基础概念
### 1.1 数据快递单
就像网购填写的快递单，JSON是用于系统间传递信息的标准格式：

```json
{
  "快递单号": "SF123456789",
  "寄件人": {
    "姓名": "张三",
    "联系方式": {
      "手机": "138-1234-5678",
      "微信": "tech_zhang"
    }
  },
  "物品清单": ["手机", "充电宝", "耳机"]
}
```

### 1.2 核心组成
**键(Key)**  
- 数据项名称（必须用双引号）  
- 示例：`"用户名"`、`"订单号"`

**值(Value)**  
- 支持7种数据类型：
  ```json
  {
    "字符串": "文本内容",
    "数字": 3.14,
    "布尔值": true,
    "空值": null,
    "对象": {"嵌套": "数据"},
    "数组": [1, 2, 3],
    "特殊值": "NaN/Infinity"
  }
  ```

## 2. 格式规范
### 正确写法
```json
{
  "appConfig": {
    "theme": "dark",
    "fontSize": 14,
    "components": ["header", "footer"]
  },
  "lastLogin": "2024-03-15T08:30:00Z"
}
```

### 常见错误
| 错误类型 | 错误示例 | 修正方案 |
|---------|---------|---------|
| 单引号 | `'key': 'value'` | 改用双引号 |
| 尾部逗号 | `"age": 25,` | 删除最后一个逗号 |
| 注释 | `// 用户ID` | JSON不支持注释 |
| 十六进制 | `"color": #FF0000` | 改用字符串 |

## 3. 实战应用
### 3.1 API交互
```json
// 请求示例
{
  "apiVersion": "1.0",
  "method": "user/login",
  "params": {
    "username": "tech_guy",
    "password": "******"
  }
}

// 响应示例
{
  "code": 200,
  "data": {
    "userId": 12345,
    "token": "abcd1234efgh"
  },
  "timestamp": 1712000000
}
```

### 3.2 配置文件
```json
{
  "database": {
    "host": "localhost",
    "port": 3306,
    "credentials": {
      "username": "admin",
      "password": "securePass123"
    }
  },
  "logging": {
    "level": "debug",
    "retentionDays": 30
  }
}
```

## 4. 进阶技巧
### 4.1 数据嵌套
三层嵌套示例：
```json
{
  "学校": {
    "班级": [
      {
        "班主任": "王老师",
        "学生": [
          {
            "姓名": "小明",
            "成绩": {
              "数学": 95,
              "语文": 88
            }
          }
        ]
      }
    ]
  }
}
```

### 4.2 格式校验
推荐工具：
- [JSONLint](https://jsonlint.com)
- VSCode JSON验证插件
- Postman 自动格式化

> 最佳实践：始终使用2空格缩进，键名采用camelCase命名，字符串值使用双引号。

## 5. 伪JSON详解

### 5.1 常见伪JSON形式

```javascript
// 典型伪JSON示例
{
  'user': '张三',            // 单引号
  age: 25,                  // 无引号key
  hobbies: [ "篮球", /* 主要爱好 */ "游戏" ],  // 包含注释
  vip: true,                // 正确格式
  "lastLogin": "2024-01-01", // 正确格式
  "tags": ["new", ]        // 尾部逗号
}
```

### 5.2 伪JSON危害

| 类型        | 后果示例                  | 解决方案               |
|------------|-------------------------|----------------------|
| 单引号      | 解析器报错               | 双引号自动转换工具       |
| 无引号key   | 数据丢失                 | 严格模式校验           |
| 注释        | 解析中断                 | 使用专用配置字段         |
| 十六进制     | 类型错误                 | 字符串存储+转换逻辑     |

### 5.3 转换工具

```python
# Python转换示例
import json
from jsoncomment import JsonComment

parser = JsonComment()
with open('pseudo.json') as f:
    data = parser.load(f)  # 支持含注释的JSON解析
    valid_json = json.dumps(data, ensure_ascii=False)
```

## 6. 数据嵌套（增强）

### 6.1 层级划分标准

```json
{
  // 第一层：根对象
  "学校": {  // 第二层：嵌套对象
    "班级": [  // 第三层：数组
      {  // 第四层：数组元素对象
        "班主任": "王老师",
        "学生": [  // 第五层：嵌套数组
          {  // 第六层：学生对象
            "成绩": {  // 第七层：成绩对象
              "数学": 95
            }
          }
        ]
      }
    ]
  }
}
```

### 6.2 访问路径示例

| 层级 | 访问路径                     | 示例值     |
|------|----------------------------|-----------|
| L1   | $.学校                     | { ... }   |
| L3   | $.学校.班级[0]             | 班级对象   |
| L5   | $.学校.班级[0].学生[0]     | 学生对象   |
| L7   | $.学校.班级[0].学生[0].成绩.数学 | 95       |

### 6.3 调试技巧

```javascript
// Chrome控制台调试
let data = JSON.parse(jsonStr);
console.log('%c嵌套结构', 'color:blue', JSON.stringify(data, null, 2));

// 断点调试建议
debugger; // 在关键层级设置断点
```

## 7. 可视化工具

### 7.1 推荐工具对比

| 工具名称       | 嵌套可视化         | 格式校验 | 在线地址                  |
|---------------|-------------------|---------|--------------------------|
| JSON Crack    | 树状图+缩进       | ✔️      | [jsoncrack.com](https://jsoncrack.com) |
| JSON Hero     | 交互式导航        | ✔️      | [jsonhero.io](https://jsonhero.io)   |
| VSCode插件     | 大纲视图          | ✔️      | 内置插件市场              |

![嵌套可视化示例](https://example.com/nested-json-vis.png)

> 🛠️ 最佳实践：当嵌套超过5层时，建议进行数据结构优化