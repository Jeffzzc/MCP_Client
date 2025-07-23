# MCP Client

> 一个轻量级的 Python 框架，用于按照 **Model Context Protocol (MCP)** 调用本地或远程工具服务器，并与 LangGraph 的 ReAct Agent 深度集成。

## 📦 项目简介
**MCP Client** 通过 `autoagentsai.client.MCPClient` 把 MCP Server 映射成 LangChain/LangGraph 兼容工具，搭配 `create_react_agent` 即可在几行代码内跑通带工具的智能体推理循环。项目代码量 <100 行，适合作为理解 MCP 与 Agent Workflow 的最小实现。

## ✨ 主要特性
- **即插即用的 MCP 客户端**：自动发现并加载多个 MCP Server，生成 LangChain Tool。
- **多传输层支持**：内置 `stdio` 与 **Streamable HTTP**（MCP v2025‑03‑26）。
- **与 LangGraph ReAct Agent 无缝对接**：示例中演示 GPT‑4o + 工具的完整闭环。
- **完全异步**：基于 `asyncio`，高并发低延迟。
- **极简依赖**：核心仅依赖 `autoagentsai`、`langgraph` 及 OpenAI/LangChain 生态。

## 🚀 快速开始

### 环境要求
- Python ≥ 3.9
- OpenAI API Key（如需 GPT‑4o/DALL·E）
- 可选：Google Serper API Key（示例搜索）

### 安装
```bash
pip install autoagentsai langgraph langchain_openai langchain_community google-serper
````

### 克隆仓库

```bash
git clone https://github.com/Jeffzzc/MCP_Client.git
cd MCP_Client
```

### 配置环境变量

在根目录创建 `.env` 并填入：

```env
OPENAI_API_KEY=your_openai_key
SERPER_API_KEY=your_serper_key   # 可选
```

### 运行示例

> 本地数学工具 + 远程天气工具 + GPT‑4o ReAct Agent

```bash
python main.py
```

若要体验扩展示例（Serper + DALL·E）：

```bash
python test.py
```

## 🗂️ 目录结构

```
MCP_Client/
├─ autoagentsai/      # MCP Client 核心实现
├─ main.py            # 基础示例：MCP Client + ReAct Agent
├─ test.py            # 扩展示例：搜索 & 图像生成
├─ .env               # 环境变量模板
└─ LICENSE            # GPL‑3.0
```

## 🔧 依赖说明

| 库                          | 作用                          |
| -------------------------- | --------------------------- |
| **autoagentsai**           | MCP 协议客户端实现                 |
| **langgraph**              | ReAct Agent 构建与执行流          |
| **Model Context Protocol** | 工具调用统一规范                    |
| **langchain\_openai**      | ChatOpenAI + 工具调用           |
| **langchain\_community**   | Google Serper / DALL·E 工具封装 |
| **streamable-http**        | MCP Streamable HTTP 传输层     |

## 🤝 贡献指南

* 在提交 PR 前请确保：

  1. 新增/修改代码已通过测试；
  2. 同步更新文档；
  3. Commit 信息清晰、原子。
* 项目采用 **GitHub Flow** 工作流。

## 📄 License

本项目基于 **GNU GPL‑3.0** 许可证发布，详见 [LICENSE](./LICENSE)。

## 📚 参考资料

* [MCP Specification 2025‑03‑26](https://modelcontextprotocol.io/specification/2025-03-26)
* [Streamable HTTP Transport](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports)
* [LangGraph create\_react\_agent](https://langchain-ai.github.io/langgraph/reference/prebuilt/#langgraph.prebuilt.chat_agent_executor.create_react_agent)
