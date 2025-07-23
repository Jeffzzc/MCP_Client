from typing import Any, Optional
from starlette.responses import JSONResponse
import httpx
from mcp.server.fastmcp import FastMCP
from mcp.server import Server  
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
from starlette.routing import Mount, Route
import uvicorn


class WeatherServer(Server):
    """天气服务类，继承自mcp的Server基类，封装天气相关工具和服务逻辑"""
    
    def __init__(self, service_name: str = "weather"):
        super().__init__(service_name)  # 调用父类初始化
        self.mcp = FastMCP(service_name)  # 初始化FastMCP实例
        self._register_tools()  # 注册天气工具
        
        # 常量定义（移至类内作为属性，便于维护）
        self.NWS_API_BASE = "https://api.weather.gov"
        self.USER_AGENT = "weather-app/1.0"

    def _register_tools(self) -> None:
        """注册天气相关工具（get_alerts和get_forecast）"""
        # 用类方法注册工具，绑定到当前实例
        @self.mcp.tool()
        async def get_alerts(state: str) -> str:
            """Get weather alerts for a US state.
            
            Args:
                state: Two-letter US state code (e.g. CA, NY)
            """
            return await self._get_alerts_impl(state)

        @self.mcp.tool()
        async def get_forecast(latitude: float, longitude: float) -> str:
            """Get weather forecast for a location.
            
            Args:
                latitude: Latitude of the location
                longitude: Longitude of the location
            """
            return await self._get_forecast_impl(latitude, longitude)

    async def _make_nws_request(self, url: str) -> Optional[dict[str, Any]]:
        """内部工具方法：向NWS API发送请求（封装复用）"""
        headers = {
            "User-Agent": self.USER_AGENT,
            "Accept": "application/geo+json"
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=30.0)
                response.raise_for_status()
                return response.json()
        except Exception:
            return None

    @staticmethod
    def _format_alert(feature: dict) -> str:
        """格式化天气警报信息"""
        props = feature["properties"]
        return f"""
        Event: {props.get('event', 'Unknown')}
        Area: {props.get('areaDesc', 'Unknown')}
        Severity: {props.get('severity', 'Unknown')}
        Description: {props.get('description', 'No description available')}
        Instructions: {props.get('instruction', 'No specific instructions provided')}
        """

    async def _get_alerts_impl(self, state: str) -> str:
        """获取天气警报的具体实现（内部调用）"""
        url = f"{self.NWS_API_BASE}/alerts/active/area/{state}"
        data = await self._make_nws_request(url)

        if not data or "features" not in data:
            return "Unable to fetch alerts or no alerts found."
        if not data["features"]:
            return "No active alerts for this state."

        alerts = [self._format_alert(feature) for feature in data["features"]]
        return "\n---\n".join(alerts)

    async def _get_forecast_impl(self, latitude: float, longitude: float) -> str:
        """获取天气预报的具体实现（内部调用）"""
        # 先获取预报网格端点
        points_url = f"{self.NWS_API_BASE}/points/{latitude},{longitude}"
        points_data = await self._make_nws_request(points_url)
        if not points_data:
            return "Unable to fetch forecast data for this location."

        # 再获取具体预报
        forecast_url = points_data["properties"]["forecast"]
        forecast_data = await self._make_nws_request(forecast_url)
        if not forecast_data:
            return "Unable to fetch detailed forecast."

        # 格式化预报信息（取前5个时段）
        periods = forecast_data["properties"]["periods"]
        forecasts = []
        for period in periods[:5]:
            forecast = f"""
            {period['name']}:
            Temperature: {period['temperature']}°{period['temperatureUnit']}
            Wind: {period['windSpeed']} {period['windDirection']}
            Forecast: {period['detailedForecast']}
            """
            forecasts.append(forecast)
        return "\n---\n".join(forecasts)

    def get_mcp_server(self):
        """获取内部的mcp服务器实例，用于启动服务"""
        return self.mcp._mcp_server  # 暴露内部服务实例（保持原有逻辑）


def create_starlette_app(weather_server: WeatherServer, *, debug: bool = False) -> Starlette:
    """创建Starlette应用，绑定天气服务的SSE通信"""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,  # noqa: SLF001
        ) as (read_stream, write_stream):
            await weather_server.get_mcp_server().run(
                read_stream,
                write_stream,
                weather_server.get_mcp_server().create_initialization_options(),
            )
    
    # 修复工具列表端点
    async def handle_tools(request: Request) -> JSONResponse:
        # 获取工具列表的正确方式（根据mcp库API调整）
        try:
            # 使用反射获取工具列表（假设存在get_tools方法）
            tool_manager = weather_server.get_mcp_server()
            tools_method = getattr(tool_manager, "get_tools", None)
            
            if callable(tools_method):
                tools = tools_method()
            else:
                # 回退方案：手动定义工具
                tools = [
                    {
                        "name": "get_forecast",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "latitude": {"type": "number"},
                                "longitude": {"type": "number"}
                            },
                            "required": ["latitude", "longitude"]
                        },
                        "description": "Get weather forecast for a location."
                    },
                    {
                        "name": "get_alerts",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "state": {"type": "string"}
                            },
                            "required": ["state"]
                        },
                        "description": "Get weather alerts for a US state."
                    }
                ]
            
            return JSONResponse({"tools": tools})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
            Route("/tools", endpoint=handle_tools),  # 工具列表端点
        ],
    )

if __name__ == "__main__":
    # 实例化天气服务（现在可以被其他模块导入的WeatherServer）
    weather_server = WeatherServer()

    import argparse
    parser = argparse.ArgumentParser(description='Run Weather MCP SSE Server')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8888, help='Port to listen on')
    args = parser.parse_args()

    # 创建并启动应用
    starlette_app = create_starlette_app(weather_server, debug=True)
    uvicorn.run(starlette_app, host=args.host, port=args.port)