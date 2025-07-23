# from langchain.agents import AgentExecutor, create_openai_functions_agent
# from langchain.chat_models import init_chat_model
# from langchain.prompts import PromptTemplate
# from langchain_core.tools import BaseTool

# # 初始化LLM
# llm = init_chat_model("openai:gpt-4o")  # 注意：原代码中的"gpt-4.1"可能不是有效型号，这里修正为gpt-4o（可根据实际情况调整）

# def create_react_agent(llm: init_chat_model, tools: list[BaseTool]):
#     """创建用AgentExecutor包装的ReAct agent"""
#     # 提示词模板（包含agent_scratchpad）
#     prompt_template = """Answer the following questions as best you can. You have access to the following tools:

#     {tools}

#     Use the following format:
#     Question: {input}
#     Thought: You should always think about what to do
#     Action: The action to take, should be one of [{tool_names}]
#     Action Input: The input to the action
#     Observation: The result of the action
#     ...（可重复Thought/Action/Action Input/Observation）
#     Thought: I now know the final answer
#     Final Answer: The final answer to the original input question

#     Begin!

#     # 中间思考区域
#     {agent_scratchpad}

#     Question: {input}
#     """

#     # 格式化工具信息
#     tools_description = "\n".join([f"{tool.name}: {tool.description}" for tool in tools])
#     tool_names = ", ".join([tool.name for tool in tools])
    
#     # 声明提示词模板（包含必要变量）
#     prompt = PromptTemplate(
#         template=prompt_template,
#         input_variables=["input", "agent_scratchpad", "tools", "tool_names"]
#     )
#     prompt = prompt.partial(tools=tools_description, tool_names=tool_names)

#     # 创建agent并使用AgentExecutor包装
#     agent = create_openai_functions_agent(llm, tools, prompt)
#     return AgentExecutor(agent=agent, tools=tools, verbose=True)  # 关键：用Executor包装

# # 示例用法
# async def main():
#     # 初始化工具（示例为空，可替换为实际工具）
#     tools = []
    
#     # 创建带Executor的agent
#     agent_executor = create_react_agent(llm, tools)
    
#     # 通过Executor调用（而非直接调用agent）
#     res = await agent_executor.ainvoke({"input": "What is 1 + 6 / 9?"})
#     print("Answer:", res["output"])

# # 运行异步函数
# import asyncio
# asyncio.run(main())


# autoagentsai/prebuilt/create_react_agent.py

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.chat_models import ChatOpenAI  # 直接导入ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.tools import BaseTool

from langchain.tools import BaseTool
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI

def create_react_agent(llm_model: str, tools: list):
    """
    创建ReAct agent，支持传入LLM模型名称和工具列表
    
    Args:
        llm_model: LLM模型名称（如"gpt-4o"或"openai:gpt-4o"）
        tools: 工具列表（可以是BaseTool实例或包含name/description属性的对象）
    """
    # 解析模型名称（处理"openai:"前缀）
    if llm_model.startswith("openai:"):
        model_name = llm_model[7:]  # 去掉"openai:"前缀
    else:
        model_name = llm_model
    
    # 初始化LLM
    llm = ChatOpenAI(
        model_name=model_name,
        temperature=0,  # 设置温度为0，使输出更确定
        verbose=True    # 启用详细日志
    )
    
    # 构建提示词模板
    prompt_template = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: {input}
Thought: You should always think about what to do
Action: The action to take, should be one of [{tool_names}]
Action Input: The input to the action
Observation: The result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: The final answer to the original input question

Begin!

{agent_scratchpad}

Question: {input}
"""

    # 确保工具是BaseTool类型
    processed_tools = []
    for tool in tools:
        if isinstance(tool, BaseTool):
            processed_tools.append(tool)
        else:
            # 将普通对象转换为FunctionTool
            processed_tools.append(
                FunctionTool(
                    name=getattr(tool, "name", "unknown"),
                    description=getattr(tool, "description", ""),
                    func=lambda *args, **kwargs: getattr(tool, "run", lambda *a, **kw: "Tool execution not implemented")(*args, **kwargs),
                    parameters=getattr(tool, "parameters", {})
                )
            )
    
    # 格式化工具描述和名称
    tools_description = "\n".join([f"{tool.name}: {tool.description}" for tool in processed_tools])
    tool_names = ", ".join([tool.name for tool in processed_tools])
    
    # 创建提示词
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["input", "agent_scratchpad", "tools", "tool_names"]
    )
    prompt = prompt.partial(tools=tools_description, tool_names=tool_names)

    # 创建agent
    agent = create_openai_functions_agent(llm, processed_tools, prompt)

    return AgentExecutor(agent=agent, tools=processed_tools, verbose=True)

# 辅助类：用于将普通对象转换为LangChain工具
class FunctionTool(BaseTool):
    name: str
    description: str
    func: callable
    parameters: dict = {}
    
    def _run(self, *args, **kwargs) -> str:
        return self.func(*args, **kwargs)
    
    async def _arun(self, *args, **kwargs) -> str:
        return self.func(*args, **kwargs)