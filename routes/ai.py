from flask import Blueprint, jsonify, session
import os
import sys
import asyncio
from openai import AsyncOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ai_bp = Blueprint('ai', __name__)

async def call_ai_agent(user_id):
    if not os.getenv('OPENAI_API_KEY'):
        return "伺服器未設定 OPENAI_API_KEY，無法呼叫 AI。"
        
    client = AsyncOpenAI()
    
    mcp_server_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'mcp_server.py')
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[mcp_server_path],
        env=os.environ.copy()
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as mcp_session:
            await mcp_session.initialize()
            
            tools_response = await mcp_session.list_tools()
            available_tools = [{ 
                "type": "function", 
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.inputSchema
                }
            } for t in tools_response.tools]
            
            messages = [
                {"role": "system", "content": "你是一個專業的健康顧問 AI。請調用工具取得該用戶的個人資料、血壓紀錄與姿勢狀態。如果職業為長期久坐的工程師且有圓肩現象，結合血壓數據，請給出針對性的伸展與作息建議。回答要求專業、精簡。"},
                {"role": "user", "content": f"請針對 user_id={user_id} 分析並提出綜合健康建議。"}
            ]
            
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=available_tools
            )
            
            message = response.choices[0].message
            msg_dict = {"role": message.role, "content": message.content}
            if message.tool_calls:
                msg_dict["tool_calls"] = [{
                    "id": tc.id,
                    "type": tc.type,
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                } for tc in message.tool_calls]
            messages.append(msg_dict)
            
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    import json
                    args = json.loads(tool_call.function.arguments)
                    
                    result = await mcp_session.call_tool(tool_call.function.name, arguments=args)
                    tool_result_text = "\n".join([c.text for c in result.content if c.type == 'text'])
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result_text
                    })
                
                final_response = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages
                )
                return final_response.choices[0].message.content
            else:
                return message.content

@ai_bp.route('/api/ai_advice')
def ai_advice():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
        
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        advice = loop.run_until_complete(call_ai_agent(user_id))
        return jsonify({'success': True, 'advice': advice})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500
