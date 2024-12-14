# MCP LLM Bridge

## 项目概述

MCP LLM Bridge 是一个创新的桥接工具，用于连接 Model Context Protocol (MCP) 服务器和兼容 OpenAI API 的大语言模型。该项目实现了 MCP 和 OpenAI function calling 接口之间的双向协议转换，使得任何兼容 OpenAI API 的语言模型都能够通过标准化接口使用 MCP 工具。

### 主要特性

- **协议转换**: 将 MCP 工具规范转换为 OpenAI 函数模式
- **双向兼容**: 支持 OpenAI API 和实现 OpenAI API 规范的本地端点
- **灵活集成**: 可与多种 LLM 服务集成，包括 OpenAI、Ollama 和 LM Studio

## 技术原理

### MCP (Model Context Protocol) 简介

MCP 是由 Anthropic 提出的一个标准协议，用于定义 AI 模型与外部工具和资源的交互方式。它包含三个核心概念：

1. **Resources（资源）**: 
   - 定义模型可访问的外部数据和状态
   - 提供标准化的数据访问接口

2. **Prompts（提示）**: 
   - 定义模型的输入格式和上下文
   - 支持动态参数和模板化

3. **Tools（工具）**: 
   - 定义模型可以调用的函数和操作
   - 提供标准化的工具调用接口

### 桥接机制

本项目通过以下方式实现 MCP 和 OpenAI API 的桥接：

1. **协议转换层**:
   - MCP Tool → OpenAI Function Schema
   - OpenAI Function Call → MCP Tool Execution

2. **会话管理**:
   - 维护 MCP 服务器连接
   - 处理 LLM API 调用

3. **数据流转**:
   ```
   MCP Server ←→ Bridge ←→ LLM API
   ```

## 快速开始

### 环境配置

1. 安装依赖：
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/bartolli/mcp-llm-bridge.git
cd mcp-llm-bridge
uv venv
source .venv/bin/activate
uv pip install -e .
```

2. 创建测试数据库：
```bash
python -m mcp_llm_bridge.create_test_db
```

### 配置选项

1. **OpenAI 配置**

创建 `.env` 文件：
```bash
OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-4 # 或其他支持工具调用的 OpenAI 模型
```

2. **Ollama 配置**
```python
llm_config=LLMConfig(
    api_key="not-needed",
    model="mistral-nemo:12b-instruct-2407-q8_0",
    base_url="http://localhost:11434/v1"
)
```

3. **LM Studio 配置**
```python
llm_config=LLMConfig(
    api_key="not-needed",
    model="local-model",
    base_url="http://localhost:1234/v1"
)
```

## 使用示例

1. 启动服务：
```bash
python -m mcp_llm_bridge.main
```

2. 示例查询：
```
"What are the most expensive products in the database?"
```

## 开发指南

### 项目结构
```
mcp-llm-bridge/
├── src/                 # 源代码
├── tests/              # 测试文件
├── References/         # MCP 相关文档
└── assets/            # 项目资源
```

### 扩展开发
1. **添加新的 LLM 支持**:
   - 实现兼容的 API 接口
   - 配置相应的 LLMConfig

2. **自定义 MCP 工具**:
   - 在 src 目录下创建新的工具定义
   - 实现工具的执行逻辑

## 测试

运行测试套件：
```bash
python -m pytest
```

## 参考资源

- [MCP Resources Documentation](https://modelcontextprotocol.io/docs/concepts/resources)
- [MCP Prompts Documentation](https://modelcontextprotocol.io/docs/concepts/prompts)
- [MCP Tools Documentation](https://modelcontextprotocol.io/docs/concepts/tools)
- [MCP Sampling Documentation](https://modelcontextprotocol.io/docs/concepts/sampling)

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE.md](LICENSE.md) 文件。
