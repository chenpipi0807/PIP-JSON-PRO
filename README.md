# PIP-JSON-PRO

## 什么是PIP-JSON-PRO

PIP-JSON-PRO是一套专业级的ComfyUI JSON处理节点，专为处理AI大语言模型生成的各种JSON数据而设计。它能解决LLM输出的JSON常见问题，如引号不匹配、多余逗号、缺少引号等格式错误，并提供强大的数据提取和分析功能。

![微信截图_20250401202446](https://github.com/user-attachments/assets/204a2dc6-c23f-43eb-bb08-a461da9c2603)

## PIP-JSON-PRO的优势

相比一般的JSON处理工具，PIP-JSON-PRO具有以下优势：

* 处理和分析JSON数据
* 支持多种数据格式转换
* 提供高性能和高效的数据处理能力

## 用法

### 基本使用方法

1. 将PIP-JSON-PRO节点拖拽到ComfyUI工作区
2. 配置节点的输入和输出参数
3. 点击运行按钮即可开始处理数据

## PIP-JSON-PRO的特点

PIP-JSON-PRO节点具有以下特点：

* 高性能和高效的数据处理能力
* 支持多种数据格式转换
* 易于使用和配置
* 可以与其他ComfyUI节点集成使用

## 节点详细说明

### 1. PIP JSON处理-Pro

这个节点用于处理和纠正LLM输出的各种JSON格式问题，确保JSON可以被正确解析和使用。

#### JSON处理节点参数

* 输入文本：需要处理的JSON文本
* 处理模式：
  * 标准模式：处理常见的格式错误（引号不匹配、多余逗号等）
  * 兼容模式：处理更复杂的格式错误（如JavaScript注释等）
  * 严格模式：严格按照JSON标准处理，可能会丢失一些信息
* 输出格式：是否输出格式化的JSON
* 缩进大小：输出格式化JSON的缩进大小
* 排序方式：是否对输出的JSON进行排序
* 测试模式：测试处理过程中的错误

### 2. PIP JSON提取-Pro

这个节点用于从JSON中提取特定的值，支持多层级的键值对提取和数组索引提取。

#### JSON提取节点参数

* JSON文本：需要提取的JSON文本
* 提取模式：
  * 键值对：提取键值对中的值
  * 数组索引：提取数组中的值
* 键名1-5：需要提取的键名
* 数组长度：提取数组中的值的长度
* 测试模式：测试提取过程中的错误

### 3. PIP JSON分解

这个节点用于将JSON分解为不同的部分，方便查看和分析JSON的结构。

#### JSON分解节点参数

* JSON文本：需要分解的JSON文本
* 分解模式：
  * 树状结构：显示JSON的树状结构
  * 键值对列表：显示JSON的键值对列表
  * 数组索引：显示JSON的数组索引
* 最大深度：分解的最大深度
* 过滤模式：过滤不需要的键值对

### 4. PIP JSON预览

这个节点用于预览JSON，支持多种预览模式，方便查看JSON的内容和结构。

#### JSON预览节点参数

* JSON文本：需要预览的JSON文本
* 预览模式：
  * 美化：美化JSON格式
  * 压缩：压缩JSON格式
  * 格式化：格式化JSON格式
* 缩进大小：预览JSON的缩进大小

## 常见使用场景

1. 配合LLM输出：当你使用大语言模型生成JSON数据时，可能会遇到格式问题，使用PIP JSON处理-Pro可以轻松修复这些问题
2. 数据分析：从复杂的JSON中提取特定的值，使用PIP JSON提取-Pro可以轻松完成
3. 数据可视化：使用PIP JSON分解和PIP JSON预览可以更好地理解JSON的结构和内容

## 安装

```bash
cd 你的ComfyUI\custom_nodes
git clone https://github.com/chenpipi0807/PIP-JSON-PRO.git
pip install jsoncomment demjson3 chardet
```

## 许可证

MIT
