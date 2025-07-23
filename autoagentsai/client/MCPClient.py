import asyncio
import json
import os
import traceback
from typing import Optional
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()  # load environment variables from .env

class MCPClient():
    """
    MCPClient is a client for interacting with MCP (Multi-Channel Protocol) servers.
    It allows you to initialize tools based on the MCP configuration and interact with them.
    """
    def __init__(self, tools_config):
        """
        初始化MCPClient，解析传入的工具配置。
        
        :param tools_config: 字典，包含多个工具的配置。
        """
        self.tools = {}
        
        for tool_name, tool_config in tools_config.items():
            # 解析每个工具的配置
            self.tools[tool_name] = tool_config
        
    def get_tools(self):
        """
        获取已初始化的所有工具对象列表。
        
        :return: 工具对象列表，每个对象包含name, description等属性。
        """
        tool_objects = []
        
        for tool_name, tool_config in self.tools.items():
            # 创建工具对象
            tool = type('Tool', (object,), {
                'name': tool_name,
                'description': tool_config.get('description', ''),
                'parameters': tool_config.get('parameters', {}),
                # 添加其他必要属性
            })
            tool_objects.append(tool)
        
        return tool_objects



# # autoagentsai/client.py

# import asyncio
# import subprocess
# import json
# from typing import List, Dict, Any, Union, Optional
# from langchain_core.tools import BaseTool
# import websockets
# import httpx

# class MCPClient:
#     """
#     多服务MCP客户端，支持读取配置并将不同服务转换为LangChain工具
#     """
    
#     def __init__(self, service_configs: Dict[str, Dict[str, Any]]):
#         self.service_configs = service_configs
#         self.services = {}
        
#         # 初始化各个服务
#         for service_name, config in service_configs.items():
#             transport = config.get("transport")
            
#             if transport == "stdio":
#                 self.services[service_name] = StdioServiceClient(config)
#             elif transport == "streamable_http":
#                 self.services[service_name] = StreamableHttpServiceClient(config)
#             elif transport == "websocket":
#                 self.services[service_name] = WebSocketServiceClient(config)
#             else:
#                 raise ValueError(f"Unsupported transport type '{transport}' for {service_name} service")
    
#     async def get_tools(self) -> List[BaseTool]:
#         """获取所有服务的工具列表"""
#         tools = []
        
#         for service_name, service_client in self.services.items():
#             try:
#                 service_tools = await service_client.get_tools()
#                 for tool_info in service_tools:
#                     tool = self._create_langchain_tool(service_name, tool_info)
#                     tools.append(tool)
#             except Exception as e:
#                 print(f"Error getting tools from {service_name}: {e}")
        
#         return tools
    
#     def _create_langchain_tool(self, service_name: str, tool_info: Dict[str, Any]) -> BaseTool:
#         """
#         根据工具信息创建LangChain工具对象
#         """
#         tool_name = tool_info.get("name", f"unnamed_tool_{service_name}")
#         tool_description = tool_info.get("description", f"Tool from {service_name} service")
        
#         class MCPTool(BaseTool):
#             name = f"{service_name}_{tool_name}"
#             description = tool_description
            
#             async def _arun(self, tool_input: str) -> str:
#                 return await service_client.invoke_tool(tool_name, tool_input)
            
#             def _run(self, tool_input: str) -> str:
#                 # 同步版本（如果需要）
#                 return asyncio.run(service_client.invoke_tool(tool_name, tool_input))
        
#         return MCPTool()
    
#     async def close(self) -> None:
#         """
#         关闭所有服务连接和子进程
#         """
#         # 关闭子进程
#         for service_name, process in self.processes.items():
#             if process.poll() is None:  # 如果进程还在运行
#                 process.terminate()
#                 try:
#                     process.wait(timeout=2)
#                 except subprocess.TimeoutExpired:
#                     process.kill()
#                 print(f"Closed {service_name} subprocess")
        
#         # 关闭服务客户端
#         for service_name, client in self.services.items():
#             await client.close()


# # 不同传输类型的服务客户端实现

# class StdioServiceClient:
#     """
#     通过标准输入输出与MCP服务通信的客户端
#     """
    
#     def __init__(self, config: Dict[str, Any]):
#         command = config.get("command")
#         args = config.get("args", [])
        
#         if not command:
#             raise ValueError("Missing 'command' for stdio service")
        
#         # 启动子进程
#         self.process = subprocess.Popen(
#             [command] + args,
#             stdin=subprocess.PIPE,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True
#         )
    
#     async def get_tools(self) -> List[Dict[str, Any]]:
#         """获取工具列表"""
#         # 发送获取工具的请求
#         self._send_message({"type": "get_tools"})
        
#         # 读取响应
#         response = await self._read_message()
#         return response.get("tools", [])
    
#     async def invoke_tool(self, tool_name: str, tool_input: str) -> str:
#         """调用工具"""
#         # 发送调用工具的请求
#         self._send_message({
#             "type": "invoke_tool",
#             "tool_name": tool_name,
#             "tool_input": tool_input
#         })
        
#         # 读取响应
#         response = await self._read_message()
#         return response.get("result", "")
    
#     def _send_message(self, message: Dict[str, Any]) -> None:
#         """发送JSON消息到服务"""
#         if self.process.stdin:
#             json.dump(message, self.process.stdin)
#             self.process.stdin.write('\n')
#             self.process.stdin.flush()
    
#     async def _read_message(self) -> Dict[str, Any]:
#         """异步读取服务的JSON响应"""
#         if self.process.stdout:
#             # 注意：这不是真正的异步实现，仅作示例
#             # 实际实现需要使用asyncio.subprocess或其他异步方式
#             line = self.process.stdout.readline()
#             return json.loads(line)
#         return {}
    
#     async def close(self) -> None:
#         """关闭连接"""
#         # 由主客户端处理进程关闭


# class HttpServiceClient:
#     """
#     通过HTTP与MCP服务通信的客户端
#     """
    
#     def __init__(self, base_url: str):
#         self.base_url = base_url
#         self.client = httpx.AsyncClient()
    
#     async def get_tools(self) -> List[Dict[str, Any]]:
#         """获取工具列表"""
#         response = await self.client.get(f"{self.base_url}/tools")
#         return response.json().get("tools", [])
    
#     async def invoke_tool(self, tool_name: str, tool_input: str) -> str:
#         """调用工具"""
#         response = await self.client.post(
#             f"{self.base_url}/tools/{tool_name}",
#             json={"input": tool_input}
#         )
#         return response.json().get("result", "")
    
#     async def close(self) -> None:
#         """关闭连接"""
#         await self.client.aclose()


# class WebSocketServiceClient:
#     """
#     通过WebSocket与MCP服务通信的客户端
#     """
    
#     def __init__(self, ws_url: str):
#         self.ws_url = ws_url
#         self.websocket = None
    
#     async def _ensure_connected(self) -> None:
#         """确保WebSocket连接已建立"""
#         if not self.websocket or self.websocket.closed:
#             self.websocket = await websockets.connect(self.ws_url)
    
#     async def get_tools(self) -> List[Dict[str, Any]]:
#         """获取工具列表"""
#         await self._ensure_connected()
#         await self.websocket.send(json.dumps({"type": "get_tools"}))
#         response = await self.websocket.recv()
#         return json.loads(response).get("tools", [])
    
#     async def invoke_tool(self, tool_name: str, tool_input: str) -> str:
#         """调用工具"""
#         await self._ensure_connected()
#         await self.websocket.send(json.dumps({
#             "type": "invoke_tool",
#             "tool_name": tool_name,
#             "tool_input": tool_input
#         }))
#         response = await self.websocket.recv()
#         return json.loads(response).get("result", "")
    
#     async def close(self) -> None:
#         """关闭连接"""
#         if self.websocket and not self.websocket.closed:
#             await self.websocket.close()

# class StreamableHttpServiceClient:
#     """
#     通过流式HTTP与MCP服务通信的客户端（适用于天气服务）
#     """
    
#     def __init__(self, config: Dict[str, Any]):
#         self.base_url = config.get("url")
#         if not self.base_url:
#             raise ValueError("Missing 'url' for streamable_http service")
        
#         # 确保URL格式正确
#         if not self.base_url.startswith("http"):
#             self.base_url = f"http://{self.base_url}"
        
#         # 服务端点
#         self.sse_url = f"{self.base_url}/sse"
#         self.messages_url = f"{self.base_url}/messages/"
#         self.tools_url = f"{self.base_url}/tools"
    
#     async def get_tools(self) -> List[Dict[str, Any]]:
#         """获取工具列表"""
#         try:
#             async with httpx.AsyncClient() as client:
#                 response = await client.get(self.tools_url)
#                 response.raise_for_status()
#                 return response.json().get("tools", [])
#         except Exception as e:
#             print(f"Error fetching tools: {e}")
#             # 回退方案：手动定义工具列表
#             return [
#                 {
#                     "name": "get_forecast",
#                     "description": "Get weather forecast for a location.",
#                     "parameters": {
#                         "type": "object",
#                         "properties": {
#                             "latitude": {"type": "number"},
#                             "longitude": {"type": "number"}
#                         },
#                         "required": ["latitude", "longitude"]
#                     }
#                 },
#                 {
#                     "name": "get_alerts",
#                     "description": "Get weather alerts for a US state.",
#                     "parameters": {
#                         "type": "object",
#                         "properties": {
#                             "state": {"type": "string"}
#                         },
#                         "required": ["state"]
#                     }
#                 }
#             ]
    
#     async def invoke_tool(self, tool_name: str, tool_input: str) -> str:
#         """调用工具（通过SSE协议）"""
#         try:
#             # 解析工具输入为JSON
#             params = json.loads(tool_input)
            
#             # 发送工具调用请求
#             async with httpx.AsyncClient() as client:
#                 response = await client.post(
#                     self.messages_url,
#                     json={
#                         "type": "function_call",
#                         "name": tool_name,
#                         "parameters": params
#                     }
#                 )
#                 response.raise_for_status()
            
#             # 建立SSE连接接收结果
#             sse = SSEClient(self.sse_url)
            
#             # 等待工具执行结果
#             for event in sse:
#                 if event.event == "function_call_result":
#                     data = json.loads(event.data)
#                     if data.get("name") == tool_name:
#                         return data.get("parameters", {}).get("result", "")
            
#             return "No result received from service"
            
#         except Exception as e:
#             return f"Error invoking tool: {str(e)}"