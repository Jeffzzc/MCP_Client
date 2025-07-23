# math_server.py
import json
import sys
import traceback

def main():
    # 定义数学工具描述（固定格式，与客户端匹配）
    tools = [
        {
            "name": "calculate",
            "description": "执行数学计算，支持加减乘除、括号优先级",
            "parameters": {
                "expression": {
                    "type": "string",
                    "description": "数学表达式，例如 '2 + 2 / 7 - 9' 或 '(5 + 3) * 2'"
                }
            }
        }
    ]
    
    print("数学服务启动成功，等待命令...", file=sys.stderr)  # 仅用于调试，不影响客户端通信
    
    while True:
        try:
            # 读取客户端命令（同步读取，更稳定）
            line = sys.stdin.readline()
            if not line:  # 客户端关闭连接
                print("客户端断开连接", file=sys.stderr)
                break
            
            command = line.strip()
            print(f"收到命令: {command}", file=sys.stderr)  # 调试信息
            
            # 处理 LIST 命令（返回工具列表）
            if command == "LIST":
                response = {
                    "tools": tools
                }
                # 输出JSON响应 + 换行符（客户端用readline()读取）
                print(json.dumps(response))
                sys.stdout.flush()  # 强制刷新，否则客户端收不到
            
            # 处理 INVOKE 命令（执行计算）
            elif command.startswith("INVOKE "):
                try:
                    # 解析参数
                    payload_str = command[len("INVOKE "):]
                    payload = json.loads(payload_str)
                    tool_name = payload["name"]
                    params = payload["parameters"]
                    
                    if tool_name == "calculate":
                        expression = params.get("expression", "")
                        # 安全计算（避免eval风险，使用简单表达式解析）
                        try:
                            # 仅允许数字和运算符，禁止函数调用
                            allowed_chars = set("0123456789+-*/(). ")
                            if not all(c in allowed_chars for c in expression):
                                raise ValueError("表达式包含不允许的字符")
                            result = eval(expression)  # 此处仅示例，生产环境需用更安全的方式
                            response = {"result": float(result)}  # 统一返回浮点数
                        except Exception as e:
                            response = {"error": f"计算错误: {str(e)}"}
                    else:
                        response = {"error": f"未知工具: {tool_name}"}
                    
                    print(json.dumps(response))
                    sys.stdout.flush()
                
                except Exception as e:
                    response = {"error": f"解析错误: {str(e)}"}
                    print(json.dumps(response))
                    sys.stdout.flush()
            
            # 处理未知命令
            else:
                response = {"error": f"未知命令: {command}，支持 LIST 或 INVOKE"}
                print(json.dumps(response))
                sys.stdout.flush()
        
        except Exception as e:
            # 捕获所有异常，确保服务不崩溃
            error_msg = f"服务内部错误: {str(e)}\n{traceback.format_exc()}"
            print(json.dumps({"error": error_msg}))
            sys.stdout.flush()
            print(error_msg, file=sys.stderr)  # 输出到 stderr 用于调试

if __name__ == "__main__":
    main()